"""Offline AppTest integration with the real graph/mocks and test-only model scripts."""

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
from unittest.mock import Mock

import httpx
import pytest
from streamlit.testing.v1 import AppTest
from streamlit.testing.v1.errors import AppTestError

from payment_ops.connectors.mock_core import MockCoreBankingConnector
from payment_ops.connectors.mock_fraud import MockFraudConnector
from payment_ops.connectors.mock_limits import MockLimitsConnector
from payment_ops.connectors.mock_sanctions import MockSanctionsConnector
from payment_ops.investigation.planner import InvestigationPlanner
from payment_ops.investigation.review import ReviewValidationError
from payment_ops.investigation.runtime import create_investigation_controller
from payment_ops.investigation.tools import TOOLS, lookup_payment


APP = Path(__file__).resolve().parents[1] / "src/payment_ops/ui/app.py"
AGENT = "Payment Investigation Agent"


class ScriptedUIProvider:
    """Explicit test dependency only; no production UI path imports this class."""

    def __init__(self):
        self.steps = iter([*TOOLS, "finish"])
        self.calls = []

    def generate(self, system_prompt, user_prompt):
        self.calls.append(json.loads(user_prompt))
        return json.dumps({"action": next(self.steps), "reason": "Collect outstanding evidence."})


@pytest.fixture(autouse=True)
def offline_and_isolated(monkeypatch):
    import streamlit as st
    st.cache_resource.clear()
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    calls = []
    def no_http(*args, **kwargs):
        calls.append(True)
        raise AssertionError("No external API calls permitted in UI tests")
    monkeypatch.setattr(httpx.Client, "request", no_http)
    monkeypatch.setattr(httpx.AsyncClient, "request", no_http)
    yield
    st.cache_resource.clear()
    assert calls == []


@pytest.fixture
def mounted(monkeypatch):
    from payment_ops.investigation import runtime
    from payment_ops.ui import investigation_view as view
    spies = {c: [] for c in ("core", "limits", "fraud", "sanctions")}
    for control, attr, implementation in [
        ("core", "MockCoreBankingConnector", MockCoreBankingConnector),
        ("limits", "MockLimitsConnector", MockLimitsConnector),
        ("fraud", "MockFraudConnector", MockFraudConnector),
        ("sanctions", "MockSanctionsConnector", MockSanctionsConnector),
    ]:
        def factory(control=control, implementation=implementation):
            wrapped = Mock(spec=implementation, wraps=implementation())
            spies[control].append(wrapped)
            return wrapped
        monkeypatch.setattr(runtime, attr, factory)
    created = []
    def create(payment_id):
        provider = ScriptedUIProvider()
        controller = runtime.create_investigation_controller(payment_id, planner=InvestigationPlanner(provider))
        created.append((controller, provider))
        return controller
    monkeypatch.setattr(view, "create_investigation_controller", create)
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    return app, created, spies


def element(collection, label):
    matches = [item for item in collection if item.label == label]
    assert len(matches) == 1, label
    return matches[0]


def open_agent(app):
    return app.sidebar.radio(key="workspace_view").set_value(AGENT).run()


def start(app, payment_id="SYNTHETIC-WIRE-001"):
    element(app.selectbox, "Select a synthetic wire payment").set_value(payment_id).run()
    return element(app.button, "Investigate Payment").click().run()


def snapshot(app):
    return app.session_state["investigation_controller"].snapshot()


def test_third_view_and_selection_are_lazy_and_wire_default_is_preserved(mounted):
    app, created, spies = mounted
    assert app.sidebar.radio(key="workspace_view").options == ["Wire Validation", "Knowledge Assistant", AGENT]
    assert [m.value for m in app.metric] == ["20", "$300,107.02", "4", "6", "10"]
    open_agent(app)
    assert not app.exception and created == []
    assert any("Synthetic educational" in c.value for c in app.caption)
    element(app.selectbox, "Select a synthetic wire payment").set_value("SYNTHETIC-WIRE-LOW-BALANCE").run()
    app.run()
    assert created == [] and all(not values for values in spies.values())
    assert not any(b.label == "Accept Investigation Recommendation" for b in app.button)


