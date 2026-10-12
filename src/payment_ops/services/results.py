"""Immutable service results separating connector evidence from decisions."""

from dataclasses import dataclass

from payment_ops.connectors.base import AccountResponse, FraudResponse, LimitsResponse, SanctionsResponse
from payment_ops.services.decision_engine import DecisionResult


@dataclass(frozen=True)
class ConnectorEvidence:
    """Retrieved responses; absent values are explained by decision findings."""

    account: AccountResponse | None = None
    limits: LimitsResponse | None = None
    fraud: FraudResponse | None = None
    sanctions: SanctionsResponse | None = None


@dataclass(frozen=True)
class PaymentProcessingResult:
    decision: DecisionResult
    evidence: ConnectorEvidence
