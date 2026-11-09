"""Offline public KnowledgeService integration and bounded-query isolation."""

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from payment_ops.investigation.guidance import TOPICS, finding_related_topics, find_operational_guidance
from payment_ops.investigation.planner import InvestigationPlanner
from payment_ops.investigation.runtime import create_investigation_controller
from payment_ops.investigation.tools import TOOLS
from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import RetrievalHit
from payment_ops.knowledge.service import AnswerResult, KnowledgeService


@pytest.fixture
def grounded():
    # Actual frozen corpus and actual Week 2 validator; only retrieval/model are doubles.
    chunks = chunk_documents(load_documents(Path("data/knowledge/documents")))
    quote = "ACCEPTED does not mean SETTLED."
    chunk = next(c for c in chunks if c.document_id == "SYN-STATUS" and c.section_id == "SS-STATES" and quote in c.content)
    provider = Mock()
    provider.generate.return_value = json.dumps({"status": "answered", "statements": [
        {"text": "Acceptance does not establish settlement.", "evidence": [{"source_id": "S1", "quote": quote}]}],
        "clarification_question": None, "required_sections": [],
    })
    retriever = Mock()
    retriever.retrieve.return_value = (RetrievalHit(chunk, 1.0, 1),)
    service = KnowledgeService({"dense": retriever}, provider, section_catalog=(chunk,))
    return service, provider


def test_actual_public_service_validates_citations_and_keeps_them_unchanged(grounded):
    service, provider = grounded
    result = find_operational_guidance("status", service_factory=lambda: service)
    assert result.error_category is None and result.answer.status == "answered"
    citation = result.answer.citations[0]
    assert citation.document_id == "SYN-STATUS" and citation.section_id == "SS-STATES"
    assert citation.passages[0].quote == "ACCEPTED does not mean SETTLED."
    assert citation.evidence_quote == citation.passages[0].quote
    assert provider.generate.call_count == 1


@pytest.mark.parametrize("topic", TOPICS, ids=lambda t: t.topic_id)
def test_queries_are_fixed_generic_and_never_accept_transaction_fields(topic, grounded):
    real, _ = grounded
    answer = real.ask(TOPICS[-1].question)
    service = Mock()
    service.ask.return_value = answer
    result = find_operational_guidance(topic.topic_id, service_factory=lambda: service)
    service.ask.assert_called_once_with(topic.question)
    assert result.answer is answer  # preserve validated citations/status, no rewriting
    assert len(topic.question) < 250
    assert all(word not in topic.question for word in ("SYNTHETIC-WIRE-001", "12500", "SYNTHETIC-SENDER", "account_id", "beneficiary_name"))


@pytest.mark.parametrize("topic", ["insufficient_balance", "sanctions", "fraud", "release_payment", ""])
def test_unsupported_topic_never_initializes_service(topic):
    factory = Mock(side_effect=AssertionError("Must not initialize"))
    result = find_operational_guidance(topic, service_factory=factory)
    assert result.error_category == "unsupported_topic" and result.answer is None
    factory.assert_not_called()


@pytest.mark.parametrize("status,reason", [
    ("limited_answer", "limited_answer"), ("clarification", "clarification"),
    ("insufficient_evidence", "insufficient_evidence"), ("unavailable", "provider_failure"),
    ("insufficient_evidence", "invalid_response"),
])
def test_actual_statuses_are_preserved(grounded, status, reason):
    service, _ = grounded
    original = service.ask(TOPICS[-1].question)
    answer = replace(original, status=status, reason_code=reason,
                     citations=original.citations if status == "limited_answer" else ())
    stub = Mock()
    stub.ask.return_value = answer
    result = find_operational_guidance("status", service_factory=lambda: stub)
    assert result.answer is answer and result.answer.reason_code == reason


@pytest.mark.parametrize("failure", [RuntimeError("SECRET provider error"), TypeError("SECRET response")])
def test_errors_are_sanitized(failure):
    result = find_operational_guidance("exception", service_factory=Mock(side_effect=failure))
    assert result.error_category == "knowledge_unavailable" and "SECRET" not in repr(result)


@pytest.mark.parametrize("answer", [None, {}, "raw response", AnswerResult("answered", "uncited", (), "dense", (), "answered"),
    AnswerResult("unsupported-status", "SECRET", (), "dense", (), "answered")])
def test_malformed_return_contract_is_not_displayable(answer):
    service = Mock()
    service.ask.return_value = answer
    result = find_operational_guidance("exception", service_factory=lambda: service)
    assert result.error_category == "malformed_response" and result.answer is None


def test_actual_invalid_model_quote_remains_rejected(grounded):
    service, provider = grounded
    provider.generate.return_value = '{"status":"answered","statements":[]}'
    result = find_operational_guidance("status", service_factory=lambda: service)
    assert result.answer.status == "insufficient_evidence" and result.answer.reason_code == "invalid_response"
    assert not result.answer.citations


def test_existing_retrieval_failure_status_is_preserved(grounded):
    service, provider = grounded
    service.retrievers["dense"].retrieve.side_effect = RuntimeError("SECRET retrieval")
    result = find_operational_guidance("status", service_factory=lambda: service)
    assert result.answer.status == "unavailable" and result.answer.reason_code == "retrieval_failure"
    assert not result.answer.citations and provider.generate.call_count == 0


def test_public_ask_exception_is_sanitized():
    service = Mock()
    service.ask.side_effect = RuntimeError("SECRET ask failure")
    result = find_operational_guidance("exception", service_factory=lambda: service)
    assert result.error_category == "knowledge_unavailable" and "SECRET" not in repr(result)


@pytest.mark.parametrize("payment,related", [
    ("SYNTHETIC-WIRE-001", ()), ("SYNTHETIC-WIRE-LOW-BALANCE", ("exception",)),
    ("SYNTHETIC-WIRE-UNAVAILABLE", ("exception",)),
])
def test_suggestions_use_only_recorded_findings_and_cannot_mutate_state(payment, related):
    provider = Mock()
    provider.generate.side_effect = [json.dumps({"action": a, "reason": "Collect evidence."}) for a in (*TOOLS, "finish")]
    controller = create_investigation_controller(payment, planner=InvestigationPlanner(provider))
    state = controller.start()
    original = deepcopy(state)
    assert finding_related_topics(state) == related
    assert state == original == controller.snapshot()
    assert "balance" not in related and "sanctions" not in related
