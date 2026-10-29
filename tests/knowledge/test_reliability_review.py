"""Offline reliability contracts; simulated quotes are not captured model output."""

from dataclasses import asdict
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

from payment_ops.knowledge.answer_evaluation import disposition_correct, summarize
from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.generation import GenerationError
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import RetrievalHit
from payment_ops.knowledge.service import KnowledgeService, SYSTEM_PROMPT, build_context, validate_answer


@pytest.mark.parametrize("status,reason,expected", [
    ("insufficient_evidence", "policy_period_unsupported", True),
    ("answered", "policy_period_unsupported", False),
    ("unavailable", "policy_period_unsupported", False),
    ("insufficient_evidence", "invalid_response", False),
    ("insufficient_evidence", "retrieval_failure", False),
    ("insufficient_evidence", "provider_failure", False),
    ("insufficient_evidence", "evaluation_service_failure", False),
    ("insufficient_evidence", "unknown_reason", False),
])
def test_historical_abstention_is_narrowly_allowlisted(status, reason, expected):
    row = dict(classification="unsupported", status=status, reason_code=reason)
    assert disposition_correct(row) is expected


def test_historical_abstention_does_not_satisfy_answerable_or_ambiguous():
    for classification in ("answerable", "ambiguous"):
        assert not disposition_correct(dict(classification=classification, status="insufficient_evidence",
                                            reason_code="policy_period_unsupported"))


@pytest.fixture
def chunks():
    return chunk_documents(load_documents(Path("data/knowledge/documents")))


def payload(quote, source="S1", **changes):
    output = dict(status="answered", statements=[dict(text="A simulated claim.",
                  evidence=[dict(source_id=source, quote=quote)])], clarification_question=None, required_sections=[])
    output.update(changes)
    return json.dumps(output)


@pytest.mark.parametrize("section", ["EC-BENEFICIARY", "AR-NEXT", "SS-DELAY"])
def test_exact_markdown_excerpt_preserves_offsets(chunks, section):
    chunk = next(c for c in chunks if c.section_id == section)
    quote = next(line for line in chunk.content.splitlines() if line.startswith("| SYN-") or line.startswith("1. "))
    _, sources = build_context("Operational question", (RetrievalHit(chunk, 1, 1),))
    status, _, citations = validate_answer(payload(quote), sources)
    assert status == "answered"
    passage = citations[0].passages[0]
    assert chunk.content[passage.start:passage.end] == quote == passage.quote
    assert passage.chunk_id == chunk.chunk_id and passage.source_id == "S1"


@pytest.mark.parametrize("section,malformation", [
    ("EC-BENEFICIARY", "SYN-BEN-301 means name mismatch; compare the submitted name with the verified record."),
    ("AR-NEXT", "For SYN-ACH-201, do not retry to the same closed account."),
    ("SS-DELAY", "Capture the last status ... resolve duplicates and resend."),
])
def test_rewritten_quotes_fail_closed_without_payload_logging(chunks, section, malformation):
    chunk = next(c for c in chunks if c.section_id == section)
    class Retriever:
        def retrieve(self, query, k=5):
            return (RetrievalHit(chunk, 1, 1),)
    class Provider:
        def generate(self, system, user):
            return payload(malformation)
    answer = KnowledgeService({"dense": Retriever()}, Provider(), as_of_date=date(2026, 10, 28)).ask("Explain the documented checks")
    assert answer.status == "insufficient_evidence" and answer.reason_code == "invalid_response"
    assert answer.diagnostics[0].category == "quote_not_found"
    assert not answer.citations
    assert malformation not in answer.answer
    diagnostic = asdict(answer.diagnostics[0])
    assert diagnostic["quote_sha256"] == sha256(malformation.encode()).hexdigest()
    assert malformation not in json.dumps(diagnostic)


