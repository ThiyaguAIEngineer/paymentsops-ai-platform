"""Offline model-selection traces: scripted providers are test infrastructure only."""

from copy import deepcopy
from dataclasses import asdict
import json

import pytest

from payment_ops.connectors.base import FraudDecision, FraudResponse
from payment_ops.connectors.mock_core import MockCoreBankingConnector
from payment_ops.connectors.mock_fraud import MockFraudConnector
from payment_ops.connectors.mock_limits import MockLimitsConnector
from payment_ops.connectors.mock_sanctions import MockSanctionsConnector
from payment_ops.investigation.graph import build_investigation_graph, invoke_investigation
from payment_ops.investigation.planner import ExecutionBudgets, InvestigationPlanner
from payment_ops.investigation.state import ToolPolicyError
from payment_ops.investigation.tools import TOOLS, lookup_payment
from payment_ops.knowledge.generation import GenerationDiagnostic, GenerationError
from payment_ops.services.payment_service import PaymentService


class ScriptedProvider:
    """Test-only provider: predefined JSON is never used by production runtime."""

    def __init__(self, steps):
        self.steps = iter(steps)
        self.calls = []

    def generate(self, system_prompt, user_prompt):
        self.calls.append(json.loads(user_prompt))
        step = next(self.steps)
        if isinstance(step, Exception):
            raise step
        return step


def action(name):
    return json.dumps({"action": name, "reason": "Collect the next eligible evidence."})


@pytest.fixture
def run_graph(make_run, connectors):
    def run(steps=None, *, payment_id="SYNTHETIC-WIRE-001", budgets=None, recursion_limit=40):
        initial, _ = make_run(payment_id)
        before = deepcopy(initial)
        provider = ScriptedProvider([action(n) for n in (*TOOLS, "finish")] if steps is None else steps)
        graph = build_investigation_graph(
            initial, **connectors, planner=InvestigationPlanner(provider),
            budgets=budgets or ExecutionBudgets(),
        )
        result = invoke_investigation(graph, initial, recursion_limit=recursion_limit)
        assert initial == before
        return result, provider, graph, initial
    return run


def expected_decision(payment_id):
    return PaymentService(MockCoreBankingConnector(), MockLimitsConnector(),
                          MockFraudConnector(), MockSanctionsConnector()).process_payment(lookup_payment(payment_id))


@pytest.mark.parametrize("order", [
    list(TOOLS), ["get_sanctions_evidence", "get_fraud_evidence", "get_limit_evidence", "get_core_evidence"],
])
def test_two_model_selected_orders_invoke_real_tools_and_match_existing_engine(run_graph, connectors, order):
    result, provider, graph, initial = run_graph([action(n) for n in (*order, "finish")])
    assert result["phase"] == "awaiting_review"
    assert result["outcome_reason"] == "recommendation_ready"
    assert result["planning_status"] == "succeeded"
    assert result["planner_call_count"] == 5 and len(provider.calls) == 5
    assert result["tool_attempt_count"] == 5
    assert [a["tool_name"] for a in result["tool_attempts"]] == ["lookup_payment", *order]
    assert [d["action"] for d in result["planner_decisions"]] == [*order, "finish"]
    assert all(d["source"] == "model" for d in result["planner_decisions"])
    assert provider.calls[1]["completed_controls"] == [TOOLS[order[0]]]
    assert len(provider.calls[1]["normalized_observations"]) == 1
    assert provider.calls[1]["deterministic_findings"] is not None
    assert result["findings"]["decision"] == "READY FOR PROCESSING"
    assert result["findings"]["primary_reason"] == expected_decision(initial["payment_id"]).primary_reason
    assert all(len(c.mock_calls) == 1 for c in connectors.values())
    assert result["human_review"]["decision"] is None
    assert result["summary"]["review_required"] and result["summary"]["human_review_implemented"]
    assert "no permission" in result["recommendation"]["text"]
    assert json.loads(json.dumps(result, allow_nan=False)) == result
    config = {"configurable": {"thread_id": initial["thread_id"]}}
    assert graph.get_state(config).values == result and graph.get_state(config).next == ("human_review",)
    assert len(list(graph.get_state_history(config))) >= 10


@pytest.mark.parametrize("payment_id,decision", [
    ("SYNTHETIC-WIRE-LOW-BALANCE", "REJECTED"),
    ("SYNTHETIC-WIRE-BLOCKED", "REJECTED"),
    ("SYNTHETIC-WIRE-MULTIPLE-REVIEW", "MANUAL REVIEW"),
    ("SYNTHETIC-WIRE-REJECT-REVIEW", "REJECTED"),
])
def test_adverse_findings_use_existing_engine_without_payment_mutation(run_graph, payment_id, decision):
    payment = lookup_payment(payment_id)
    before = asdict(payment)
    result, _, _, _ = run_graph(payment_id=payment_id)
    assert result["findings"]["decision"] == decision
    expected = expected_decision(payment_id)
    assert result["findings"]["checks"] == [
        {"area": c.area.value, "status": c.status.value, "reasons": list(c.reasons)} for c in expected.checks
    ]
    assert result["phase"] == "awaiting_review" and result["planning_status"] == "succeeded"
    assert asdict(payment) == before
    assert result["payment_snapshot"]["amount"] == str(payment.amount)
    assert result["summary"]["unresolved_evidence_gaps"] == []


