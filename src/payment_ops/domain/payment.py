"""Payment instructions independent of validation and external systems."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Payment:
    """A payment instruction that may be incomplete pending validation."""

    payment_id: str | None = None
    customer_name: str | None = None
    sender_account_id: str | None = None
    beneficiary_name: str | None = None
    beneficiary_account: str | None = None
    routing_number: str | None = None
    amount: Decimal | None = None
    payment_date: date | None = None
