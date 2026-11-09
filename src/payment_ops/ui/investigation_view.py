"""Session-owned UI over the existing investigation controller; no banking rules."""

from uuid import uuid4

import streamlit as st

from payment_ops.investigation.review import ACCEPT, ESCALATE, FURTHER, ReviewValidationError
from payment_ops.investigation.runtime import create_investigation_controller
from payment_ops.investigation.report import generate_investigation_report, ReportValidationError
from payment_ops.ui.investigation_guidance import clear_guidance, render_operational_guidance
from payment_ops.samples.payments import SYNTHETIC_PAYMENTS


CONTROL_LABELS = {"core": "Core Banking", "limits": "Limits", "fraud": "Fraud", "sanctions": "Sanctions"}
REVIEW_ERRORS = {
    "further_investigation_requires_note": "Enter a short reviewer note before requesting a further check.",
    "shared_extra_connector_attempt_already_used": "The shared additional connector attempt has already been used.",
    "further_investigation_cycle_already_used": "The further-investigation cycle has already been used.",
    "tool_attempt_budget_exhausted": "The tool-attempt budget is exhausted. Accept the recommendation or end and escalate.",
    "active_execution_budget_exhausted": "The active execution budget is exhausted. No additional check can run.",
    "stale_review_id": "This review is stale. Use the current recommendation's review controls.",
    "recommendation_revision_mismatch": "The recommendation changed. Review the current revision before submitting.",
    "review_already_submitted": "This review was already submitted. No repeated action was applied.",
    "investigation_checkpoint_unavailable": "The investigation checkpoint is unavailable. Start a new investigation.",
}


def _arm_new_investigation():
    if st.session_state.get("investigation_busy", False):
        return
    st.session_state["investigation_start_armed"] = True
    st.session_state["investigation_start_token"] = uuid4().hex
    st.session_state.pop("investigation_error", None)


def _identity(state):
    return {k: state[k] for k in ("run_id", "thread_id", "payment_id")}


def _current_state(controller):
    if controller is None:
        return None
    try:
        state = controller.snapshot()
        if not state or _identity(state) != st.session_state.get("investigation_identity"):
            return None
        return state
    except Exception:
        return None


def _render_result(state):
    st.subheader("Investigation results")
    st.text(f"Investigation payment: {state['payment_id']}")
    st.caption(f"Run: {state['run_id']} | Thread: {state['thread_id']}")
    phase = state["phase"]
    if phase == "awaiting_review":
        st.info("Awaiting human review — graph paused for analyst input.")
    elif phase == "completed_reviewed":
        st.success("Completed and reviewed investigation")
    elif phase == "escalated":
        st.warning("Escalated investigation")
    elif phase == "failed":
        st.error("Failed investigation")
    else:
        st.info(f"Investigation lifecycle: {phase}")
    if state["planning_status"] == "degraded":
        st.warning("Planning degraded — deterministic fallback or orchestration failure; autonomous investigation success is not established.")
    elif state["planning_status"] == "succeeded":
        st.caption("Planning: model-selected actions validated. Evidence completeness is shown separately.")
    else:
        st.caption(f"Planning: {state['planning_status']}")
    st.caption(f"Tool attempts: {state['tool_attempt_count']} | Planner attempts: {state['planner_call_count']} | Review rounds: {state['review_round_count']}")

    st.subheader("Action sequence")
    decisions = state["planner_decisions"]
    model_tools = [d["action"] for d in decisions if d["source"] == "model" and d["action"] != "finish"]
    st.text("Model-selected tool sequence: " + (" -> ".join(model_tools) or "No model-selected tools"))
    if decisions:
        st.dataframe([{
            "Step": i, "Action": d["action"],
            "Source": "Model" if d["source"] == "model" else "Deterministic fallback",
            "Explanation": d["reason"],
        } for i, d in enumerate(decisions, 1)], hide_index=True, width="stretch")

    st.subheader("Tool execution history")
    if state["tool_attempts"]:
        st.dataframe([{
            "Attempt": a["attempt_number"], "Tool": a["tool_name"], "Purpose": a["purpose"],
            "Result": "Evidence retrieved" if a["success"] else "Unavailable / failed",
            "Evidence / attempt ID": a["attempt_id"],
            "Error category": a["error"]["category"] if a["error"] else "",
        } for a in state["tool_attempts"]], hide_index=True, width="stretch")
        for attempt in state["tool_attempts"]:
            with st.expander(f"Attempt {attempt['attempt_number']}: {attempt['tool_name']} ({attempt['purpose']})"):
                st.caption(attempt["attempt_id"])
                st.json(attempt["result"] if attempt["success"] else attempt["error"])

    st.subheader("Current connector evidence")
    for control, label in CONTROL_LABELS.items():
        evidence = state["current_evidence"].get(control)
        with st.expander(label):
            if evidence is None:
                st.warning(f"{label}: no usable current evidence. This is not a passing control.")
            else:
                st.caption(f"Evidence reference: {evidence['attempt_id']}")
                st.json(evidence["result"])
    if state["errors"]:
        st.subheader("Recorded failures")
        st.dataframe([{
            "Source": e["tool_name"], "Category": e["category"],
            "Reference": e["attempt_id"], "Transient recovery eligible": e["retryable"],
        } for e in state["errors"]], hide_index=True, width="stretch")
    gaps = state["unresolved_controls"]
    if gaps:
        st.warning("Missing usable evidence: " + ", ".join(CONTROL_LABELS[c] for c in gaps))
    else:
        st.caption("All mandatory controls have usable current evidence.")

    st.subheader("Deterministic simulator findings")
    if state["findings"] is None:
        st.info("No payment validation finding is available for this investigation.")
    else:
        st.text(f"Simulator finding: {state['findings']['decision']}")
        st.text(state["findings"]["primary_reason"])
        st.dataframe([{
            "Control": c["area"], "Status": c["status"], "Reasons": " ".join(c["reasons"]),
        } for c in state["findings"]["checks"]], hide_index=True, width="stretch")
    st.subheader("Investigation recommendation")
    st.text(state["recommendation"]["text"] or "No recommendation is available.")
    st.caption(f"Recommendation revision: {state['recommendation']['revision']}")
    if state["human_review"]["acknowledgment_only"]:
        st.warning("Acceptance recorded as acknowledgment only; escalation remains required.")
    if state["human_review"]["events"]:
        st.subheader("Human review history")
        st.dataframe(state["human_review"]["events"], hide_index=True, width="stretch")


