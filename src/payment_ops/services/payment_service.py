"""Coordinate input validation, injected connectors, and decision evaluation."""

import logging
from collections.abc import Callable

from payment_ops.connectors.base import (
    AccountResponse, ConnectorError, CoreBankingConnector, FraudConnector,
    FraudResponse, LimitsConnector, LimitsResponse, SanctionsConnector,
    SanctionsResponse,
)
from payment_ops.domain.payment import Payment
from payment_ops.domain.validation import validate_payment
from payment_ops.services.decision_engine import DecisionResult, evaluate_payment


logger = logging.getLogger(__name__)


def _lookup[T](label: str, operation: Callable[[], T], response_type: type[T]) -> T | ConnectorError:
    """Normalize failures at the connector boundary without exposing details."""
    try:
        response = operation()
    except Exception:
        # Connector implementations may raise transport errors outside ConnectorError.
        # Do not log exception messages or tracebacks containing payment details.
        logger.warning("%s connector lookup failed; control unavailable.", label)
        return ConnectorError(f"{label} connector lookup failed")
    if not isinstance(response, response_type):
        logger.warning("%s connector returned missing or invalid information.", label)
        return ConnectorError(f"{label} connector returned missing or invalid information")
    return response


class PaymentService:
    """Process a payment using interface dependencies supplied by the caller."""

    def __init__(
        self,
        core: CoreBankingConnector,
        limits: LimitsConnector,
        fraud: FraudConnector,
        sanctions: SanctionsConnector,
    ) -> None:
        self._core = core
        self._limits = limits
        self._fraud = fraud
        self._sanctions = sanctions

    def process_payment(self, payment: Payment) -> DecisionResult:
        if validate_payment(payment):
            return evaluate_payment(payment)

        # Validated identifiers are present. Each independent lookup is attempted,
        # preserving available rejection/review facts when another control fails.
        account = _lookup("Core banking", lambda: self._core.get_account(payment.sender_account_id), AccountResponse)
        limits = _lookup("Limits", lambda: self._limits.get_limit(payment.sender_account_id), LimitsResponse)
        fraud = _lookup("Fraud", lambda: self._fraud.screen(payment.payment_id), FraudResponse)
        sanctions = _lookup("Sanctions", lambda: self._sanctions.screen(payment), SanctionsResponse)
        return evaluate_payment(payment, account=account, limits=limits, fraud=fraud, sanctions=sanctions)
