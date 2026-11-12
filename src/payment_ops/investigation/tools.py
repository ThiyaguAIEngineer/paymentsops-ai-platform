"""Run-bound read-only connector tools and a trusted, serial state dispatcher.

No planner, graph, payment action or automatic retry. Connector schemas have zero
arguments; run/request IDs and retry purpose belong to application dispatch only.
"""

from copy import deepcopy
from decimal import Decimal
from time import perf_counter

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, ConfigDict

from payment_ops.connectors.base import (
    AccountResponse, AccountStatus, ConnectorError, CoreBankingConnector,
    FraudConnector, FraudDecision, FraudResponse, LimitsConnector, LimitsResponse,
    RecordNotFoundError, SanctionsConnector, SanctionsResponse, SanctionsResult,
)
from payment_ops.domain.payment import Payment
from payment_ops.domain.validation import validate_payment
from payment_ops.investigation.state import (
    Control, InvestigationState, JSONValue, Purpose, ToolError, ToolPolicyError,
    check_connector_attempt, check_execution_budget, payment_snapshot,
    record_tool_attempt, recorded_request,
)
from payment_ops.samples.payments import SYNTHETIC_PAYMENTS


TOOLS: dict[str, Control] = {
    "get_core_evidence": "core", "get_limit_evidence": "limits",
    "get_fraud_evidence": "fraud", "get_sanctions_evidence": "sanctions",
}


class NoToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")


class InvalidConnectorResponse(ValueError):
    """A response violates its existing connector contract; never contains raw data."""


def lookup_payment(payment_id: str) -> Payment:
    """Exact lookup over existing samples, separate from model-selected tools.

    The run dispatcher below records/budgets this operation. This pure lookup
    helper does not invoke connectors, infer identifiers or construct payments.
    """
    if not isinstance(payment_id, str) or not payment_id.strip():
        raise RecordNotFoundError("invalid_selection")
    for payment in SYNTHETIC_PAYMENTS:
        if payment.payment_id == payment_id:
            return payment
    raise RecordNotFoundError("invalid_selection")


def _finite_decimal(value: object) -> bool:
    return isinstance(value, Decimal) and value.is_finite()


def _normalize(control: Control, response: object) -> dict[str, JSONValue]:
    """Validate/serialize response contracts, not additional payment decision rules."""
    if control == "core" and isinstance(response, AccountResponse):
        if (isinstance(response.account_status, AccountStatus)
                and _finite_decimal(response.available_balance)
                and type(response.wire_payments_enabled) is bool):
            return {"account_status": response.account_status.value,
                    "available_balance": str(response.available_balance),
                    "wire_payments_enabled": response.wire_payments_enabled}
    elif control == "limits" and isinstance(response, LimitsResponse):
        if _finite_decimal(response.single_wire_limit) and response.single_wire_limit >= 0:
            return {"single_wire_limit": str(response.single_wire_limit)}
    elif control == "fraud" and isinstance(response, FraudResponse):
        if (type(response.score) is int and 0 <= response.score <= 100
                and isinstance(response.decision, FraudDecision)):
            return {"score": response.score, "decision": response.decision.value}
    elif control == "sanctions" and isinstance(response, SanctionsResponse):
        if isinstance(response.result, SanctionsResult):
            return {"result": response.result.value}
    raise InvalidConnectorResponse("invalid_connector_response")


def _sanitize_error(error: Exception) -> ToolError:
    # Retry eligibility is deliberately narrow. Generic ConnectorError is not
    # proof of a transient outage; no exception text/traceback enters state.
    if isinstance(error, InvalidConnectorResponse):
        category, retryable = "invalid_response", False
    elif isinstance(error, RecordNotFoundError):
        category, retryable = "record_not_found", False
    elif isinstance(error, (TimeoutError, ConnectionError)):
        category, retryable = "transient_transport_error", True
    elif isinstance(error, PermissionError):
        category, retryable = "configuration_error", False
    elif isinstance(error, ConnectorError):
        category, retryable = "connector_unavailable", False
    elif isinstance(error, (ValueError, TypeError)):
        category, retryable = "invalid_request", False
    else:
        category, retryable = "connector_failure", False
    return {"category": category, "retryable": retryable}


