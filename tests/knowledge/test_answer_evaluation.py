"""Offline answer-evaluation tests; outputs here are not official live metrics."""

from copy import deepcopy
import csv
from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest

from payment_ops.knowledge.answer_evaluation import (
    candidate_claims, citation_checks, disposition_correct, percentile,
    read_human_review, summarize, write_review_files,
)
from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.evaluate_answers import main, render_report, run_questions
from payment_ops.knowledge.evaluation import EvaluationError, load_dataset
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import RetrievalHit
from payment_ops.knowledge.service import AnswerResult, DISCLOSURE, build_context, validate_answer


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def inputs():
    documents = load_documents(ROOT / "data/knowledge/documents")
    _, records = load_dataset(ROOT / "evaluation/week2/golden_questions.json", documents)
    chunks = chunk_documents(documents)
    return records, chunks


class FakeService:
    """Captures normal service arguments; never calls a model or scores gold itself."""
    def __init__(self, answer):
        self.answer, self.calls = answer, []
    def ask(self, question):
        self.calls.append(question)
        return self.answer


def valid_answer(chunks):
    chunk = next(c for c in chunks if c.section_id == "EC-BENEFICIARY")
    hits = (RetrievalHit(chunk, 1, 1),)
    _, sources = build_context("q", hits)
    payload = {"status":"answered", "statements":[{"text":"SYN-BEN-301 is a name mismatch. Compare the submitted name with the verified record.",
               "evidence":[{"source_id":"S1","quote":"Name mismatch"},
                           {"source_id":"S1","quote":"Compare submitted name with verified beneficiary record"}]}],
               "clarification_question":None, "required_sections":[]}
    status, text, citations = validate_answer(json.dumps(payload), sources)
    return AnswerResult(status, DISCLOSURE + "\n\n" + text, citations, "dense", (chunk.chunk_id,), status)


def rows_fixture(inputs):
    records, chunks = inputs
    service = FakeService(valid_answer(chunks))
    counter = iter(range(36))
    return run_questions(service, records, chunks, clock=lambda: next(counter)), service


def test_all_18_questions_only_text_sent_and_fixtures_deferred(inputs):
    rows, service = rows_fixture(inputs)
    records, _ = inputs
    assert len(rows) == len(service.calls) == 18
    assert service.calls == [r["question"] for r in records if r["classification"] != "fixture-dependent"]
    assert {r["question_id"] for r in rows}.isdisjoint({"Q17", "Q18"})
    assert all(r["elapsed_seconds"] == 1 for r in rows)
    from payment_ops.knowledge.service import PROMPT_VERSION
    assert all(r["prompt_version"] == PROMPT_VERSION for r in rows)
    assert rows[0]["gold_evidence"] is not None


def test_citations_and_quotes_are_independent_objective_checks(inputs):
    rows, _ = rows_fixture(inputs)
    row = rows[0]
    chunks = {c.chunk_id:c for c in inputs[1]}
    checks = citation_checks(row, chunks)
    assert checks["valid_citation_count"] == checks["citation_count"] == 1
    assert checks["verified_passage_count"] == checks["passage_count"] == 2
    broken = deepcopy(row)
    broken["citations"][0]["passages"][0]["quote"] = "Invented rule"
    assert "invalid_supporting_passage" in citation_checks(broken, chunks)["issues"]
    broken = deepcopy(row)
    broken["retrieved_chunk_ids"] = []
    assert "invalid_citation_membership" in citation_checks(broken, chunks)["issues"]
    broken = deepcopy(row)
    broken["citations"][0]["document_version"] = "9.0.0"
    assert citation_checks(broken, chunks)["valid_citation_count"] == 0


@pytest.mark.parametrize("classification,status,reason,expected", [
    ("answerable","answered","answered",True),
    ("answerable","limited_answer","limited_answer",True),
    ("answerable","insufficient_evidence","incomplete_evidence",False),
    ("unsupported","insufficient_evidence","insufficient_evidence",True),
    ("unsupported","insufficient_evidence","invalid_response",False),
    ("ambiguous","clarification","missing_transaction_context",True),
    ("ambiguous","answered","answered",False),
])
def test_dispositions_are_not_faithfulness(classification,status,reason,expected):
    assert disposition_correct({"classification":classification,"status":status,"reason_code":reason}) is expected


