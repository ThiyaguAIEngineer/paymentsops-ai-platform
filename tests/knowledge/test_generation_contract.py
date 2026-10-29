"""grounded-v3 schema, scope and clarification regressions; no live API calls."""

import json
from pathlib import Path

import pytest

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import RetrievalHit
from payment_ops.knowledge.service import DISCLOSURE, SYSTEM_PROMPT, KnowledgeService


@pytest.fixture
def corpus():
    return chunk_documents(load_documents(Path(__file__).resolve().parents[2] / "data/knowledge/documents"))


class Provider:
    def __init__(self, payload):
        self.payload, self.calls = json.dumps(payload), []
    def generate(self, system, user):
        self.calls.append((system, json.loads(user)))
        return self.payload


class Retriever:
    def __init__(self, chunks):
        self.calls = []
        self.hits = tuple(RetrievalHit(c, .5, i) for i, c in enumerate(chunks, 1))
    def retrieve(self, query, k=5):
        self.calls.append((query, k))
        return self.hits[:k]


def make(corpus, sections, *, quote="ACCEPTED does not mean SETTLED.", text="Acceptance does not establish settlement.", status="answered"):
    chunks = tuple(next(c for c in corpus if c.section_id == section and quote in c.content)
                   if i == 0 else next(c for c in corpus if c.section_id == section)
                   for i, section in enumerate(sections))
    payload = {"status": status, "statements": [{"text": text, "evidence": [{"source_id":"S1", "quote":quote}]}],
               "clarification_question":None, "required_sections":[]}
    provider, retriever = Provider(payload), Retriever(chunks)
    return KnowledgeService({"dense":retriever}, provider), provider, retriever, payload


@pytest.mark.parametrize("required,value_type,item_index", [
    (None,"null",None), ({},"object",None), ("SYN-STATUS/SS-STATES","string",None),
    ([{"document_id":"SYN-STATUS","section_id":"SS-STATES"}],"object",1),
    (["SS-STATES"],"string",1), (["S1"],"string",1), ([False],"boolean",1),
])
def test_factual_required_sections_shape_is_strict_and_diagnostic(corpus, required, value_type, item_index):
    service, provider, _, payload = make(corpus, ["SS-STATES"])
    payload["required_sections"] = required
    provider.payload = json.dumps(payload)
    answer = service.ask("Does ACCEPTED mean a payment has settled?")
    assert answer.reason_code == "invalid_response"
    diagnostic = answer.diagnostics[0]
    assert diagnostic.stage == "schema_validation" and diagnostic.category == "invalid_required_sections"
    assert diagnostic.field_name == "required_sections"
    assert diagnostic.value_type == value_type and diagnostic.item_index == item_index
    assert not answer.citations


def test_required_sections_is_not_silently_defaulted(corpus):
    service, provider, _, payload = make(corpus, ["SS-STATES"])
    del payload["required_sections"]
    provider.payload = json.dumps(payload)
    answer = service.ask("Does ACCEPTED mean a payment has settled?")
    assert answer.diagnostics[0].category == "missing_required_field"
    assert answer.diagnostics[0].field_name == "required_sections"


@pytest.mark.parametrize("required", [[], ["SYN-STATUS/SS-STATES"]])
def test_factual_valid_schema_and_explicit_reference(corpus, required):
    service, provider, _, payload = make(corpus, ["SS-STATES"])
    payload["required_sections"] = required
    provider.payload = json.dumps(payload)
    answer = service.ask("Does ACCEPTED mean a payment has settled?")
    assert answer.status == "answered"
    assert provider.calls[0][1]["sources"][0]["section_reference"] == "SYN-STATUS/SS-STATES"
    assert "array of\nstrings, NEVER null" in SYSTEM_PROMPT


def test_wire_starting_guidance_does_not_require_later_closure(corpus):
    quote = "Create or link one recall case and preserve the original instruction unchanged."
    service, provider, _, payload = make(corpus, ["WR-REQUEST","WR-SCOPE","WR-ELIGIBILITY","WR-ESCALATE","EC-WIRE"],
        quote=quote, status="limited_answer", text="For initial case preparation only, create or link one recall case and preserve the original instruction. This does not establish follow-up or closure steps.")
    payload["required_sections"] = ["SYN-WIRE-RECALL/WR-REQUEST"]
    provider.payload = json.dumps(payload)
    answer = service.ask("We already sent the wire and want to get the money back. Where do we start?")
    assert answer.status == "limited_answer" and answer.reason_code == "limited_answer"
    assert "not a complete end-to-end procedure" in answer.answer and DISCLOSURE in answer.answer
    assert "SYN-EXCEPTION/EX-CLOSE" in provider.calls[0][1]["unretrieved_section_references"]
    assert "SYN-WIRE-RECALL/WR-TRACK" in provider.calls[0][1]["unretrieved_section_references"]
    assert answer.citations[0].section_id == "WR-REQUEST"


