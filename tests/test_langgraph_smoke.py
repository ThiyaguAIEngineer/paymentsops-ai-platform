"""Isolated LangGraph compatibility checks using dummy state and no app services."""

from typing import TypedDict

import httpx
import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class DummyState(TypedDict, total=False):
    value: int
    needs_review: bool
    review_response: str
    outcome: str


@pytest.mark.parametrize(
    "needs_review,response,expected_outcome",
    [(True, "accept", "accepted"), (True, "decline", "declined"),
     (False, None, "review_not_required")],
)
def test_dummy_graph_routing_checkpoint_and_review_resume(
    monkeypatch, needs_review, response, expected_outcome,
):
    # Keep ambient tracing settings from turning this offline smoke test into I/O.
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")

    def forbid_http(*args, **kwargs):
        raise AssertionError("The LangGraph smoke test must not make HTTP calls")

    monkeypatch.setattr(httpx.Client, "request", forbid_http)
    monkeypatch.setattr(httpx.AsyncClient, "request", forbid_http)
    prepare_calls = []

    def prepare(state: DummyState):
        prepare_calls.append(state["value"])
        return {"value": state["value"] + 1}

    def route(state: DummyState):
        return "review" if state["needs_review"] else "finish"

    def review(state: DummyState):
        decision = interrupt({"question": "Review dummy value", "value": state["value"]})
        assert decision in ("accept", "decline")
        return {"review_response": decision}

    def finish(state: DummyState):
        outcome = {"accept": "accepted", "decline": "declined"}.get(
            state.get("review_response"), "review_not_required",
        )
        return {"value": state["value"] * 2, "outcome": outcome}

    builder = StateGraph(DummyState)
    builder.add_node("prepare", prepare)
    builder.add_node("review", review)
    builder.add_node("finish", finish)
    builder.add_edge(START, "prepare")
    builder.add_conditional_edges("prepare", route, {"review": "review", "finish": "finish"})
    builder.add_edge("review", "finish")
    builder.add_edge("finish", END)
    saver = InMemorySaver()
    graph = builder.compile(checkpointer=saver)
    config = {"configurable": {"thread_id": "dummy-smoke-thread"}}

    result = graph.invoke({"value": 2, "needs_review": needs_review}, config)
    if needs_review:
        assert result["__interrupt__"][0].value == {
            "question": "Review dummy value", "value": 3,
        }
        paused = graph.get_state(config)
        assert paused.values["value"] == 3
        assert "outcome" not in paused.values  # finish has not run before review
        assert paused.next == ("review",)
        assert saver.get_tuple(config) is not None
        # Same graph/thread resumes the stored state; do not submit initial state again.
        result = graph.invoke(Command(resume=response), config)
        assert result["review_response"] == response
    else:
        assert "__interrupt__" not in result
        assert "review_response" not in result

    assert prepare_calls == [2]  # resuming review did not repeat the earlier node
    assert result["value"] == 6
    assert result["outcome"] == expected_outcome
    completed = graph.get_state(config)
    assert completed.values["value"] == 6
    assert completed.values["outcome"] == expected_outcome
    assert completed.next == ()
    assert saver.get_tuple(config) is not None
    assert graph.get_state({"configurable": {"thread_id": "other-thread"}}).values == {}
