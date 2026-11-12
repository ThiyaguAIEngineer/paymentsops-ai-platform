"""JSON serialization, detached history and shared budget boundaries."""

from copy import deepcopy
import json

import pytest

from payment_ops.investigation.state import (
    ToolPolicyError, check_execution_budget, new_investigation_state,
    payment_from_snapshot, payment_snapshot, record_tool_attempt,
)
from payment_ops.samples.payments import SYNTHETIC_PAYMENTS


@pytest.mark.parametrize("payment", SYNTHETIC_PAYMENTS, ids=lambda p: p.payment_id)
def test_all_existing_payment_snapshots_are_json_safe_and_round_trip(payment):
    snapshot = payment_snapshot(payment)
    assert json.loads(json.dumps(snapshot, allow_nan=False)) == snapshot
    restored = payment_from_snapshot(snapshot)
    # NaN is deliberately invalid input and not equal to itself: compare strings.
    assert payment_snapshot(restored) == snapshot
    if payment.amount is not None:
        assert isinstance(snapshot["amount"], str)
        assert str(restored.amount) == str(payment.amount)
    assert restored.payment_date == payment.payment_date


def test_initial_state_is_complete_and_detached():
    first = new_investigation_state(run_id="r1", thread_id="t1", payment_id="id")
    second = new_investigation_state(run_id="r2", thread_id="t2", payment_id="id")
    first["recommendation"]["evidence_ids"].append("local")
    assert second["recommendation"]["evidence_ids"] == []
    assert first["remaining_controls"] == ["core", "limits", "fraud", "sanctions"]
    assert first["human_review"]["decision"] is None
    assert first["findings"] is None and first["planner_decisions"] == []
    assert json.loads(json.dumps(first, allow_nan=False)) == first


@pytest.mark.parametrize("field,value", [("run_id", ""), ("thread_id", None), ("payment_id", 42)])
def test_invalid_identity_is_rejected(field, value):
    args = dict(run_id="r", thread_id="t", payment_id="id")
    args[field] = value
    with pytest.raises(ToolPolicyError, match="invalid_run_identity"):
        new_investigation_state(**args)


def test_seventh_attempt_is_allowed_and_eighth_is_refused():
    state = new_investigation_state(run_id="r", thread_id="t", payment_id="id")
    # Generic bookkeeping helper also reserves capacity for future guidance;
    # no guidance tool or orchestration is implemented by this dummy test.
    for number in range(1, 8):
        state = record_tool_attempt(
            state, request_id=f"request-{number}", tool_name="dummy_read", control=None,
            purpose="initial", result=None,
            error={"category": "dummy_failure", "retryable": False}, elapsed_seconds=0.25,
        )
    assert state["tool_attempt_count"] == 7 and len(state["errors"]) == 7
    assert state["tool_attempts"][-1]["attempt_id"] == "r:attempt:07"
    assert state["active_elapsed_seconds"] == 1.75
    before = deepcopy(state)
    with pytest.raises(ToolPolicyError, match="tool_attempt_budget_exhausted"):
        check_execution_budget(state)
    assert state == before


@pytest.mark.parametrize("elapsed", [180.0, 181.0, float("nan"), -1, True])
def test_elapsed_budget_is_checked_before_dispatch(elapsed):
    state = new_investigation_state(run_id="r", thread_id="t", payment_id="id")
    state["active_elapsed_seconds"] = elapsed
    with pytest.raises(ToolPolicyError):
        check_execution_budget(state)


def test_counter_cannot_hide_recorded_attempts():
    state = new_investigation_state(run_id="r", thread_id="t", payment_id="id")
    state["tool_attempt_count"] = 1
    with pytest.raises(ToolPolicyError, match="invalid_attempt_counter"):
        check_execution_budget(state)
