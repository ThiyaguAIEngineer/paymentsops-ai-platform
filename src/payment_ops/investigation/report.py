"""Read-only snapshot projection. No graph, connector, provider or UI dependencies."""

from dataclasses import dataclass

from pydantic import TypeAdapter, ValidationError

from payment_ops.investigation.state import InvestigationState


class ReportValidationError(ValueError):
    """A snapshot is absent, malformed or not ready for reporting."""


@dataclass(frozen=True)
class ReportSection:
    title: str
    rows: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CaseReport:
    payment_id: str
    provisional: bool
    sections: tuple[ReportSection, ...]


LIFECYCLES = {
    "awaiting_review": "Awaiting human review - PROVISIONAL",
    "completed_reviewed": "Completed and reviewed investigation",
    "escalated": "Escalated investigation",
    "failed": "Failed investigation",
}
DISCLAIMER = (
    "Synthetic educational data only. All banking connectors are simulated mocks. "
    "This report does not authorize release, rejection, cancellation, settlement "
    "or execution of a payment. Human review concerns the investigation recommendation only."
)
_SNAPSHOT = TypeAdapter(InvestigationState)


def _text(value):
    return "Not recorded" if value is None or value == "" else str(value)


def prepare_case_report(snapshot: InvestigationState) -> CaseReport:
    """Validate/detach known state and project facts; never recompute payment rules.

    This checks report readiness and structural consistency, not authenticity of
    arbitrary externally supplied data. Production input is controller.snapshot().
    Optional identities/dates/notes stay absent rather than being inferred.
    """
    try:
        state = _SNAPSHOT.validate_python(snapshot, strict=True)
        if (state["phase"] not in LIFECYCLES or not state["run_id"].strip()
                or not state["thread_id"].strip() or not state["payment_id"].strip()
                or state["tool_attempt_count"] != len(state["tool_attempts"])
                or any(a["payment_id"] != state["payment_id"] for a in state["tool_attempts"])
                or (state["payment_snapshot"] is not None
                    and state["payment_snapshot"]["payment_id"] != state["payment_id"])):
            raise ReportValidationError("Report snapshot is not ready or inconsistent")
    except (ValidationError, TypeError, KeyError):
        raise ReportValidationError("Report snapshot is not ready or inconsistent") from None

    sections = []

    def section(title, rows):
        sections.append(ReportSection(title, tuple((str(k), _text(v)) for k, v in rows)))

    section("Case overview", [
        ("Payment reference", state["payment_id"]), ("Run reference", state["run_id"]),
        ("Thread reference", state["thread_id"]), ("Lifecycle", LIFECYCLES[state["phase"]]),
        ("Outcome reason", state["outcome_reason"]), ("Planning status", state["planning_status"]),
        ("Tool / planner attempts", f"{state['tool_attempt_count']} / {state['planner_call_count']}"),
        ("Review rounds", state["review_round_count"]),
    ])
    payment = state["payment_snapshot"] or {}
    section("Selected synthetic payment", [(label, payment.get(key)) for key, label in (
        ("customer_name", "Customer"), ("sender_account_id", "Sender account"),
        ("beneficiary_name", "Beneficiary"), ("beneficiary_account", "Beneficiary account"),
        ("routing_number", "Routing number"), ("amount", "Amount (USD)"),
        ("payment_date", "Instruction date"),
    )])
    findings = state["findings"] or {}
    section("Deterministic simulator finding", [
        ("Simulator finding (not a payment action)", findings.get("decision")),
        ("Primary reason", findings.get("primary_reason")),
        ("Recorded reasons", "; ".join(findings.get("reasons", [])) or None),
        ("Input errors", "; ".join(state["input_errors"]) or "None recorded"),
    ])
    section("Control results", [
        (_text(c.get("area")), f"{_text(c.get('status'))}: " + "; ".join(c.get("reasons", [])))
        for c in findings.get("checks", [])
    ] or [("Controls", "No simulator checks recorded")])

    evidence_fields = {
        "core": ("account_status", "available_balance", "wire_payments_enabled"),
        "limits": ("single_wire_limit",), "fraud": ("score", "decision"), "sanctions": ("result",),
    }
    for control, keys in evidence_fields.items():
        evidence = state["current_evidence"].get(control)
        section(f"Current evidence: {control}", (
            [("Evidence reference", evidence["attempt_id"])] +
            [(key.replace("_", " ").capitalize(), evidence["result"].get(key)) for key in keys]
        ) if evidence else [("Availability", "No usable current evidence - not PASS")])

    section("Planner action history", [
        (f"Decision {i} - {'Model' if d['source'] == 'model' else 'Deterministic fallback'}",
         f"{d['action']} | planner attempt {d['planner_call_number']} | "
         f"{d['decision_id']} | {d['reason']}")
        for i, d in enumerate(state["planner_decisions"], 1)
    ] or [("Actions", "None recorded")])
    section("Tool execution and evidence history", [
        (f"Attempt {a['attempt_number']} - {a['tool_name']}",
         f"{a['purpose']} | {'Evidence retrieved' if a['success'] else 'Unavailable / failed'} | "
         f"{a['attempt_id']} | request {a['request_id']} | "
         + ("; ".join(f"{k.replace('_', ' ')}: {_text(v)}" for k, v in (a['result'] or {}).items())
            if a['success'] else _text((a['error'] or {}).get('category'))))
        for a in state["tool_attempts"]
    ] or [("Attempts", "None recorded")])
    section("Recorded failures", [
        (e["tool_name"], f"{e['category']} | {e['attempt_id']} | retryable: {e['retryable']}")
        for e in state["errors"]
    ] or [("Failures", "None recorded")])
    section("Evidence gaps and recommendation", [
        ("Unresolved controls", ", ".join(state["unresolved_controls"]) or "None recorded"),
        ("Recommendation revision", state["recommendation"]["revision"]),
        ("Recommendation", state["recommendation"]["text"]),
        ("Supporting evidence IDs", "; ".join(state["recommendation"]["evidence_ids"]) or None),
        ("Pending review reference", state["human_review"]["pending_review_id"]),
        ("Acknowledgment of escalation only", state["human_review"]["acknowledgment_only"]),
    ])
    section("Human review history (identities not authenticated)", [
        (f"Review event {i} - revision {e.get('recommendation_revision', 'Not recorded')}",
         " | ".join(f"{label}: {_text(e.get(key))}" for key, label in (
             ("event_id", "Event"), ("review_id", "Review"), ("action", "Action"),
             ("disposition", "Disposition"), ("reviewer_label", "Reviewer label"),
             ("requested_control", "Requested control"), ("note", "Note"))))
        for i, e in enumerate(state["human_review"]["events"], 1)
    ] or [("Review events", "None recorded; no human acceptance inferred")])
    return CaseReport(state["payment_id"], state["phase"] == "awaiting_review", tuple(sections))


def generate_investigation_report(snapshot: InvestigationState) -> bytes:
    """Return deterministic PDF bytes without I/O, calls or snapshot mutation.

    No generation timestamp is added. ReportLab invariant mode stabilizes PDF
    metadata/identifiers. Exact bytes are reproducible with the locked dependencies.
    """
    from payment_ops.investigation.report_pdf import render_case_report

    return render_case_report(prepare_case_report(snapshot))
