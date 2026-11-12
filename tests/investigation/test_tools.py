"""Actual bound mock invocations and conservative evidence/error history."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
from decimal import Decimal
import json

import pytest
from langchain_core.tools import StructuredTool

from payment_ops.connectors.base import (
    AccountResponse, AccountStatus, ConnectorError, FraudDecision, FraudResponse,
    LimitsResponse, RecordNotFoundError, SanctionsResponse,
)
from payment_ops.investigation.state import ToolPolicyError, record_tool_attempt
from payment_ops.investigation.tools import TOOLS, InvestigationTools, lookup_payment
from payment_ops.samples.payments import SYNTHETIC_PAYMENTS


@pytest.mark.parametrize("payment", SYNTHETIC_PAYMENTS, ids=lambda p: p.payment_id)
def test_deterministic_lookup_returns_existing_immutable_payment(payment):
    assert lookup_payment(payment.payment_id) is payment


def test_lookup_records_attempt_and_preserves_input_state(make_run):
    state, tools = make_run()
    before = deepcopy(state)
    updated = tools.lookup_payment(state, request_id="lookup")
    assert state == before
    assert updated["tool_attempt_count"] == 1
    assert updated["phase"] == "collecting"
    assert updated["payment_snapshot"]["amount"] == "12500.50"
    assert updated["payment_snapshot"]["payment_date"] == "2026-10-12"
    assert updated["tool_attempts"][0]["tool_name"] == "lookup_payment"
    assert updated["tool_attempts"][0]["success"]
    assert updated["remaining_controls"] == list(TOOLS.values())
    assert tools.lookup_payment(updated, request_id="lookup") == updated
    with pytest.raises(ToolPolicyError, match="payment_lookup_already_attempted"):
        tools.lookup_payment(updated, request_id="new-lookup")


@pytest.mark.parametrize("payment_id", ["unknown", "SYNTHETIC-WIRE-001 "])
def test_unknown_lookup_fails_safely_and_consumes_one_attempt(make_run, connectors, payment_id):
    state, tools = make_run(payment_id)
    updated = tools.lookup_payment(state, request_id="lookup")
    assert updated["phase"] == "failed" and updated["outcome_reason"] == "invalid_selection"
    assert updated["tool_attempt_count"] == 1
    assert updated["current_evidence"] == {} and updated["payment_snapshot"] is None
    assert updated["errors"][0]["category"] == "invalid_selection"
    with pytest.raises(ToolPolicyError):
        tools.invoke(updated, "get_fraud_evidence", request_id="fraud")
    assert all(not c.mock_calls for c in connectors.values())


@pytest.mark.parametrize("payment", SYNTHETIC_PAYMENTS[15:19], ids=lambda p: p.payment_id)
def test_invalid_payment_input_skips_connectors(make_run, connectors, payment):
    state, tools = make_run(payment.payment_id)
    state = tools.lookup_payment(state, request_id="lookup")
    assert state["input_errors"] and state["phase"] == "summarizing"
    for name in TOOLS:
        with pytest.raises(ToolPolicyError, match="invalid_payment_input"):
            tools.invoke(state, name, request_id=name)
    assert all(not c.mock_calls for c in connectors.values())
    assert state["tool_attempt_count"] == 1


def test_four_wrappers_call_actual_methods_with_bound_arguments(make_run, connectors, monkeypatch):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    invoked = []
    original = StructuredTool.invoke

    def observe(tool, arguments, *args, **kwargs):
        invoked.append((tool.name, arguments))
        return original(tool, arguments, *args, **kwargs)

    monkeypatch.setattr(StructuredTool, "invoke", observe)
    for name in TOOLS:
        state = tools.invoke(state, name, request_id=name)
    payment = SYNTHETIC_PAYMENTS[0]
    connectors["core"].get_account.assert_called_once_with(payment.sender_account_id)
    connectors["limits"].get_limit.assert_called_once_with(payment.sender_account_id)
    connectors["fraud"].screen.assert_called_once_with(payment.payment_id)
    connectors["sanctions"].screen.assert_called_once_with(payment)
    assert invoked == [(name, {}) for name in TOOLS]
    assert state["tool_attempt_count"] == 5
    assert state["remaining_controls"] == state["failed_controls"] == state["unresolved_controls"] == []
    assert state["completed_controls"] == list(TOOLS.values())
    assert state["current_evidence"]["core"]["result"] == {
        "account_status": "ACTIVE", "available_balance": "100000.00", "wire_payments_enabled": True,
    }
    assert state["current_evidence"]["limits"]["result"] == {"single_wire_limit": "50000.00"}
    assert state["current_evidence"]["fraud"]["result"] == {"score": 10, "decision": "PASS"}
    assert state["current_evidence"]["sanctions"]["result"] == {"result": "CLEAR"}
    assert json.loads(json.dumps(state, allow_nan=False)) == state
    assert payment is lookup_payment(payment.payment_id)
    with pytest.raises(FrozenInstanceError):
        payment.amount = Decimal("1")


@pytest.mark.parametrize("key,value", [("payment_id", "different"), ("run_id", "other"), ("thread_id", "other")])
def test_identity_changes_are_refused(make_run, connectors, key, value):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    state[key] = value
    with pytest.raises(ToolPolicyError, match="run_binding_mismatch"):
        tools.invoke(state, "get_core_evidence", request_id="core")
    assert not connectors["core"].mock_calls


def test_mutated_snapshot_and_model_arguments_cannot_redirect_tools(make_run, connectors):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    for spec in tools.tool_specs:
        assert spec["parameters"]["properties"] == {}
        assert spec["parameters"]["additionalProperties"] is False
    for arguments in ({"payment_id": "other"}, {"sender_account_id": "other"}, {"payment": {}}):
        with pytest.raises(ToolPolicyError, match="unexpected_tool_arguments"):
            tools.invoke(state, "get_core_evidence", request_id="redirect", arguments=arguments)
    tampered = deepcopy(state)
    tampered["payment_snapshot"]["amount"] = "0.01"
    with pytest.raises(ToolPolicyError, match="payment_snapshot_mismatch"):
        tools.invoke(tampered, "get_core_evidence", request_id="core")
    assert all(not c.mock_calls for c in connectors.values())


def test_lookup_required_and_unknown_tool_refused(make_run, connectors):
    state, tools = make_run()
    with pytest.raises(ToolPolicyError, match="payment_lookup_required"):
        tools.invoke(state, "get_core_evidence", request_id="core")
    with pytest.raises(ToolPolicyError, match="unknown_connector_tool"):
        tools.invoke(state, "lookup_payment", request_id="switch")
    assert state["tool_attempt_count"] == 0


@pytest.mark.parametrize("failure,category,retryable", [
    (TimeoutError("SECRET transport"), "transient_transport_error", True),
    (ConnectionError("SECRET transport"), "transient_transport_error", True),
    (PermissionError("SECRET credentials"), "configuration_error", False),
    (RecordNotFoundError("SECRET record"), "record_not_found", False),
    (ConnectorError("SECRET outage"), "connector_unavailable", False),
    (ValueError("SECRET request"), "invalid_request", False),
    (RuntimeError("SECRET failure"), "connector_failure", False),
])
def test_errors_are_sanitized_without_automatic_retry(make_run, connectors, failure, category, retryable):
    connectors["fraud"].screen.side_effect = failure
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    updated = tools.invoke(state, "get_fraud_evidence", request_id="fraud")
    connectors["fraud"].screen.assert_called_once()
    assert updated["tool_attempts"][-1]["result"] is None
    assert updated["tool_attempts"][-1]["error"] == {"category": category, "retryable": retryable}
    assert updated["failed_controls"] == ["fraud"] and "fraud" not in updated["current_evidence"]
    assert "fraud" not in updated["remaining_controls"] and "fraud" in updated["unresolved_controls"]
    assert "SECRET" not in json.dumps(updated)
    assert state["tool_attempt_count"] == 1  # copy-on-update


@pytest.mark.parametrize("name,connector,method,response", [
    ("get_core_evidence", "core", "get_account", None),
    ("get_core_evidence", "core", "get_account", AccountResponse("ACTIVE", Decimal("10"), True)),
    ("get_core_evidence", "core", "get_account", AccountResponse(AccountStatus.ACTIVE, Decimal("NaN"), True)),
    ("get_core_evidence", "core", "get_account", AccountResponse(AccountStatus.ACTIVE, Decimal("10"), 1)),
    ("get_limit_evidence", "limits", "get_limit", LimitsResponse(Decimal("-1"))),
    ("get_limit_evidence", "limits", "get_limit", LimitsResponse(10.0)),
    ("get_fraud_evidence", "fraud", "screen", {}),
    ("get_fraud_evidence", "fraud", "screen", FraudResponse(True, FraudDecision.PASS)),
    ("get_fraud_evidence", "fraud", "screen", FraudResponse(101, FraudDecision.PASS)),
    ("get_fraud_evidence", "fraud", "screen", FraudResponse(1, "PASS")),
    ("get_sanctions_evidence", "sanctions", "screen", SanctionsResponse("CLEAR")),
])
def test_malformed_responses_never_become_success(make_run, connectors, name, connector, method, response):
    getattr(connectors[connector], method).return_value = response
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    state = tools.invoke(state, name, request_id="bad-response")
    assert not state["tool_attempts"][-1]["success"]
    assert state["errors"][-1]["category"] == "invalid_response"
    assert state["current_evidence"] == {}


def test_transient_recovery_retains_failure_and_consumes_shared_extra(make_run, connectors):
    connectors["fraud"].screen.side_effect = [TimeoutError("private"), FraudResponse(10, FraudDecision.PASS)]
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    failed = tools.invoke(state, "get_fraud_evidence", request_id="fraud-first")
    recovered = tools.invoke(failed, "get_fraud_evidence", request_id="fraud-retry", purpose="transient_recovery")
    assert len(recovered["tool_attempts"]) == 3 and len(recovered["errors"]) == 1
    assert recovered["tool_attempts"][1]["success"] is False
    assert recovered["tool_attempts"][2]["success"] is True
    assert recovered["current_evidence"]["fraud"]["attempt_id"] == "test-run:attempt:03"
    assert recovered["completed_controls"] == ["fraud"] and recovered["failed_controls"] == []
    assert recovered["extra_connector_attempt_used"]
    with pytest.raises(ToolPolicyError, match="extra_connector_attempt_exhausted"):
        tools.invoke(recovered, "get_fraud_evidence", request_id="human", purpose="human_recheck")
    assert connectors["fraud"].screen.call_count == 2
    assert failed["current_evidence"] == {}


def test_human_recheck_failure_replaces_current_evidence_but_preserves_history(make_run, connectors):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    initial = tools.invoke(state, "get_core_evidence", request_id="core")
    connectors["core"].get_account.side_effect = TimeoutError("private")
    updated = tools.invoke(initial, "get_core_evidence", request_id="core-recheck", purpose="human_recheck")
    assert updated["tool_attempts"][1]["result"]["account_status"] == "ACTIVE"
    assert updated["tool_attempts"][2]["result"] is None
    assert updated["current_evidence"] == {} and updated["failed_controls"] == ["core"]
    assert initial["current_evidence"]["core"]["result"]["account_status"] == "ACTIVE"
    # The same shared allowance cannot be spent on a different control either.
    updated = tools.invoke(updated, "get_limit_evidence", request_id="limits")
    with pytest.raises(ToolPolicyError, match="extra_connector_attempt_exhausted"):
        tools.invoke(updated, "get_limit_evidence", request_id="limits-recheck", purpose="human_recheck")


def test_persistent_existing_outage_keeps_other_evidence(make_run):
    state, tools = make_run("SYNTHETIC-WIRE-UNAVAILABLE")
    state = tools.lookup_payment(state, request_id="lookup")
    for name in TOOLS:
        state = tools.invoke(state, name, request_id=name)
    assert state["completed_controls"] == ["core", "limits", "sanctions"]
    assert state["failed_controls"] == ["fraud"] and state["remaining_controls"] == []
    assert state["unresolved_controls"] == ["fraud"]
    with pytest.raises(ToolPolicyError, match="recovery_requires_transient_failure"):
        tools.invoke(state, "get_fraud_evidence", request_id="retry", purpose="transient_recovery")


def test_duplicate_requests_are_idempotent_and_conflicts_are_rejected(make_run, connectors):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    state = tools.invoke(state, "get_core_evidence", request_id="core-request")
    assert tools.invoke(state, "get_core_evidence", request_id="core-request") == state
    connectors["core"].get_account.assert_called_once()
    with pytest.raises(ToolPolicyError, match="conflicting_request_id"):
        tools.invoke(state, "get_limit_evidence", request_id="core-request")
    with pytest.raises(ToolPolicyError, match="duplicate_control_attempt"):
        tools.invoke(state, "get_core_evidence", request_id="new-request")
    with pytest.raises(ToolPolicyError, match="recheck_requires_previous_attempt"):
        tools.invoke(state, "get_limit_evidence", request_id="new-review", purpose="human_recheck")
    assert not connectors["limits"].mock_calls


@pytest.mark.parametrize("failure", [PermissionError("private"), ValueError("private"), RecordNotFoundError("private")])
def test_permanent_failures_cannot_consume_automatic_recovery(make_run, connectors, failure):
    connectors["core"].get_account.side_effect = failure
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    state = tools.invoke(state, "get_core_evidence", request_id="core")
    with pytest.raises(ToolPolicyError, match="recovery_requires_transient_failure"):
        tools.invoke(state, "get_core_evidence", request_id="retry", purpose="transient_recovery")
    connectors["core"].get_account.assert_called_once()


def test_budget_refusals_do_not_call_connectors(make_run, connectors):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    state["active_elapsed_seconds"] = 180.0
    with pytest.raises(ToolPolicyError, match="active_execution_budget_exhausted"):
        tools.invoke(state, "get_core_evidence", request_id="core")
    assert not connectors["core"].mock_calls


def test_runtime_can_be_rebound_from_recorded_lookup_without_new_attempt(make_run, connectors):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    fresh_tools = InvestigationTools(state, **connectors)
    restored = fresh_tools.lookup_payment(state, request_id="lookup")
    assert restored == state and restored["tool_attempt_count"] == 1
    state = fresh_tools.invoke(restored, "get_limit_evidence", request_id="limits")
    assert state["tool_attempt_count"] == 2


def test_restored_runtime_refuses_tampered_snapshot(make_run, connectors):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    state["payment_snapshot"]["sender_account_id"] = "other-account"
    restored = InvestigationTools(state, **connectors)
    with pytest.raises(ToolPolicyError, match="payment_snapshot_mismatch"):
        restored.lookup_payment(state, request_id="lookup")
    assert all(not c.mock_calls for c in connectors.values())


def test_all_initial_controls_plus_one_recheck_total_six_without_optional_guidance(make_run, connectors):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    for name in TOOLS:
        state = tools.invoke(state, name, request_id=name)
    state = tools.invoke(state, "get_core_evidence", request_id="recheck", purpose="human_recheck")
    assert state["tool_attempt_count"] == 6  # seventh slot is reserved for optional future guidance
    assert [a["attempt_number"] for a in state["tool_attempts"]] == list(range(1, 7))
    with pytest.raises(ToolPolicyError, match="extra_connector_attempt_exhausted"):
        tools.invoke(state, "get_limit_evidence", request_id="second-extra", purpose="human_recheck")
    assert connectors["core"].get_account.call_count == 2
    assert connectors["limits"].get_limit.call_count == 1


def test_dispatch_respects_seven_attempt_budget_without_connector_call(make_run, connectors):
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    # Exercise the generic dispatch guard against a fully consumed checkpoint.
    for number in range(6):
        state = record_tool_attempt(
            state, request_id=f"dummy-{number}", tool_name="dummy_read", control=None,
            purpose="initial", result={"value": number}, error=None, elapsed_seconds=0,
        )
    with pytest.raises(ToolPolicyError, match="tool_attempt_budget_exhausted"):
        tools.invoke(state, "get_core_evidence", request_id="core")
    assert not connectors["core"].mock_calls


def test_failed_transient_recovery_is_retained_and_cannot_retry_again(make_run, connectors):
    connectors["fraud"].screen.side_effect = TimeoutError("private")
    state, tools = make_run()
    state = tools.lookup_payment(state, request_id="lookup")
    state = tools.invoke(state, "get_fraud_evidence", request_id="first")
    state = tools.invoke(state, "get_fraud_evidence", request_id="retry", purpose="transient_recovery")
    assert len(state["errors"]) == 2 and state["current_evidence"] == {}
    assert state["failed_controls"] == ["fraud"] and state["extra_connector_attempt_used"]
    with pytest.raises(ToolPolicyError, match="extra_connector_attempt_exhausted"):
        tools.invoke(state, "get_fraud_evidence", request_id="again", purpose="transient_recovery")
    assert connectors["fraud"].screen.call_count == 2


@pytest.mark.parametrize("payment_id,tool_name,control,key,value", [
    ("SYNTHETIC-WIRE-LOW-BALANCE", "get_core_evidence", "core", "available_balance", "100.00"),
    ("SYNTHETIC-WIRE-HOLD", "get_fraud_evidence", "fraud", "decision", "HOLD"),
    ("SYNTHETIC-WIRE-BLOCKED", "get_sanctions_evidence", "sanctions", "result", "BLOCKED"),
])
def test_adverse_observations_are_preserved_without_new_decision_rules(
    make_run, payment_id, tool_name, control, key, value,
):
    state, tools = make_run(payment_id)
    state = tools.lookup_payment(state, request_id="lookup")
    state = tools.invoke(state, tool_name, request_id="evidence")
    assert state["current_evidence"][control]["result"][key] == value
    assert state["findings"] is None and state["recommendation"]["text"] is None
