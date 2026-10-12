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
    columns = st.columns(5)
    columns[0].metric("Total Payments", metrics["total_payments"])
    columns[1].metric("Total Payment Value", format_amount(metrics["total_value"]))
    for column, decision in zip(columns[2:], (
        PaymentDecision.READY_FOR_PROCESSING, PaymentDecision.MANUAL_REVIEW, PaymentDecision.REJECTED,
    ), strict=True):
        column.metric(decision.value.title(), metrics["decision_counts"][decision])
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


def main() -> None:
    st.set_page_config(page_title="Payment Operations Intelligence Platform", page_icon="🏦", layout="wide")
    st.title("Payment Operations Intelligence Platform")
    st.subheader("Commercial Wire Validation Simulator")
    st.caption("Week 1 • Synthetic data only • Read-only educational simulator")
    try:
        entries = load_payments()
        processing_results = load_processing_results()
    except Exception:
        st.error("The synthetic payment dataset could not be loaded. Restart the dashboard and try again.")
        return
    render_metrics(entries)
    st.subheader("Payments")
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


if __name__ == "__main__":
    main()