def test_persistent_fraud_failure_preserves_other_evidence_and_escalates(run_graph, connectors):
    order = ["get_fraud_evidence", "get_sanctions_evidence", "get_core_evidence", "get_limit_evidence", "finish"]
    result, provider, _, _ = run_graph([action(n) for n in order], payment_id="SYNTHETIC-WIRE-UNAVAILABLE")
    assert result["phase"] == "awaiting_review" and result["outcome_reason"] == "incomplete_evidence"
    assert result["planning_status"] == "succeeded"  # valid planning, incomplete tool evidence
    assert result["findings"]["decision"] == "MANUAL REVIEW"
    assert result["summary"]["unresolved_evidence_gaps"] == ["fraud"]
    assert set(result["current_evidence"]) == {"core", "limits", "sanctions"}
    assert provider.calls[1]["failures"][0]["category"] == "connector_unavailable"
    assert "get_fraud_evidence" not in provider.calls[1]["eligible_actions"]
    fraud = next(c for c in result["summary"]["controls"] if c["control"] == "fraud")
    assert fraud["availability"] == "unavailable" and fraud["evidence_id"] is None
    assert fraud["engine_checks"][0]["status"] == "UNAVAILABLE"
    assert all(len(c.mock_calls) == 1 for c in connectors.values())


def test_one_model_selected_transient_recovery_is_explicit_and_bounded(run_graph, connectors):
    connectors["fraud"].screen.side_effect = [TimeoutError("SECRET"), FraudResponse(10, FraudDecision.PASS)]
    steps = ["get_fraud_evidence", "get_core_evidence", "get_fraud_evidence",
             "get_limit_evidence", "get_sanctions_evidence", "finish"]
    result, _, _, _ = run_graph([action(n) for n in steps])
    assert result["tool_attempt_count"] == 6 and result["planner_call_count"] == 6
    assert result["tool_attempts"][3]["purpose"] == "transient_recovery"
    assert result["extra_connector_attempt_used"]
    assert result["current_evidence"]["fraud"]["result"]["decision"] == "PASS"
    assert len(result["errors"]) == 1 and result["summary"]["unresolved_evidence_gaps"] == []
    assert result["phase"] == "awaiting_review" and "SECRET" not in json.dumps(result)


def test_second_recovery_is_rejected_and_does_not_loop(run_graph, connectors):
    connectors["fraud"].screen.side_effect = TimeoutError("SECRET")
    result, provider, _, _ = run_graph([action("get_fraud_evidence")] * 3)
    assert result["planning_status"] == "degraded" and result["phase"] == "awaiting_review"
    assert connectors["fraud"].screen.call_count == 2
    assert result["tool_attempt_count"] == 6 and len(provider.calls) == 3
    assert result["summary"]["unresolved_evidence_gaps"] == ["fraud"]


def test_unknown_payment_never_calls_planner_or_connectors(run_graph, connectors):
    result, provider, _, _ = run_graph(payment_id="missing-payment")
    assert result["phase"] == "failed" and result["tool_attempt_count"] == 1
    assert result["findings"] is None and result["summary"]["decision_engine_finding"] is None
    assert not provider.calls and not any(c.mock_calls for c in connectors.values())


@pytest.mark.parametrize("payment_id", ["SYNTHETIC-WIRE-MISSING", "SYNTHETIC-WIRE-NAN", "SYNTHETIC-WIRE-ZERO", "SYNTHETIC-WIRE-NEGATIVE"])
def test_invalid_input_skips_planning_and_downstream_controls(run_graph, connectors, payment_id):
    result, provider, _, _ = run_graph(payment_id=payment_id)
    assert result["findings"]["decision"] == "REJECTED"
    assert result["outcome_reason"] == "invalid_payment_input"
    assert not provider.calls and not any(c.mock_calls for c in connectors.values())
    assert result["planning_status"] == "not_run"
    assert all(c["engine_checks"][0]["status"] == "SKIPPED" for c in result["summary"]["controls"])


