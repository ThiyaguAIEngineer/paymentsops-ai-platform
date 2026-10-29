"""Offline metric arithmetic and gold contracts; no official fake-vector scores."""

from collections import Counter
from copy import deepcopy
from dataclasses import replace
import json
import math
from pathlib import Path
import sys

import pytest

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.evaluate_retrieval import main, render_report
from payment_ops.knowledge.evaluation import (
    EvaluationError, evaluate_rankings, load_dataset, mandatory_documents, score_ranking, validate_dataset,
)
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import RetrievalHit


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def gold():
    docs = load_documents(ROOT / "data/knowledge/documents")
    dataset, records = load_dataset(ROOT / "evaluation/week2/golden_questions.json", docs)
    return docs, dataset, records


def hit_factory(docs):
    base = chunk_documents(docs)[0]
    def hit(ref, rank):
        doc_id, section_id = ref.split("/")
        return RetrievalHit(replace(base, document_id=doc_id, section_id=section_id,
                                    chunk_id=f"{ref}:{rank}"), 1 / rank, rank)
    return hit


def test_original_questions_categories_counts_and_references(gold):
    docs, dataset, records = gold
    planned = {}
    for line in (ROOT / "docs/WEEK2_CORPUS_DESIGN.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| Q"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            planned[cells[0]] = (cells[1], cells[2])
    assert {r["question_id"]: (r["question"], r["category"]) for r in records} == planned
    assert Counter(r["classification"] for r in records) == {
        "answerable": 12, "unsupported": 4, "ambiguous": 2, "fixture-dependent": 2,
    }
    assert sum(len(mandatory_documents(r)) > 1 for r in records) == 2
    assert validate_dataset(dataset, docs) == records
    assert validate_dataset({**dataset, "questions": list(reversed(dataset["questions"]))}, docs) == records


def test_hand_calculated_metrics_and_multiple_sections(gold):
    docs, _, records = gold
    record = next(r for r in records if r["question_id"] == "Q07")
    a, b, c = record["relevant_sections"]
    make = hit_factory(docs)
    ranked = tuple(make(ref, rank) for rank, ref in enumerate(["OTHER/NONE", a, a, b, c], 1))
    result = score_ranking(record, ranked)
    m = result["metrics"]
    assert m["recall_at_5"] == 1
    assert m["precision_at_5"] == 3 / 5
    assert m["mrr_at_5"] == 1 / 2
    dcg = 1 / math.log2(3) + 1 / math.log2(5) + 1 / math.log2(6)
    ideal = 1 + 1 / math.log2(3) + 1 / math.log2(4)
    assert m["ndcg_at_5"] == pytest.approx(dcg / ideal)
    assert m["complete_evidence"] is True
    assert m["multi_document_evidence_coverage"] == 1
    assert result["missing_sections"] == []


def test_empty_ranking_is_zero_for_answerable(gold):
    record = gold[2][0]
    m = score_ranking(record, ())["metrics"]
    assert all(m[key] == 0 for key in ("recall_at_5", "precision_at_5", "mrr_at_5", "ndcg_at_5", "evidence_group_coverage"))
    assert m["complete_evidence"] is False


def test_empty_relevance_is_undefined_and_excluded(gold):
    record = next(r for r in gold[2] if r["question_id"] == "Q13")
    assert all(value is None for value in score_ranking(record, ())["metrics"].values())
    rankings = {"test-only": {r["question_id"]: () for r in gold[2] if r["classification"] != "fixture-dependent"}}
    result = evaluate_rankings(gold[2], rankings)["test-only"]
    assert result["evaluated_questions"] == 12
    assert result["multi_document_questions"] == 2
    assert len(result["questions"]) == 18
    assert all(r["scoring"] is None for r in result["questions"] if r["classification"] != "answerable")


def test_alternative_evidence_not_all_required(gold):
    docs, _, records = gold
    record = next(r for r in records if r["question_id"] == "Q03")
    hit = hit_factory(docs)(record["relevant_sections"][0], 1)
    m = score_ranking(record, (hit,))["metrics"]
    assert m["recall_at_5"] == .5
    assert m["precision_at_5"] == .2
    assert m["evidence_group_coverage"] == 1
    assert m["multi_document_evidence_coverage"] is None
    assert m["complete_evidence"] is True


def test_document_presence_does_not_prove_group_coverage(gold):
    docs, _, records = gold
    record = next(r for r in records if r["question_id"] == "Q07")
    make = hit_factory(docs)
    ranked = (make("SYN-STATUS/SS-DELAY", 1), make("SYN-EXCEPTION/EX-DUPLICATE", 2))
    m = score_ranking(record, ranked)["metrics"]
    assert m["required_document_coverage"] == 1
    assert m["multi_document_evidence_coverage"] == pytest.approx(2 / 3)
    assert m["complete_evidence"] is False


def test_one_catalog_section_can_support_both_comparison_groups(gold):
    docs, _, records = gold
    record = next(r for r in records if r["question_id"] == "Q12")
    make = hit_factory(docs)
    metrics = score_ranking(record, (make("SYN-ERROR-CATALOG/EC-BENEFICIARY", 1),))["metrics"]
    assert metrics["evidence_group_coverage"] == 1
    assert record["multiple_sections_required"] is False
    branch = score_ranking(record, (make("SYN-BENEFICIARY/BV-NAME", 1),))["metrics"]
    assert branch["evidence_group_coverage"] == .5


def test_cutoff_and_duplicate_sections_do_not_inflate(gold):
    docs, _, records = gold
    record = records[0]
    make = hit_factory(docs)
    ref = record["relevant_sections"][0]
    duplicate = tuple(make(ref, rank) for rank in range(1, 6))
    m = score_ranking(record, duplicate)["metrics"]
    assert m["precision_at_5"] == .2
    assert m["ndcg_at_5"] == 1
    below_cutoff = tuple(make("OTHER/NONE", i) for i in range(1, 6)) + (make(ref, 6),)
    assert score_ranking(record, below_cutoff)["metrics"]["recall_at_5"] == 0


@pytest.mark.parametrize("change", [
    lambda d: d.update(schema_version=9),
    lambda d: d.update(questions=d["questions"][:-1]),
    lambda d: d["questions"][0].update(question=""),
    lambda d: d["questions"][0].update(question_id="Q02"),
    lambda d: d["questions"][0].update(classification="unknown"),
    lambda d: d["questions"][0].update(relevant_sections=["SYN-STATUS/SS-MISSING"]),
    lambda d: d["questions"][0].update(context_sections=["SYN-MISSING/WR-SCOPE"]),
    lambda d: d["questions"][0].update(required_evidence_groups=[]),
    lambda d: d["questions"][0].update(multiple_sections_required="false"),
    lambda d: d["questions"][0].update(extra_field="bad"),
    lambda d: d["questions"][0]["required_evidence_groups"][0].update(alternatives=[]),
    lambda d: d["questions"][0]["required_evidence_groups"].append(deepcopy(d["questions"][0]["required_evidence_groups"][0])),
])
def test_malformed_gold_rejected(gold, change):
    docs, dataset, _ = gold
    broken = deepcopy(dataset)
    change(broken)
    with pytest.raises(EvaluationError):
        validate_dataset(broken, docs)


def test_bad_json_and_missing_results(gold, tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{bad", encoding="utf-8")
    with pytest.raises(EvaluationError, match="JSON"):
        load_dataset(path, gold[0])
    with pytest.raises(EvaluationError, match="missing results"):
        evaluate_rankings(gold[2], {"test-only": {}})


def test_deterministic_evaluation_and_render(gold):
    records = gold[2]
    rankings = {"test-only": {r["question_id"]: () for r in records if r["classification"] != "fixture-dependent"}}
    assert evaluate_rankings(records, rankings) == evaluate_rankings(records, rankings)
    pending = {"status": "pending", "configuration": {}, "methods": {}, "blocker": "test only"}
    assert render_report(pending, records) == render_report(pending, records)
    report = render_report(pending, records)
    assert "Pending" in report and "Q20:" in report and "Q17:" in report


def test_completed_report_comparison_and_exclusions(gold):
    # Hand-authored empty rankings exercise report arithmetic, not live quality.
    records = gold[2]
    questions = {r["question_id"]: () for r in records if r["classification"] != "fixture-dependent"}
    methods = evaluate_rankings(records, {name: questions for name in ("Dense", "BM25", "Hybrid")})
    result = {"status": "test-only", "configuration": {}, "methods": methods}
    report = render_report(result, records)
    assert "Hybrid minus Dense = +0.0000" in report
    assert "Deferred until isolated evaluation fixtures exist" in report
    assert "12" in report


def test_offline_cli_creates_pending_artifacts_without_provider(gold, tmp_path, monkeypatch):
    import payment_ops.knowledge.evaluate_retrieval as runner
    def forbidden(**kwargs):
        pytest.fail("Offline report must not initialize a provider")
    monkeypatch.setattr(runner, "NebiusEmbeddings", forbidden)
    output, report = tmp_path / "results.json", tmp_path / "report.md"
    monkeypatch.setattr(sys, "argv", ["evaluation", "--documents", str(ROOT / "data/knowledge/documents"),
                                     "--gold", str(ROOT / "evaluation/week2/golden_questions.json"),
                                     "--output", str(output), "--report", str(report)])
    assert main() == 0
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["status"] == "pending" and result["methods"] == {}
    assert result["configuration"]["model"] == "Qwen/Qwen3-Embedding-8B"
    assert len(result["configuration"]["corpus_sha256"]) == 6
    assert len(result["configuration"]["chunk_ids"]) == 32
    assert result["configuration"]["actual_dimensions"] is None


def test_live_cli_missing_key_is_explicit_and_secret_free(gold, tmp_path, monkeypatch):
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    output, report = tmp_path / "results.json", tmp_path / "report.md"
    monkeypatch.setattr(sys, "argv", ["evaluation", "--live", "--documents", str(ROOT / "data/knowledge/documents"),
                                     "--gold", str(ROOT / "evaluation/week2/golden_questions.json"),
                                     "--output", str(output), "--report", str(report)])
    assert main() == 1
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["status"] == "pending" and result["methods"] == {}
    assert result["blocker"] == "NEBIUS_API_KEY is required"
