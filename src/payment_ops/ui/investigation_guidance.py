"""Optional analyst-requested guidance; no graph actions or transaction queries."""

import streamlit as st

from payment_ops.investigation.guidance import (
    TOPICS, NO_PROCEDURE, finding_related_topics, find_operational_guidance,
)


def clear_guidance():
    for key in ("investigation_guidance_context", "investigation_guidance_results"):
        st.session_state.pop(key, None)


def _knowledge_service():
    # Reuse the existing lazy browser-session resource, not a global result cache.
    from payment_ops.ui.knowledge_view import get_knowledge_service

    return get_knowledge_service()


def render_operational_guidance(state, *, busy=False):
    context = (state["run_id"], state["payment_id"])
    if st.session_state.get("investigation_guidance_context") != context:
        clear_guidance()
        st.session_state["investigation_guidance_context"] = context
        st.session_state["investigation_guidance_results"] = {}
    st.subheader("Operational Guidance")
    st.caption("Optional synthetic SOP guidance, separate from payment evidence. It cannot change findings, review decisions or authorize a payment action.")
    st.caption("No balance-remediation, fraud-treatment or sanctions-specific SOP is available. General lookups do not establish applicability to this payment, recall eligibility or settlement.")
    related = finding_related_topics(state)
    if related:
        st.info("An adverse or unavailable control supports consulting general exception triage; this is not a control-specific remedy.")
        st.caption("For a control-specific remedy: " + NO_PROCEDURE)
    else:
        st.caption("No finding-specific procedure is inferred. Choose a manual/general educational lookup if useful.")
    options = {t.topic_id: t for t in TOPICS}
    topic_id = st.selectbox(
        "Procedure topic", list(options),
        format_func=lambda key: ("Finding-related: " if key in related else "Manual/general: ") + options[key].label,
        key=f"investigation_guidance_topic_{state['run_id']}", disabled=busy,
    )
    topic = options[topic_id]
    st.caption("Corpus scope: " + topic.corpus_scope + ". These references describe topic coverage, not retrieved answer citations.")
    st.text("Generic lookup: " + topic.question)
    results = st.session_state["investigation_guidance_results"]
    if st.button("Find Operational Guidance", key=f"investigation_guidance_find_{state['run_id']}", disabled=busy):
        if topic_id not in results:
            with st.spinner("Retrieving and validating synthetic procedure guidance..."):
                results[topic_id] = find_operational_guidance(topic_id, service_factory=_knowledge_service)
    if topic_id not in results:
        return
    st.caption("Result retained for this investigation and topic; rerenders and repeated requests reuse it.")
    result = results[topic_id]
    if result.error_category is not None:
        st.caption("Guidance status: " + result.error_category)
        st.warning(NO_PROCEDURE)
        st.info("The investigation is unchanged. Knowledge service or response validation may be unavailable; no rejected content is shown.")
        return
    answer = result.answer
    st.caption("KnowledgeService status: " + answer.status)
    st.caption("KnowledgeService reason: " + answer.reason_code)
    if (answer.status in {"insufficient_evidence", "unavailable"}
            or answer.reason_code in {"invalid_response", "unvalidated_response"}):
        st.warning(NO_PROCEDURE)
        # Do not render unavailable/rejected bodies, even from a faulty service.
        if answer.status == "unavailable":
            st.info("Knowledge service unavailable. The investigation remains unchanged.")
        return
    from payment_ops.ui.knowledge_view import render_answer

    render_answer(answer)
