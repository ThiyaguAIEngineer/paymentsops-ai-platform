"""Predetermined synthetic outcomes, not a fraud detection algorithm."""

from types import MappingProxyType

from payment_ops.connectors.base import ConnectorError, FraudDecision, FraudResponse, RecordNotFoundError


_SCREENINGS = MappingProxyType({
    "SYNTHETIC-WIRE-SMALL": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-BALANCE-BOUNDARY": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-LIMIT-BOUNDARY": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-LOW-BALANCE": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-FROZEN": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-CLOSED": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-WIRES-DISABLED": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-LIMIT-EXCEEDED": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-MULTIPLE-REVIEW": FraudResponse(55, FraudDecision.REVIEW),
    "SYNTHETIC-WIRE-REJECT-REVIEW": FraudResponse(90, FraudDecision.HOLD),
    "SYNTHETIC-WIRE-001": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-REVIEW": FraudResponse(55, FraudDecision.REVIEW),
    "SYNTHETIC-WIRE-HOLD": FraudResponse(90, FraudDecision.HOLD),
    "SYNTHETIC-WIRE-POTENTIAL-MATCH": FraudResponse(10, FraudDecision.PASS),
    "SYNTHETIC-WIRE-BLOCKED": FraudResponse(10, FraudDecision.PASS),
})


class MockFraudConnector:
    def screen(self, payment_id: str) -> FraudResponse:
        if payment_id == "SYNTHETIC-WIRE-UNAVAILABLE":
            raise ConnectorError("Synthetic fraud screening unavailable.")
        try:
            return _SCREENINGS[payment_id]
        except KeyError as exc:
            raise RecordNotFoundError(f"Fraud screening record not found for {payment_id!r}.") from exc
