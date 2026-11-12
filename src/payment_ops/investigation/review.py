"""Recommendation-only review policy and JSON payloads, independent of graph I/O."""

from copy import deepcopy
from dataclasses import dataclass

from payment_ops.investigation.planner import ExecutionBudgets
from payment_ops.investigation.state import (
    CONTROLS, MAX_REVIEW_ROUNDS, InvestigationState, ToolPolicyError,
    check_connector_attempt, check_execution_budget,
)


ACCEPT = "accept_recommendation"
FURTHER = "request_further_investigation"
ESCALATE = "end_and_escalate"
REVIEW_ACTIONS = (ACCEPT, FURTHER, ESCALATE)


class ReviewValidationError(ToolPolicyError):
    """Sanitized refusal; leave the current checkpoint available for valid review."""


@dataclass(frozen=True)
class ReviewResponse:
    action: str
    note: str
    reviewer_label: str
    requested_control: str | None


def further_unavailable_reason(state: InvestigationState, budgets: ExecutionBudgets) -> str | None:
    if state["extra_connector_attempt_used"]:
        return "shared_extra_connector_attempt_already_used"
    if any(e["action"] == FURTHER for e in state["human_review"]["events"]):
        return "further_investigation_cycle_already_used"
    if state["review_round_count"] >= MAX_REVIEW_ROUNDS:
        return "review_round_budget_exhausted"
    if state["input_errors"]:
        return "invalid_payment_input"
    if state["tool_attempt_count"] >= budgets.max_tool_attempts:
        return "tool_attempt_budget_exhausted"
    if state["active_elapsed_seconds"] >= budgets.max_active_seconds:
        return "active_execution_budget_exhausted"
    try:
        check_execution_budget(state)
    except ToolPolicyError:
        return "execution_budget_unavailable"
    return None


def eligible_review_controls(state: InvestigationState, budgets: ExecutionBudgets) -> list[str]:
    if further_unavailable_reason(state, budgets) is not None:
        return []
    eligible = []
    for control in CONTROLS:
        try:
            check_connector_attempt(state, control, "human_recheck")
        except ToolPolicyError:
            continue
        eligible.append(control)
    return eligible


def can_complete_reviewed(state: InvestigationState, budgets: ExecutionBudgets) -> bool:
    """Investigation completeness, not a second implementation of payment rules."""
    return (state["findings"] is not None and not state["input_errors"]
            and state["planning_status"] == "succeeded" and not state["unresolved_controls"]
            and all(c in state["current_evidence"] for c in CONTROLS)
            and state["tool_attempt_count"] <= budgets.max_tool_attempts
            and state["planner_call_count"] <= budgets.max_planner_calls
            and state["active_elapsed_seconds"] < budgets.max_active_seconds)


def prepare_review(state: InvestigationState, budgets: ExecutionBudgets) -> InvestigationState:
    """Commit the versioned payload before entering the interruptible node."""
    updated = deepcopy(state)
    if updated["phase"] == "failed":
        return updated
    if updated["review_round_count"] >= MAX_REVIEW_ROUNDS:
        updated["phase"], updated["outcome_reason"] = "escalated", "review_round_budget_exhausted"
        updated["human_review"]["pending_review_id"] = None
        updated["human_review"]["payload"] = None
        return updated
    updated["review_round_count"] += 1
    updated["phase"] = "awaiting_review"
    review = updated["human_review"]
    review["pending_review_id"] = f"{updated['run_id']}:review:{updated['recommendation']['revision']:02d}"
    review["decision"], review["note"], review["reviewer_label"] = None, None, None
    review["requested_control"], review["acknowledgment_only"] = None, False
    eligible = eligible_review_controls(updated, budgets)
    actions = list(REVIEW_ACTIONS) if eligible else [ACCEPT, ESCALATE]
    review["payload"] = {
        "run_id": updated["run_id"], "review_id": review["pending_review_id"],
        "payment_id": updated["payment_id"],
        "recommendation_revision": updated["recommendation"]["revision"],
        "findings": deepcopy(updated["findings"]),
        "evidence_gaps": list(updated["unresolved_controls"]),
        "recommendation": deepcopy(updated["recommendation"]),
        "planning_status": updated["planning_status"],
        "permitted_actions": actions, "eligible_controls": eligible,
        "further_investigation_unavailable_reason": None if eligible else (
            further_unavailable_reason(updated, budgets) or "no_eligible_connector"
        ),
        "remaining_tool_attempts": max(0, budgets.max_tool_attempts - updated["tool_attempt_count"]),
        "reviewer_identity_authenticated": False,
    }
    return updated


