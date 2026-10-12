"""Integration and failure-boundary tests with synthetic data only."""

from dataclasses import replace
from unittest.mock import Mock

import pytest

from payment_ops.connectors.base import (
    ConnectorError, CoreBankingConnector, FraudConnector, LimitsConnector,
    RecordNotFoundError, SanctionsConnector,
)
from payment_ops.connectors.mock_core import MockCoreBankingConnector
from payment_ops.connectors.mock_fraud import MockFraudConnector
from payment_ops.connectors.mock_limits import MockLimitsConnector
from payment_ops.connectors.mock_sanctions import MockSanctionsConnector
from payment_ops.domain.payment import Payment
from payment_ops.samples.payments import SYNTHETIC_PAYMENTS
from payment_ops.services.decision_engine import (
    CheckStatus, PaymentDecision, ValidationArea, evaluate_payment,
)
from payment_ops.services.payment_service import PaymentService


@pytest.fixture
def connectors() -> tuple[Mock, ...]:
    return (
        Mock(spec=CoreBankingConnector, wraps=MockCoreBankingConnector()),
        Mock(spec=LimitsConnector, wraps=MockLimitsConnector()),
        Mock(spec=FraudConnector, wraps=MockFraudConnector()),
        Mock(spec=SanctionsConnector, wraps=MockSanctionsConnector()),
    )


def test_success_interactions_and_engine_consistency(connectors: tuple[Mock, ...]) -> None:
    payment = SYNTHETIC_PAYMENTS[0]
    result = PaymentService(*connectors).process_payment(payment)
    core, limits, fraud, sanctions = connectors
    core.get_account.assert_called_once_with(payment.sender_account_id)
    limits.get_limit.assert_called_once_with(payment.sender_account_id)
    fraud.screen.assert_called_once_with(payment.payment_id)
    sanctions.screen.assert_called_once_with(payment)
    expected = evaluate_payment(
        payment, account=MockCoreBankingConnector().get_account(payment.sender_account_id),
        limits=MockLimitsConnector().get_limit(payment.sender_account_id),
        fraud=MockFraudConnector().screen(payment.payment_id),
        sanctions=MockSanctionsConnector().screen(payment),
    )
    assert result == expected
    assert result.decision is PaymentDecision.READY_FOR_PROCESSING


@pytest.mark.parametrize("payment", [Payment(), *SYNTHETIC_PAYMENTS[15:19]], ids=["all-missing", "missing", "nan", "zero", "negative"])
def test_invalid_input_skips_all_calls(connectors: tuple[Mock, ...], payment: Payment) -> None:
    result = PaymentService(*connectors).process_payment(payment)
    assert result == evaluate_payment(payment)
    assert result.decision is PaymentDecision.REJECTED
    assert all(check.status is CheckStatus.SKIPPED for check in result.checks[1:])
    for connector in connectors:
        assert connector.mock_calls == []


@pytest.mark.parametrize("index,method,areas", [
    (0, "get_account", (ValidationArea.ACCOUNT, ValidationArea.BALANCE)),
    (1, "get_limit", (ValidationArea.LIMIT,)),
    (2, "screen", (ValidationArea.FRAUD,)),
    (3, "screen", (ValidationArea.SANCTIONS,)),
])
@pytest.mark.parametrize("failure", [ConnectorError("private details"), RecordNotFoundError("private details"), TimeoutError("private details"), RuntimeError("private details")])
def test_errors_are_safe_and_other_controls_continue(connectors: tuple[Mock, ...], index: int, method: str, areas: tuple, failure: Exception, caplog) -> None:
    getattr(connectors[index], method).side_effect = failure
    payment = SYNTHETIC_PAYMENTS[0]
    result = PaymentService(*connectors).process_payment(payment)
    assert result.decision is PaymentDecision.MANUAL_REVIEW
    assert tuple(check.area for check in result.checks if check.status is CheckStatus.UNAVAILABLE) == areas
    assert all(len(connector.mock_calls) == 1 for connector in connectors)
    for sensitive in ("private details", payment.sender_account_id, payment.beneficiary_name, payment.beneficiary_account):
        assert sensitive not in caplog.text
        assert sensitive not in " ".join(result.reasons)
    assert "connector lookup failed" in caplog.text


@pytest.mark.parametrize("index,method", [(0, "get_account"), (1, "get_limit"), (2, "screen"), (3, "screen")])
@pytest.mark.parametrize("response", [None, {}])
def test_missing_and_wrong_response_types(connectors: tuple[Mock, ...], index: int, method: str, response: object) -> None:
    getattr(connectors[index], method).return_value = response
    result = PaymentService(*connectors).process_payment(SYNTHETIC_PAYMENTS[0])
    assert result.decision is PaymentDecision.MANUAL_REVIEW
    assert any(check.status is CheckStatus.UNAVAILABLE for check in result.checks)


