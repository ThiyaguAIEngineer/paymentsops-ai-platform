"""Simulated failure categories, NOT captured live failures or live confirmations."""

from dataclasses import asdict, replace
from hashlib import sha256
import json
from pathlib import Path
import sys

import httpx
import pytest

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.generation import GenerationDiagnostic, GenerationError, NebiusGenerationProvider
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import RetrievalHit
from payment_ops.knowledge.service import DISCLOSURE, KnowledgeService, build_context, locate_quote


@pytest.fixture
def corpus():
    return chunk_documents(load_documents(Path(__file__).resolve().parents[2] / "data/knowledge/documents"))


class Provider:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def generate(self, system, user):
        self.calls.append((system, user))
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class Retriever:
    def __init__(self, chunks):
        self.hits = tuple(RetrievalHit(c, .9, i) for i, c in enumerate(chunks, 1))

    def retrieve(self, query, k=5):
        return self.hits[:k]


def run(chunks, payload, query="What does SYN-BEN-301 mean, and what should I do first?"):
    provider = Provider(payload)
    service = KnowledgeService({"dense": Retriever(chunks)}, provider)
    return service.ask(query), provider


def answered(quote, source_id="S1", *, required=None):
    payload = {"status": "answered", "statements": [{"text": "A supported claim.",
               "evidence": [{"source_id": source_id, "quote": quote}]}], "clarification_question": None, "required_sections": []}
    if required is not None:
        payload["required_sections"] = required
    return payload


def select(corpus, section):
    return next(c for c in corpus if c.section_id == section)


@pytest.mark.parametrize("raw,stage,category", [
    ('```json\n{}\n```', "parsing", "invalid_json"),
    ('{"status":"answered","status":"clarification"}', "parsing", "duplicate_json_field"),
    ('{}', "schema_validation", "missing_required_field"),
    (json.dumps({"status":"answered","statements":[],"clarification_question":None,"required_sections":[]}), "schema_validation", "invalid_status_combination"),
])
def test_parsing_and_schema_categories_not_hidden(corpus, raw, stage, category):
    answer, _ = run((select(corpus, "EC-BENEFICIARY"),), raw)
    assert answer.reason_code == "invalid_response"
    assert (answer.diagnostics[0].stage, answer.diagnostics[0].category) == (stage, category)
    assert not answer.citations and DISCLOSURE in answer.answer


def test_syn_ben_301_simulated_table_quote_failure_is_identifiable(corpus):
    # This paraphrase is not a verbatim table passage. It represents a possible
    # failure category; the original live payload is not available to this test.
    bad_quote = "SYN-BEN-301 means a beneficiary name mismatch"
    answer, _ = run((select(corpus, "EC-BENEFICIARY"),), json.dumps(answered(bad_quote)))
    diagnostic = answer.diagnostics[0]
    assert diagnostic.stage == "grounding_validation" and diagnostic.category == "quote_not_found"
    assert diagnostic.statement_index == diagnostic.evidence_index == 1
    assert diagnostic.source_id == "S1"
    assert diagnostic.quote_characters == len(bad_quote)
    assert diagnostic.quote_sha256 == sha256(bad_quote.encode()).hexdigest()
    assert bad_quote not in answer.answer and bad_quote not in json.dumps(asdict(diagnostic))


def test_wrong_source_quote_reported_but_never_silently_remapped(corpus):
    chunks = (select(corpus, "EC-BENEFICIARY"), select(corpus, "SS-DELAY"))
    answer, _ = run(chunks, json.dumps(answered("Name mismatch", source_id="S2")))
    assert answer.reason_code == "invalid_response"
    assert answer.diagnostics[0].category == "quote_in_different_source"
    assert answer.diagnostics[0].matching_source_ids == ("S1",)
    assert not answer.citations


