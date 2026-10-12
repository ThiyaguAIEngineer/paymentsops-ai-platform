"""Twenty deterministic synthetic wire instructions for Week 1 demonstrations.

Scenario identifiers correspond to explicit mock connector records. The
UNAVAILABLE scenario intentionally triggers a synthetic fraud connector error.
No balances, screening results, or expected decisions are embedded in Payments.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

from payment_ops.domain.payment import Payment


_BASE = Payment(
    payment_id="SYNTHETIC-WIRE-001",
    customer_name="Synthetic Commercial Customer LLC",
    sender_account_id="SYNTHETIC-SENDER-001",
    beneficiary_name="Synthetic Supplier LLC",
    beneficiary_account="000000123456",
    routing_number="000000000",
    amount=Decimal("12500.50"),
    payment_date=date(2026, 10, 12),
)


SYNTHETIC_PAYMENTS: tuple[Payment, ...] = (
    _BASE,
    replace(_BASE, payment_id="SYNTHETIC-WIRE-SMALL", amount=Decimal("1.00")),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-BALANCE-BOUNDARY", sender_account_id="SYNTHETIC-SENDER-LOW-BALANCE", amount=Decimal("100.00")),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-LIMIT-BOUNDARY", amount=Decimal("50000.00")),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-LOW-BALANCE", sender_account_id="SYNTHETIC-SENDER-LOW-BALANCE"),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-FROZEN", sender_account_id="SYNTHETIC-SENDER-FROZEN"),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-CLOSED", sender_account_id="SYNTHETIC-SENDER-CLOSED"),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-WIRES-DISABLED", sender_account_id="SYNTHETIC-SENDER-WIRES-DISABLED"),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-LIMIT-EXCEEDED", amount=Decimal("50000.01")),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-REVIEW"),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-HOLD"),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-POTENTIAL-MATCH"),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-BLOCKED"),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-MULTIPLE-REVIEW", sender_account_id="SYNTHETIC-SENDER-LOW-LIMIT"),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-REJECT-REVIEW", sender_account_id="SYNTHETIC-SENDER-LOW-BALANCE", amount=Decimal("50000.01")),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-MISSING", beneficiary_name=None, routing_number=" "),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-NAN", amount=Decimal("NaN")),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-ZERO", amount=Decimal("0")),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-NEGATIVE", amount=Decimal("-1.00")),
    replace(_BASE, payment_id="SYNTHETIC-WIRE-UNAVAILABLE"),
)