def test_successful_investigation_displays_actual_trace_and_accepts_without_repeated_calls(mounted):
    app, created, spies = mounted
    payment = lookup_payment("SYNTHETIC-WIRE-001")
    original = asdict(payment)
    open_agent(app)
    start(app)
    assert not app.exception and len(created) == 1
    before = snapshot(app)
    assert before["phase"] == "awaiting_review" and before["payment_id"] == payment.payment_id
    assert any("Awaiting human review" in i.value for i in app.info)
    tables = [d.value for d in app.dataframe]
    history = next(t for t in tables if "Tool" in t.columns)
    assert list(history["Tool"]) == ["lookup_payment", *TOOLS]
    actions = next(t for t in tables if "Source" in t.columns and "Action" in t.columns)
    assert set(actions["Source"]) == {"Model"}
    assert any("Simulator finding: READY FOR PROCESSING" == t.value for t in app.text)
    spies["core"][0].get_account.assert_called_once_with(payment.sender_account_id)
    spies["sanctions"][0].screen.assert_called_once_with(payment)
    assert element(app.button, "Investigate Payment").disabled
    element(app.button, "Accept Investigation Recommendation").click().run()
    assert not app.exception and snapshot(app)["phase"] == "completed_reviewed"
    assert app.success[0].value == "Completed and reviewed investigation"
    assert snapshot(app)["tool_attempts"] == before["tool_attempts"]
    assert all(len(values[0].mock_calls) == 1 for values in spies.values())
    assert len(created[0][1].calls) == 5 and asdict(payment) == original
    assert not any(b.label == "Accept Investigation Recommendation" for b in app.button)


def test_low_balance_recheck_uses_same_thread_and_requires_second_review(mounted):
    app, created, spies = mounted
    open_agent(app)
    start(app, "SYNTHETIC-WIRE-LOW-BALANCE")
    before = snapshot(app)
    assert before["findings"]["decision"] == "REJECTED"
    element(app.selectbox, "Connector to recheck").set_value("core")
    element(app.text_area, "Reviewer note").input("Please verify the available balance.")
    element(app.button, "Request Further Investigation").click().run()
    assert not app.exception
    second = snapshot(app)
    assert second["thread_id"] == before["thread_id"] and second["run_id"] == before["run_id"]
    assert second["tool_attempts"][:-1] == before["tool_attempts"]
    assert second["tool_attempt_count"] == 6 and second["recommendation"]["revision"] == 2
    assert second["phase"] == "awaiting_review" and second["review_round_count"] == 2
    assert element(app.button, "Request Further Investigation").disabled
    assert spies["core"][0].get_account.call_count == 2
    assert all(len(v[0].mock_calls) == 1 for k, v in spies.items() if k != "core")
    assert len(created[0][1].calls) == 5
    element(app.button, "Accept Investigation Recommendation").click().run()
    assert snapshot(app)["phase"] == "completed_reviewed"
    assert snapshot(app)["findings"]["decision"] == "REJECTED"


def test_fraud_unavailable_remains_unavailable_and_acceptance_acknowledges_escalation(mounted):
    app, _, spies = mounted
    open_agent(app)
    start(app, "SYNTHETIC-WIRE-UNAVAILABLE")
    assert not app.exception
    state = snapshot(app)
    assert state["unresolved_controls"] == ["fraud"]
    assert any("Missing usable evidence: Fraud" in w.value for w in app.warning)
    checks = next(d.value for d in app.dataframe if "Status" in d.value.columns)
    assert checks.loc[checks["Control"] == "Fraud", "Status"].tolist() == ["UNAVAILABLE"]
    assert set(state["current_evidence"]) == {"core", "limits", "sanctions"}
    element(app.button, "Accept Investigation Recommendation").click().run()
    assert snapshot(app)["phase"] == "escalated"
    assert any("acknowledgment only" in w.value for w in app.warning)
    assert all(len(values[0].mock_calls) == 1 for values in spies.values())


