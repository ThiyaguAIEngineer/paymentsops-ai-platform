"""Bounded investigation with genuine recommendation-only review interrupts."""

from copy import deepcopy
from time import perf_counter
from weakref import finalize

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphInterrupt, GraphRecursionError
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from payment_ops.connectors.base import CoreBankingConnector, FraudConnector, LimitsConnector, SanctionsConnector
from payment_ops.investigation.planner import (
    ExecutionBudgets, InvestigationPlanner, action_purpose,
    create_nebius_planner, eligible_actions, outstanding_controls,
    planner_failure_category, validate_action,
)
from payment_ops.investigation.state import InvestigationState, ToolPolicyError
from payment_ops.investigation.review import (
    FURTHER, ReviewValidationError, finalize_review, prepare_review,
    record_review_response, validate_review_response,
)
from payment_ops.investigation.summary import evaluate_findings, summarize_investigation
from payment_ops.investigation.tools import TOOLS, InvestigationTools


def _failure(state: InvestigationState, category: str, *, tool_name: str = "planner"):
    """All categories passed here are application constants, not raw exception text."""
    updated = deepcopy(state)
    updated["planning_status"] = "degraded"
    updated["pending_action"] = None
    updated["errors"].append({
        "attempt_id": f"{state['run_id']}:{tool_name}-failure:{len(state['errors']) + 1:02d}",
        "tool_name": tool_name, "category": category, "retryable": False,
    })
    return updated


def _decision(state, action, reason, source):
    updated = deepcopy(state)
    updated["planner_decisions"].append({
        "decision_id": f"{state['run_id']}:decision:{len(state['planner_decisions']) + 1:02d}",
        "planner_call_number": state["planner_call_count"],
        "action": action, "reason": reason, "source": source,
    })
    updated["pending_action"] = None if action == "finish" else action
    return updated


def _fallback(state: InvestigationState, budgets: ExecutionBudgets):
    """Outstanding initial controls only; never retries failures or calls a model."""
    eligible = eligible_actions(state, budgets)
    remaining = outstanding_controls(state)
    for action, control in TOOLS.items():
        if control in remaining and action in eligible:
            return _decision(state, action, "Degraded fallback: collect outstanding mandatory evidence.", "fallback")
    return _decision(state, "finish", "Degraded fallback ended; review evidence gaps and failures.", "fallback")


