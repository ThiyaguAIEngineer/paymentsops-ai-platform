"""Offline run/connector fixtures; all evidence comes from existing mocks."""

from unittest.mock import Mock

import httpx
import pytest

from payment_ops.connectors.base import (
    CoreBankingConnector, FraudConnector, LimitsConnector, SanctionsConnector,
)
from payment_ops.connectors.mock_core import MockCoreBankingConnector
from payment_ops.connectors.mock_fraud import MockFraudConnector
from payment_ops.connectors.mock_limits import MockLimitsConnector
from payment_ops.connectors.mock_sanctions import MockSanctionsConnector
from payment_ops.investigation.state import new_investigation_state
from payment_ops.investigation.tools import InvestigationTools


@pytest.fixture(autouse=True)
def no_external_calls(monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")

    def forbidden(*args, **kwargs):
        raise AssertionError("Investigation foundation tests must remain offline")

    monkeypatch.setattr(httpx.Client, "request", forbidden)
    monkeypatch.setattr(httpx.AsyncClient, "request", forbidden)


@pytest.fixture
def connectors():
    return dict(
        core=Mock(spec=CoreBankingConnector, wraps=MockCoreBankingConnector()),
        limits=Mock(spec=LimitsConnector, wraps=MockLimitsConnector()),
        fraud=Mock(spec=FraudConnector, wraps=MockFraudConnector()),
        sanctions=Mock(spec=SanctionsConnector, wraps=MockSanctionsConnector()),
    )


@pytest.fixture
def make_run(connectors):
    def create(payment_id="SYNTHETIC-WIRE-001"):
        state = new_investigation_state(run_id="test-run", thread_id="test-thread", payment_id=payment_id)
        return state, InvestigationTools(state, **connectors)
    return create
