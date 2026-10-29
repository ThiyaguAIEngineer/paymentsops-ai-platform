"""Task 15 offline regressions; scripted output does not establish live coverage."""

from dataclasses import replace
from datetime import date
from hashlib import sha256
import json
from pathlib import Path

import pytest

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import RetrievalHit, include_requested_section
from payment_ops.knowledge.service import KnowledgeService, unknown_code_identifiers


@pytest.fixture
def chunks():
    return chunk_documents(load_documents(Path("data/knowledge/documents")))


class Retriever:
    def __init__(self, chunks):
        self.hits = tuple(RetrievalHit(c, .8, i) for i, c in enumerate(chunks, 1))
        self.calls = []

    def retrieve(self, query, k=5):
        self.calls.append((query, k))
        return self.hits[:k]


class Provider:
    def __init__(self, callback=None):
        self.calls = []
        self.callback = callback

    def generate(self, system, context):
        data = json.loads(context)
        self.calls.append(data)
        if self.callback:
            return self.callback(data)
        pytest.fail("Unknown codes and guard clarifications must not reach generation")


def service(chunks, seeds, provider):
    retriever = Retriever(tuple(c for section in seeds for c in chunks if c.section_id == section))
    return KnowledgeService({"dense": retriever}, provider, section_catalog=chunks,
                            as_of_date=date(2026, 10, 28)), retriever


@pytest.mark.parametrize("question,identifier", [
    ("What does SYN-ACH-299 mean?", "SYN-ACH-299"),
    ("Explain SYN-BEN-999", "SYN-BEN-999"),
    ("Tell me about syn-wr-987", "syn-wr-987"),
])
def test_unknown_identifier_abstains_preserves_text_and_cites_only_real_guidance(chunks, question, identifier):
    provider = Provider()
    assistant, retriever = service(chunks, ("EC-ACH", "EC-LOOKUP"), provider)
    answer = assistant.ask(question)
    assert answer.status == "insufficient_evidence" and answer.reason_code == "insufficient_evidence"
    assert identifier in answer.answer and "meaning" in answer.answer and "cannot be established" in answer.answer
    assert "route to the relevant operations owner" in answer.answer
    assert "Do not guess" in answer.answer
    assert provider.calls == [] and retriever.calls[0][1] == 5
    assert {c.section_id for c in answer.citations} == {"EC-LOOKUP"}
    by_id = {c.chunk_id: c for c in chunks}
    for citation in answer.citations:
        for passage in citation.passages:
            assert by_id[passage.chunk_id].content[passage.start:passage.end] == passage.quote


@pytest.mark.parametrize("code,section", [("SYN-ACH-201", "EC-ACH"), ("SYN-ACH-202", "EC-ACH"), ("SYN-BEN-301", "EC-BENEFICIARY")])
def test_documented_codes_keep_normal_generation(chunks, code, section):
    def generate(data):
        source = next(s for s in data["sources"] if s["section_id"] == section)
        row = next(line for line in source["text"].splitlines() if line.startswith(f"| {code} |"))
        return json.dumps(dict(status="answered", clarification_question=None, required_sections=[],
                              statements=[dict(text=row, evidence=[dict(source_id=source["source_id"], quote=row)])]))
    provider = Provider(generate)
    assistant, _ = service(chunks, (section,), provider)
    answer = assistant.ask(f"What does {code} mean?")
    assert answer.status == "answered" and len(provider.calls) == 1
    assert answer.citations[0].section_id == section
    if code == "SYN-ACH-201":
        assert "No immediate retry" in answer.answer


def test_prose_mention_is_not_a_catalog_definition(chunks):
    poisoned = tuple(replace(c, content=c.content + "\nExample unknown SYN-ACH-299.") for c in chunks)
    assert unknown_code_identifiers("Explain SYN-ACH-299", poisoned) == ("SYN-ACH-299",)
    assert unknown_code_identifiers("Explain SYN-ACH-201", chunks) == ()
    assert unknown_code_identifiers("Explain SYN-ACH-299", ()) == ()


def test_invalid_guidance_is_rejected_instead_of_bypassing_validation(chunks):
    changed = tuple(replace(c, content="4. For an undocumented identifier, do not guess [1].")
                    if c.section_id == "EC-LOOKUP" else c for c in chunks)
    assistant, _ = service(changed, ("EC-LOOKUP",), Provider())
    answer = assistant.ask("Explain SYN-WR-987")
    assert answer.status == "insufficient_evidence" and answer.reason_code == "invalid_response"
    assert not answer.citations
    assert answer.diagnostics[0].category == "invalid_statement_text"


