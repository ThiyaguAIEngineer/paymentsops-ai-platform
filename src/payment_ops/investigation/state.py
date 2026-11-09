"""JSON-safe investigation state and bounded, copy-on-update attempt bookkeeping.

State is application-owned. A future planner may propose actions, never state
patches. Mutable JSON snapshots are checked against the bound immutable Payment
before dispatch; Python callers must retain the returned state between calls.
"""

from copy import deepcopy
from dataclasses import asdict
from datetime import date
from decimal import Decimal
import math
from typing import Literal, TypedDict

from payment_ops.domain.payment import Payment


Control = Literal["core", "limits", "fraud", "sanctions"]
Purpose = Literal["initial", "transient_recovery", "human_recheck"]
CONTROLS: tuple[Control, ...] = ("core", "limits", "fraud", "sanctions")
MAX_TOOL_ATTEMPTS = 7
MAX_PLANNER_CALLS = 8
MAX_REVIEW_ROUNDS = 2
MAX_ACTIVE_SECONDS = 180.0
type JSONValue = str | int | float | bool | None | list[JSONValue] | dict[str, JSONValue]


class PaymentSnapshot(TypedDict):
    payment_id: str | None
    customer_name: str | None
    sender_account_id: str | None
    beneficiary_name: str | None
    beneficiary_account: str | None
    routing_number: str | None
    amount: str | None
    payment_date: str | None


class ToolError(TypedDict):
    category: str
    retryable: bool


class ToolAttempt(TypedDict):
    attempt_id: str
    request_id: str
    attempt_number: int
    tool_name: str
    control: Control | None
    purpose: Purpose
    payment_id: str
    success: bool
    result: dict[str, JSONValue] | None
    error: ToolError | None
    elapsed_seconds: float


class EvidenceRecord(TypedDict):
    attempt_id: str
    result: dict[str, JSONValue]


class PlannerDecision(TypedDict):
    action: str
    reason: str
    source: Literal["model", "fallback"]
    decision_id: str
    planner_call_number: int


class ErrorRecord(TypedDict):
    attempt_id: str
    tool_name: str
    category: str
    retryable: bool


class RecommendationMetadata(TypedDict):
    revision: int
    text: str | None
    evidence_ids: list[str]


class HumanReviewState(TypedDict):
    pending_review_id: str | None
    decision: str | None
    note: str | None
    reviewer_label: str | None
    requested_control: Control | None
    events: list[dict[str, JSONValue]]


class InvestigationState(TypedDict):
    run_id: str
    thread_id: str
    payment_id: str
    payment_snapshot: PaymentSnapshot | None
    input_errors: list[str]
    phase: Literal["loading", "collecting", "summarizing", "awaiting_review", "completed", "escalated", "failed"]
    outcome_reason: str | None
    attempted_controls: list[Control]
    completed_controls: list[Control]
    failed_controls: list[Control]
    remaining_controls: list[Control]  # Not yet attempted; failures are separate.
    unresolved_controls: list[Control]  # Missing usable current evidence.
    current_evidence: dict[Control, EvidenceRecord]
    tool_attempts: list[ToolAttempt]
    planner_decisions: list[PlannerDecision]
    planning_status: Literal["not_run", "running", "succeeded", "degraded"]
    summary: dict[str, JSONValue] | None
    errors: list[ErrorRecord]
    pending_action: str | None
    tool_attempt_count: int
    planner_call_count: int
    extra_connector_attempt_used: bool
    guidance_used: bool
    review_round_count: int
    active_elapsed_seconds: float
    findings: dict[str, JSONValue] | None
    recommendation: RecommendationMetadata
    human_review: HumanReviewState


class ToolPolicyError(ValueError):
    """A sanitized pre-dispatch refusal; no tool was invoked or budget consumed."""


def payment_snapshot(payment: Payment) -> PaymentSnapshot:
    """Serialize existing samples, including invalid-input NaN, without float loss."""
    result = asdict(payment)
    result["amount"] = str(payment.amount) if payment.amount is not None else None
    result["payment_date"] = payment.payment_date.isoformat() if payment.payment_date is not None else None
    return result


def payment_from_snapshot(snapshot: PaymentSnapshot) -> Payment:
    """Rehydrate an application-validated snapshot, not arbitrary model input."""
    values = dict(snapshot)
    values["amount"] = Decimal(snapshot["amount"]) if snapshot["amount"] is not None else None
    values["payment_date"] = date.fromisoformat(snapshot["payment_date"]) if snapshot["payment_date"] is not None else None
    return Payment(**values)


def new_investigation_state(*, run_id: str, thread_id: str, payment_id: str) -> InvestigationState:
    if any(not isinstance(v, str) or not v.strip() for v in (run_id, thread_id, payment_id)):
        raise ToolPolicyError("invalid_run_identity")
    return InvestigationState(
        run_id=run_id, thread_id=thread_id, payment_id=payment_id,
        payment_snapshot=None, input_errors=[], phase="loading", outcome_reason=None,
        attempted_controls=[], completed_controls=[], failed_controls=[],
        remaining_controls=list(CONTROLS), unresolved_controls=list(CONTROLS),
        current_evidence={}, tool_attempts=[], planner_decisions=[], errors=[],
        planning_status="not_run", summary=None,
        pending_action=None, tool_attempt_count=0, planner_call_count=0,
        extra_connector_attempt_used=False, guidance_used=False, review_round_count=0,
        active_elapsed_seconds=0.0, findings=None,
        recommendation={"revision": 0, "text": None, "evidence_ids": []},
        human_review={"pending_review_id": None, "decision": None, "note": None,
                     "reviewer_label": None, "requested_control": None, "events": []},
    )


