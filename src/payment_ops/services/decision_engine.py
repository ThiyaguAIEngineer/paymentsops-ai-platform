"""Deterministic evaluation of payment instructions and supplied control facts."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from payment_ops.connectors.base import (
    AccountResponse, AccountStatus, ConnectorError, FraudDecision, FraudResponse,
    LimitsResponse, SanctionsResponse, SanctionsResult,
)
from payment_ops.domain.payment import Payment
from payment_ops.domain.validation import validate_payment


class PaymentDecision(StrEnum):
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL REVIEW"
    READY_FOR_PROCESSING = "READY FOR PROCESSING"


class CheckStatus(StrEnum):
    PASS = "PASS"
    REJECTED = "REJECTED"
    REVIEW = "REVIEW"
    UNAVAILABLE = "UNAVAILABLE"
    SKIPPED = "SKIPPED"


class ValidationArea(StrEnum):
    INPUT = "Payment input"
    ACCOUNT = "Account"
    BALANCE = "Available balance"
    LIMIT = "Wire limit"
    FRAUD = "Fraud"
    SANCTIONS = "Sanctions"


@dataclass(frozen=True)
class CheckResult:
    area: ValidationArea
    status: CheckStatus
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class DecisionResult:
    payment_id: str | None
    decision: PaymentDecision
    checks: tuple[CheckResult, ...]
    reasons: tuple[str, ...]
    primary_reason: str


def _unavailable(area: ValidationArea, response: object) -> CheckResult:
    detail = str(response) if isinstance(response, ConnectorError) else "missing or invalid connector information"
    return CheckResult(area, CheckStatus.UNAVAILABLE, (f"{area.value} check unavailable: {detail}.",))


def _finite_decimal(value: object) -> bool:
    return isinstance(value, Decimal) and value.is_finite()


def _result(payment: Payment, checks: list[CheckResult]) -> DecisionResult:
    """Select severity first, then the earliest check in fixed evaluation order."""
    rejected = [check for check in checks if check.status is CheckStatus.REJECTED]
    review = [check for check in checks if check.status in (CheckStatus.REVIEW, CheckStatus.UNAVAILABLE)]
    if rejected:
        decision = PaymentDecision.REJECTED
        primary = rejected[0].reasons[0]
    elif review:
        decision = PaymentDecision.MANUAL_REVIEW
        primary = review[0].reasons[0]
    else:
        decision = PaymentDecision.READY_FOR_PROCESSING
        primary = "All mandatory validation checks passed."
    reasons = tuple(reason for check in checks if check.status is not CheckStatus.PASS for reason in check.reasons)
    return DecisionResult(payment.payment_id, decision, tuple(checks), reasons, primary)


def evaluate_payment(
    payment: Payment,
    *,
    account: AccountResponse | ConnectorError | None = None,
    limits: LimitsResponse | ConnectorError | None = None,
    fraud: FraudResponse | ConnectorError | None = None,
    sanctions: SanctionsResponse | ConnectorError | None = None,
) -> DecisionResult:
    """Evaluate supplied facts without I/O or mutations.

    Callers supply ConnectorError or None when a mandatory lookup fails.
    Invalid input skips downstream controls. Unavailable controls require review.
    Findings remain in input, account, balance, limit, fraud, sanctions order.
    """
    input_errors = validate_payment(payment)
    if input_errors:
        checks = [CheckResult(ValidationArea.INPUT, CheckStatus.REJECTED, tuple(input_errors))]
        checks.extend(
            CheckResult(area, CheckStatus.SKIPPED, (f"{area.value} check skipped because payment input is invalid.",))
            for area in ValidationArea if area is not ValidationArea.INPUT
        )
        return _result(payment, checks)

    checks = [CheckResult(ValidationArea.INPUT, CheckStatus.PASS, ("Payment input is valid.",))]

    if not isinstance(account, AccountResponse):
        checks.append(_unavailable(ValidationArea.ACCOUNT, account))
        checks.append(_unavailable(ValidationArea.BALANCE, account))
    else:
        account_reasons: list[str] = []
        if isinstance(account.account_status, AccountStatus) and account.account_status is not AccountStatus.ACTIVE:
            account_reasons.append(f"Account status is {account.account_status.value}; ACTIVE is required.")
        if account.wire_payments_enabled is False:
            account_reasons.append("Wire payments are disabled for the account.")
        if account_reasons:
            checks.append(CheckResult(ValidationArea.ACCOUNT, CheckStatus.REJECTED, tuple(account_reasons)))
        elif not isinstance(account.account_status, AccountStatus) or account.wire_payments_enabled is not True:
            checks.append(_unavailable(ValidationArea.ACCOUNT, account))
        else:
            checks.append(CheckResult(ValidationArea.ACCOUNT, CheckStatus.PASS, ("Account is ACTIVE and wire-enabled.",)))

        if not _finite_decimal(account.available_balance):
            checks.append(_unavailable(ValidationArea.BALANCE, account))
        elif account.available_balance < payment.amount:
            checks.append(CheckResult(ValidationArea.BALANCE, CheckStatus.REJECTED, ("Available balance is less than the payment amount.",)))
        else:
            checks.append(CheckResult(ValidationArea.BALANCE, CheckStatus.PASS, ("Available balance covers the payment amount.",)))

    if not isinstance(limits, LimitsResponse) or not _finite_decimal(limits.single_wire_limit) or limits.single_wire_limit < 0:
        checks.append(_unavailable(ValidationArea.LIMIT, limits))
    elif payment.amount > limits.single_wire_limit:
        checks.append(CheckResult(ValidationArea.LIMIT, CheckStatus.REVIEW, ("Payment amount exceeds the configured single-wire limit.",)))
    else:
        checks.append(CheckResult(ValidationArea.LIMIT, CheckStatus.PASS, ("Payment amount is within the single-wire limit.",)))

    if not isinstance(fraud, FraudResponse) or not isinstance(fraud.decision, FraudDecision):
        checks.append(_unavailable(ValidationArea.FRAUD, fraud))
    elif fraud.decision is FraudDecision.PASS:
        checks.append(CheckResult(ValidationArea.FRAUD, CheckStatus.PASS, ("Fraud screening returned PASS.",)))
    else:
        checks.append(CheckResult(ValidationArea.FRAUD, CheckStatus.REVIEW, (f"Fraud screening returned {fraud.decision.value}; manual review is required.",)))

    if not isinstance(sanctions, SanctionsResponse) or not isinstance(sanctions.result, SanctionsResult):
        checks.append(_unavailable(ValidationArea.SANCTIONS, sanctions))
    elif sanctions.result is SanctionsResult.BLOCKED:
        checks.append(CheckResult(ValidationArea.SANCTIONS, CheckStatus.REJECTED, ("Sanctions screening returned BLOCKED.",)))
    elif sanctions.result is SanctionsResult.POTENTIAL_MATCH:
        checks.append(CheckResult(ValidationArea.SANCTIONS, CheckStatus.REVIEW, ("Sanctions screening returned POTENTIAL_MATCH; manual review is required.",)))
    else:
        checks.append(CheckResult(ValidationArea.SANCTIONS, CheckStatus.PASS, ("Sanctions screening returned CLEAR.",)))

    return _result(payment, checks)
