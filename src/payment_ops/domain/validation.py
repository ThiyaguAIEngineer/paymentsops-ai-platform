"""Required-field validation for payment instructions."""

from datetime import date
from decimal import Decimal

from payment_ops.domain.payment import Payment


def validate_payment(payment: Payment) -> list[str]:
    """Collect input errors without modifying the payment instruction."""
    errors: list[str] = []

    for field_name, label in (
        ("payment_id", "Payment ID"),
        ("customer_name", "Customer name"),
        ("sender_account_id", "Sender account ID"),
        ("beneficiary_name", "Beneficiary name"),
        ("beneficiary_account", "Beneficiary account"),
        ("routing_number", "Routing number"),
    ):
        value = getattr(payment, field_name)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{label} is required.")
        elif not isinstance(value, str):
            errors.append(f"{label} must be a string.")

    if payment.amount is None:
        errors.append("Payment amount is required.")
    elif not isinstance(payment.amount, Decimal) or not payment.amount.is_finite():
        errors.append("Payment amount must be a finite Decimal value.")
    elif payment.amount <= 0:
        errors.append("Payment amount must be positive.")

    if payment.payment_date is None:
        errors.append("Payment date is required.")
    elif not isinstance(payment.payment_date, date):
        errors.append("Payment date must be a Python date object.")

    return errors