def test_latencies_nearest_rank_and_empty_values():
    assert percentile(list(range(1,21)), .5) == 10
    assert percentile(list(range(1,21)), .95) == 19
    assert percentile([], .95) is None
    with pytest.raises(EvaluationError): percentile([float("nan")], .95)
    with pytest.raises(EvaluationError): percentile([1], 0)


def test_summary_does_not_assign_semantic_scores(inputs):
    rows, _ = rows_fixture(inputs)
    summary = summarize(rows)
    assert summary["evaluated_questions"] == 18
    assert summary["successful_generation_rate"] == 1
    assert summary["disposition_by_class"]["unsupported"]["disposition_accuracy"] == 0
    assert summary["quote_verification_rate"] == 1
    assert "faithfulness" not in summary
    assert summary["latency"]["p95_seconds"] == 1


def test_no_claims_is_not_perfect_faithfulness_or_citation_validity(inputs, tmp_path):
    records, chunks = inputs
    answer = AnswerResult("insufficient_evidence", DISCLOSURE + "\n\nInsufficient evidence.", (), "dense", (), "insufficient_evidence")
    rows = run_questions(FakeService(answer), records, chunks)
    result = {"questions":rows}
    write_review_files(result, tmp_path)
    review = read_human_review(result, tmp_path)
    assert review["answerable_claim_faithfulness"] is None
    assert review["all_generated_claim_faithfulness"] is None
    assert not review["claim_review_complete"]
    assert summarize(rows)["citation_membership_validity"] is None


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def save_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def test_blank_review_pending_then_partial_is_not_full_credit(inputs,tmp_path):
    rows, _ = rows_fixture(inputs)
    result = {"questions":rows}
    write_review_files(result, tmp_path)
    initial = read_human_review(result, tmp_path)
    assert initial["answerable_claim_faithfulness"] is None
    fields, claims = read_csv(tmp_path / "claims.csv")
    assert all(not c["assessment"] and not c["reviewer"] for c in claims)
    for claim in claims:
        claim.update(assessment="Partially supported", reviewer="Reviewer A", segmentation_confirmed="yes")
    save_csv(tmp_path / "claims.csv", fields, claims)
    review = read_human_review(result, tmp_path)
    assert review["claim_review_complete"]
    assert review["answerable_claim_faithfulness"] == 0
    assert review["all_generated_claim_faithfulness"] == 0


def test_review_coverage_missing_rows_and_no_segmentation_cannot_get_score(inputs,tmp_path):
    rows, _ = rows_fixture(inputs)
    result = {"questions":rows}
    write_review_files(result, tmp_path)
    fields, claims = read_csv(tmp_path / "claims.csv")
    for claim in claims:
        claim.update(assessment="Supported", reviewer="Reviewer A", segmentation_confirmed="yes")
    save_csv(tmp_path / "claims.csv", fields, claims[:-1])
    assert read_human_review(result, tmp_path)["answerable_claim_faithfulness"] is None
    claims[0]["segmentation_confirmed"] = "no"
    save_csv(tmp_path / "claims.csv", fields, claims)
    assert read_human_review(result, tmp_path)["answerable_claim_faithfulness"] is None


def test_review_can_split_claims_without_dropping_original_coverage(inputs,tmp_path):
    rows, _ = rows_fixture(inputs)
    result = {"questions":rows}
    write_review_files(result,tmp_path)
    fields, claims = read_csv(tmp_path / "claims.csv")
    child = {**claims[0], "claim_id":claims[0]["claim_id"] + ".child", "claim_text":"Human separated assertion."}
    claims.append(child)
    for claim in claims:
        claim.update(assessment="Supported", reviewer="Reviewer A", segmentation_confirmed="yes")
    save_csv(tmp_path / "claims.csv",fields,claims)
    review=read_human_review(result,tmp_path)
    assert review["answerable_claim_faithfulness"] == 1
    assert review["claim_review_complete"]