def build_investigation_graph(initial_state: InvestigationState, *,
                              core: CoreBankingConnector, limits: LimitsConnector,
                              fraud: FraudConnector, sanctions: SanctionsConnector,
                              planner: InvestigationPlanner | None = None,
                              budgets: ExecutionBudgets = ExecutionBudgets(), checkpointer=None):
    """Build one run-bound graph; injected planners/providers belong to the caller.

    Without injection, a separate Nebius planner is initialized lazily. Its owned
    client is closed at summarization (or graph reclamation). Never initializes
    KnowledgeService. All callbacks/tools are runtime dependencies outside state.
    """
    tools = InvestigationTools(initial_state, core=core, limits=limits, fraud=fraud, sanctions=sanctions)
    owned = []

    def close_owned():
        while owned:
            owned.pop().provider.close()

    def load_payment(state):
        try:
            return tools.lookup_payment(state, request_id=f"{state['run_id']}:lookup")
        except ToolPolicyError:
            updated = _failure(state, "invalid_initial_state", tool_name="orchestrator")
            updated["payment_snapshot"] = None
            updated["phase"], updated["outcome_reason"] = "failed", "invalid_initial_state"
            return updated

    def plan_next(state):
        updated = deepcopy(state)
        updated["findings"] = evaluate_findings(updated)
        if updated["planning_status"] == "degraded":
            return _fallback(updated, budgets)
        if updated["active_elapsed_seconds"] >= budgets.max_active_seconds:
            return _fallback(_failure(updated, "active_execution_budget_exhausted"), budgets)
        if updated["tool_attempt_count"] >= budgets.max_tool_attempts and outstanding_controls(updated):
            return _fallback(_failure(updated, "tool_attempt_budget_exhausted"), budgets)
        if updated["planner_call_count"] >= budgets.max_planner_calls:
            return _fallback(_failure(updated, "planner_budget_exhausted"), budgets)
        updated["planner_call_count"] += 1  # Includes failed planner attempts.
        updated["planning_status"] = "running"
        started = perf_counter()
        error = None
        try:
            active_planner = planner
            if active_planner is None:
                if not owned:
                    owned.append(create_nebius_planner())
                active_planner = owned[0]
            action = active_planner.plan(updated, budgets)
            # A second check at dispatch planning boundary prevents stale eligibility.
            action = validate_action({"action": action.action, "reason": action.reason}, updated, budgets)
        except Exception as exc:
            error = planner_failure_category(exc)
        updated["active_elapsed_seconds"] += perf_counter() - started
        if updated["active_elapsed_seconds"] >= budgets.max_active_seconds:
            error = "active_execution_budget_exhausted"
        if error is not None:
            return _fallback(_failure(updated, error), budgets)
        updated = _decision(updated, action.action, action.reason, "model")
        if action.action == "finish":
            updated["planning_status"] = "succeeded"
        return updated

    def execute_tool(state):
        action = state["pending_action"]
        # The model never supplies request IDs, retry flags or connector arguments.
        if action not in eligible_actions(state, budgets) or action not in TOOLS:
            updated = _failure(state, "ineligible_dispatch", tool_name="orchestrator")
            updated["phase"] = "summarizing"
            return updated
        try:
            return tools.invoke(
                state, action, request_id=state["planner_decisions"][-1]["decision_id"],
                purpose=action_purpose(state, action),
            )
        except ToolPolicyError:
            updated = _failure(state, "dispatch_policy_refusal", tool_name="orchestrator")
            updated["phase"] = "summarizing"
            return updated

    def evaluate_and_summarize(state):
        try:
            if (state["active_elapsed_seconds"] >= budgets.max_active_seconds
                    and state["planning_status"] != "degraded"):
                state = _failure(state, "active_execution_budget_exhausted", tool_name="orchestrator")
            return summarize_investigation(state)
        finally:
            close_owned()

    def human_review(state):
        # Pure validation/payload work only: this node restarts on resume. When
        # a raw caller bypasses controller preflight, re-interrupt instead of
        # raising and leaving an invalid cached resume value stuck in the task.
        payload = deepcopy(state["human_review"]["payload"])
        while True:
            response = interrupt(payload)
            try:
                validated = validate_review_response(state, response, budgets)
            except ReviewValidationError as error:
                payload = {**deepcopy(state["human_review"]["payload"]), "validation_error": str(error)}
                continue
            return record_review_response(state, validated, budgets)

    def execute_review_check(state):
        review = state["human_review"]
        events = review["events"]
        control = review["requested_control"]
        action = next((name for name, value in TOOLS.items() if value == control), None)
        if (review["decision"] != FURTHER or not events or events[-1]["action"] != FURTHER
                or sum(e["action"] == FURTHER for e in events) != 1 or action is None
                or state["tool_attempt_count"] >= budgets.max_tool_attempts
                or state["active_elapsed_seconds"] >= budgets.max_active_seconds):
            return _failure(state, "human_recheck_refused", tool_name="orchestrator")
        try:
            return tools.invoke(state, action, request_id=f"{events[-1]['review_id']}:recheck",
                                purpose="human_recheck")
        except ToolPolicyError:
            return _failure(state, "human_recheck_refused", tool_name="orchestrator")

    builder = StateGraph(InvestigationState)
    builder.add_node("load_payment", load_payment)
    builder.add_node("plan_next", plan_next)
    builder.add_node("execute_tool", execute_tool)  # Task 3 dispatcher also records evidence.
    builder.add_node("evaluate_and_summarize", evaluate_and_summarize)
    builder.add_node("prepare_review", lambda s: prepare_review(s, budgets))
    builder.add_node("human_review", human_review)
    builder.add_node("execute_review_check", execute_review_check)
    builder.add_node("finalize_review", lambda s: finalize_review(s, budgets))
    builder.add_edge(START, "load_payment")
    builder.add_conditional_edges("load_payment", lambda s: "plan" if s["phase"] == "collecting" else "summary",
                                  {"plan": "plan_next", "summary": "evaluate_and_summarize"})
    builder.add_conditional_edges("plan_next", lambda s: "tool" if s["pending_action"] else "summary",
                                  {"tool": "execute_tool", "summary": "evaluate_and_summarize"})
    builder.add_conditional_edges("execute_tool", lambda s: "summary" if s["phase"] == "summarizing" else "plan",
                                  {"summary": "evaluate_and_summarize", "plan": "plan_next"})
    builder.add_conditional_edges("evaluate_and_summarize", lambda s: "end" if s["phase"] == "failed" else "review",
                                  {"end": END, "review": "prepare_review"})
    builder.add_conditional_edges("prepare_review", lambda s: "review" if s["phase"] == "awaiting_review" else "end",
                                  {"review": "human_review", "end": END})
    builder.add_conditional_edges("human_review", lambda s: "recheck" if s["human_review"]["decision"] == FURTHER else "finalize",
                                  {"recheck": "execute_review_check", "finalize": "finalize_review"})
    builder.add_edge("execute_review_check", "evaluate_and_summarize")
    builder.add_edge("finalize_review", END)
    graph = builder.compile(checkpointer=checkpointer if checkpointer is not None else InMemorySaver())
    finalize(graph, close_owned)
    return graph


