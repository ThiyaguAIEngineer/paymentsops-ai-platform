"""Generalized offline regressions; no model-quality claims from scripted answers."""

from dataclasses import replace
from datetime import date
import json
from pathlib import Path

import pytest

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.policy_period import PolicyPeriod, applicable_chunk, requested_policy_period
from payment_ops.knowledge.retrieval import RetrievalHit, follow_explicit_reference
from payment_ops.knowledge.service import KnowledgeService, clarification_needed, SYSTEM_PROMPT


@pytest.fixture
def chunks():
    return chunk_documents(load_documents(Path("data/knowledge/documents")))


class OriginalRetriever:
    """Only the original retrieve(query, k) contract; no optional capabilities."""

    def __init__(self, hits):
        self.hits = hits
        self.calls = []

    def retrieve(self, query, k=5):
        self.calls.append((query, k))
        return self.hits


class Provider:
    def __init__(self):
        self.calls = []

    def generate(self, system, context):
        self.calls.append(json.loads(context))
        return json.dumps(dict(status="insufficient_evidence", statements=[],
                               clarification_question=None, required_sections=[]))


def service_for(chunk, **kwargs):
    retriever = OriginalRetriever((RetrievalHit(chunk, .8, 1),))
    provider = Provider()
    return KnowledgeService({"dense": retriever}, provider, as_of_date=date(2026, 10, 28), **kwargs), retriever, provider


def test_original_retriever_contract_reaches_generation(chunks):
    service, retriever, provider = service_for(chunks[0])
    answer = service.ask("Explain this documented concept")
    assert answer.reason_code == "insufficient_evidence"
    assert retriever.calls == [("Explain this documented concept", 5)]
    assert len(provider.calls) == 1
    assert answer.reference_expansions == ()


def test_actual_retrieval_failure_stays_safe(chunks):
    class Broken:
        def retrieve(self, query, k=5):
            raise RuntimeError("sensitive exception text")
    answer = KnowledgeService({"dense": Broken()}, Provider()).ask("Explain a code")
    assert answer.status == "unavailable" and answer.reason_code == "retrieval_failure"
    assert answer.diagnostics[0].exception_type == "RuntimeError"
    assert "sensitive" not in str(answer)


@pytest.mark.parametrize("year", [1999, 2018, 2023, 2025])
def test_missing_historical_versions_never_reach_provider(chunks, year):
    service, _, provider = service_for(chunks[0], section_catalog=chunks)
    answer = service.ask(f"Which procedure applied in {year}?")
    assert answer.reason_code == "policy_period_unsupported"
    assert not answer.citations and not provider.calls


@pytest.mark.parametrize("question", ["Explain the current SOP", "Which procedure applies as of 2026-10-28?", "Explain procedure version 1.0.0"])
def test_supported_current_questions_reach_generation(chunks, question):
    service, _, provider = service_for(chunks[0], section_catalog=chunks)
    assert service.ask(question).reason_code == "insufficient_evidence"
    assert len(provider.calls) == 1


def test_known_historical_version_applicability(chunks):
    old = replace(chunks[0], effective_date=date(2020, 1, 1), document_version="0.9.0")
    catalog = (old, chunks[0])
    assert applicable_chunk(old, PolicyPeriod(date(2022, 1, 1), date(2022, 12, 31)), catalog, date(2026, 10, 28))
    assert not applicable_chunk(old, PolicyPeriod(date(2026, 10, 28), date(2026, 10, 28)), catalog, date(2026, 10, 28))
    assert not applicable_chunk(chunks[0], PolicyPeriod(date(2022, 1, 1), date(2022, 12, 31)), catalog, date(2026, 10, 28))
    service, _, provider = service_for(old, section_catalog=catalog)
    service.ask("What did the procedure require in 2022?")
    assert provider.calls[0]["sources"][0]["document_version"] == "0.9.0"


@pytest.mark.parametrize("question", ["Explain the previous procedure", "Compare policy in 2020 and 2021", "Policy as of 2022-02-30"])
def test_unclear_period_requests_clarification(chunks, question):
    service, _, provider = service_for(chunks[0])
    assert service.ask(question).reason_code == "ambiguous_policy_period"
    assert not provider.calls


def test_future_and_supersession_boundaries(chunks):
    chunk = replace(chunks[0], effective_date=date(2020, 1, 1))
    newer = replace(chunk, effective_date=date(2022, 6, 1), document_version="2.0.0")
    assert not applicable_chunk(chunk, PolicyPeriod(date(2022, 1, 1), date(2022, 12, 31)), (chunk, newer), date(2026, 1, 1))
    assert not applicable_chunk(chunk, PolicyPeriod(date(2030, 1, 1), date(2030, 1, 1)), (chunk,), date(2026, 1, 1))
    period, _ = requested_policy_period("Explain last year's procedure", date(2030, 7, 1))
    assert period == PolicyPeriod(date(2029, 1, 1), date(2029, 12, 31))