@pytest.mark.parametrize("field,value", [("assessment","Probably fine"),("question_id","Q99"),("generated_answer","Different run"),("segmentation_confirmed","auto-approved")])
def test_malformed_or_mismatched_human_reviews_rejected(inputs,tmp_path,field,value):
    rows,_=rows_fixture(inputs)
    result={"questions":rows}
    write_review_files(result,tmp_path)
    fields,claims=read_csv(tmp_path / "claims.csv")
    claims[0][field]=value
    save_csv(tmp_path / "claims.csv",fields,claims)
    with pytest.raises(EvaluationError):read_human_review(result,tmp_path)


def test_completeness_is_separate_and_includes_abstention_cases(inputs,tmp_path):
    rows,_=rows_fixture(inputs)
    result={"questions":rows}
    write_review_files(result,tmp_path)
    fields,procedures=read_csv(tmp_path / "completeness.csv")
    assert len(procedures)==12
    for row in procedures: row.update(assessment="appropriately_bounded_answer",reviewer="Reviewer A")
    save_csv(tmp_path / "completeness.csv",fields,procedures)
    review=read_human_review(result,tmp_path)
    assert review["completeness_review_complete"]
    assert review["completeness_counts"]=={"appropriately_bounded_answer":12}
    assert review["answerable_claim_faithfulness"] is None
    with pytest.raises(EvaluationError):write_review_files(result,tmp_path)


def test_guard_latency_and_missing_declarations_captured(inputs):
    from payment_ops.knowledge.generation import GenerationDiagnostic
    answer=AnswerResult("insufficient_evidence",DISCLOSURE+"\n\nMissing evidence.",(),"dense",(),"incomplete_evidence",
                        diagnostics=(GenerationDiagnostic("evidence_sufficiency","incomplete_retrieval_evidence",missing_sections=("SYN-BENEFICIARY/BV-NAME",)),))
    rows=run_questions(FakeService(answer),inputs[0],inputs[1])
    assert rows[0]["missing_evidence_declarations"]==["SYN-BENEFICIARY/BV-NAME"]
    assert summarize(rows)["incomplete_evidence_frequency"]==1


def test_claim_candidates_preserve_citation_association(inputs):
    rows,_=rows_fixture(inputs)
    claims=candidate_claims(rows[0])
    assert len(claims)==2
    assert all(json.loads(c["citation_numbers"])==[1] for c in claims)
    assert all(c["assessment"]=="" for c in claims)


def test_pending_cli_no_api_calls_and_report_has_no_measurements(inputs,tmp_path,monkeypatch):
    import payment_ops.knowledge.evaluate_answers as runner
    def forbidden(**kwargs):pytest.fail("Offline report cannot call a provider")
    monkeypatch.setattr(runner,"create_generation_provider",forbidden)
    report=tmp_path / "report.md"
    monkeypatch.setattr(sys,"argv",["evaluation","--documents",str(ROOT / "data/knowledge/documents"),
                                   "--gold",str(ROOT / "evaluation/week2/golden_questions.json"),"--report",str(report)])
    assert main()==0
    text=report.read_text(encoding="utf-8")
    assert "90% faithfulness target: not measured" in text
    assert "Pending: no full live QA baseline measured" in text


def test_live_cli_no_key_safe_pending_no_fabricated_results(inputs,tmp_path,monkeypatch):
    monkeypatch.delenv("NEBIUS_API_KEY",raising=False)
    output=tmp_path / "runs"
    monkeypatch.setattr(sys,"argv",["evaluation","--live","--documents",str(ROOT / "data/knowledge/documents"),
                                   "--gold",str(ROOT / "evaluation/week2/golden_questions.json"),
                                   "--output-root",str(output),"--report",str(tmp_path / "report.md")])
    assert main()==1
    result=json.loads(next(output.glob("*/results.json")).read_text(encoding="utf-8"))
    assert result["questions"]==[] and result["summary"] is None
    assert result["safe_diagnostics"][0]["category"]=="missing_credentials"


def test_service_failure_is_recorded_without_sensitive_exception(inputs):
    class Broken:
        def ask(self, question):raise RuntimeError("never print this secret")
    rows=run_questions(Broken(),inputs[0],inputs[1])
    assert len(rows)==18 and all(r["status"]=="unavailable" for r in rows)
    assert "never print" not in json.dumps(rows)
