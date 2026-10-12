"""Read-only connector contracts; implementations must raise on lookup failures."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from payment_ops.domain.payment import Payment


class ConnectorError(Exception):
    """A connector could not provide a response; never implies approval."""


class RecordNotFoundError(ConnectorError):
    """No record exists for the supplied lookup identifier."""


class AccountStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RESTRICTED = "RESTRICTED"
    CLOSED = "CLOSED"


class FraudDecision(StrEnum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    HOLD = "HOLD"


class SanctionsResult(StrEnum):
    CLEAR = "CLEAR"
    POTENTIAL_MATCH = "POTENTIAL_MATCH"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class AccountResponse:
    account_status: AccountStatus
    available_balance: Decimal
    wire_payments_enabled: bool


@dataclass(frozen=True)
class LimitsResponse:
    single_wire_limit: Decimal


@dataclass(frozen=True)
class FraudResponse:
    """Predetermined synthetic score on a 0–100 scale and screening decision."""

    score: int
    decision: FraudDecision


@dataclass(frozen=True)
class SanctionsResponse:
    result: SanctionsResult


class CoreBankingConnector(Protocol):
    def get_account(self, sender_account_id: str) -> AccountResponse:
        """Retrieve account facts, or raise ConnectorError."""
        ...


class LimitsConnector(Protocol):
    def get_limit(self, customer_or_account_id: str) -> LimitsResponse:
        """Retrieve the configured single-wire limit, or raise ConnectorError."""
        ...


class FraudConnector(Protocol):
    def screen(self, payment_id: str) -> FraudResponse:
        """Retrieve screening facts, or raise ConnectorError."""
        ...


class SanctionsConnector(Protocol):
    def screen(self, payment: Payment) -> SanctionsResponse:
        """Screen payment information, or raise ConnectorError."""
        ...