def validate_review_response(state: InvestigationState, payload: object,
                             budgets: ExecutionBudgets) -> ReviewResponse:
    required = {"run_id", "review_id", "payment_id", "recommendation_revision", "action"}
    optional = {"note", "reviewer_label", "requested_control"}
    if not isinstance(payload, dict) or not required <= set(payload) or set(payload) - required - optional:
        raise ReviewValidationError("invalid_review_schema")
    review = state["human_review"]
    if any(event["review_id"] == payload["review_id"] for event in review["events"]):
        raise ReviewValidationError("review_already_submitted")
    if state["phase"] != "awaiting_review" or not review["pending_review_id"]:
        raise ReviewValidationError("investigation_not_awaiting_review")
    if payload["run_id"] != state["run_id"] or payload["payment_id"] != state["payment_id"]:
        raise ReviewValidationError("review_identity_mismatch")
    if payload["review_id"] != review["pending_review_id"]:
        raise ReviewValidationError("stale_review_id")
    if (type(payload["recommendation_revision"]) is not int
            or payload["recommendation_revision"] != state["recommendation"]["revision"]):
        raise ReviewValidationError("recommendation_revision_mismatch")
    action = payload["action"]
    if action not in REVIEW_ACTIONS:
        raise ReviewValidationError("unknown_review_action")
    note, label = payload.get("note", ""), payload.get("reviewer_label", "Analyst")
    if not isinstance(note, str) or len(note) > 500 or "\x00" in note:
        raise ReviewValidationError("invalid_reviewer_note")
    if not isinstance(label, str) or not label.strip() or len(label) > 80 or not label.isprintable():
        raise ReviewValidationError("invalid_reviewer_label")
    control = payload.get("requested_control")
    if action == FURTHER:
        if not note.strip():
            raise ReviewValidationError("further_investigation_requires_note")
        reason = further_unavailable_reason(state, budgets)
        if reason is not None:
            raise ReviewValidationError(reason)
        if control not in eligible_review_controls(state, budgets):
            raise ReviewValidationError("ineligible_review_connector")
    elif control is not None:
        raise ReviewValidationError("unexpected_requested_control")
    return ReviewResponse(action, note.strip(), label.strip(), control)


def record_review_response(state: InvestigationState, response: ReviewResponse,
                           budgets: ExecutionBudgets) -> InvestigationState:
    updated = deepcopy(state)
    review = updated["human_review"]
    acknowledged = response.action == ACCEPT and not can_complete_reviewed(updated, budgets)
    disposition = ("acknowledged_escalation" if acknowledged else "accepted") if response.action == ACCEPT else response.action
    review["events"].append({
        "event_id": f"{review['pending_review_id']}:decision",
        "review_id": review["pending_review_id"],
        "recommendation_revision": updated["recommendation"]["revision"],
        "action": response.action, "disposition": disposition, "note": response.note,
        "reviewer_label": response.reviewer_label, "requested_control": response.requested_control,
    })
    review["decision"], review["note"], review["reviewer_label"] = response.action, response.note, response.reviewer_label
    review["requested_control"], review["acknowledgment_only"] = response.requested_control, acknowledged
    review["pending_review_id"], review["payload"] = None, None
    if response.action == FURTHER:
        updated["phase"] = "collecting"
    return updated


def finalize_review(state: InvestigationState, budgets: ExecutionBudgets) -> InvestigationState:
    """Only investigation metadata changes; findings and evidence are untouched."""
    updated = deepcopy(state)
    if updated["human_review"]["decision"] == ACCEPT and can_complete_reviewed(updated, budgets):
        updated["phase"], updated["outcome_reason"] = "completed_reviewed", "recommendation_accepted"
    elif updated["human_review"]["decision"] == ACCEPT:
        updated["phase"], updated["outcome_reason"] = "escalated", "recommendation_acknowledged_escalation"
        updated["human_review"]["acknowledgment_only"] = True
    else:
        updated["phase"], updated["outcome_reason"] = "escalated", "reviewer_ended_investigation"
    if updated["summary"] is not None:
        updated["summary"]["review_required"] = False
        updated["summary"]["outcome_reason"] = updated["outcome_reason"]
        updated["summary"]["investigation_outcome"] = updated["phase"]
    return updated
