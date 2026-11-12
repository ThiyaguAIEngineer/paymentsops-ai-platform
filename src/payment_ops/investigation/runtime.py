"""Small composition boundary: existing mocks, unique identity, actual controller."""

from uuid import uuid4

from payment_ops.connectors.mock_core import MockCoreBankingConnector
from payment_ops.connectors.mock_fraud import MockFraudConnector
from payment_ops.connectors.mock_limits import MockLimitsConnector
from payment_ops.connectors.mock_sanctions import MockSanctionsConnector
from payment_ops.investigation.controller import InvestigationController
from payment_ops.investigation.state import new_investigation_state


def create_investigation_controller(payment_id: str, *, planner=None) -> InvestigationController:
    """No I/O on composition. Default planner is the graph's lazy Nebius planner.

    Explicit planner injection is for dependency composition/tests; production UI
    does not inject a scripted provider or cache controllers globally.
    """
    state = new_investigation_state(run_id=uuid4().hex, thread_id=uuid4().hex, payment_id=payment_id)
    return InvestigationController(
        state, core=MockCoreBankingConnector(), limits=MockLimitsConnector(),
        fraud=MockFraudConnector(), sanctions=MockSanctionsConnector(), planner=planner,
    )
