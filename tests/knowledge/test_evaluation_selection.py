"""Offline selection/runner regressions; simulated outputs are never quality metrics."""

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from payment_ops.knowledge.answer_evaluation import write_review_files
from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.evaluation import EvaluationError, evaluate_rankings, load_dataset
from payment_ops.knowledge.evaluation_selection import select_questions
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import RetrievalHit
from payment_ops.knowledge.service import AnswerResult, DISCLOSURE


GOLD = Path("evaluation/week2/golden_questions.json")
PROFILE = Path("evaluation/week2/profiles/curated15_v1.json")
IDS = ["Q01", "Q02", "Q03", "Q04", "Q05", "Q07", "Q08", "Q09", "Q10", "Q11", "Q12", "Q13", "Q15", "Q19", "Q20"]


@pytest.fixture
def inputs():
    docs = load_documents(Path("data/knowledge/documents"))
    _, records = load_dataset(GOLD, docs)
    return records, chunk_documents(docs)


def test_curated15_is_exact_unchanged_subset_with_complete_acceptance_metadata(inputs):
    records, _ = inputs
    original = deepcopy(records)
    selected, metadata = select_questions(records, GOLD, PROFILE)
    assert metadata["selected_ids"] == metadata["executed_ids"] == IDS
    assert len(selected) == len(set(IDS)) == 15
    assert Counter(r["classification"] for r in selected) == {"answerable": 10, "ambiguous": 2, "unsupported": 3}
    assert selected == [next(r for r in records if r["question_id"] == qid) for qid in IDS]
    assert records == original
    assert metadata["deferred_ids"] == ["Q17", "Q18"]
    assert set(metadata["excluded_ids"]) == {"Q06", "Q14", "Q16", "Q17", "Q18"}
    assert metadata["profile_sha256"] == sha256(PROFILE.read_bytes()).hexdigest()
    for r in selected:
        expected = metadata["expectations"][r["question_id"]]
        assert expected["question"] == r["question"]
        assert expected["relevant_sections"] == r["relevant_sections"]
        assert expected["required_evidence_groups"] == r["required_evidence_groups"]
        assert expected["expected_dispositions"]
        assert metadata["acceptance"][r["question_id"]]["criteria"]
        assert metadata["acceptance"][r["question_id"]]["safety_restrictions"]
        if r["classification"] != "answerable":
            assert not expected["expected_document_ids"] and not expected["relevant_sections"]


def test_original_full_selection_remains_available(inputs):
    selected, metadata = select_questions(inputs[0], GOLD)
    assert selected == inputs[0] and len(selected) == 20
    assert len(metadata["executed_ids"]) == 18
    assert metadata["distribution"] == {"answerable": 12, "unsupported": 4, "ambiguous": 2, "fixture-dependent": 2}


@pytest.mark.parametrize("change", [
    lambda p: p["question_ids"].append("Q01"),
    lambda p: p["question_ids"].append("Q99"),
    lambda p: p.update(gold_sha256="wrong"),
    lambda p: p.update(schema_version=True),
    lambda p: p.update(expected_distribution={"answerable": 15}),
    lambda p: p["acceptance"].pop("Q01"),
])
def test_invalid_profile_rejected(inputs, tmp_path, change):
    data = json.loads(PROFILE.read_text())
    change(data)
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(data))
    with pytest.raises(EvaluationError):
        select_questions(inputs[0], GOLD, path)


def test_retrieval_metrics_score_ten_and_leave_others_unscored(inputs):
    records, _ = select_questions(inputs[0], GOLD, PROFILE)
    rankings = {"Dense": {r["question_id"]: () for r in records}}
    result = evaluate_rankings(records, rankings)["Dense"]
    assert result["evaluated_questions"] == 10 and len(result["questions"]) == 15
    for row in result["questions"]:
        assert (row["scoring"] is None) == (row["classification"] != "answerable")
    assert set(result["macro_metrics"]) >= {"recall_at_5", "precision_at_5", "mrr_at_5", "ndcg_at_5", "evidence_group_coverage", "multi_document_evidence_coverage"}


@pytest.mark.parametrize("runner_name", ["evaluate_retrieval", "evaluate_answers"])
def test_profile_pending_cli_is_offline_identified_and_non_overwriting(inputs, tmp_path, monkeypatch, runner_name):
    from importlib import import_module
    runner = import_module("payment_ops.knowledge." + runner_name)
    def forbidden(*args, **kwargs):
        pytest.fail("No live calls permitted for pending profile execution")
    monkeypatch.setattr(runner, "NebiusEmbeddings", forbidden)
    if runner_name == "evaluate_answers":
        monkeypatch.setattr(runner, "create_generation_provider", forbidden)
    root = tmp_path / "runs"
    monkeypatch.setattr(sys, "argv", ["evaluation", "--profile", str(PROFILE), "--output-root", str(root)])
    assert runner.main() == 0
    paths = list(root.glob("*/results.json"))
    first = paths[0].read_bytes()
    result = json.loads(first)
    assert result["configuration"]["selection"]["selected_ids"] == IDS
    assert result["status"] == "pending"
    assert runner.main() == 0
    assert len(list(root.glob("*/results.json"))) == 2 and paths[0].read_bytes() == first
    existing = tmp_path / "existing.md"
    existing.write_text("do not overwrite")
    monkeypatch.setattr(sys, "argv", ["evaluation", "--report", str(existing)])
    with pytest.raises(SystemExit) as error:
        runner.main()
    assert error.value.code == 2 and existing.read_text() == "do not overwrite"


