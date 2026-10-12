"""Payment input validation tests using synthetic instructions."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from payment_ops.domain.payment import Payment
from payment_ops.domain.validation import validate_payment


@pytest.fixture
def payment() -> Payment:
    return Payment(
        payment_id="SYNTHETIC-WIRE-001",
        customer_name="Synthetic Customer LLC",
        sender_account_id="SYNTHETIC-SENDER-001",
        beneficiary_name="Synthetic Supplier LLC",
        beneficiary_account="000000123456",
        routing_number="000000000",
        amount=Decimal("12500.50"),
        payment_date=date(2026, 10, 12),
    )


def test_valid_payment(payment: Payment) -> None:
    assert validate_payment(payment) == []


def test_missing_fields_collects_all_errors() -> None:
    assert validate_payment(Payment()) == [
        "Payment ID is required.",
        "Customer name is required.",
        "Sender account ID is required.",
        "Beneficiary name is required.",
        "Beneficiary account is required.",
        "Routing number is required.",
        "Payment amount is required.",
        "Payment date is required.",
    ]


@pytest.mark.parametrize("field_name", [
    "payment_id", "customer_name", "sender_account_id",
    "beneficiary_name", "beneficiary_account", "routing_number",
])
@pytest.mark.parametrize("value", [None, "", " ", "\t\n"])
def test_required_strings(payment: Payment, field_name: str, value: str | None) -> None:
    errors = validate_payment(replace(payment, **{field_name: value}))
    assert len(errors) == 1
    assert errors[0].endswith("is required.")


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-0"), Decimal("-0.01")])
def test_nonpositive_amounts(payment: Payment, amount: Decimal) -> None:
    assert validate_payment(replace(payment, amount=amount)) == [
        "Payment amount must be positive."
    ]


@pytest.mark.parametrize("amount", [
    "12500.50", "invalid", 100, 1.5, True,
    Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity"),
])
def test_invalid_amounts(payment: Payment, amount: object) -> None:
    assert validate_payment(replace(payment, amount=amount)) == [
        "Payment amount must be a finite Decimal value."
    ]


@pytest.mark.parametrize("value", ["2026-10-12", "invalid", 123])
def test_invalid_dates(payment: Payment, value: object) -> None:
    assert validate_payment(replace(payment, payment_date=value)) == [
        "Payment date must be a Python date object."
    ]


def test_nonstring_field(payment: Payment) -> None:
    assert validate_payment(replace(payment, routing_number=123)) == [
        "Routing number must be a string."
    ]


def test_validation_preserves_original_values(payment: Payment) -> None:
    instruction = replace(payment, customer_name="  Synthetic Customer LLC  ")
    original = replace(instruction)
    assert validate_payment(instruction) == []
    assert instruction == original


def test_collects_errors_across_field_types(payment: Payment) -> None:
    instruction = replace(payment, payment_id="", amount=Decimal("NaN"), payment_date=None)
    assert validate_payment(instruction) == [
        "Payment ID is required.",
        "Payment amount must be a finite Decimal value.",
        "Payment date is required.",
    ]
