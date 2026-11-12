"""Launch with uv run streamlit run src/payment_ops/ui/app.py."""

from dataclasses import fields

import streamlit as st

from payment_ops.connectors.mock_core import MockCoreBankingConnector
from payment_ops.connectors.mock_fraud import MockFraudConnector
from payment_ops.connectors.mock_limits import MockLimitsConnector
from payment_ops.connectors.mock_sanctions import MockSanctionsConnector
from payment_ops.samples.payments import SYNTHETIC_PAYMENTS
from payment_ops.services.decision_engine import CheckStatus, PaymentDecision
from payment_ops.services.payment_service import PaymentService
from payment_ops.services.results import PaymentProcessingResult
from payment_ops.ui.helpers import (
    DECISION_LABELS, PaymentEntry, aggregate_metrics, filter_payments,
    evidence_rows, format_amount, payment_rows,
)
from payment_ops.ui.presentation import console_styles, metric_cards, page_header, control_findings


CHECK_LABELS = {
    CheckStatus.PASS: "✅ PASS",
    CheckStatus.REVIEW: "🟠 REVIEW",
    CheckStatus.REJECTED: "🔴 REJECTED",
    CheckStatus.UNAVAILABLE: "⚠️ UNAVAILABLE",
    CheckStatus.SKIPPED: "➖ SKIPPED",
}


@st.cache_data(show_spinner=False)
def load_processing_results() -> dict[str, PaymentProcessingResult]:
    service = PaymentService(
        MockCoreBankingConnector(), MockLimitsConnector(),
        MockFraudConnector(), MockSanctionsConnector(),
    )
    return {payment.payment_id: service.process_payment_with_evidence(payment) for payment in SYNTHETIC_PAYMENTS}


def load_payments() -> list[PaymentEntry]:
    """Keep the existing dashboard helper contract using cached rich results."""
    results = load_processing_results()
    return [(payment, results[payment.payment_id].decision) for payment in SYNTHETIC_PAYMENTS]


def render_metrics(entries: list[PaymentEntry]) -> None:
    metrics = aggregate_metrics(entries)
    metric_cards([
        ("Total Payments", metrics["total_payments"]),
        ("Total Payment Value", format_amount(metrics["total_value"])),
        *((d.value.title(), metrics["decision_counts"][d]) for d in (
            PaymentDecision.READY_FOR_PROCESSING, PaymentDecision.MANUAL_REVIEW, PaymentDecision.REJECTED)),
    ], key="kpi_wire")
    st.caption(
        f"Metrics cover all instructions. Total value sums finite, positive amounts in USD; "
        f"{metrics['excluded_amounts']} invalid or missing amounts excluded."
    )


def render_detail(entry: PaymentEntry, processing: PaymentProcessingResult) -> None:
    payment, result = entry
    st.subheader("Payment detail")
    message = f"{DECISION_LABELS[result.decision]} — {result.primary_reason}"
    if result.decision is PaymentDecision.REJECTED:
        st.error(message)
    elif result.decision is PaymentDecision.MANUAL_REVIEW:
        st.warning(message)
    else:
        st.success(message)

    st.table([
        {
            "Payment information": field.name.replace("_", " ").title(),
            "Value": format_amount(payment.amount) if field.name == "amount" else (
                "Missing" if getattr(payment, field.name) is None else str(getattr(payment, field.name))
            ),
        }
        for field in fields(payment)
    ])
    st.subheader("Validation checks")
    control_findings([{"area": c.area.value, "status": c.status.value, "reasons": c.reasons} for c in result.checks])
    with st.expander("Control comparison table"):
        st.dataframe([
            {"Control": check.area.value, "Status": CHECK_LABELS[check.status], "Explanation": " ".join(check.reasons)}
            for check in result.checks
        ], hide_index=True, width="stretch")
    st.caption("UNAVAILABLE means control information could not be evaluated. SKIPPED means the check was not performed.")
    st.subheader("Review and rejection findings")
    if result.reasons:
        for reason in result.reasons:
            st.write(reason)
    else:
        st.write("No review or rejection findings.")
    st.subheader("Connector evidence")
    st.table(evidence_rows(processing))
    st.caption("Read-only synthetic responses used for this decision. Retrieved evidence does not imply a PASS; see the validation checks above.")


def render_wire_validation() -> None:
    page_header("Wire Validation", "Review synthetic instructions, control findings and the evidence behind each simulator decision.", eyebrow="01 / VALIDATE")
    st.caption("Week 1 • Synthetic data only • Read-only educational simulator")
    try:
        entries = load_payments()
        processing_results = load_processing_results()
    except Exception:
        st.error("The synthetic payment dataset could not be loaded. Restart the dashboard and try again.")
        return
    render_metrics(entries)
    st.subheader("Payments")
    with st.container(border=True):
        decision_filter = st.selectbox("Filter by decision", ["All decisions", *(decision.value for decision in PaymentDecision)], key="decision_filter")
    selected_decision = None if decision_filter == "All decisions" else PaymentDecision(decision_filter)
    filtered = filter_payments(entries, selected_decision)
    st.caption(f"Showing {len(filtered)} of {len(entries)} payments")
    if not filtered:
        st.info("No payments match this decision filter.")
        return
    st.dataframe(payment_rows(filtered), hide_index=True, width="stretch")
    selected_id = st.selectbox("Select a payment", [payment.payment_id for payment, _ in filtered], key="selected_payment")
    render_detail(next(entry for entry in filtered if entry[0].payment_id == selected_id), processing_results[selected_id])


def main() -> None:
    st.set_page_config(page_title="PaymentOps Intelligence Console", page_icon="🏦", layout="wide")
    console_styles()
    with st.sidebar:
        with st.container(key="console_brand"):
            st.subheader("PaymentOps")
            st.caption("OPERATIONS INTELLIGENCE")
        st.info("SYNTHETIC DEMONSTRATION ENVIRONMENT")
        view = st.radio("Workspace", ["Wire Validation", "Knowledge Assistant", "Payment Investigation Agent"], key="workspace_view")
        st.divider()
        st.caption("Read-only mock integrations. No real bank connectivity or payment execution.")
    with st.container(key="paymentops_console"):
        st.title("Payment Operations Intelligence Console")
        st.caption("SYNTHETIC DEMONSTRATION ENVIRONMENT · No payment authorization")
        _render_workspace(view)


def _render_workspace(view):
    if view == "Knowledge Assistant":
        # Lazy import keeps Week 1 startup independent of RAG configuration.
        from payment_ops.ui.knowledge_view import render_knowledge_assistant
        render_knowledge_assistant()
    elif view == "Payment Investigation Agent":
        from payment_ops.ui.investigation_view import render_investigation_agent

        render_investigation_agent()
    else:
        render_wire_validation()


if __name__ == "__main__":
    main()