class InvestigationTools:
    """Inject existing connectors; carry only runtime bindings outside graph state.

    Usage: create with a new state; call lookup_payment(state, request_id=...),
    then invoke(updated_state, tool_name, request_id=...). Always use the returned
    state. Single serial owner required; this foundation provides no concurrent
    dispatch lock or durable idempotency store. Only tool_specs goes to a planner.
    """

    def __init__(self, state: InvestigationState, *, core: CoreBankingConnector,
                 limits: LimitsConnector, fraud: FraudConnector, sanctions: SanctionsConnector):
        self._identity = (state["run_id"], state["thread_id"], state["payment_id"])
        self._core, self._limits, self._fraud, self._sanctions = core, limits, fraud, sanctions
        self._tools: dict[str, StructuredTool] = {}
        self._payment: Payment | None = None

    def _check_binding(self, state: InvestigationState) -> None:
        if (state["run_id"], state["thread_id"], state["payment_id"]) != self._identity:
            raise ToolPolicyError("run_binding_mismatch")
        if self._payment is not None and state["payment_snapshot"] != payment_snapshot(self._payment):
            raise ToolPolicyError("payment_snapshot_mismatch")

    @property
    def tool_specs(self) -> list[dict[str, JSONValue]]:
        """Descriptors only, with no payment lookup or state-changing arguments."""
        return [{"name": name, "description": f"Retrieve read-only {control} evidence for the selected payment.",
                 "parameters": NoToolArguments.model_json_schema()} for name, control in TOOLS.items()]

    def lookup_payment(self, state: InvestigationState, *, request_id: str) -> InvestigationState:
        self._check_binding(state)
        replay = recorded_request(state, request_id, "lookup_payment", "initial")
        if replay is not None:
            # Restore runtime closures after loading an already-recorded state.
            if replay["success"]:
                self._bind(lookup_payment(self._identity[2]))
                self._check_binding(state)
            return deepcopy(state)
        check_execution_budget(state)
        if state["phase"] != "loading" or any(a["tool_name"] == "lookup_payment" for a in state["tool_attempts"]):
            raise ToolPolicyError("payment_lookup_already_attempted")
        started = perf_counter()
        try:
            payment = lookup_payment(self._identity[2])
        except RecordNotFoundError:
            updated = record_tool_attempt(
                state, request_id=request_id, tool_name="lookup_payment", control=None,
                purpose="initial", result=None, error={"category": "invalid_selection", "retryable": False},
                elapsed_seconds=perf_counter() - started,
            )
            updated["phase"], updated["outcome_reason"] = "failed", "invalid_selection"
            return updated
        snapshot = payment_snapshot(payment)
        updated = record_tool_attempt(
            state, request_id=request_id, tool_name="lookup_payment", control=None,
            purpose="initial", result=dict(snapshot), error=None, elapsed_seconds=perf_counter() - started,
        )
        updated["payment_snapshot"] = snapshot
        updated["input_errors"] = validate_payment(payment)
        updated["phase"] = "summarizing" if updated["input_errors"] else "collecting"
        updated["outcome_reason"] = "invalid_payment_input" if updated["input_errors"] else None
        self._bind(payment)
        return updated

    def _bind(self, payment: Payment) -> None:
        self._payment = payment

        def get_core_evidence():
            return _normalize("core", self._core.get_account(payment.sender_account_id))

        def get_limit_evidence():
            return _normalize("limits", self._limits.get_limit(payment.sender_account_id))

        def get_fraud_evidence():
            return _normalize("fraud", self._fraud.screen(payment.payment_id))

        def get_sanctions_evidence():
            return _normalize("sanctions", self._sanctions.screen(payment))

        functions = (get_core_evidence, get_limit_evidence, get_fraud_evidence, get_sanctions_evidence)
        self._tools = {
            function.__name__: StructuredTool.from_function(
                func=function, name=function.__name__, description=f"Read-only {TOOLS[function.__name__]} evidence.",
                args_schema=NoToolArguments,
            ) for function in functions
        }

    def invoke(self, state: InvestigationState, tool_name: str, *, request_id: str,
               purpose: Purpose = "initial", arguments: dict | None = None) -> InvestigationState:
        """Dispatch exactly one bound tool; never selects recovery or the next tool."""
        self._check_binding(state)
        if tool_name not in TOOLS:
            raise ToolPolicyError("unknown_connector_tool")
        if arguments is not None and (not isinstance(arguments, dict) or arguments):
            raise ToolPolicyError("unexpected_tool_arguments")
        if self._payment is None or state["payment_snapshot"] is None:
            raise ToolPolicyError("payment_lookup_required")
        if validate_payment(self._payment):
            raise ToolPolicyError("invalid_payment_input")
        if recorded_request(state, request_id, tool_name, purpose) is not None:
            return deepcopy(state)
        if state["phase"] != "collecting":
            raise ToolPolicyError("connector_dispatch_not_collecting")
        check_execution_budget(state)
        control = TOOLS[tool_name]
        check_connector_attempt(state, control, purpose)
        started = perf_counter()
        result, error = None, None
        try:
            result = self._tools[tool_name].invoke({})
        except Exception as exc:
            error = _sanitize_error(exc)
        return record_tool_attempt(
            state, request_id=request_id, tool_name=tool_name, control=control,
            purpose=purpose, result=result, error=error, elapsed_seconds=perf_counter() - started,
        )