def test_answer_subset_sends_only_exact_question_text_and_separates_expansion(inputs):
    from payment_ops.knowledge.evaluate_answers import run_questions
    records, chunks = inputs
    selected, _ = select_questions(records, GOLD, PROFILE)
    seed, expansion = chunks[0], chunks[-1]
    class Spy:
        def __init__(self):
            self.calls = []
        def ask(self, question):
            assert isinstance(question, str)
            self.calls.append(question)
            return AnswerResult("insufficient_evidence", DISCLOSURE + "\n\nInsufficient evidence.", (), "dense",
                                (seed.chunk_id, expansion.chunk_id), "insufficient_evidence",
                                reference_expansions=((expansion.chunk_id, seed.chunk_id),))
    spy = Spy()
    rows = run_questions(spy, selected, chunks)
    assert spy.calls == [r["question"] for r in selected]
    assert [r["question_id"] for r in rows] == IDS
    assert all(r["ranked_seed_chunk_ids"] == [seed.chunk_id] for r in rows)
    assert all(r["expanded_chunk_ids"] == [expansion.chunk_id] for r in rows)
    assert all(r["gold_evidence"] is None for r in rows if r["classification"] != "answerable")


@pytest.mark.parametrize("curated", [True, False])
def test_completed_profile_can_export_and_review_without_overwriting_input(inputs, tmp_path, monkeypatch, curated):
    from payment_ops.knowledge import evaluate_answers as runner
    records, selection = select_questions(inputs[0], GOLD, PROFILE if curated else None)
    class Spy:
        def ask(self, question):
            return AnswerResult("insufficient_evidence", DISCLOSURE + "\n\nInsufficient evidence.", (), "dense", (), "insufficient_evidence")
    rows = runner.run_questions(Spy(), records, inputs[1])
    source = tmp_path / "input"
    source.mkdir()
    result = dict(status="complete-real-qa", configuration={"selection": selection}, questions=rows, summary=None,
                  human_review=None, eligibility={"eligible": len(rows)})
    saved = json.dumps(result)
    (source / "results.json").write_text(saved)
    (source / "report.md").write_text("unchanged")
    write_review_files(result, source)
    import csv
    with (source / "completeness.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == (10 if curated else 12)
    before = {p.name: p.read_bytes() for p in source.iterdir()}
    monkeypatch.setattr(sys, "argv", ["evaluation", "--review", str(source), "--output-root", str(tmp_path / "reviewed")])
    assert runner.main() == 0
    assert {p.name: p.read_bytes() for p in source.iterdir()} == before
    reviewed = json.loads(next((tmp_path / "reviewed").glob("*/results.json")).read_text())
    assert reviewed["human_review"]["answerable_claim_faithfulness"] is None
    assert reviewed["configuration"]["selection"]["selected_ids"] == (IDS if curated else [r["question_id"] for r in inputs[0]])


def test_answer_runner_executes_selected_fifteen_with_offline_service_double(inputs, tmp_path, monkeypatch):
    from payment_ops.knowledge import evaluate_answers as runner
    calls = []
    generation = SimpleNamespace(verify_model=lambda: None, close=lambda: None)
    embedding = SimpleNamespace(cache_identity="offline-test", close=lambda: None)
    monkeypatch.setattr(runner, "create_generation_provider", lambda **kwargs: generation)
    monkeypatch.setattr(runner, "NebiusEmbeddings", lambda **kwargs: embedding)
    monkeypatch.setattr(runner, "CachedEmbeddings", lambda delegate, **kwargs: delegate)
    monkeypatch.setattr(runner, "LocalVectorIndex", lambda chunks, cached: SimpleNamespace(dimensions=4096))
    monkeypatch.setattr(runner, "DenseRetriever", lambda index: "offline-retriever")
    class Spy:
        def ask(self, question):
            calls.append(question)
            return AnswerResult("insufficient_evidence", DISCLOSURE + "\n\nInsufficient evidence.", (), "dense", (), "insufficient_evidence")
    def compose(retrievers, provider, *, section_catalog):
        assert retrievers == {"dense": "offline-retriever"} and provider is generation
        assert section_catalog == inputs[1]  # Corpus only, never acceptance labels.
        return Spy()
    monkeypatch.setattr(runner, "KnowledgeService", compose)
    root = tmp_path / "simulated-not-real-metrics"
    monkeypatch.setattr(sys, "argv", ["evaluation", "--live", "--profile", str(PROFILE), "--output-root", str(root)])
    assert runner.main() == 0  # Every provider/service is a local double.
    expected, _ = select_questions(inputs[0], GOLD, PROFILE)
    assert calls == [r["question"] for r in expected]
    result = json.loads(next(root.glob("*/results.json")).read_text())
    assert [r["question_id"] for r in result["questions"]] == IDS
    assert result["eligibility"]["eligible"] == 15
    assert result["answer_relevance"] is None and result["human_review"] is None


def test_unsupported_only_retrieval_report_has_na_not_invented_relevance(inputs):
    from payment_ops.knowledge.evaluate_retrieval import render_report
    records = [r for r in inputs[0] if r["classification"] == "unsupported"]
    rankings = {name: {r["question_id"]: () for r in records} for name in ("Dense", "BM25", "Hybrid")}
    report = render_report(dict(status="offline-test-only", configuration={}, methods=evaluate_rankings(records, rankings)), records)
    assert "N/A" in report
    assert all(not r["relevant_sections"] for r in records)


def test_all_prior_artifacts_and_gold_are_unchanged():
    manifest = json.loads(Path("evaluation/week2/task17a_preservation_manifest.json").read_text())
    for path, digest in manifest["files_sha256"].items():
        if Path(path).exists():
            assert sha256(Path(path).read_bytes()).hexdigest() == digest
