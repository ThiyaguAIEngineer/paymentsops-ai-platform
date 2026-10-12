"""Deterministic control evaluation using synthetic payment facts."""

from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal

import pytest

from payment_ops.connectors.base import (
    AccountResponse, AccountStatus, ConnectorError, FraudDecision, FraudResponse,
    LimitsResponse, RecordNotFoundError, SanctionsResponse, SanctionsResult,
)
from payment_ops.domain.payment import Payment
from payment_ops.domain.validation import validate_payment
from payment_ops.services.decision_engine import (
    CheckStatus, PaymentDecision, ValidationArea, evaluate_payment,
)


@pytest.fixture
def payment() -> Payment:
    return Payment(
        payment_id="SYNTHETIC-WIRE-001", customer_name="Synthetic Customer LLC",
        sender_account_id="SYNTHETIC-SENDER-001", beneficiary_name="Synthetic Supplier LLC",
        beneficiary_account="000000123456", routing_number="000000000",
        amount=Decimal("100.00"), payment_date=date(2026, 10, 12),
    )


@pytest.fixture
def controls() -> dict:
    return {
        "account": AccountResponse(AccountStatus.ACTIVE, Decimal("200.00"), True),
        "limits": LimitsResponse(Decimal("200.00")),
        "fraud": FraudResponse(10, FraudDecision.PASS),
        "sanctions": SanctionsResponse(SanctionsResult.CLEAR),
    }


def test_success_is_deterministic_and_immutable(payment: Payment, controls: dict) -> None:
    original = replace(payment)
    result = evaluate_payment(payment, **controls)
    assert result == evaluate_payment(payment, **controls)
    assert result.payment_id == payment.payment_id
    assert result.decision is PaymentDecision.READY_FOR_PROCESSING
    assert [check.area for check in result.checks] == list(ValidationArea)
    assert all(check.status is CheckStatus.PASS for check in result.checks)
    assert result.reasons == ()
    assert result.primary_reason == "All mandatory validation checks passed."
    assert payment == original
    with pytest.raises(FrozenInstanceError):
        result.primary_reason = "changed"


@pytest.mark.parametrize("status", [AccountStatus.INACTIVE, AccountStatus.FROZEN, AccountStatus.CLOSED, AccountStatus.RESTRICTED])
def test_nonactive_accounts(payment: Payment, controls: dict, status: AccountStatus) -> None:
    controls["account"] = replace(controls["account"], account_status=status)
    result = evaluate_payment(payment, **controls)
    assert result.decision is PaymentDecision.REJECTED
    assert status.value in result.primary_reason
    assert result.checks[1].status is CheckStatus.REJECTED


def test_wire_disabled(payment: Payment, controls: dict) -> None:
    controls["account"] = replace(controls["account"], wire_payments_enabled=False)
    result = evaluate_payment(payment, **controls)
    assert result.decision is PaymentDecision.REJECTED
    assert result.primary_reason == "Wire payments are disabled for the account."


@pytest.mark.parametrize("balance,decision", [
    ("99.99", PaymentDecision.REJECTED),
    ("100.00", PaymentDecision.READY_FOR_PROCESSING),
    ("100.01", PaymentDecision.READY_FOR_PROCESSING),
])
def test_balance_boundary(payment: Payment, controls: dict, balance: str, decision: PaymentDecision) -> None:
    controls["account"] = replace(controls["account"], available_balance=Decimal(balance))
    result = evaluate_payment(payment, **controls)
    assert result.decision is decision
    assert result.checks[2].status is (CheckStatus.REJECTED if decision is PaymentDecision.REJECTED else CheckStatus.PASS)


@pytest.mark.parametrize("limit,decision", [
    ("99.99", PaymentDecision.MANUAL_REVIEW),
    ("100.00", PaymentDecision.READY_FOR_PROCESSING),
    ("100.01", PaymentDecision.READY_FOR_PROCESSING),
])
def test_limit_boundary(payment: Payment, controls: dict, limit: str, decision: PaymentDecision) -> None:
    controls["limits"] = LimitsResponse(Decimal(limit))
    result = evaluate_payment(payment, **controls)
    assert result.decision is decision
    assert result.checks[3].status is (CheckStatus.REVIEW if decision is PaymentDecision.MANUAL_REVIEW else CheckStatus.PASS)


@pytest.mark.parametrize("decision", list(FraudDecision))
def test_fraud_uses_decision_not_score(payment: Payment, controls: dict, decision: FraudDecision) -> None:
    controls["fraud"] = FraudResponse(100 if decision is FraudDecision.PASS else 0, decision)
    result = evaluate_payment(payment, **controls)
    expected = PaymentDecision.READY_FOR_PROCESSING if decision is FraudDecision.PASS else PaymentDecision.MANUAL_REVIEW
    assert result.decision is expected
    assert decision.value in result.checks[4].reasons[0]


@pytest.mark.parametrize("screening,decision,status", [
    (SanctionsResult.CLEAR, PaymentDecision.READY_FOR_PROCESSING, CheckStatus.PASS),
    (SanctionsResult.POTENTIAL_MATCH, PaymentDecision.MANUAL_REVIEW, CheckStatus.REVIEW),
    (SanctionsResult.BLOCKED, PaymentDecision.REJECTED, CheckStatus.REJECTED),
])
def test_sanctions(payment: Payment, controls: dict, screening: SanctionsResult, decision: PaymentDecision, status: CheckStatus) -> None:
    controls["sanctions"] = SanctionsResponse(screening)
    result = evaluate_payment(payment, **controls)
    assert result.decision is decision
    assert result.checks[5].status is status