@pytest.mark.parametrize("question", [
    "An ACH return cites invalid account details. What correction and case evidence are needed?",
    "Which fields are required in the case record for a returned ACH entry?",
    "What evidence for a case should I preserve during ACH correction?",
])
def test_case_evidence_lookup_and_all_required_field_quotes(chunks, question):
    def generate(data):
        sources = {s["section_id"]: s for s in data["sources"]}
        assert "BV-CORRECT" in sources and "EX-EVIDENCE" in sources
        assert sources["EX-EVIDENCE"]["retrieval_origin"] == "requested_section"
        assert sources["EX-EVIDENCE"]["linked_from_chunk_id"] is None
        rows = [line for line in sources["EX-EVIDENCE"]["text"].splitlines() if line.startswith("| ")][2:]
        correction = sources["BV-CORRECT"]
        statements = [dict(text="Verified correction records and independent review are required.",
                           evidence=[dict(source_id=correction["source_id"], quote=correction["text"])])]
        statements.extend(dict(text=row, evidence=[dict(source_id=sources["EX-EVIDENCE"]["source_id"], quote=row)]) for row in rows)
        return json.dumps(dict(status="answered", clarification_question=None, required_sections=[], statements=statements))
    provider = Provider(generate)
    seeds = ("EC-ACH", "AR-NEXT", "AR-SCOPE", "AR-CLASSIFY", "SS-RETURNS")
    assistant, retriever = service(chunks, seeds, provider)
    answer = assistant.ask(question)
    assert answer.status == "answered" and retriever.calls[0][1] == 5
    assert len(answer.retrieved_chunk_ids) == 7
    assert {c.section_id for c in answer.citations} == {"BV-CORRECT", "EX-EVIDENCE"}
    for field in ("Identity", "Instruction context", "Observed condition", "Evidence provenance",
                  "Request context", "Work performed", "Ownership", "Follow-up"):
        assert field in answer.answer


def test_general_correction_does_not_always_expand_case_record(chunks):
    provider = Provider(lambda data: json.dumps(dict(status="insufficient_evidence", statements=[], clarification_question=None, required_sections=[])))
    assistant, _ = service(chunks, ("AR-NEXT",), provider)
    answer = assistant.ask("Explain verified correction")
    assert not any(c.section_id == "EX-EVIDENCE" for c in chunks if c.chunk_id in answer.retrieved_chunk_ids)


def test_missing_or_multichunk_requested_section_is_not_invented(chunks):
    target = next(c for c in chunks if c.section_id == "EX-EVIDENCE")
    assert include_requested_section((), (), "SYN-EXCEPTION/EX-EVIDENCE") == ()
    duplicate = replace(target, chunk_id="test-copy", chunk_index=1)
    assert include_requested_section((), (target, duplicate), "SYN-EXCEPTION/EX-EVIDENCE") == ()
    hits = include_requested_section((), (target,), "SYN-EXCEPTION/EX-EVIDENCE")
    assert include_requested_section(hits, (target,), "SYN-EXCEPTION/EX-EVIDENCE") == hits


@pytest.mark.parametrize("question", ["How do I reverse this payment?", "It failed. Should I retry?"])
def test_q09_q10_clarification_still_precedes_retrieval(chunks, question):
    provider = Provider()
    assistant, retriever = service(chunks, ("EC-ACH",), provider)
    assert assistant.ask(question).reason_code == "missing_transaction_context"
    assert retriever.calls == [] and provider.calls == []


def test_q07_duplicate_stop_rule_is_preserved_in_context(chunks):
    def generate(data):
        source = next(s for s in data["sources"] if s["section_id"] == "SS-DELAY")
        quote = source["text"]
        return json.dumps(dict(status="answered", statements=[dict(text="Do not resend while payment status or duplicate risk remains unresolved.",
                         evidence=[dict(source_id=source["source_id"], quote=quote)])], clarification_question=None, required_sections=[]))
    provider = Provider(generate)
    assistant, _ = service(chunks, ("SS-DELAY", "EC-STATUS", "EX-ESCALATE", "SS-ESCALATE", "WR-ESCALATE"), provider)
    answer = assistant.ask("A status update is delayed and the analyst wants to resend. What checks and escalation apply?")
    assert answer.status == "answered" and "Do not resend" in answer.answer
    assert "EX-DUPLICATE" in {s["section_id"] for s in provider.calls[0]["sources"]}


def test_task15_reference_run_unchanged():
    manifest = json.loads(Path("evaluation/week2/task15_reference_manifest.json").read_text())
    for path, digest in manifest["files_sha256"].items():
        if Path(path).exists():
            assert sha256(Path(path).read_bytes()).hexdigest() == digest