def test_end_and_escalate_does_not_invoke_more_tools(mounted):
    app, created, spies = mounted
    open_agent(app)
    start(app)
    element(app.button, "End and Escalate").click().run()
    assert snapshot(app)["phase"] == "escalated"
    assert snapshot(app)["outcome_reason"] == "reviewer_ended_investigation"
    assert all(len(values[0].mock_calls) == 1 for values in spies.values())
    assert len(created[0][1].calls) == 5


def test_reruns_navigation_and_duplicate_start_do_not_reexecute(mounted):
    app, created, spies = mounted
    open_agent(app)
    start(app)
    before = snapshot(app)
    controller = app.session_state["investigation_controller"]
    app.run()
    with pytest.raises(AppTestError, match="disabled"):
        element(app.button, "Investigate Payment").click()
    app.run()
    app.sidebar.radio(key="workspace_view").set_value("Wire Validation").run()
    assert [m.value for m in app.metric] == ["20", "$300,107.02", "4", "6", "10"]
    app.sidebar.radio(key="workspace_view").set_value("Knowledge Assistant").run()
    assert app.text_area(key="knowledge_question")
    open_agent(app)
    assert snapshot(app) == before and app.session_state["investigation_controller"] is controller
    assert len(created) == 1 and all(len(values[0].mock_calls) == 1 for values in spies.values())


def test_changed_selection_hides_previous_review_until_matching_selection_or_new_run(mounted):
    app, created, _ = mounted
    open_agent(app)
    start(app)
    before = snapshot(app)
    element(app.selectbox, "Select a synthetic wire payment").set_value("SYNTHETIC-WIRE-LOW-BALANCE").run()
    assert not any(b.label == "Accept Investigation Recommendation" for b in app.button)
    assert any("Review controls are hidden" in i.value for i in app.info)
    assert snapshot(app) == before and len(created) == 1
    element(app.button, "Start New Investigation").click().run()
    assert snapshot(app) == before  # arming alone does not discard the trace
    assert not element(app.button, "Investigate Payment").disabled
    element(app.button, "Investigate Payment").click().run()
    assert len(created) == 2 and snapshot(app)["payment_id"] == "SYNTHETIC-WIRE-LOW-BALANCE"
    assert snapshot(app)["run_id"] != before["run_id"] and snapshot(app)["thread_id"] != before["thread_id"]


def test_stale_review_widget_cannot_accept_new_revision_and_duplicate_accept_is_harmless(mounted):
    app, _, spies = mounted
    open_agent(app)
    start(app)
    stale_accept = element(app.button, "Accept Investigation Recommendation")
    old_key = stale_accept.key
    before = snapshot(app)
    payload = before["human_review"]["payload"]
    stale_response = {k: payload[k] for k in ("run_id", "review_id", "payment_id", "recommendation_revision")}
    stale_response["action"] = "accept_recommendation"
    element(app.text_area, "Reviewer note").input("Recheck core.")
    element(app.button, "Request Further Investigation").click().run()
    assert element(app.button, "Accept Investigation Recommendation").key != old_key
    assert old_key not in [b.key for b in app.button]
    # AppTest cannot serialize a removed widget's old tree; submit its captured
    # identity through the same controller API to prove authoritative refusal.
    with pytest.raises(ReviewValidationError, match="review_already_submitted"):
        app.session_state["investigation_controller"].resume(stale_response)
    app.run()
    assert snapshot(app)["phase"] == "awaiting_review" and len(snapshot(app)["human_review"]["events"]) == 1
    current_accept = element(app.button, "Accept Investigation Recommendation")
    payload = snapshot(app)["human_review"]["payload"]
    current_response = {k: payload[k] for k in ("run_id", "review_id", "payment_id", "recommendation_revision")}
    current_response["action"] = "accept_recommendation"
    current_accept.click().run()
    final = deepcopy(snapshot(app))
    with pytest.raises(ReviewValidationError, match="review_already_submitted"):
        app.session_state["investigation_controller"].resume(current_response)
    app.run()
    assert snapshot(app) == final
    assert spies["core"][0].get_account.call_count == 2


def test_note_validation_is_delegated_to_controller(mounted):
    app, _, spies = mounted
    open_agent(app)
    start(app)
    before = snapshot(app)
    element(app.button, "Request Further Investigation").click().run()
    assert any("Enter a short reviewer note" in e.value for e in app.error)
    assert snapshot(app) == before and all(len(v[0].mock_calls) == 1 for v in spies.values())