def test_all_findings_preserved_and_rejection_precedes_review(payment: Payment, controls: dict) -> None:
    controls["limits"] = LimitsResponse(Decimal("50"))
    controls["fraud"] = FraudResponse(55, FraudDecision.REVIEW)
    controls["sanctions"] = SanctionsResponse(SanctionsResult.POTENTIAL_MATCH)
    review = evaluate_payment(payment, **controls)
    assert review.decision is PaymentDecision.MANUAL_REVIEW
    assert len(review.reasons) == 3
    assert review.primary_reason == review.checks[3].reasons[0]

    controls["sanctions"] = SanctionsResponse(SanctionsResult.BLOCKED)
    rejected = evaluate_payment(payment, **controls)
    assert rejected.decision is PaymentDecision.REJECTED
    assert len(rejected.reasons) == 3
    assert rejected.primary_reason == rejected.checks[5].reasons[0]

    controls["account"] = AccountResponse(AccountStatus.FROZEN, Decimal("0"), False)
    multiple = evaluate_payment(payment, **controls)
    assert len(multiple.reasons) == 6
    assert multiple.primary_reason == multiple.checks[1].reasons[0]


@pytest.mark.parametrize("changes", [
    {"amount": Decimal("NaN")}, {"amount": Decimal("Infinity")},
    {"amount": Decimal("0")}, {"amount": Decimal("-1")},
    {"amount": "100"}, {"customer_name": " "}, {"payment_date": None},
    {"payment_id": None},
])
def test_invalid_input_skips_downstream(payment: Payment, controls: dict, changes: dict) -> None:
    invalid = replace(payment, **changes)
    result = evaluate_payment(invalid, **controls)
    assert result.decision is PaymentDecision.REJECTED
    assert result.checks[0].reasons == tuple(validate_payment(invalid))
    assert all(check.status is CheckStatus.SKIPPED for check in result.checks[1:])
    assert result.primary_reason == validate_payment(invalid)[0]


def test_all_missing_payment_fields() -> None:
    result = evaluate_payment(Payment())
    assert result.payment_id is None
    assert result.decision is PaymentDecision.REJECTED
    assert len(result.checks[0].reasons) == 8
    assert len(result.checks) == 6


@pytest.mark.parametrize("control,index", [("account", 1), ("limits", 3), ("fraud", 4), ("sanctions", 5)])
@pytest.mark.parametrize("failure", [None, ConnectorError("Synthetic timeout"), RecordNotFoundError("Synthetic missing record")])
def test_unavailable_controls(payment: Payment, controls: dict, control: str, index: int, failure: object) -> None:
    controls[control] = failure
    result = evaluate_payment(payment, **controls)
    assert result.decision is PaymentDecision.MANUAL_REVIEW
    assert result.checks[index].status is CheckStatus.UNAVAILABLE
    assert "unavailable" in result.primary_reason
    if failure is not None:
        assert str(failure) in result.primary_reason
    if control == "account":
        assert result.checks[2].status is CheckStatus.UNAVAILABLE


def test_all_controls_unavailable(payment: Payment) -> None:
    result = evaluate_payment(payment)
    assert result.decision is PaymentDecision.MANUAL_REVIEW
    assert all(check.status is CheckStatus.UNAVAILABLE for check in result.checks[1:])
    assert result.primary_reason == result.checks[1].reasons[0]


def test_unavailable_does_not_override_rejection(payment: Payment, controls: dict) -> None:
    controls["account"] = ConnectorError("Synthetic timeout")
    controls["fraud"] = None
    controls["sanctions"] = SanctionsResponse(SanctionsResult.BLOCKED)
    result = evaluate_payment(payment, **controls)
    assert result.decision is PaymentDecision.REJECTED
    assert result.primary_reason == "Sanctions screening returned BLOCKED."
    assert len(result.reasons) == 4


@pytest.mark.parametrize("control,response,index", [
    ("account", AccountResponse("UNKNOWN", Decimal("200"), True), 1),
    ("account", AccountResponse(AccountStatus.ACTIVE, Decimal("NaN"), True), 2),
    ("account", AccountResponse(AccountStatus.ACTIVE, Decimal("Infinity"), True), 2),
    ("account", AccountResponse(AccountStatus.ACTIVE, "200", True), 2),
    ("account", AccountResponse(AccountStatus.ACTIVE, Decimal("200"), None), 1),
    ("limits", LimitsResponse(Decimal("sNaN")), 3),
    ("limits", LimitsResponse(Decimal("Infinity")), 3),
    ("limits", LimitsResponse(Decimal("-1")), 3),
    ("limits", LimitsResponse("200"), 3),
    ("fraud", FraudResponse(10, "UNKNOWN"), 4),
    ("sanctions", SanctionsResponse("UNKNOWN"), 5),
    ("fraud", object(), 4),
])
def test_malformed_control_cannot_release(payment: Payment, controls: dict, control: str, response: object, index: int) -> None:
    controls[control] = response
    result = evaluate_payment(payment, **controls)
    assert result.decision is PaymentDecision.MANUAL_REVIEW
    assert result.checks[index].status is CheckStatus.UNAVAILABLE
