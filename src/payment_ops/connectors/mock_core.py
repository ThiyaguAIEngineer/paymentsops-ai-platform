"""Synthetic core account records; no balances are changed by lookups."""

from decimal import Decimal
from types import MappingProxyType

from payment_ops.connectors.base import AccountResponse, AccountStatus, RecordNotFoundError


_ACCOUNTS = MappingProxyType({
    "SYNTHETIC-SENDER-001": AccountResponse(AccountStatus.ACTIVE, Decimal("100000.00"), True),
    "SYNTHETIC-SENDER-RESTRICTED": AccountResponse(AccountStatus.RESTRICTED, Decimal("100000.00"), True),
    "SYNTHETIC-SENDER-CLOSED": AccountResponse(AccountStatus.CLOSED, Decimal("0.00"), False),
    "SYNTHETIC-SENDER-LOW-BALANCE": AccountResponse(AccountStatus.ACTIVE, Decimal("100.00"), True),
    "SYNTHETIC-SENDER-WIRES-DISABLED": AccountResponse(AccountStatus.ACTIVE, Decimal("100000.00"), False),
    "SYNTHETIC-SENDER-LOW-LIMIT": AccountResponse(AccountStatus.ACTIVE, Decimal("100000.00"), True),
})


class MockCoreBankingConnector:
    def get_account(self, sender_account_id: str) -> AccountResponse:
        try:
            return _ACCOUNTS[sender_account_id]
        except KeyError as exc:
            raise RecordNotFoundError(f"Core account record not found for {sender_account_id!r}.") from exc