def drive_investigation(graph, graph_input, config):
    """Internal driver shared by start/resume; omit non-JSON Interrupt objects."""
    try:
        graph.invoke(graph_input, config)
        return deepcopy(graph.get_state(config).values)
    except GraphRecursionError:
        saved = graph.get_state(config).values
        final = summarize_investigation(_failure(saved, "graph_step_budget_exhausted", tool_name="orchestrator"))
        final["phase"], final["outcome_reason"] = "escalated", "graph_step_budget_exhausted"
        final["human_review"]["pending_review_id"], final["human_review"]["payload"] = None, None
        final["summary"]["review_required"] = False
        final["summary"]["outcome_reason"] = final["outcome_reason"]
        # Finalizer's outgoing edge is END; do not leave a phantom pending review.
        graph.update_state(config, final, as_node="finalize_review")
        return final
    except (GraphInterrupt, ReviewValidationError):
        # Never translate a review pause or invalid review response into success.
        raise
    except Exception:
        # Unexpected orchestration failures are terminal and sanitized. Do not
        # retry the failing node, synthesize evidence, or rerun payment evaluation.
        saved = graph.get_state(config).values
        if not saved:
            raise ToolPolicyError("investigation_checkpoint_unavailable") from None
        final = _failure(saved, "orchestration_failure", tool_name="orchestrator")
        final["phase"], final["outcome_reason"] = "failed", "orchestration_failure"
        final["pending_action"] = None
        final["human_review"]["pending_review_id"], final["human_review"]["payload"] = None, None
        final["summary"] = deepcopy(final["summary"]) or {
            "payment_id": final["payment_id"], "decision_engine_finding": deepcopy(final["findings"]),
        }
        final["summary"].update({
            "investigation_outcome": "failed", "outcome_reason": "orchestration_failure",
            "review_required": False, "human_review_implemented": True,
        })
        graph.update_state(config, final, as_node="finalize_review")
        return final


def invoke_investigation(graph, initial_state: InvestigationState, *, recursion_limit: int = 40):
    """Drive a new run until its genuine review interrupt or safe terminal failure."""
    if type(recursion_limit) is not int or not 1 <= recursion_limit <= 40:
        raise ValueError("Invalid graph recursion limit")
    config = {"configurable": {"thread_id": initial_state["thread_id"]}, "recursion_limit": recursion_limit}
    if graph.get_state(config).values:
        raise ToolPolicyError("investigation_already_started")
    return drive_investigation(graph, deepcopy(initial_state), config)
