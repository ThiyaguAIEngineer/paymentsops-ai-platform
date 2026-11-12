"""Session-owned in-process controller. Store this object outside JSON graph state.

No Streamlit dependency, global cache, database or authenticated reviewer identity.
Retain the same controller in one browser session across reruns. Losing it or its
in-memory checkpoints requires a new run; a different instance cannot resume it.
"""

from copy import deepcopy
from threading import RLock

from langgraph.types import Command

from payment_ops.investigation.graph import build_investigation_graph, drive_investigation, invoke_investigation
from payment_ops.investigation.planner import ExecutionBudgets
from payment_ops.investigation.review import ReviewValidationError, validate_review_response


class InvestigationController:
    def __init__(self, initial_state, *, core, limits, fraud, sanctions, planner=None,
                 budgets: ExecutionBudgets = ExecutionBudgets()):
        self._initial = deepcopy(initial_state)
        self._identity = (initial_state["run_id"], initial_state["thread_id"], initial_state["payment_id"])
        self._budgets = budgets
        self._lock = RLock()
        self._config = {"configurable": {"thread_id": initial_state["thread_id"]}, "recursion_limit": 40}
        self.graph = build_investigation_graph(
            self._initial, core=core, limits=limits, fraud=fraud, sanctions=sanctions,
            planner=planner, budgets=budgets,
        )

    def snapshot(self):
        """Detached, JSON-safe view. Reading state never invokes a node or tool."""
        with self._lock:
            state = deepcopy(self.graph.get_state(self._config).values)
            if state and (state["run_id"], state["thread_id"], state["payment_id"]) != self._identity:
                raise ReviewValidationError("controller_identity_mismatch")
            return state

    def start(self):
        with self._lock:
            return invoke_investigation(self.graph, self._initial)

    def resume(self, payload):
        """Validate before consuming an interrupt; revalidate inside its node too.

        Lock covers validation plus graph execution so double clicks/concurrent
        callbacks cannot consume the same review twice in this process/session.
        The thread ID is controller-owned, never supplied in reviewer input.
        """
        with self._lock:
            state = self.snapshot()
            if not state:
                raise ReviewValidationError("investigation_checkpoint_unavailable")
            validate_review_response(state, payload, self._budgets)
            checkpoint = self.graph.get_state(self._config)
            if checkpoint.next != ("human_review",) or not any(t.interrupts for t in checkpoint.tasks):
                raise ReviewValidationError("investigation_not_paused_for_review")
            return drive_investigation(self.graph, Command(resume=deepcopy(payload)), self._config)