@pytest.mark.parametrize("bad_step", [
    "bad JSON SECRET", action("release_payment"), action("finish"),
    '{"action":"get_limit_evidence","reason":"x","account_id":"SECRET"}',
    TimeoutError("SECRET timeout"), RuntimeError("SECRET provider error"),
    GenerationError("SECRET credentials", diagnostic=GenerationDiagnostic("configuration", "missing_credentials")),
    GenerationError("SECRET timeout", diagnostic=GenerationDiagnostic("provider_communication", "timeout")),
])
def test_planner_failures_use_visible_bounded_fallback(run_graph, connectors, bad_step):
    result, provider, _, _ = run_graph([bad_step])
    assert result["phase"] == "awaiting_review" and result["outcome_reason"] == "planner_degraded"
    assert result["planning_status"] == "degraded" and result["planner_call_count"] == 1
    assert len(provider.calls) == 1 and result["tool_attempt_count"] == 5
    assert all(d["source"] == "fallback" for d in result["planner_decisions"])
    assert result["findings"]["decision"] == "READY FOR PROCESSING"
    assert "degraded" in result["recommendation"]["text"]
    assert result["summary"]["planner_failures"] and "SECRET" not in json.dumps(result)
    assert all(len(c.mock_calls) == 1 for c in connectors.values())


def test_duplicate_completed_action_falls_back_without_repeating_connector(run_graph, connectors):
    result, provider, _, _ = run_graph([action("get_core_evidence"), action("get_core_evidence")])
    assert len(provider.calls) == 2 and result["planning_status"] == "degraded"
    connectors["core"].get_account.assert_called_once()
    assert [d["source"] for d in result["planner_decisions"]] == ["model", "fallback", "fallback", "fallback", "fallback"]
    assert result["errors"][-1]["category"] == "ineligible_action"


def test_planner_budget_uses_no_more_model_calls_but_collects_outstanding_checks(run_graph):
    result, provider, _, _ = run_graph(budgets=ExecutionBudgets(max_planner_calls=1))
    assert result["planner_call_count"] == len(provider.calls) == 1
    assert result["tool_attempt_count"] == 5 and result["planning_status"] == "degraded"
    assert result["errors"][-1]["category"] == "planner_budget_exhausted"


def test_tool_budget_terminates_with_honest_partial_summary(run_graph, connectors):
    result, provider, _, _ = run_graph(budgets=ExecutionBudgets(max_tool_attempts=2))
    assert result["tool_attempt_count"] == 2 and len(provider.calls) == 1
    assert result["summary"]["unresolved_evidence_gaps"] == ["limits", "fraud", "sanctions"]
    assert result["phase"] == "awaiting_review"
    assert not connectors["fraud"].mock_calls
    assert result["errors"][-1]["category"] == "tool_attempt_budget_exhausted"


def test_finish_is_allowed_at_exact_tool_budget_when_all_controls_attempted(run_graph):
    result, provider, _, _ = run_graph(budgets=ExecutionBudgets(max_tool_attempts=5))
    assert result["tool_attempt_count"] == 5 and len(provider.calls) == 5
    assert result["planning_status"] == "succeeded"


def test_time_exhausted_during_planning_prevents_tool_dispatch(run_graph, monkeypatch, connectors):
    from payment_ops.investigation import graph as module
    clock = iter([0.0, 2.0])
    monkeypatch.setattr(module, "perf_counter", lambda: next(clock))
    result, provider, _, _ = run_graph(budgets=ExecutionBudgets(max_active_seconds=1))
    assert len(provider.calls) == 1 and result["tool_attempt_count"] == 1
    assert result["errors"][-1]["category"] == "active_execution_budget_exhausted"
    assert not any(c.mock_calls for c in connectors.values())


def test_recursion_guard_produces_checkpointed_escalation(run_graph):
    result, _, graph, initial = run_graph(recursion_limit=1)
    assert result["phase"] == "escalated"
    assert result["errors"][-1]["category"] == "graph_step_budget_exhausted"
    config = {"configurable": {"thread_id": initial["thread_id"]}}
    assert graph.get_state(config).values["summary"] == result["summary"]
    assert graph.get_state(config).next == ()


def test_already_started_run_cannot_be_replayed_as_new_investigation(run_graph, connectors):
    _, _, graph, initial = run_graph()
    with pytest.raises(ToolPolicyError, match="investigation_already_started"):
        invoke_investigation(graph, initial)
    assert all(len(c.mock_calls) == 1 for c in connectors.values())


def test_lazy_default_planner_configuration_failure_falls_back_without_network(make_run, connectors, monkeypatch):
    from payment_ops.investigation import graph as module
    def unavailable():
        raise GenerationError("SECRET", diagnostic=GenerationDiagnostic("configuration", "missing_credentials"))
    monkeypatch.setattr(module, "create_nebius_planner", unavailable)
    initial, _ = make_run()
    graph = build_investigation_graph(initial, **connectors)
    result = invoke_investigation(graph, initial)
    assert result["planning_status"] == "degraded" and result["tool_attempt_count"] == 5
    assert "SECRET" not in json.dumps(result)
