"""Scripted recovery and checklist contracts, not live-model quality evidence."""

from dataclasses import asdict, replace
from datetime import date
from hashlib import sha256
import json
from pathlib import Path

import pytest

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.generation import GenerationDiagnostic, GenerationError
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import RetrievalHit
from payment_ops.knowledge.service import KnowledgeService, QUOTE_RETRY_INSTRUCTION


@pytest.fixture
def chunks():
    return chunk_documents(load_documents(Path("data/knowledge/documents")))


class Provider:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = []

    def generate(self, system, context):
        self.calls.append((system, context))
        output = next(self.outputs)
        if isinstance(output, Exception):
            raise output
        return output


class Retriever:
    def __init__(self, chunks):
        self.hits = tuple(RetrievalHit(c, .8, i) for i, c in enumerate(chunks, 1))
        self.calls = []

    def retrieve(self, question, k=5):
        self.calls.append((question, k))
        return self.hits[:k]


def response(quote="Name mismatch", source="S1", **changes):
    output = dict(status="answered", statements=[dict(text="A simulated supported claim.",
                  evidence=[dict(source_id=source, quote=quote)])], clarification_question=None, required_sections=[])
    output.update(changes)
    return json.dumps(output)


def setup_service(chunks, outputs, sections=("EC-BENEFICIARY",), *, catalog=False):
    seeds = tuple(next(c for c in chunks if c.section_id == section) for section in sections)
    provider, retriever = Provider(outputs), Retriever(seeds)
    assistant = KnowledgeService({"dense": retriever}, provider, section_catalog=chunks if catalog else (),
                                 as_of_date=date(2026, 10, 28))
    return assistant, provider, retriever


def test_unmatched_quote_gets_one_fresh_fully_validated_attempt(chunks):
    bad = "Fabricated code meaning and invented policy"
    assistant, provider, retriever = setup_service(chunks, [response(bad), response()])
    answer = assistant.ask("Explain the documented code")
    assert answer.status == "answered"
    assert [d.category for d in answer.diagnostics] == ["quote_not_found", "quote_retry_validated"]
    assert len(provider.calls) == 2 and len(retriever.calls) == 1
    assert provider.calls[0][1] == provider.calls[1][1]
    assert provider.calls[1][0].endswith(QUOTE_RETRY_INSTRUCTION)
    assert bad not in provider.calls[1][0] and bad not in provider.calls[1][1]
    assert bad not in json.dumps([asdict(d) for d in answer.diagnostics])
    assert answer.citations[0].evidence_quote == "Name mismatch"


def test_two_unmatched_quotes_stop_without_returning_partial_claims(chunks):
    assistant, provider, _ = setup_service(chunks, [response("Invented excerpt"), response("Another fabricated excerpt")])
    answer = assistant.ask("Explain the documented code")
    assert answer.reason_code == "invalid_response" and not answer.citations
    assert len(provider.calls) == 2
    assert [d.category for d in answer.diagnostics] == ["quote_not_found", "quote_not_found"]


@pytest.mark.parametrize("output,category", [
    ("not json", "invalid_json"),
    (response(source="S99"), "unknown_source_id"),
    (response(quote=""), "empty_or_invalid_quote"),
    (response(required_sections=None), "invalid_required_sections"),
])
def test_other_validation_errors_do_not_retry(chunks, output, category):
    assistant, provider, _ = setup_service(chunks, [output])
    answer = assistant.ask("Explain the documented code")
    assert answer.reason_code == "invalid_response" and answer.diagnostics[0].category == category
    assert len(provider.calls) == 1


def test_wrong_source_does_not_retry_or_substitute(chunks):
    assistant, provider, _ = setup_service(chunks, [response(source="S2")], ("EC-BENEFICIARY", "AR-NEXT"))
    answer = assistant.ask("Explain the documented code")
    assert answer.diagnostics[0].category == "quote_in_different_source"
    assert not answer.citations and len(provider.calls) == 1


