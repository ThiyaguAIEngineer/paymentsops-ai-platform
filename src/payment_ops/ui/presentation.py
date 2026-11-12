"""Small native presentation helpers. No business decisions or model calls."""

from pathlib import Path

import streamlit as st


def console_styles():
    # Trusted, repository-owned CSS only. Never interpolate data or model text.
    st.html("<style>" + Path(__file__).with_name("console.css").read_text(encoding="utf-8") + "</style>")


def page_header(title, description, *, eyebrow):
    st.caption(eyebrow)
    st.subheader(title)
    st.write(description)


def metric_cards(items, *, key):
    with st.container(key=key):
        for column, (label, value) in zip(st.columns(len(items)), items, strict=True):
            with column, st.container(border=True):
                st.metric(label, value)


def status_indicator(status):
    colors = {"PASS": "green", "REJECTED": "red", "REVIEW": "orange",
              "UNAVAILABLE": "gray", "SKIPPED": "gray"}
    labels = {"PASS": "Passed", "REJECTED": "Rejected / blocked", "REVIEW": "Needs review",
              "UNAVAILABLE": "Unavailable", "SKIPPED": "Not performed"}
    st.badge(labels.get(status, "Unknown") + " · " + str(status), color=colors.get(status, "gray"))


def control_findings(checks):
    """Display the recorded check status verbatim; never derive a new result."""
    with st.container(key="control_findings"):
        for start in range(0, len(checks), 2):
            for column, check in zip(st.columns(2), checks[start:start + 2]):
                with column, st.container(border=True):
                    st.text(check["area"])
                    status_indicator(check["status"])
                    st.text(" ".join(check["reasons"]) or "No additional explanation recorded.")