def _render_review(controller, state):
    if st.session_state.get("investigation_busy", False):
        st.info("An investigation request is in progress. Review controls will return when it finishes.")
        return
    payload = state["human_review"]["payload"]
    if state["phase"] != "awaiting_review" or payload is None:
        return
    st.subheader("Human review")
    st.caption("Review accepts an investigation recommendation only. Reviewer identity is not authenticated in this demonstration.")
    review_id = payload["review_id"]
    allowed, controls = payload["permitted_actions"], payload["eligible_controls"]
    if FURTHER not in allowed:
        reason = payload["further_investigation_unavailable_reason"] or "no_eligible_connector"
        st.info("Further investigation unavailable: " + reason.replace("_", " "))
    with st.form(f"investigation_review_form_{review_id}"):
        note = st.text_area("Reviewer note", max_chars=500, key=f"investigation_note_{review_id}")
        selected_control = st.selectbox(
            "Connector to recheck", controls, format_func=lambda c: CONTROL_LABELS[c],
            disabled=not controls, key=f"investigation_recheck_control_{review_id}",
        )
        accept = st.form_submit_button("Accept Investigation Recommendation", key=f"investigation_accept_{review_id}", disabled=ACCEPT not in allowed)
        further = st.form_submit_button("Request Further Investigation", key=f"investigation_further_{review_id}", disabled=FURTHER not in allowed)
        escalate = st.form_submit_button("End and Escalate", key=f"investigation_escalate_{review_id}", disabled=ESCALATE not in allowed)
    if not (accept or further or escalate):
        return
    response = {k: payload[k] for k in ("run_id", "review_id", "payment_id", "recommendation_revision")}
    response.update(action=ACCEPT if accept else FURTHER if further else ESCALATE, note=note)
    if further:
        response["requested_control"] = selected_control
    st.session_state.pop("investigation_error", None)
    st.session_state["investigation_busy"] = True
    try:
        with st.spinner("Resuming the investigation and preserving its evidence…"):
            controller.resume(response)
    except ReviewValidationError as error:
        st.session_state["investigation_error"] = REVIEW_ERRORS.get(
            str(error), "No review action was applied. Use the current review controls or start a new investigation.",
        )
    except Exception:
        st.session_state["investigation_error"] = "The investigation could not resume. No payment action was performed. Check the current state before trying again."
    finally:
        st.session_state["investigation_busy"] = False
    st.rerun()