def test_error_preserves_rejection_and_review(connectors: tuple[Mock, ...]) -> None:
    connectors[3].screen.side_effect = ConnectorError("Synthetic outage")
    payment = SYNTHETIC_PAYMENTS[14]
    result = PaymentService(*connectors).process_payment(payment)
    assert result.decision is PaymentDecision.REJECTED
    assert result.primary_reason == result.checks[2].reasons[0]
    assert [check.status for check in result.checks[2:]] == [
        CheckStatus.REJECTED, CheckStatus.REVIEW, CheckStatus.REVIEW, CheckStatus.UNAVAILABLE,
    ]


def test_all_connector_errors(connectors: tuple[Mock, ...]) -> None:
    for connector, method in zip(connectors, ("get_account", "get_limit", "screen", "screen"), strict=True):
        getattr(connector, method).side_effect = ConnectorError("Synthetic outage")
    result = PaymentService(*connectors).process_payment(SYNTHETIC_PAYMENTS[0])
    assert result.decision is PaymentDecision.MANUAL_REVIEW
    assert all(check.status is CheckStatus.UNAVAILABLE for check in result.checks[1:])


# Independent expected outcomes; neither the sample inputs nor mocks carry
# final decisions. Nonlisted areas must pass, catching accidental missing records.
_EXPECTED = (
    (PaymentDecision.READY_FOR_PROCESSING, {}),
    (PaymentDecision.READY_FOR_PROCESSING, {}),
    (PaymentDecision.READY_FOR_PROCESSING, {}),
    (PaymentDecision.READY_FOR_PROCESSING, {}),
    (PaymentDecision.REJECTED, {ValidationArea.BALANCE: CheckStatus.REJECTED}),
    (PaymentDecision.REJECTED, {ValidationArea.ACCOUNT: CheckStatus.REJECTED}),
    (PaymentDecision.REJECTED, {ValidationArea.ACCOUNT: CheckStatus.REJECTED, ValidationArea.BALANCE: CheckStatus.REJECTED, ValidationArea.LIMIT: CheckStatus.REVIEW}),
    (PaymentDecision.REJECTED, {ValidationArea.ACCOUNT: CheckStatus.REJECTED}),
    (PaymentDecision.MANUAL_REVIEW, {ValidationArea.LIMIT: CheckStatus.REVIEW}),
    (PaymentDecision.MANUAL_REVIEW, {ValidationArea.FRAUD: CheckStatus.REVIEW}),
    (PaymentDecision.MANUAL_REVIEW, {ValidationArea.FRAUD: CheckStatus.REVIEW}),
    (PaymentDecision.MANUAL_REVIEW, {ValidationArea.SANCTIONS: CheckStatus.REVIEW}),
    (PaymentDecision.REJECTED, {ValidationArea.SANCTIONS: CheckStatus.REJECTED}),
    (PaymentDecision.MANUAL_REVIEW, {ValidationArea.LIMIT: CheckStatus.REVIEW, ValidationArea.FRAUD: CheckStatus.REVIEW, ValidationArea.SANCTIONS: CheckStatus.REVIEW}),
    (PaymentDecision.REJECTED, {ValidationArea.BALANCE: CheckStatus.REJECTED, ValidationArea.LIMIT: CheckStatus.REVIEW, ValidationArea.FRAUD: CheckStatus.REVIEW, ValidationArea.SANCTIONS: CheckStatus.REVIEW}),
    *((PaymentDecision.REJECTED, {area: CheckStatus.REJECTED if area is ValidationArea.INPUT else CheckStatus.SKIPPED for area in ValidationArea}),) * 4,
    (PaymentDecision.MANUAL_REVIEW, {ValidationArea.FRAUD: CheckStatus.UNAVAILABLE}),
)


@pytest.mark.parametrize("payment,expected", list(zip(SYNTHETIC_PAYMENTS, _EXPECTED, strict=True)), ids=[payment.payment_id for payment in SYNTHETIC_PAYMENTS])
def test_complete_dataset(connectors: tuple[Mock, ...], payment: Payment, expected: tuple) -> None:
    service = PaymentService(*connectors)
    result = service.process_payment(payment)
    decision, findings = expected
    assert result.payment_id == payment.payment_id
    assert result.decision is decision
    assert len(result.checks) == 6
    assert {check.area: check.status for check in result.checks} == {
        area: findings.get(area, CheckStatus.PASS) for area in ValidationArea
    }
    assert result.reasons == tuple(reason for check in result.checks if check.status is not CheckStatus.PASS for reason in check.reasons)
    if findings:
        assert result.primary_reason in result.reasons
    assert service.process_payment(payment) == result


def test_dataset_integrity() -> None:
    assert len(SYNTHETIC_PAYMENTS) == 20
    assert len({payment.payment_id for payment in SYNTHETIC_PAYMENTS}) == 20


def test_unknown_records_do_not_pass(connectors: tuple[Mock, ...]) -> None:
    payment = replace(SYNTHETIC_PAYMENTS[0], payment_id="SYNTHETIC-UNKNOWN", sender_account_id="SYNTHETIC-UNKNOWN")
    result = PaymentService(*connectors).process_payment(payment)
    assert result.decision is PaymentDecision.MANUAL_REVIEW
    assert all(check.status is CheckStatus.UNAVAILABLE for check in result.checks[1:])