def test_nonadjacent_cells_must_be_separate_evidence_items(chunks):
    chunk = next(c for c in chunks if c.section_id == "EC-BENEFICIARY")
    _, sources = build_context("Explain a code", (RetrievalHit(chunk, 1, 1),))
    joined = "Name mismatch Compare submitted name with verified beneficiary record"
    with pytest.raises(GenerationError) as error:
        validate_answer(payload(joined), sources)
    assert error.value.diagnostic.category == "quote_not_found"
    valid = json.loads(payload("Name mismatch"))
    valid["statements"][0]["evidence"].append(dict(source_id="S1", quote="Compare submitted name with verified beneficiary record"))
    assert len(validate_answer(json.dumps(valid), sources)[2][0].passages) == 2


def test_exact_quote_cannot_be_reassigned_to_another_source(chunks):
    catalog = next(c for c in chunks if c.section_id == "EC-BENEFICIARY")
    runbook = next(c for c in chunks if c.section_id == "AR-NEXT")
    _, sources = build_context("q", (RetrievalHit(catalog, 1, 1), RetrievalHit(runbook, 1, 2)))
    with pytest.raises(GenerationError) as error:
        validate_answer(payload("Compare submitted name with verified beneficiary record", "S2"), sources)
    assert error.value.diagnostic.category == "quote_in_different_source"
    assert error.value.diagnostic.matching_source_ids == ("S1",)
    with pytest.raises(GenerationError) as error:
        validate_answer(payload("Name mismatch", "S99"), sources)
    assert error.value.diagnostic.category == "unknown_source_id"


def test_case_evidence_gap_can_be_explicitly_bounded_without_inventing_checklist(chunks):
    correction = next(c for c in chunks if c.section_id == "BV-CORRECT")
    _, sources = build_context("What correction and case records are needed?", (RetrievalHit(correction, 1, 1),))
    quote = next(line for line in correction.content.splitlines() if line.startswith("1. "))
    output = json.loads(payload(quote, status="limited_answer"))
    output["statements"][0]["text"] = "Correction guidance only: link the original instruction and case, retaining original field values. The common case-record checklist is unavailable in the retrieved context; this does not establish complete case requirements or authorize retry."
    status, text, citations = validate_answer(json.dumps(output), sources)
    assert status == "limited_answer" and "common case-record checklist is unavailable" in text
    assert len(citations) == 1 and citations[0].section_id == "BV-CORRECT"
    assert "Check EACH part of a multi-part request" in SYSTEM_PROMPT
    assert "NEVER rewrite evidence[].quote" in SYSTEM_PROMPT
    # Semantic scope remains a human-review question, not proven by this validator.


def test_saved_artifacts_are_preserved():
    manifest = json.loads(Path("evaluation/week2/reliability_artifacts_manifest.json").read_text())
    for name, digest in manifest["files_sha256"].items():
        path = Path(name)
        if path.exists():  # Ignored run artifacts can be absent in a clean checkout.
            assert sha256(path.read_bytes()).hexdigest() == digest


def test_development_report_and_saved_runs_cannot_be_overwritten(monkeypatch):
    from payment_ops.knowledge.evaluate_answers import main
    monkeypatch.setattr(sys, "argv", ["evaluation", "--report", "docs/WEEK2_ANSWER_DEVELOPMENT_COMPARISON.md"])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2


def test_temporal_gate_is_not_counted_as_model_path_latency():
    row = dict(classification="unsupported", status="insufficient_evidence", reason_code="policy_period_unsupported",
               elapsed_seconds=8, citation_checks=dict(citation_count=0, valid_citation_count=0,
               passage_count=0, verified_passage_count=0, all_claim_candidates_cited=None))
    summary = summarize([row])
    assert summary["disposition_by_class"]["unsupported"]["correct_dispositions"] == 1
    assert summary["latency"]["p95_seconds"] == 8
    assert summary["latency"]["model_path_count"] == 0
    assert summary["latency"]["model_path_p95_seconds"] is None