def test_unknown_source_id_not_echoed(corpus):
    answer, _ = run((select(corpus, "EC-BENEFICIARY"),), json.dumps(answered("Name mismatch", "secret-looking-model-text")))
    assert answer.diagnostics[0].category == "unknown_source_id"
    assert "secret-looking-model-text" not in json.dumps(asdict(answer.diagnostics[0]))


def test_table_quote_passage_is_located_exactly(corpus):
    chunk = select(corpus, "EC-BENEFICIARY")
    quote = "SYN-BEN-301 | Name mismatch"
    answer, _ = run((chunk,), json.dumps(answered(quote)))
    assert answer.status == "answered"
    passage = answer.citations[0].passages[0]
    assert chunk.content[passage.start:passage.end] == passage.quote == quote
    assert passage.chunk_id == chunk.chunk_id


def test_whitespace_only_quote_matching_retains_original_offsets():
    text = "Prefix: Hold retry\n  preparation while status is uncertain."
    span = locate_quote("Hold retry preparation", text)
    assert span is not None
    assert text[span[0]:span[1]] == "Hold retry\n  preparation"
    assert locate_quote("hold retry preparation", text) is None
    assert locate_quote("Hold retry ... preparation", text) is None


def test_citations_share_section_number_but_preserve_every_passage(corpus):
    chunk = select(corpus, "EC-BENEFICIARY")
    payload = answered("Name mismatch")
    payload["statements"].append({"text": "A further supported claim.", "evidence": [
        {"source_id":"S1","quote":"Compare submitted name with verified beneficiary record"}]})
    answer, _ = run((chunk,), json.dumps(payload))
    assert len(answer.citations) == 1 and len(answer.citations[0].passages) == 2
    assert answer.answer.count("[1]") == 2 and "[2]" not in answer.answer
    for passage in answer.citations[0].passages:
        assert chunk.content[passage.start:passage.end] == passage.quote


def test_same_section_different_retrieved_chunks_keep_both_passages(corpus):
    base = select(corpus, "EC-BENEFICIARY")
    # Synthetic test-only split section; no source document is changed.
    first = replace(base, chunk_id="fixture-a", content="First exact passage.")
    second = replace(base, chunk_id="fixture-b", content="Second exact passage.")
    payload = answered("First exact passage.")
    payload["statements"][0]["evidence"].append({"source_id":"S2","quote":"Second exact passage."})
    answer, _ = run((first, second), json.dumps(payload))
    assert len(answer.citations) == 1
    assert {p.chunk_id for p in answer.citations[0].passages} == {"fixture-a", "fixture-b"}


@pytest.mark.parametrize("status", ["answered", "insufficient_evidence"])
def test_delayed_status_incomplete_evidence_is_not_malformed_generation(corpus, status):
    # Recorded Dense baseline's five sections; EX-DUPLICATE is absent.
    chunks = tuple(select(corpus, s) for s in ("SS-DELAY", "EC-STATUS", "WR-ESCALATE", "EX-ESCALATE", "SS-ESCALATE"))
    payload = answered("Hold retry preparation while status or duplicate risk is unresolved", required=["SYN-EXCEPTION/EX-DUPLICATE"])
    if status == "insufficient_evidence":
        payload.update(status=status, statements=[])
    answer, provider = run(chunks, json.dumps(payload), "A status update is delayed and the analyst wants to resend. What checks and escalation apply?")
    assert answer.status == "insufficient_evidence" and answer.reason_code == "incomplete_evidence"
    diagnostic = answer.diagnostics[0]
    assert diagnostic.stage == "evidence_sufficiency" and diagnostic.category == "incomplete_retrieval_evidence"
    assert diagnostic.missing_sections == ("SYN-EXCEPTION/EX-DUPLICATE",)
    assert "complete answer cannot be provided" in answer.answer
    context = json.loads(provider.calls[0][1])
    assert "SYN-EXCEPTION/EX-DUPLICATE" in context["unretrieved_section_references"]
    assert not any(s["section_id"] == "EX-DUPLICATE" for s in context["sources"])
    assert not answer.citations


