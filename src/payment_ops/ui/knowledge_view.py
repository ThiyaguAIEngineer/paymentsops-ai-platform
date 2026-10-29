"""Thin Streamlit view over the existing KnowledgeService and AnswerResult."""

import streamlit as st

from payment_ops.knowledge.runtime import create_knowledge_service
from payment_ops.knowledge.generation import GenerationError
from payment_ops.knowledge.service import AnswerResult, DISCLOSURE, KnowledgeService


@st.cache_resource(show_spinner=False, scope="session")
def get_knowledge_service() -> KnowledgeService:
    """One resource per browser session, reused on reruns and repeated submissions."""
    return create_knowledge_service()


def format_answer_markdown(text: str) -> str:
    """Separate Markdown table blocks for readable rendering; evidence stays exact."""
    lines = []
    in_table = False
    for line in text.splitlines():
        is_table = line.lstrip().startswith("|")
        if is_table != in_table and lines and lines[-1].strip() and line.strip():
            lines.append("")
        lines.append(line)
        in_table = is_table
    return "\n".join(lines)


def render_answer(answer: AnswerResult) -> None:
    # Rejected/unavailable envelopes never render their body or citations, even
    # when a faulty test double/caller supplies untrusted content in those fields.
    if answer.reason_code in {"invalid_response", "unvalidated_response"} or answer.status not in {
        "answered", "limited_answer", "clarification", "insufficient_evidence", "unavailable",
    }:
        st.warning("Response rejected — validation did not establish a supported answer.")
        st.info("Please rephrase the question or try again. No rejected model output is shown.")
        return
    if answer.status == "unavailable":
        st.error("Knowledge service unavailable. Please try again later.")
        return
    if answer.status == "answered":
        st.success("Answered")
    elif answer.status == "limited_answer":
        st.warning("Limited answer — review the stated scope and missing evidence.")
    elif answer.status == "clarification":
        st.info("Clarification required")
    else:
        st.warning("Insufficient evidence")
    st.markdown(format_answer_markdown(answer.answer), unsafe_allow_html=False)
    if answer.citations:
        st.subheader("Sources")
        for citation in answer.citations:
            st.text(f"[{citation.number}] {citation.document_title}")
            st.caption(f"{citation.document_id} · Section {citation.section_id} · Version {citation.document_version}")
            with st.expander(f"Supporting evidence [{citation.number}]"):
                for passage in citation.passages:
                    st.caption(f"Chunk: {passage.chunk_id} · Source: {passage.source_id}")
                    st.code(passage.quote, language="text", wrap_lines=True)


def render_knowledge_assistant() -> None:
    st.subheader("Knowledge Assistant")
    st.caption(DISCLOSURE)
    st.write("Ask about documented payment procedures, exceptions, statuses, or synthetic error codes.")
    st.caption("Use synthetic examples only. This assistant cannot inspect live payments or execute actions.")
    with st.form("knowledge_question_form"):
        question = st.text_area("Question", key="knowledge_question", placeholder="What does ACCEPTED mean?")
        submitted = st.form_submit_button("Ask", key="knowledge_ask")
    if submitted:
        for key in ("knowledge_result", "knowledge_answered_question", "knowledge_error"):
            st.session_state.pop(key, None)
        if not question.strip():
            st.session_state["knowledge_error"] = "Enter a payment procedure or error-code question."
        else:
            try:
                with st.spinner("Retrieving synthetic evidence and validating the response…"):
                    service = get_knowledge_service()
                    answer = service.ask(question.strip())
                    if not isinstance(answer, AnswerResult):
                        raise TypeError("Unexpected knowledge response contract")
                st.session_state["knowledge_result"] = answer
                st.session_state["knowledge_answered_question"] = question.strip()
            except GenerationError as exc:
                st.session_state["knowledge_error"] = (
                    "Knowledge Assistant is not configured or its model is unavailable. "
                    "Ask the operator to check provider credentials and model settings."
                    if exc.diagnostic.stage == "configuration" else
                    "Knowledge Assistant could not respond. Check provider configuration and connectivity, then try again."
                )
            except Exception:
                st.session_state["knowledge_error"] = (
                    "Knowledge Assistant could not respond. Check provider configuration and connectivity, then try again."
                )
    if "knowledge_error" in st.session_state:
        st.error(st.session_state["knowledge_error"])
    if "knowledge_result" in st.session_state:
        st.caption("Response to:")
        st.text(st.session_state["knowledge_answered_question"])
        render_answer(st.session_state["knowledge_result"])