def test_lost_session_controller_never_renders_review_or_recreates_it_automatically(mounted):
    app, created, _ = mounted
    open_agent(app)
    start(app)
    del app.session_state["investigation_controller"]
    app.run()
    assert any("session or checkpoint unavailable" in w.value for w in app.warning)
    assert not any(b.label == "Accept Investigation Recommendation" for b in app.button)
    assert len(created) == 1


def test_separate_app_sessions_do_not_share_controllers(mounted):
    app, created, _ = mounted
    open_agent(app)
    start(app)
    first = snapshot(app)
    second = AppTest.from_file(str(APP), default_timeout=30).run()
    open_agent(second)
    assert len(created) == 1 and not any(b.label == "Accept Investigation Recommendation" for b in second.button)
    start(second)
    assert len(created) == 2 and snapshot(second)["thread_id"] != first["thread_id"]
    assert snapshot(app) == first


def test_missing_nebius_configuration_uses_actual_degraded_graph_without_network(monkeypatch):
    for name in ("NEBIUS_API_KEY", "NEBIUS_GENERATION_MODEL", "INVESTIGATION_GENERATION_MODEL"):
        monkeypatch.delenv(name, raising=False)
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    open_agent(app)
    start(app)
    assert not app.exception
    state = snapshot(app)
    assert state["planning_status"] == "degraded" and state["tool_attempt_count"] == 5
    assert state["errors"][0]["category"] == "planner_unavailable"
    assert any("Planning degraded" in w.value for w in app.warning)
    actions = next(d.value for d in app.dataframe if "Action" in d.value.columns)
    assert set(actions["Source"]) == {"Deterministic fallback"}
    element(app.button, "Accept Investigation Recommendation").click().run()
    assert snapshot(app)["phase"] == "escalated"


def test_start_composition_error_is_sanitized_and_does_not_display_credentials(monkeypatch):
    from payment_ops.ui import investigation_view
    def broken(payment_id):
        raise RuntimeError("SECRET_TOKEN provider response")
    monkeypatch.setattr(investigation_view, "create_investigation_controller", broken)
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    open_agent(app)
    start(app)
    assert not app.exception and app.error
    assert any("could not start" in e.value for e in app.error)
    assert not any("SECRET_TOKEN" in e.value for e in app.error)


def test_runtime_factory_is_lazy_and_allocates_unique_identities(monkeypatch):
    from payment_ops.investigation import graph
    def no_planner():
        raise AssertionError("Composition must not initialize the planner")
    monkeypatch.setattr(graph, "create_nebius_planner", no_planner)
    first = create_investigation_controller("SYNTHETIC-WIRE-001")
    second = create_investigation_controller("SYNTHETIC-WIRE-001")
    assert first.snapshot() == second.snapshot() == {}
    assert first._identity[0] != second._identity[0] and first._identity[1] != second._identity[1]


def test_navigation_retains_nondefault_payment_choice_and_pending_review(mounted):
    app, created, _ = mounted
    open_agent(app)
    start(app, "SYNTHETIC-WIRE-LOW-BALANCE")
    before = snapshot(app)
    app.sidebar.radio(key="workspace_view").set_value("Wire Validation").run()
    open_agent(app)
    assert element(app.selectbox, "Select a synthetic wire payment").value == "SYNTHETIC-WIRE-LOW-BALANCE"
    assert snapshot(app) == before and len(created) == 1
    assert element(app.button, "Accept Investigation Recommendation")


def test_in_progress_request_disables_new_starts_and_hides_review_controls(mounted):
    app, created, _ = mounted
    open_agent(app)
    start(app)
    before = snapshot(app)
    app.session_state["investigation_busy"] = True
    app.run()
    assert element(app.button, "Investigate Payment").disabled
    assert element(app.button, "Start New Investigation").disabled
    assert not any(b.label == "Accept Investigation Recommendation" for b in app.button)
    app.session_state["investigation_busy"] = False
    app.run()
    assert snapshot(app) == before and len(created) == 1
    assert element(app.button, "Accept Investigation Recommendation")