def test_missing_cross_reference_is_not_a_blanket_abstention_rule(corpus):
    chunk = select(corpus, "EC-BENEFICIARY")
    answer, provider = run((chunk,), json.dumps(answered("Name mismatch")))
    assert "SYN-BENEFICIARY/BV-NAME" in json.loads(provider.calls[0][1])["unretrieved_section_references"]
    assert answer.status == "answered"  # Narrow catalog question can be sufficient.


def test_incomplete_context_does_not_hide_malformed_statements(corpus):
    payload = answered("unused", required=["SYN-EXCEPTION/EX-DUPLICATE"])
    payload["statements"] = [{"wrong":"fields"}]
    answer, _ = run((select(corpus, "SS-DELAY"),), json.dumps(payload))
    assert answer.reason_code == "invalid_response"
    assert answer.diagnostics[0].stage == "schema_validation"


def test_unsupported_and_ambiguous_statuses_remain_distinct(corpus):
    chunk = select(corpus, "SS-DELAY")
    abstain = {"status":"insufficient_evidence", "statements":[], "clarification_question":None,"required_sections":[]}
    answer, _ = run((chunk,), json.dumps(abstain))
    assert answer.diagnostics[0].category == "model_abstention"
    clarify = {"status":"clarification", "statements":[], "clarification_question":"Which rail and current status?","required_sections":[]}
    answer, _ = run((chunk,), json.dumps(clarify))
    assert answer.status == "clarification" and answer.reason_code == "clarification"


def test_provider_failure_diagnostic_is_distinct_and_sanitized(corpus):
    error = GenerationError("raw secret", diagnostic=GenerationDiagnostic("provider_communication", "timeout"))
    answer, _ = run((select(corpus, "SS-DELAY"),), error)
    assert answer.reason_code == "provider_failure" and answer.diagnostics[0].category == "timeout"
    assert "raw secret" not in answer.answer and "raw secret" not in str(answer.diagnostics)


@pytest.mark.parametrize("mode,category", [("auth", "authentication_failed"), ("timeout", "timeout"), ("truncated", "truncated_response")])
def test_provider_transport_categories(monkeypatch, mode, category):
    monkeypatch.setenv("NEBIUS_API_KEY", "offline-only")
    def handle(request):
        if mode == "timeout":
            raise httpx.ReadTimeout("sensitive transport text", request=request)
        if mode == "auth":
            return httpx.Response(401, text="sensitive body")
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data":[{"id":"fixture"}]})
        return httpx.Response(200, json={"choices":[{"finish_reason":"length","message":{"role":"assistant","content":"truncated"}}]})
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        provider = NebiusGenerationProvider(model="fixture", client=client)
        with pytest.raises(GenerationError) as error:
            provider.generate("system", "user")
        assert error.value.diagnostic.category == category
        assert "sensitive" not in str(error.value)


def test_cli_saves_allowlisted_diagnostics_for_all_six_scenarios(tmp_path, monkeypatch, capsys):
    import payment_ops.knowledge.inspect_generation as cli
    class OfflineInspectionProvider(Provider):
        model = "offline-fixture-not-live"
        chat_verified = False
        def verify_model(self): pass
        def close(self): pass
        def generate(self, system, user):
            self.chat_verified = True
            return super().generate(system, user)
    provider = OfflineInspectionProvider(json.dumps({"status":"insufficient_evidence","statements":[],"clarification_question":None,"required_sections":[]}))
    monkeypatch.setattr(cli, "create_generation_provider", lambda **kwargs: provider)
    path = tmp_path / "diagnostics.json"
    monkeypatch.setattr(sys, "argv", ["inspect", "--method", "bm25", "--diagnostics", "--diagnostics-json", str(path)])
    assert cli.main() == 0
    output = json.loads(path.read_text(encoding="utf-8"))
    assert len(output["scenarios"]) == 6
    assert "raw_response" not in path.read_text(encoding="utf-8")
    assert all("diagnostics" in row and "sources" in row for row in output["scenarios"])
