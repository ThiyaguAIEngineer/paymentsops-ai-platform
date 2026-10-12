"""Read-only connector tests using only synthetic banking records."""

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from payment_ops.connectors.base import (
    AccountStatus, ConnectorError, CoreBankingConnector, FraudConnector,
    FraudDecision, LimitsConnector, RecordNotFoundError, SanctionsConnector,
    SanctionsResult,
)
from payment_ops.connectors.mock_core import MockCoreBankingConnector
from payment_ops.connectors.mock_fraud import MockFraudConnector
from payment_ops.connectors.mock_limits import MockLimitsConnector
from payment_ops.connectors.mock_sanctions import MockSanctionsConnector
from payment_ops.domain.payment import Payment


@pytest.mark.parametrize("account_id,status,balance,enabled", [
    ("SYNTHETIC-SENDER-001", AccountStatus.ACTIVE, "100000.00", True),
    ("SYNTHETIC-SENDER-RESTRICTED", AccountStatus.RESTRICTED, "100000.00", True),
    ("SYNTHETIC-SENDER-CLOSED", AccountStatus.CLOSED, "0.00", False),
    ("SYNTHETIC-SENDER-LOW-BALANCE", AccountStatus.ACTIVE, "100.00", True),
    ("SYNTHETIC-SENDER-WIRES-DISABLED", AccountStatus.ACTIVE, "100000.00", False),
    ("SYNTHETIC-SENDER-LOW-LIMIT", AccountStatus.ACTIVE, "100000.00", True),
])
def test_core_accounts(account_id: str, status: AccountStatus, balance: str, enabled: bool) -> None:
    connector: CoreBankingConnector = MockCoreBankingConnector()
    response = connector.get_account(account_id)
    assert response.account_status is status
    assert response.available_balance == Decimal(balance)
    assert isinstance(response.available_balance, Decimal)
    assert response.wire_payments_enabled is enabled
    assert connector.get_account(account_id) == response
    with pytest.raises(FrozenInstanceError):
        response.available_balance = Decimal("0")


@pytest.mark.parametrize("account_id,limit", [
    ("SYNTHETIC-SENDER-001", "50000.00"),
    ("SYNTHETIC-SENDER-RESTRICTED", "50000.00"),
    ("SYNTHETIC-SENDER-CLOSED", "0.00"),
    ("SYNTHETIC-SENDER-LOW-BALANCE", "50000.00"),
    ("SYNTHETIC-SENDER-WIRES-DISABLED", "50000.00"),
    ("SYNTHETIC-SENDER-LOW-LIMIT", "1000.00"),
])
def test_wire_limits(account_id: str, limit: str) -> None:
    connector: LimitsConnector = MockLimitsConnector()
    response = connector.get_limit(account_id)
    assert response.single_wire_limit == Decimal(limit)
    assert isinstance(response.single_wire_limit, Decimal)
    assert connector.get_limit(account_id) == response
    with pytest.raises(FrozenInstanceError):
        response.single_wire_limit = Decimal("0")


@pytest.mark.parametrize("payment_id,score,decision", [
    ("SYNTHETIC-WIRE-001", 10, FraudDecision.PASS),
    ("SYNTHETIC-WIRE-REVIEW", 55, FraudDecision.REVIEW),
    ("SYNTHETIC-WIRE-HOLD", 90, FraudDecision.HOLD),
    ("SYNTHETIC-WIRE-POTENTIAL-MATCH", 10, FraudDecision.PASS),
    ("SYNTHETIC-WIRE-BLOCKED", 10, FraudDecision.PASS),
])
def test_fraud_screenings(payment_id: str, score: int, decision: FraudDecision) -> None:
    connector: FraudConnector = MockFraudConnector()
    response = connector.screen(payment_id)
    assert response.score == score
    assert response.decision is decision
    assert connector.screen(payment_id) == response
    with pytest.raises(FrozenInstanceError):
        response.score = 0


@pytest.mark.parametrize("payment_id,result", [
    ("SYNTHETIC-WIRE-001", SanctionsResult.CLEAR),
    ("SYNTHETIC-WIRE-REVIEW", SanctionsResult.CLEAR),
    ("SYNTHETIC-WIRE-HOLD", SanctionsResult.CLEAR),
    ("SYNTHETIC-WIRE-POTENTIAL-MATCH", SanctionsResult.POTENTIAL_MATCH),
    ("SYNTHETIC-WIRE-BLOCKED", SanctionsResult.BLOCKED),
])
def test_sanctions_screenings(payment_id: str, result: SanctionsResult) -> None:
    connector: SanctionsConnector = MockSanctionsConnector()
    payment = Payment(payment_id=payment_id, beneficiary_name="Synthetic Supplier LLC")
    response = connector.screen(payment)
    assert response.result is result
    assert connector.screen(payment) == response
    assert payment.beneficiary_name == "Synthetic Supplier LLC"
    with pytest.raises(FrozenInstanceError):
        response.result = SanctionsResult.CLEAR


@pytest.mark.parametrize("identifier", ["SYNTHETIC-UNKNOWN", "", " ", None])
@pytest.mark.parametrize("lookup,label", [
    (MockCoreBankingConnector().get_account, "Core account"),
    (MockLimitsConnector().get_limit, "Wire limit"),
    (MockFraudConnector().screen, "Fraud screening"),
    (lambda identifier: MockSanctionsConnector().screen(Payment(payment_id=identifier)), "Sanctions screening"),
])
def test_missing_records_raise_explicit_errors(lookup, label: str, identifier: str | None) -> None:
    with pytest.raises(RecordNotFoundError, match=f"{label} record not found") as error:
        lookup(identifier)
    assert isinstance(error.value, ConnectorError)
    assert isinstance(error.value.__cause__, KeyError)
