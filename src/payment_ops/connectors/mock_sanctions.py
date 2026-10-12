"""Predetermined synthetic screening keyed by payment ID, not name matching."""

from types import MappingProxyType

from payment_ops.connectors.base import RecordNotFoundError, SanctionsResponse, SanctionsResult
from payment_ops.domain.payment import Payment


_SCREENINGS = MappingProxyType({
    "SYNTHETIC-WIRE-001": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-REVIEW": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-HOLD": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-POTENTIAL-MATCH": SanctionsResponse(SanctionsResult.POTENTIAL_MATCH),
    "SYNTHETIC-WIRE-BLOCKED": SanctionsResponse(SanctionsResult.BLOCKED),
})


class MockSanctionsConnector:
    def screen(self, payment: Payment) -> SanctionsResponse:
        try:
            return _SCREENINGS[payment.payment_id]
        except KeyError as exc:
            raise RecordNotFoundError(f"Sanctions screening record not found for {payment.payment_id!r}.") from exc
