"""Streamlit integration tests with injected responses; no live API calls."""

from dataclasses import replace
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from payment_ops.knowledge.service import AnswerResult, Citation, DISCLOSURE, EvidencePassage
from payment_ops.ui.knowledge_view import format_answer_markdown


APP = Path(__file__).resolve().parents[1] / "src/payment_ops/ui/app.py"


@pytest.fixture(autouse=True)
def isolated_resource_cache():
    # AppTest uses the literal "test session id" for every instance. Isolate
    # tests while retaining genuine cache reuse across reruns within each test.
    import streamlit as st
    st.cache_resource.clear()
    yield
    st.cache_resource.clear()


class Service:
    def __init__(self, answer):
        self.answer, self.calls = answer, []

    def ask(self, question):
        self.calls.append(question)
        if isinstance(self.answer, Exception):
            raise self.answer
        return self.answer


@pytest.fixture
def answer():
    quote = "ACCEPTED does not mean SETTLED."
    passage = EvidencePassage("synthetic-test-chunk", "S1", quote, 0, len(quote))
    citation = Citation(1, "Settlement and Payment Status Guide", "SYN-STATUS", "SS-STATES", "1.0.0",
                        passage.chunk_id, "data/knowledge/documents/settlement_payment_status_guide.md", quote, (passage,))
    return AnswerResult("answered", DISCLOSURE + "\n\nACCEPTED does not mean SETTLED. [1]", (citation,), "dense", (passage.chunk_id,), "answered")


def mount(monkeypatch, answer):
    import payment_ops.ui.knowledge_view as view
    service = Service(answer)
    initializations = []

    def create():
        initializations.append(True)
        return service

    monkeypatch.setattr(view, "create_knowledge_service", create)
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    return app, service, initializations


def open_knowledge(app):
    return app.sidebar.radio(key="workspace_view").set_value("Knowledge Assistant").run()


def ask(app, question="Does ACCEPTED mean settled?"):
    app.text_area(key="knowledge_question").input(question)
    return app.button(key="knowledge_ask").click().run()


def test_navigation_is_lazy_and_wire_dashboard_stays_default(monkeypatch, answer):
    app, service, initializations = mount(monkeypatch, answer)
    assert [m.value for m in app.metric] == ["20", "$300,107.02", "4", "6", "10"]
    assert app.selectbox(key="selected_payment")
    open_knowledge(app)
    assert not app.exception and not app.metric
    assert not service.calls and not initializations
    assert any(DISCLOSURE == c.value for c in app.caption)


def test_success_sources_and_exact_supporting_evidence(monkeypatch, answer):
    app, service, initializations = mount(monkeypatch, answer)
    open_knowledge(app)
    ask(app)
    assert not app.exception
    assert app.success[0].value == "Answered"
    assert any("ACCEPTED does not mean SETTLED. [1]" in m.value for m in app.markdown)
    assert any("Settlement and Payment Status Guide" in t.value for t in app.text)
    assert any("SS-STATES" in c.value and "1.0.0" in c.value for c in app.caption)
    assert app.expander[0].label == "Supporting evidence [1]"
    assert app.code[0].value == answer.citations[0].passages[0].quote
    assert service.calls == ["Does ACCEPTED mean settled?"] and len(initializations) == 1


@pytest.mark.parametrize("status,reason,body,label,element", [
    ("clarification", "missing_transaction_context", "Which payment rail and status?", "Clarification required", "info"),
    ("insufficient_evidence", "insufficient_evidence", "The catalog cannot establish this code's meaning.", "Insufficient evidence", "warning"),
    ("limited_answer", "limited_answer", "Only the supported correction scope is available.", "Limited answer", "warning"),
])
def test_safe_response_statuses(monkeypatch, answer, status, reason, body, label, element):
    result = replace(answer, status=status, reason_code=reason, answer=DISCLOSURE + "\n\n" + body, citations=())
    app, _, _ = mount(monkeypatch, result)
    ask(open_knowledge(app), "How do I proceed?")
    assert not app.exception
    assert any(label in entry.value for entry in getattr(app, element))
    assert any(body in m.value for m in app.markdown)
    assert not app.expander


@pytest.mark.parametrize("status,reason,label,element", [
    ("insufficient_evidence", "invalid_response", "Response rejected", "warning"),
    ("insufficient_evidence", "unvalidated_response", "Response rejected", "warning"),
    ("unavailable", "provider_failure", "service unavailable", "error"),
    ("unavailable", "retrieval_failure", "service unavailable", "error"),
    ("unexpected_status", "unexpected", "Response rejected", "warning"),
])
def test_rejected_and_unavailable_bodies_never_render(monkeypatch, answer, status, reason, label, element):
    unsafe = replace(answer, status=status, reason_code=reason, answer="REJECTED-SECRET-PAYLOAD")
    app, _, _ = mount(monkeypatch, unsafe)
    ask(open_knowledge(app))
    assert not app.exception
    assert any(label in e.value for e in getattr(app, element))
    assert all("REJECTED-SECRET" not in m.value for m in app.markdown)
    assert not app.expander and not app.code


