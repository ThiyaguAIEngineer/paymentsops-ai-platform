"""Offline PDF facts, validity, immutability and export isolation."""

from copy import deepcopy
from io import BytesIO
import json

from pypdf import PdfReader
import pytest

from payment_ops.investigation.controller import InvestigationController
from payment_ops.investigation.planner import InvestigationPlanner
from payment_ops.investigation.report import generate_investigation_report, prepare_case_report, ReportValidationError
from payment_ops.investigation.tools import TOOLS


class ReportTestProvider:
    def __init__(self, timeout=False):
        self.calls = 0
        self.timeout = timeout

    def generate(self, *_):
        self.calls += 1
        if self.timeout and self.calls == 2:
            raise TimeoutError("not retained")
        return json.dumps({"action": [*TOOLS, "finish"][self.calls - 1], "reason": "Collect evidence."})


@pytest.fixture
def case(make_run, connectors):
    def create(payment="SYNTHETIC-WIRE-001", timeout=False):
        initial, _ = make_run(payment)
        provider = ReportTestProvider(timeout)
        controller = InvestigationController(initial, **connectors, planner=InvestigationPlanner(provider))
        controller.start()
        return controller, provider
    return create


def review(controller, action, **extra):
    state = controller.snapshot()
    payload = state["human_review"]["payload"]
    return controller.resume({**{k: payload[k] for k in (
        "run_id", "review_id", "payment_id", "recommendation_revision")}, "action": action, **extra})


def text(pdf):
    assert pdf.startswith(b"%PDF-") and pdf.rstrip().endswith(b"%%EOF")
    reader = PdfReader(BytesIO(pdf), strict=True)
    assert reader.pages
    return " ".join(" ".join(p.extract_text() for p in reader.pages).split())


@pytest.mark.parametrize("payment,expected", [
    ("SYNTHETIC-WIRE-001", "READY FOR PROCESSING"),
    ("SYNTHETIC-WIRE-LOW-BALANCE", "REJECTED"),
    ("SYNTHETIC-WIRE-UNAVAILABLE", "MANUAL REVIEW"),
])
def test_pending_reports_show_real_findings_and_provenance(case, connectors, payment, expected):
    controller, provider = case(payment)
    before = controller.snapshot()
    calls = {k: len(v.mock_calls) for k, v in connectors.items()}
    count = provider.calls
    pdf = generate_investigation_report(before)
    output = text(pdf)
    assert payment in output and expected in output and "PROVISIONAL" in output
    for attempt in before["tool_attempts"]:
        assert attempt["attempt_id"] in output
    assert "does not authorize" in output and "synthetic" in output.lower()
    assert all(s in output.lower() for s in ("account", "balance", "sanctions"))
    assert "Model" in output and "None recorded; no human acceptance inferred" in output
    if payment.endswith("UNAVAILABLE"):
        assert "connector_unavailable" in output and "No usable current evidence - not PASS" in output
        assert "fraud" in output
    assert generate_investigation_report(before) == pdf
    assert controller.snapshot() == before
    assert calls == {k: len(v.mock_calls) for k, v in connectors.items()} and provider.calls == count


def test_timeout_report_never_erases_degradation(case):
    controller, _ = case("SYNTHETIC-WIRE-LOW-BALANCE", timeout=True)
    output = text(generate_investigation_report(controller.snapshot()))
    assert all(s in output for s in ("planner_timeout", "degraded", "Deterministic fallback", "REJECTED"))


@pytest.mark.parametrize("action,label", [
    ("accept_recommendation", "Completed and reviewed investigation"),
    ("end_and_escalate", "Escalated investigation"),
])
def test_reviewed_reports_use_current_lifecycle(case, action, label):
    controller, _ = case()
    review(controller, action, note="Checked <evidence> & recommendation.")
    state = controller.snapshot()
    output = text(generate_investigation_report(state))
    assert label in output and "PROVISIONAL" not in output and action in output
    assert "Checked <evidence> & recommendation." in output
    assert state == controller.snapshot()


def test_recheck_preserves_revision_and_evidence_history(case):
    controller, _ = case("SYNTHETIC-WIRE-LOW-BALANCE")
    old = controller.snapshot()
    review(controller, "request_further_investigation", requested_control="core", note="Recheck balance.")
    state = controller.snapshot()
    output = text(generate_investigation_report(state))
    assert "revision 1" in output and "Recheck balance." in output
    assert "Recommendation revision 2" in output
    for a in state["tool_attempts"]:
        assert a["attempt_id"] in output
    assert state["tool_attempt_count"] == old["tool_attempt_count"] + 1


def test_absent_optional_values_and_literal_long_notes(case):
    controller, _ = case()
    review(controller, "accept_recommendation", note="<b>literal</b> & " + "x" * 470)
    state = controller.snapshot()
    for key in ("customer_name", "beneficiary_name", "payment_date"):
        state["payment_snapshot"][key] = None
    original = deepcopy(state)
    output = text(generate_investigation_report(state))
    assert "Not recorded" in output and "<b>literal</b> &" in output
    assert state == original


def test_failed_lookup_has_report_without_fabricated_payment(case):
    controller, _ = case("UNKNOWN-ID")
    output = text(generate_investigation_report(controller.snapshot()))
    assert "Failed investigation" in output and "No simulator checks recorded" in output
    assert "Not recorded" in output


@pytest.mark.parametrize("change", [
    lambda s: s.update(phase="collecting"),
    lambda s: s.update(tool_attempt_count=99),
    lambda s: s["payment_snapshot"].update(payment_id="OTHER"),
    lambda s: s.pop("human_review"),
])
def test_unready_and_inconsistent_snapshots_refused(case, change):
    controller, _ = case()
    state = controller.snapshot()
    change(state)
    with pytest.raises(ReportValidationError):
        prepare_case_report(state)
