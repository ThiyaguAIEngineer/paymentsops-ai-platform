"""Scripted providers are offline test infrastructure, never live agent behavior."""

import json

import pytest

from payment_ops.investigation.planner import (
    ExecutionBudgets, InvestigationPlanner, PlannerError, create_nebius_planner,
    eligible_actions, planner_context, planner_failure_category,
)


class ScriptedProvider:
    """Return deterministic test-only JSON/errors and retain input for assertions."""

    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def generate(self, system_prompt, user_prompt):
        self.calls.append((system_prompt, user_prompt))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
def loaded(make_run):
    state, tools = make_run()
    return tools.lookup_payment(state, request_id="lookup"), tools


def action_json(action, reason="Collect outstanding evidence."):
    return json.dumps({"action": action, "reason": reason})


def test_context_is_minimal_and_describes_real_remaining_work(loaded):
    state, tools = loaded
    state = tools.invoke(state, "get_core_evidence", request_id="core")
    payload = planner_context(state, ExecutionBudgets())
    context = json.loads(payload)
    assert context["payment_reference"] == state["payment_id"]
    assert context["completed_controls"] == ["core"]
    assert context["outstanding_controls"] == ["limits", "fraud", "sanctions"]
    assert context["normalized_observations"]["core"]["result"]["available_balance"] == "100000.00"
    assert context["remaining_budgets"]["tool_attempts"] == 5
    assert context["eligible_actions"] == ["get_limit_evidence", "get_fraud_evidence", "get_sanctions_evidence"]
    for field in ("customer_name", "beneficiary_name", "beneficiary_account", "routing_number", "sender_account_id"):
        assert field not in payload
        assert state["payment_snapshot"][field] not in payload


@pytest.mark.parametrize("raw", [
    "not JSON", "```json\n{}\n```", "[]", "null", "{}",
    '{"action":"get_core_evidence"}',
    '{"action":"get_core_evidence","reason":"x","arguments":{}}',
    '{"action":"get_core_evidence","reason":"x","payment_id":"other"}',
    '{"action":null,"reason":"x"}', '{"action":"get_core_evidence","reason":42}',
    '{"action":"get_core_evidence","action":"get_limit_evidence","reason":"x"}',
    '{"action":"get_core_evidence","reason":NaN}',
    action_json("finish"), action_json("lookup_payment"), action_json("release_payment"),
    action_json("https://example.com"), action_json("__import__('os').system('bad')"),
    action_json("get_core_evidence", ""), action_json("get_core_evidence", "x" * 241),
    action_json("get_core_evidence", "Read https://example.com"),
    action_json("get_core_evidence", "`import os`"), action_json("get_core_evidence", "line\nbreak"),
    action_json("get_core_evidence", "exec('bad')"), "x" * 4097,
])
def test_unsafe_or_malformed_plans_are_rejected(loaded, raw):
    state, _ = loaded
    provider = ScriptedProvider([raw])
    with pytest.raises(PlannerError):
        InvestigationPlanner(provider).plan(state, ExecutionBudgets())
    assert len(provider.calls) == 1
    assert state["tool_attempt_count"] == 1


def test_valid_action_is_strictly_eligible_and_reason_is_display_text(loaded):
    state, _ = loaded
    planner = InvestigationPlanner(ScriptedProvider([action_json("get_fraud_evidence", "  Collect fraud evidence.  ")]))
    action = planner.plan(state, ExecutionBudgets())
    assert action.action == "get_fraud_evidence" and action.reason == "Collect fraud evidence."


def test_duplicates_are_ineligible_but_explicit_transient_recovery_is_eligible(loaded, connectors):
    state, tools = loaded
    state = tools.invoke(state, "get_core_evidence", request_id="core")
    assert "get_core_evidence" not in eligible_actions(state, ExecutionBudgets())
    with pytest.raises(PlannerError, match="ineligible_action"):
        InvestigationPlanner(ScriptedProvider([action_json("get_core_evidence")])).plan(state, ExecutionBudgets())
    connectors["fraud"].screen.side_effect = TimeoutError("private")
    state = tools.invoke(state, "get_fraud_evidence", request_id="fraud")
    assert "get_fraud_evidence" in eligible_actions(state, ExecutionBudgets())
    state = tools.invoke(state, "get_fraud_evidence", request_id="retry", purpose="transient_recovery")
    assert "get_fraud_evidence" not in eligible_actions(state, ExecutionBudgets())


@pytest.mark.parametrize("kwargs", [
    {"max_tool_attempts": 8}, {"max_tool_attempts": 0}, {"max_tool_attempts": True},
    {"max_planner_calls": 9}, {"max_planner_calls": 0},
    {"max_active_seconds": 181}, {"max_active_seconds": float("nan")}, {"max_active_seconds": True},
])
def test_budgets_cannot_exceed_prd_or_use_invalid_values(kwargs):
    with pytest.raises(ValueError):
        ExecutionBudgets(**kwargs)


def test_week3_factory_uses_separate_adapter_settings_without_mutating_week2(monkeypatch):
    from payment_ops.investigation import planner as module
    captured = []
    monkeypatch.setenv("NEBIUS_GENERATION_MODEL", "week2-model")
    monkeypatch.setenv("INVESTIGATION_GENERATION_MODEL", "week3-model")
    monkeypatch.setattr(module, "NebiusGenerationProvider", lambda **kw: captured.append(kw) or object())
    create_nebius_planner()
    assert captured == [{"model": "week3-model", "timeout": 15, "max_tokens": 400}]
    import os
    assert os.environ["NEBIUS_GENERATION_MODEL"] == "week2-model"


def test_unknown_planner_error_category_is_not_echoed():
    assert planner_failure_category(PlannerError("SECRET")) == "planner_failure"
