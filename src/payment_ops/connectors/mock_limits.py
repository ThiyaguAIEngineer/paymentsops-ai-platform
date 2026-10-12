"""Synthetic account-keyed limits; no usage tracking or limit decisions."""

from decimal import Decimal
from types import MappingProxyType

from payment_ops.connectors.base import LimitsResponse, RecordNotFoundError


_LIMITS = MappingProxyType({
    "SYNTHETIC-SENDER-001": LimitsResponse(Decimal("50000.00")),
    "SYNTHETIC-SENDER-RESTRICTED": LimitsResponse(Decimal("50000.00")),
    "SYNTHETIC-SENDER-CLOSED": LimitsResponse(Decimal("0.00")),
    "SYNTHETIC-SENDER-LOW-BALANCE": LimitsResponse(Decimal("50000.00")),
    "SYNTHETIC-SENDER-WIRES-DISABLED": LimitsResponse(Decimal("50000.00")),
    "SYNTHETIC-SENDER-LOW-LIMIT": LimitsResponse(Decimal("1000.00")),
})


class MockLimitsConnector:
    def get_limit(self, customer_or_account_id: str) -> LimitsResponse:
        try:
            return _LIMITS[customer_or_account_id]
        except KeyError as exc:
            raise RecordNotFoundError(f"Wire limit record not found for {customer_or_account_id!r}.") from exc