def test_service_exception_is_sanitized_and_stale_answer_cleared(monkeypatch, answer):
    app, service, _ = mount(monkeypatch, answer)
    ask(open_knowledge(app))
    service.answer = RuntimeError("AUTHORIZATION private-secret")
    ask(app, "Another question")
    assert not app.exception and "could not respond" in app.error[0].value
    assert "private-secret" not in app.error[0].value
    assert not app.success and not app.expander


def test_initializer_failure_is_safe_and_not_cached_as_a_fake_service(monkeypatch, answer):
    import payment_ops.ui.knowledge_view as view
    app, _, _ = mount(monkeypatch, answer)
    def fail():
        raise RuntimeError("NEBIUS_API_KEY=never-display-this")
    monkeypatch.setattr(view, "create_knowledge_service", fail)
    ask(open_knowledge(app))
    assert not app.exception and "provider configuration" in app.error[0].value
    assert "never-display-this" not in app.error[0].value
    service = Service(answer)
    monkeypatch.setattr(view, "create_knowledge_service", lambda: service)
    ask(app)
    assert not app.error and service.calls == ["Does ACCEPTED mean settled?"]


def test_missing_credentials_has_actionable_message_without_secret(monkeypatch, answer):
    import payment_ops.ui.knowledge_view as view
    from payment_ops.knowledge.generation import GenerationDiagnostic, GenerationError
    app, _, _ = mount(monkeypatch, answer)
    def fail():
        raise GenerationError("secret config", diagnostic=GenerationDiagnostic("configuration", "missing_credentials"))
    monkeypatch.setattr(view, "create_knowledge_service", fail)
    ask(open_knowledge(app))
    assert not app.exception and "provider credentials and model settings" in app.error[0].value
    assert "secret config" not in app.error[0].value


def test_reruns_and_question_edits_do_not_call_or_reinitialize(monkeypatch, answer):
    app, service, initializations = mount(monkeypatch, answer)
    open_knowledge(app)
    ask(app)
    app.run()
    app.text_area(key="knowledge_question").input("Draft not submitted").run()
    assert len(initializations) == 1 and service.calls == ["Does ACCEPTED mean settled?"]
    assert any(t.value == "Does ACCEPTED mean settled?" for t in app.text)
    ask(app, "A second submitted question")
    assert len(initializations) == 1
    assert service.calls == ["Does ACCEPTED mean settled?", "A second submitted question"]


def test_empty_question_never_initializes_or_calls_service(monkeypatch, answer):
    app, service, initializations = mount(monkeypatch, answer)
    ask(open_knowledge(app), "   ")
    assert not app.exception and "Enter a" in app.error[0].value
    assert not service.calls and not initializations


def test_returning_from_wire_view_preserves_latest_answer_without_call(monkeypatch, answer):
    app, service, initializations = mount(monkeypatch, answer)
    ask(open_knowledge(app))
    app.sidebar.radio(key="workspace_view").set_value("Wire Validation").run()
    assert len(app.dataframe[0].value) == 20
    open_knowledge(app)
    assert app.success[0].value == "Answered"
    assert len(service.calls) == 1 and len(initializations) == 1


def test_knowledge_view_never_loads_or_sends_payment_records(monkeypatch, answer):
    import payment_ops.ui.app as main_app
    import payment_ops.ui.knowledge_view as view
    def forbidden():
        pytest.fail("Knowledge view must not load Week 1 payment records")
    monkeypatch.setattr(main_app, "load_payments", forbidden)
    service = Service(answer)
    monkeypatch.setattr(view, "create_knowledge_service", lambda: service)
    source = 'import streamlit as st\nst.session_state["workspace_view"] = "Knowledge Assistant"\nfrom payment_ops.ui.app import main\nmain()'
    app = AppTest.from_string(source, default_timeout=20).run()
    ask(app, "Explain a synthetic status")
    assert not app.exception and service.calls == ["Explain a synthetic status"]


def test_case_table_gets_markdown_boundaries_without_changing_evidence(monkeypatch, answer):
    body = "Common case requirements:\n| Case field | Required content |\n| --- | --- |\n| Ownership | Current owner |\nDo not invent missing values. [1]"
    result = replace(answer, answer=DISCLOSURE + "\n\n" + body)
    app, _, _ = mount(monkeypatch, result)
    ask(open_knowledge(app))
    rendered = next(m.value for m in app.markdown if "| Case field" in m.value)
    assert "requirements:\n\n| Case field" in rendered
    assert "| Current owner |\n\nDo not invent" in rendered
    assert app.code[0].value == answer.citations[0].passages[0].quote
    assert format_answer_markdown("Plain guidance.") == "Plain guidance."
