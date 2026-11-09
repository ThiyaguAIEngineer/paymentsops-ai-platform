"""Deterministic findings/summary from recorded evidence; no model-written decisions."""

from copy import deepcopy
from decimal import Decimal

from payment_ops.connectors.base import (
    AccountResponse, AccountStatus, ConnectorError, FraudDecision, FraudResponse,
    LimitsResponse, SanctionsResponse, SanctionsResult,
)
from payment_ops.investigation.state import CONTROLS, InvestigationState, payment_from_snapshot
from payment_ops.services.decision_engine import CheckStatus, ValidationArea, evaluate_payment


AREAS = {
    "core": (ValidationArea.ACCOUNT, ValidationArea.BALANCE),
    "limits": (ValidationArea.LIMIT,), "fraud": (ValidationArea.FRAUD,),
    "sanctions": (ValidationArea.SANCTIONS,),
}


def _responses(state: InvestigationState):
    responses = {}
    for control in CONTROLS:
        evidence = state["current_evidence"].get(control)
        if evidence is None:
            responses[control] = ConnectorError("Evidence unavailable or not collected")
            continue
        value = evidence["result"]
        try:
            if control == "core":
                response = AccountResponse(AccountStatus(value["account_status"]),
                                           Decimal(value["available_balance"]), value["wire_payments_enabled"])
            elif control == "limits":
                response = LimitsResponse(Decimal(value["single_wire_limit"]))
            elif control == "fraud":
                response = FraudResponse(value["score"], FraudDecision(value["decision"]))
            else:
                response = SanctionsResponse(SanctionsResult(value["result"]))
        except (KeyError, ValueError, TypeError, ArithmeticError):
            response = ConnectorError("Invalid recorded evidence")
        responses[control] = response
    return responses


def evaluate_findings(state: InvestigationState):
    if state["payment_snapshot"] is None:
        return None
    responses = _responses(state)
    decision = evaluate_payment(
        payment_from_snapshot(state["payment_snapshot"]), account=responses["core"],
        limits=responses["limits"], fraud=responses["fraud"], sanctions=responses["sanctions"],
    )
    return {
        "payment_id": decision.payment_id, "decision": decision.decision.value,
        "primary_reason": decision.primary_reason, "reasons": list(decision.reasons),
        "checks": [{"area": c.area.value, "status": c.status.value, "reasons": list(c.reasons)}
                   for c in decision.checks],
    }


def summarize_investigation(state: InvestigationState) -> InvestigationState:
    """Stable Task 5 boundary: produce a recommendation, never human acceptance.

    awaiting_review means ready for a future review node, not an interrupt in this
    task. The compiled Task 4 workflow ends here. Escalations still need review.
    """
    updated = deepcopy(state)
    findings = evaluate_findings(updated)
    updated["findings"] = findings
    latest = {a["control"]: a for a in updated["tool_attempts"] if a["control"] is not None}
    controls = []
    gaps = []
    for control in CONTROLS:
        evidence = updated["current_evidence"].get(control)
        checks = [] if findings is None else [
            c for c in findings["checks"] if c["area"] in [area.value for area in AREAS[control]]
        ]
        available = evidence is not None and not any(c["status"] == CheckStatus.UNAVAILABLE.value for c in checks)
        availability = "available" if available else "unavailable" if control in latest else "not_attempted"
        if not available:
            gaps.append(control)
        controls.append({
            "control": control, "availability": availability, "engine_checks": checks,
            "observation": deepcopy(evidence["result"]) if available else None,
            "evidence_id": evidence["attempt_id"] if available else None,
            "latest_error": deepcopy(latest[control]["error"]) if control in latest else None,
        })
    updated["unresolved_controls"] = gaps
    if findings is None:
        updated["phase"] = "failed"
        updated["outcome_reason"] = updated["outcome_reason"] or "invalid_selection"
        recommendation = "No payment was loaded. Resolve the selection before starting a new investigation."
    elif updated["planning_status"] == "degraded":
        updated["phase"], updated["outcome_reason"] = "escalated", "planner_degraded"
        recommendation = "Escalate this investigation: autonomous planning degraded; review all findings and gaps."
    elif updated["input_errors"]:
        updated["phase"], updated["outcome_reason"] = "awaiting_review", "invalid_payment_input"
        recommendation = "Review the invalid instruction fields. Downstream controls were skipped; no payment was changed."
    elif gaps:
        updated["phase"], updated["outcome_reason"] = "escalated", "incomplete_evidence"
        recommendation = "Escalate this investigation: mandatory evidence remains unavailable or uncollected."
    else:
        updated["phase"], updated["outcome_reason"] = "awaiting_review", "recommendation_ready"
        recommendation = "Review the evidence and existing simulator finding; accept or request further investigation in the future review step."
    disclaimer = "Investigation recommendation only; no permission to release, reject, cancel, settle or execute a payment."
    ids = [c["evidence_id"] for c in controls if c["evidence_id"] is not None]
    updated["recommendation"] = {
        "revision": updated["recommendation"]["revision"] + 1,
        "text": recommendation + " " + disclaimer, "evidence_ids": ids,
    }
    snapshot = updated["payment_snapshot"] or {}
    updated["summary"] = {
        "payment_id": updated["payment_id"],
        "payment_details": {"amount": snapshot.get("amount"), "payment_date": snapshot.get("payment_date")},
        "input_errors": list(updated["input_errors"]), "controls": controls,
        "tool_failures": [deepcopy(e) for e in updated["errors"] if e["tool_name"] != "planner"],
        "planner_failures": [deepcopy(e) for e in updated["errors"] if e["tool_name"] == "planner"],
        "unresolved_evidence_gaps": gaps, "decision_engine_finding": findings,
        "autonomous_planning": updated["planning_status"],
        "recommendation": deepcopy(updated["recommendation"]),
        "review_required": findings is not None, "human_review_implemented": False,
        "outcome_reason": updated["outcome_reason"],
    }
    updated["pending_action"] = None
    return updated
