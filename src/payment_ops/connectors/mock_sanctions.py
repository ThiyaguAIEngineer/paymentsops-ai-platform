"""Predetermined synthetic screening keyed by payment ID, not name matching."""

from types import MappingProxyType

from payment_ops.connectors.base import RecordNotFoundError, SanctionsResponse, SanctionsResult
from payment_ops.domain.payment import Payment


_SCREENINGS = MappingProxyType({
    "SYNTHETIC-WIRE-SMALL": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-BALANCE-BOUNDARY": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-LIMIT-BOUNDARY": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-LOW-BALANCE": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-FROZEN": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-CLOSED": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-WIRES-DISABLED": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-LIMIT-EXCEEDED": SanctionsResponse(SanctionsResult.CLEAR),
    "SYNTHETIC-WIRE-MULTIPLE-REVIEW": SanctionsResponse(SanctionsResult.POTENTIAL_MATCH),
    "SYNTHETIC-WIRE-REJECT-REVIEW": SanctionsResponse(SanctionsResult.POTENTIAL_MATCH),
    "SYNTHETIC-WIRE-UNAVAILABLE": SanctionsResponse(SanctionsResult.CLEAR),
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
