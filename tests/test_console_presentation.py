"""Safety checks for the shared native presentation layer."""

from streamlit.testing.v1 import AppTest


def test_untrusted_control_text_is_literal_and_unknown_status_never_passes():
    app = AppTest.from_string('''
from payment_ops.ui.presentation import control_findings
control_findings([{"area": "Fraud", "status": "UNAVAILABLE", "reasons": ["<img src=x onerror=alert(1)>"]},
                  {"area": "Unknown", "status": "UNRECOGNIZED", "reasons": []}])
''').run()
    assert not app.exception
    assert any(t.value == "<img src=x onerror=alert(1)>" for t in app.text)
    assert not app.get("html")
    badges = [m.value for m in app.markdown]
    assert any("Unavailable" in s for s in badges) and any("Unknown" in s for s in badges)
    assert not any("Passed" in s for s in badges)


def test_knowledge_answer_markup_never_enables_unsafe_html():
    app = AppTest.from_string('''
from payment_ops.ui.knowledge_view import render_answer
from payment_ops.knowledge.service import AnswerResult
render_answer(AnswerResult("clarification", "<script>alert('x')</script>", (), "dense", (), "clarification"))
''').run()
    assert not app.exception
    assert not app.get("html")
    assert all(not m.proto.allow_html for m in app.markdown)
