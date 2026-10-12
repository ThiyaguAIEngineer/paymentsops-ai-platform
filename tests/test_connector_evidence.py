"""Evidence identity, compatibility, missing data, and UI presentation tests."""

from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from streamlit.testing.v1 import AppTest

from payment_ops.connectors.base import ConnectorError
from payment_ops.connectors.mock_core import MockCoreBankingConnector
from payment_ops.connectors.mock_fraud import MockFraudConnector
from payment_ops.connectors.mock_limits import MockLimitsConnector
from payment_ops.connectors.mock_sanctions import MockSanctionsConnector
from payment_ops.domain.payment import Payment
from payment_ops.samples.payments import SYNTHETIC_PAYMENTS
from payment_ops.services.decision_engine import CheckStatus, PaymentDecision, evaluate_payment
from payment_ops.services.payment_service import PaymentService
from payment_ops.services.results import ConnectorEvidence
from payment_ops.ui.helpers import evidence_rows


@pytest.fixture
def connectors() -> tuple[Mock, ...]:
    payment = SYNTHETIC_PAYMENTS[0]
    return (
        Mock(get_account=Mock(return_value=MockCoreBankingConnector().get_account(payment.sender_account_id))),
        Mock(get_limit=Mock(return_value=MockLimitsConnector().get_limit(payment.sender_account_id))),
        Mock(screen=Mock(return_value=MockFraudConnector().screen(payment.payment_id))),
        Mock(screen=Mock(return_value=MockSanctionsConnector().screen(payment))),
    )


def test_evidence_is_exactly_what_engine_evaluated(connectors) -> None:
    with patch("payment_ops.services.payment_service.evaluate_payment", wraps=evaluate_payment) as engine:
        result = PaymentService(*connectors).process_payment_with_evidence(SYNTHETIC_PAYMENTS[0])
    assert engine.call_count == 1
    for name in ("account", "limits", "fraud", "sanctions"):
        assert getattr(result.evidence, name) is engine.call_args.kwargs[name]
    for connector in connectors:
        assert len(connector.mock_calls) == 1
    with pytest.raises(FrozenInstanceError):
        result.evidence.account = None
    with pytest.raises(FrozenInstanceError):
        result.decision = None
    with pytest.raises(FrozenInstanceError):
        result.evidence.account.available_balance = 0


@pytest.mark.parametrize("payment", SYNTHETIC_PAYMENTS, ids=[p.payment_id for p in SYNTHETIC_PAYMENTS])
def test_rich_api_preserves_all_scenario_decisions(payment) -> None:
    service = PaymentService(MockCoreBankingConnector(), MockLimitsConnector(), MockFraudConnector(), MockSanctionsConnector())
    assert service.process_payment_with_evidence(payment).decision == service.process_payment(payment)


def test_invalid_instructions_have_no_evidence_or_lookups(connectors) -> None:
    result = PaymentService(*connectors).process_payment_with_evidence(Payment())
    assert result.evidence == ConnectorEvidence()
    assert result.decision.decision is PaymentDecision.REJECTED
    assert all(check.status is CheckStatus.SKIPPED for check in result.decision.checks[1:])
    assert all(not connector.mock_calls for connector in connectors)
    assert all(row["Evidence"] == "SKIPPED" for row in evidence_rows(result))


@pytest.mark.parametrize("index,method,name", [(0, "get_account", "account"), (1, "get_limit", "limits"), (2, "screen", "fraud"), (3, "screen", "sanctions")])
@pytest.mark.parametrize("mode", ["error", "missing", "wrong-type"])
def test_unavailable_lookup_has_no_fabricated_evidence(connectors, index, method, name, mode) -> None:
    operation = getattr(connectors[index], method)
    if mode == "error":
        operation.side_effect = ConnectorError("PRIVATE INTERNAL DETAILS")
    else:
        operation.return_value = None if mode == "missing" else {}
    result = PaymentService(*connectors).process_payment_with_evidence(SYNTHETIC_PAYMENTS[0])
    assert getattr(result.evidence, name) is None
    assert result.decision.decision is PaymentDecision.MANUAL_REVIEW
    assert any(check.status is CheckStatus.UNAVAILABLE for check in result.decision.checks)
    assert "PRIVATE" not in repr(result)
    assert all(len(connector.mock_calls) == 1 for connector in connectors)
    assert any(row["Evidence"] == "UNAVAILABLE" for row in evidence_rows(result))
    for other in {"account", "limits", "fraud", "sanctions"} - {name}:
        assert getattr(result.evidence, other) is not None


def test_rejection_with_outage_retains_actual_evidence() -> None:
    service = PaymentService(MockCoreBankingConnector(), MockLimitsConnector(), MockFraudConnector(), MockSanctionsConnector())
    from dataclasses import replace
    payment = replace(SYNTHETIC_PAYMENTS[-1], sender_account_id="SYNTHETIC-SENDER-FROZEN")
    result = service.process_payment_with_evidence(payment)
    assert result.decision.decision is PaymentDecision.REJECTED
    assert "FROZEN" in result.decision.primary_reason
    assert result.evidence.account.account_status.value == "FROZEN"
    assert result.evidence.fraud is None
    assert result.decision.checks[4].status is CheckStatus.UNAVAILABLE


def test_format_actual_evidence(connectors) -> None:
    result = PaymentService(*connectors).process_payment_with_evidence(SYNTHETIC_PAYMENTS[0])
    assert {row["Field"]: row["Value"] for row in evidence_rows(result)} == {
        "Account status": "ACTIVE", "Wire-enabled": "Yes", "Available balance": "$100,000.00",
        "Single-wire limit": "$50,000.00", "Fraud score (0–100)": "10",
        "Fraud screening decision": "PASS", "Sanctions screening result": "CLEAR",
    }
    assert all(row["Evidence"] == "Retrieved" for row in evidence_rows(result))


@pytest.mark.parametrize("payment_id,field,value,availability", [
    ("SYNTHETIC-WIRE-001", "Available balance", "$100,000.00", "Retrieved"),
    ("SYNTHETIC-WIRE-REVIEW", "Fraud score (0–100)", "55", "Retrieved"),
    ("SYNTHETIC-WIRE-CLOSED", "Wire-enabled", "No", "Retrieved"),
    ("SYNTHETIC-WIRE-UNAVAILABLE", "Fraud screening decision", "UNAVAILABLE — no usable evidence", "UNAVAILABLE"),
    ("SYNTHETIC-WIRE-MISSING", "Available balance", "SKIPPED — not retrieved", "SKIPPED"),
])
def test_ui_evidence_display(payment_id, field, value, availability) -> None:
    app_path = Path(__file__).resolve().parents[1] / "src/payment_ops/ui/app.py"
    app = AppTest.from_file(str(app_path), default_timeout=20).run()
    app.selectbox(key="selected_payment").select(payment_id).run()
    assert not app.exception
    table = app.table[1].value.set_index("Field")
    assert table.loc[field, "Value"] == value
    assert table.loc[field, "Evidence"] == availability
    assert list(table.index) == ["Account status", "Wire-enabled", "Available balance", "Single-wire limit", "Fraud score (0–100)", "Fraud screening decision", "Sanctions screening result"]