def test_historical_wording_without_literal_policy_keyword(chunks):
    service, _, provider = service_for(chunks[0], section_catalog=chunks)
    assert service.ask("How were recalls handled in 2021?").reason_code == "policy_period_unsupported"
    assert not provider.calls
    assert service.ask("Explain requirements before 2025").status == "clarification"


@pytest.mark.parametrize("question", [
    "Which fields must a recall request contain?",
    "What evidence does the ACH return correction procedure require?",
    "Describe the documented requirements for recalling a wire.",
])
def test_general_procedure_questions_are_not_transaction_decisions(chunks, question):
    assert clarification_needed(question) is None
    service, _, provider = service_for(chunks[0])
    service.ask(question)
    assert provider.calls


@pytest.mark.parametrize("question", [
    "It failed. Should I retry?", "Can we resend now?", "Should we cancel it?",
    "How do I reverse this payment?", "Please stop our transfer.",
])
def test_transaction_actions_require_context(question):
    assert clarification_needed(question)


def test_explicit_reference_expansion_is_bounded_and_traceable(chunks):
    seed = next(c for c in chunks if c.section_id == "BV-NAME")
    hit = RetrievalHit(seed, .7, 1)
    hits = follow_explicit_reference((hit,), chunks)
    assert hits[0] == hit
    assert 1 < len(hits) <= 3
    assert {h.chunk.section_id for h in hits[1:]} == {"BV-CORRECT"}
    assert all(h.origin == "explicit_reference" and h.linked_from_chunk_id == seed.chunk_id for h in hits[1:])
    assert not any(h.chunk.section_id == "AR-NEXT" for h in hits)
    service, retriever, provider = service_for(seed, section_catalog=chunks)
    answer = service.ask("Explain payee discrepancy resolution")
    assert retriever.calls[0][1] == 5
    assert answer.reference_expansions
    assert provider.calls[0]["sources"][1]["retrieval_origin"] == "explicit_reference"


def test_reference_expansion_is_optional_and_literal(chunks):
    seed = replace(chunks[0], content="See a related correction procedure; no exact reference.")
    hits = (RetrievalHit(seed, .5, 1),)
    assert follow_explicit_reference(hits, chunks) == hits
    assert follow_explicit_reference(hits, ()) == hits


def test_historical_reference_followup_cannot_add_current_policy(chunks):
    seed = next(c for c in chunks if c.section_id == "BV-NAME")
    old = replace(seed, effective_date=date(2020, 1, 1), document_version="0.9.0")
    service, _, provider = service_for(old, section_catalog=(old, *chunks))
    answer = service.ask("Explain the procedure as of 2021-05-01")
    assert not answer.reference_expansions
    assert len(provider.calls[0]["sources"]) == 1


def test_oversized_reference_section_is_not_partially_included(chunks):
    seed = next(c for c in chunks if c.section_id == "BV-NAME")
    target = next(c for c in chunks if c.section_id == "BV-CORRECT")
    oversized = tuple(replace(target, chunk_id=f"test-{i}", chunk_index=i) for i in range(3))
    hits = (RetrievalHit(seed, .5, 1),)
    assert follow_explicit_reference(hits, oversized) == hits


def test_baseline_artifacts_and_gold_are_unchanged():
    from hashlib import sha256
    manifest = json.loads(Path("evaluation/week2/baseline_v1_manifest.json").read_text(encoding="utf-8"))
    for key in ("original_run", "snapshot"):
        root = Path(manifest[key])
        # Run artifacts are intentionally ignored and may be absent in a clean checkout.
        if root.exists():
            for name, digest in manifest["files_sha256"].items():
                assert sha256((root / name).read_bytes()).hexdigest() == digest
    assert sha256(Path("docs/WEEK2_ANSWER_EVALUATION.md").read_bytes()).hexdigest() == manifest["report_sha256"]
    assert sha256(Path("evaluation/week2/golden_questions.json").read_bytes()).hexdigest() == manifest["gold_sha256"]


def test_runner_rejects_writing_original_baseline_report(monkeypatch):
    import sys
    from payment_ops.knowledge.evaluate_answers import main
    monkeypatch.setattr(sys, "argv", ["evaluation", "--report", "docs/WEEK2_ANSWER_EVALUATION.md"])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2


def test_catalog_narrow_scope_can_answer_without_downstream_runbook(chunks):
    chunk = next(c for c in chunks if c.section_id == "EC-BENEFICIARY")
    service, _, provider = service_for(chunk)
    quote = next(line for line in chunk.content.splitlines() if "| SYN-BEN-301 |" in line)
    provider.generate = lambda system, context: json.dumps(dict(
        status="limited_answer", required_sections=[], clarification_question=None,
        statements=[dict(text="Name mismatch: compare the submitted name with the verified record. Do not bypass validation; correction and revalidation remain required. This covers identification and first action only.",
                         evidence=[dict(source_id="S1", quote=quote)])]))
    answer = service.ask("Explain the code meaning and initial action for SYN-BEN-301")
    assert answer.status == "limited_answer" and answer.citations
    assert "meaning and initial_action are sufficient" in SYSTEM_PROMPT
