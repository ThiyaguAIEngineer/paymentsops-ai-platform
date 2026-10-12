"""Pure presentation helpers; all decisions come from the Payment Service."""

from decimal import Decimal
from enum import StrEnum

from payment_ops.domain.payment import Payment
from payment_ops.services.decision_engine import CheckStatus, DecisionResult, PaymentDecision, ValidationArea
from payment_ops.services.results import PaymentProcessingResult


type PaymentEntry = tuple[Payment, DecisionResult]

DECISION_LABELS = {
    PaymentDecision.READY_FOR_PROCESSING: "🟢 READY FOR PROCESSING",
    PaymentDecision.MANUAL_REVIEW: "🟠 MANUAL REVIEW",
    PaymentDecision.REJECTED: "🔴 REJECTED",
}


def format_amount(amount: object) -> str:
    if amount is None:
        return "Missing"
    if not isinstance(amount, Decimal) or not amount.is_finite():
        return "Invalid amount"
    return f"${amount:,.2f}"


def aggregate_metrics(entries: list[PaymentEntry]) -> dict:
    amounts = [payment.amount for payment, _ in entries]
    included = [amount for amount in amounts if isinstance(amount, Decimal) and amount.is_finite() and amount > 0]
    return {
        "total_payments": len(entries),
        "total_value": sum(included, Decimal("0")),
        "excluded_amounts": len(amounts) - len(included),
        "decision_counts": {decision: sum(result.decision is decision for _, result in entries) for decision in PaymentDecision},
    }


def filter_payments(entries: list[PaymentEntry], decision: PaymentDecision | None) -> list[PaymentEntry]:
    return [entry for entry in entries if decision is None or entry[1].decision is decision]


def payment_rows(entries: list[PaymentEntry]) -> list[dict[str, str]]:
    return [
        {
            "Payment ID": payment.payment_id or "Missing",
            "Customer Name": payment.customer_name or "Missing",
            "Amount": format_amount(payment.amount),
            "Final Decision": DECISION_LABELS[result.decision],
            "Primary Reason": result.primary_reason,
        }
        for payment, result in entries
    ]


def evidence_rows(processing: PaymentProcessingResult) -> list[dict[str, str]]:
    """Present only explanatory fields, with no invented missing values."""
    evidence = processing.evidence
    statuses = {check.area: check.status for check in processing.decision.checks}
    rows: list[dict[str, str]] = []
    for area, response, field_name, label, kind in (
        (ValidationArea.ACCOUNT, evidence.account, "account_status", "Account status", "enum"),
        (ValidationArea.ACCOUNT, evidence.account, "wire_payments_enabled", "Wire-enabled", "bool"),
        (ValidationArea.BALANCE, evidence.account, "available_balance", "Available balance", "money"),
        (ValidationArea.LIMIT, evidence.limits, "single_wire_limit", "Single-wire limit", "money"),
        (ValidationArea.FRAUD, evidence.fraud, "score", "Fraud score (0–100)", "score"),
        (ValidationArea.FRAUD, evidence.fraud, "decision", "Fraud screening decision", "enum"),
        (ValidationArea.SANCTIONS, evidence.sanctions, "result", "Sanctions screening result", "enum"),
    ):
        value = getattr(response, field_name, None)
        if kind == "money" and isinstance(value, Decimal) and value.is_finite():
            display = format_amount(value)
        elif kind == "enum" and isinstance(value, StrEnum):
            display = value.value
        elif kind == "bool" and isinstance(value, bool):
            display = "Yes" if value else "No"
        elif kind == "score" and type(value) is int:
            display = str(value)
        else:
            display = "SKIPPED — not retrieved" if statuses[area] is CheckStatus.SKIPPED else "UNAVAILABLE — no usable evidence"
        availability = "SKIPPED" if statuses[area] is CheckStatus.SKIPPED else "UNAVAILABLE" if display.startswith("UNAVAILABLE") else "Retrieved"
        rows.append({"Field": label, "Value": display, "Evidence": availability})
    return rows