def test_true_essential_missing_evidence_still_blocks_limited_answer(corpus):
    quote = "Create or link one recall case and preserve the original instruction unchanged."
    service, provider, _, payload = make(corpus, ["WR-REQUEST"], quote=quote, status="limited_answer")
    payload["required_sections"] = ["SYN-EXCEPTION/EX-EVIDENCE"]
    provider.payload = json.dumps(payload)
    answer = service.ask("List the full case evidence needed for recall preparation.")
    assert answer.reason_code == "incomplete_evidence" and not answer.citations


@pytest.mark.parametrize("question", [
    "How do I reverse this payment?", "Can I undo that transfer?", "Please cancel my wire.",
    "How can we recover our transfer?", "Can I return the ACH entry?", "Should I retry this failed payment?",
    "What is the process to reverse this payment?", "Can I recall my payment?",
    "How can I reverse my released payment? It could be wire or ACH.",
    "Can I recall my wire? Its status could be accepted or settled.",
])
def test_transaction_action_requires_context_before_procedure(corpus, question):
    service, provider, retriever, _ = make(corpus, ["SS-STATES"])
    answer = service.ask(question)
    assert answer.status == "clarification" and answer.reason_code == "missing_transaction_context"
    assert not provider.calls and not retriever.calls and not answer.citations
    assert DISCLOSURE in answer.answer


@pytest.mark.parametrize("question", [
    "What is the difference between cancellation and recall?",
    "How do recall and cancellation differ for a payment?",
    "How do I recall my settled wire?",
    "How do I cancel my accepted wire?",
])
def test_conceptual_or_contextual_questions_are_not_blanket_clarified(corpus, question):
    service, provider, retriever, _ = make(corpus, ["SS-STATES"])
    service.ask(question)
    assert len(provider.calls) == len(retriever.calls) == 1
    assert retriever.calls[0][1] == 5


def test_delayed_status_limited_guidance_preserves_no_resend_and_source_boundary(corpus):
    quote = "Hold retry preparation while status or duplicate risk is unresolved"
    service, provider, _, payload = make(corpus, ["SS-DELAY","EX-ESCALATE"], quote=quote, status="limited_answer",
        text="For immediate handling only, hold retry preparation while status or duplicate risk is unresolved. The detailed linked duplicate-investigation procedure is not supplied here.")
    payload["required_sections"] = ["SYN-STATUS/SS-DELAY"]
    payload["statements"].append({"text":"For handoff, Reconciliation owns delayed or conflicting settlement evidence, with the relevant rail owner.",
        "evidence":[{"source_id":"S2","quote":"Delayed or conflicting settlement evidence | Reconciliation | Relevant rail owner"}]})
    provider.payload = json.dumps(payload)
    answer = service.ask("A status update is delayed and the analyst wants to resend. What checks and escalation apply?")
    assert answer.status == "limited_answer" and answer.citations[0].section_id == "SS-DELAY"
    context = provider.calls[0][1]
    assert "SYN-EXCEPTION/EX-DUPLICATE" in context["unretrieved_section_references"]
    assert all(s["section_id"] != "EX-DUPLICATE" for s in context["sources"])
    assert "do\nnot recommend resending" in SYSTEM_PROMPT
    # Declaring no dependencies is not a certificate of completeness: a forged
    # quote or source is still rejected even with required_sections=[].
    payload["required_sections"] = []
    payload["statements"][0]["evidence"][0]["quote"] = "Unverified duplicate procedure steps"
    provider.payload = json.dumps(payload)
    assert service.ask("What checks apply to a delayed status?").reason_code == "invalid_response"


def test_required_sections_is_not_a_grounding_bypass(corpus):
    service, provider, _, payload = make(corpus, ["SS-STATES"])
    payload["required_sections"] = ["SYN-STATUS/SS-STATES"]
    payload["statements"][0]["evidence"][0]["source_id"] = "S999"
    provider.payload = json.dumps(payload)
    answer = service.ask("Does ACCEPTED mean settled?")
    assert answer.diagnostics[0].category == "unknown_source_id"