def check_execution_budget(state: InvestigationState) -> None:
    """Shared tool boundary; a future graph also enforces planner/review limits."""
    count = state["tool_attempt_count"]
    elapsed = state["active_elapsed_seconds"]
    if type(count) is not int or count != len(state["tool_attempts"]) or count < 0:
        raise ToolPolicyError("invalid_attempt_counter")
    if count >= MAX_TOOL_ATTEMPTS:
        raise ToolPolicyError("tool_attempt_budget_exhausted")
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed < 0:
        raise ToolPolicyError("invalid_elapsed_time")
    if elapsed >= MAX_ACTIVE_SECONDS:
        raise ToolPolicyError("active_execution_budget_exhausted")


def recorded_request(state: InvestigationState, request_id: str, tool_name: str,
                     purpose: Purpose) -> ToolAttempt | None:
    """Identical replay is a no-op; conflicting reuse of an event ID is refused."""
    if not isinstance(request_id, str) or not request_id.strip():
        raise ToolPolicyError("invalid_request_id")
    for attempt in state["tool_attempts"]:
        if attempt["request_id"] == request_id:
            if attempt["tool_name"] != tool_name or attempt["purpose"] != purpose:
                raise ToolPolicyError("conflicting_request_id")
            return deepcopy(attempt)
    return None


def check_connector_attempt(state: InvestigationState, control: Control, purpose: Purpose) -> None:
    """Enforce one initial attempt per control and one shared explicit extra call."""
    if control not in CONTROLS or purpose not in ("initial", "transient_recovery", "human_recheck"):
        raise ToolPolicyError("invalid_control_or_purpose")
    previous = [a for a in state["tool_attempts"] if a["control"] == control]
    if not previous:
        if purpose != "initial":
            raise ToolPolicyError("recheck_requires_previous_attempt")
        return
    if purpose == "initial":
        raise ToolPolicyError("duplicate_control_attempt")
    if state["extra_connector_attempt_used"] or any(
        a["control"] is not None and a["purpose"] != "initial" for a in state["tool_attempts"]
    ):
        raise ToolPolicyError("extra_connector_attempt_exhausted")
    if purpose == "transient_recovery" and (
        previous[-1]["error"] is None or not previous[-1]["error"]["retryable"]
    ):
        raise ToolPolicyError("recovery_requires_transient_failure")


def record_tool_attempt(state: InvestigationState, *, request_id: str,
                        tool_name: str, control: Control | None, purpose: Purpose,
                        result: dict[str, JSONValue] | None, error: ToolError | None,
                        elapsed_seconds: float) -> InvestigationState:
    """Return a detached state with history, current evidence and derived work sets.

    Invoked only by the trusted serial dispatcher. No orchestration, persistence
    or automatic recovery is performed. Replaying an older state is not a lock
    against concurrent dispatch; the future graph must own the latest checkpoint.
    """
    if recorded_request(state, request_id, tool_name, purpose) is not None:
        return deepcopy(state)
    check_execution_budget(state)
    if control is not None:
        check_connector_attempt(state, control, purpose)
    if (result is None) == (error is None):
        raise ToolPolicyError("invalid_attempt_result")
    if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
        raise ToolPolicyError("invalid_attempt_elapsed_time")
    updated = deepcopy(state)
    number = updated["tool_attempt_count"] + 1
    attempt_id = f"{updated['run_id']}:attempt:{number:02d}"
    attempt = ToolAttempt(
        attempt_id=attempt_id, request_id=request_id, attempt_number=number,
        tool_name=tool_name, control=control, purpose=purpose,
        payment_id=updated["payment_id"], success=error is None,
        result=deepcopy(result), error=deepcopy(error), elapsed_seconds=elapsed_seconds,
    )
    updated["tool_attempts"].append(attempt)
    updated["tool_attempt_count"] = number
    updated["active_elapsed_seconds"] += elapsed_seconds
    if control is not None:
        if purpose != "initial":
            updated["extra_connector_attempt_used"] = True
        if error is None:
            updated["current_evidence"][control] = {"attempt_id": attempt_id, "result": deepcopy(result)}
        else:
            # Never silently retain a stale passing result after a failed recheck.
            updated["current_evidence"].pop(control, None)
    if error is not None:
        updated["errors"].append({"attempt_id": attempt_id, "tool_name": tool_name, **error})
    latest = {a["control"]: a for a in updated["tool_attempts"] if a["control"] is not None}
    updated["attempted_controls"] = [c for c in CONTROLS if c in latest]
    updated["completed_controls"] = [c for c in CONTROLS if c in latest and latest[c]["success"]]
    updated["failed_controls"] = [c for c in CONTROLS if c in latest and not latest[c]["success"]]
    updated["remaining_controls"] = [c for c in CONTROLS if c not in latest]
    updated["unresolved_controls"] = [c for c in CONTROLS if c not in updated["current_evidence"]]
    return updated