@pytest.mark.parametrize("second", ["malformed", "abstain", "provider_error"])
def test_recovery_cannot_bypass_second_attempt_validation_or_errors(chunks, second):
    outputs = {
        "malformed": "not json",
        "abstain": response(status="insufficient_evidence", statements=[]),
        "provider_error": GenerationError("sensitive message", diagnostic=GenerationDiagnostic("provider_communication", "timeout")),
    }
    assistant, provider, _ = setup_service(chunks, [response("Invented"), outputs[second]])
    answer = assistant.ask("Explain the documented code")
    assert len(provider.calls) == 2 and not answer.citations
    assert answer.diagnostics[0].category == "quote_not_found"
    assert answer.status != "answered" and "sensitive" not in str(answer)


def test_q07_recovery_keeps_duplicate_stop_evidence(chunks):
    ss = next(c for c in chunks if c.section_id == "SS-DELAY")
    valid = json.loads(response(ss.content))
    valid["statements"][0]["text"] = "Do not resend while status or duplicate risk remains unresolved."
    assistant, provider, retriever = setup_service(chunks, [response("A made-up procedure"), json.dumps(valid)],
        ("SS-DELAY", "EC-STATUS", "EX-ESCALATE", "SS-ESCALATE", "WR-ESCALATE"), catalog=True)
    answer = assistant.ask("A status update is delayed and the analyst wants to resend. What checks and escalation apply?")
    assert answer.status == "answered" and "Do not resend" in answer.answer
    assert len(retriever.calls) == 1 and len(provider.calls) == 2
    assert "EX-DUPLICATE" in {s["section_id"] for s in json.loads(provider.calls[1][1])["sources"]}


@pytest.mark.parametrize("question", [
    "An ACH return cites invalid account details. What correction and case evidence are needed?",
    "List the complete case-record requirements for an ACH exception.",
    "Which evidence for a case must we retain?",
])
def test_incomplete_model_summary_gets_all_actual_sop_fields_and_warning(chunks, question):
    # The model provides only a narrow correction claim, omitting the whole common
    # checklist, reproducing the live completeness weakness without a real API.
    assistant, provider, _ = setup_service(chunks, [response("No immediate retry")],
        ("EC-ACH", "AR-NEXT", "AR-SCOPE", "AR-CLASSIFY", "SS-RETURNS"), catalog=True)
    answer = assistant.ask(question)
    assert answer.status == "answered" and len(provider.calls) == 1
    section = next(c for c in chunks if c.section_id == "EX-EVIDENCE")
    rows = [line for line in section.content.splitlines() if line.startswith("| ")][2:]
    assert len(rows) == 8
    for row in rows:
        assert row in answer.answer
    assert "Do not invent missing values" in answer.answer and "not populated case values" in answer.answer
    citation = next(c for c in answer.citations if c.section_id == "EX-EVIDENCE")
    assert len(citation.passages) == 2
    for p in citation.passages:
        assert section.content[p.start:p.end] == p.quote
        assert p.source_id == "S7"


@pytest.mark.parametrize("mode", ["missing", "malformed"])
def test_unavailable_checklist_never_claims_complete_case_requirements(chunks, mode):
    if mode == "malformed":
        chunks = tuple(replace(c, content="No usable case-field table is supplied.") if c.section_id == "EX-EVIDENCE" else c for c in chunks)
    else:
        chunks = tuple(c for c in chunks if c.section_id != "EX-EVIDENCE")
    assistant, _, _ = setup_service(chunks, [response("No immediate retry")], ("EC-ACH",), catalog=True)
    answer = assistant.ask("What case evidence is required?")
    assert answer.status == "limited_answer"
    assert "complete common case-evidence checklist is unavailable" in answer.answer
    assert not any(c.section_id == "EX-EVIDENCE" for c in answer.citations)


def test_unsupported_code_guidance_is_prose_with_unchanged_source_quote(chunks):
    assistant, provider, _ = setup_service(chunks, [], ("EC-ACH",), catalog=True)
    answer = assistant.ask("What does SYN-ACH-299 mean?")
    assert answer.status == "insufficient_evidence" and provider.calls == []
    assert "Documented escalation guidance: For an undocumented identifier" in answer.answer
    assert "\n4." not in answer.answer
    assert "SYN-ACH-299" in answer.answer
    assert answer.citations[0].evidence_quote.startswith("4. ")


def test_task15b_reference_artifacts_are_unchanged():
    manifest = json.loads(Path("evaluation/week2/task15b_reference_manifest.json").read_text())
    for name, digest in manifest["files_sha256"].items():
        if Path(name).exists():
            assert sha256(Path(name).read_bytes()).hexdigest() == digest