def render_investigation_agent():
    st.subheader("Payment Investigation Agent")
    st.caption("Synthetic educational data only. Read-only investigation; completion is not payment authorization.")
    st.caption("State lasts only in this browser session and running application. Lost checkpoints require a new investigation.")
    if "investigation_selected_payment" not in st.session_state:
        st.session_state["investigation_selected_payment"] = st.session_state.get(
            "investigation_payment_choice", SYNTHETIC_PAYMENTS[0].payment_id,
        )
    selected_id = st.selectbox("Select a synthetic wire payment", [p.payment_id for p in SYNTHETIC_PAYMENTS], key="investigation_selected_payment")
    # Widget keys may be cleaned up when another workspace renders. Retain the
    # chosen ID separately so navigation does not silently select another wire.
    st.session_state["investigation_payment_choice"] = selected_id
    payment = next(p for p in SYNTHETIC_PAYMENTS if p.payment_id == selected_id)
    st.table([{"Payment reference": selected_id, "Amount": str(payment.amount),
               "Payment date": payment.payment_date.isoformat() if payment.payment_date else "Missing",
               "Beneficiary": payment.beneficiary_name or "Missing"}])

    controller = st.session_state.get("investigation_controller")
    has_previous = controller is not None or "investigation_identity" in st.session_state
    if "investigation_start_token" not in st.session_state:
        st.session_state["investigation_start_token"] = uuid4().hex
    busy = st.session_state.get("investigation_busy", False)
    armed = (not has_previous or st.session_state.get("investigation_start_armed", False)) and not busy
    token = st.session_state["investigation_start_token"]
    if has_previous:
        st.button("Start New Investigation", key="investigation_arm_new", on_click=_arm_new_investigation, disabled=busy)
        st.caption("To replace the retained trace, choose a payment, select Start New Investigation, then Investigate Payment.")
    submitted = st.button("Investigate Payment", key=f"investigation_start_{token}", disabled=not armed)
    if submitted and armed:
        # Consume this start event before I/O. The next render has a different
        # widget identity and cannot replay an old/double-clicked start event.
        st.session_state["investigation_start_armed"] = False
        st.session_state["investigation_busy"] = True
        st.session_state["investigation_start_token"] = uuid4().hex
        st.session_state.pop("investigation_error", None)
        try:
            with st.spinner("Investigating the selected payment using read-only tools…"):
                new_controller = create_investigation_controller(selected_id)
                state = new_controller.start()
                st.session_state["investigation_controller"] = new_controller
                st.session_state["investigation_identity"] = _identity(state)
        except Exception:
            st.session_state["investigation_error"] = "The investigation could not start. Check provider configuration and connectivity. No payment action was performed."
        finally:
            st.session_state["investigation_busy"] = False
        st.rerun()

    if "investigation_error" in st.session_state:
        st.error(st.session_state["investigation_error"])
    state = _current_state(controller)
    if has_previous and state is None:
        clear_guidance()
        st.warning("Investigation session or checkpoint unavailable. Start a new investigation; the previous review cannot be resumed.")
    if state is not None:
        _render_result(state)
        if selected_id != state["payment_id"]:
            clear_guidance()
            st.info("The selected payment differs from the retained investigation. Review controls are hidden. Select its original payment or explicitly start a new investigation.")
        else:
            if not busy:
                _render_report_download(state)
            _render_review(controller, state)
            render_operational_guidance(state, busy=busy)


def _render_report_download(state):
    """Export detached state only. Clicking downloads bytes without a rerun."""
    try:
        pdf = generate_investigation_report(state)
    except ReportValidationError:
        st.caption("An investigation report is not available for this snapshot.")
        return
    except Exception:
        st.warning("The report could not be prepared. Investigation state is unchanged.")
        return
    if state["phase"] == "awaiting_review":
        st.caption("Provisional report: human review is pending; this is not a final investigation outcome.")
    st.download_button(
        "Download Investigation Report", data=pdf, mime="application/pdf",
        file_name=f"PaymentOps-Investigation-{state['run_id']}.pdf",
        key=f"investigation_report_{state['run_id']}_{state['recommendation']['revision']}_{state['phase']}",
        on_click="ignore",
    )
