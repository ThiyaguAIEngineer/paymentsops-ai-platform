"""Tests using synthetic commercial wire instructions."""

from dataclasses import FrozenInstanceError, fields
from datetime import date
from decimal import Decimal

import pytest

from payment_ops.domain.payment import Payment


def test_synthetic_commercial_wire_attributes() -> None:
    payment = Payment(
        payment_id="SYNTHETIC-WIRE-001",
        customer_name="Synthetic Commercial Customer LLC",
        sender_account_id="SYNTHETIC-SENDER-001",
        beneficiary_name="Synthetic Supplier LLC",
        beneficiary_account="000000123456",
        routing_number="000000000",
        amount=Decimal("12500.50"),
        payment_date=date(2026, 10, 11),
    )

    assert payment.payment_id == "SYNTHETIC-WIRE-001"
    assert payment.customer_name == "Synthetic Commercial Customer LLC"
    assert payment.sender_account_id == "SYNTHETIC-SENDER-001"
    assert payment.beneficiary_name == "Synthetic Supplier LLC"
    assert payment.beneficiary_account == "000000123456"
    assert payment.routing_number == "000000000"
    assert payment.amount == Decimal("12500.50")
    assert isinstance(payment.amount, Decimal)
    assert payment.payment_date == date(2026, 10, 11)
    assert isinstance(payment.payment_date, date)


def test_payment_allows_missing_fields() -> None:
    payment = Payment()

    assert all(getattr(payment, field.name) is None for field in fields(payment))


def test_payment_is_immutable() -> None:
    payment = Payment(payment_id="SYNTHETIC-WIRE-001")

    with pytest.raises(FrozenInstanceError):
        payment.payment_id = "SYNTHETIC-WIRE-002"
