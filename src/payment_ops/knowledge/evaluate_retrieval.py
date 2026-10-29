"""Reproducible current-corpus baseline; --live uses only real Nebius embeddings."""

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform

from payment_ops.knowledge.chunking import CHUNKER_VERSION, chunk_documents
from payment_ops.knowledge.embeddings import EmbeddingError, NebiusEmbeddings
from payment_ops.knowledge.evaluation import EvaluationError, evaluate_rankings, load_dataset, mandatory_documents
from payment_ops.knowledge.evaluation_selection import ensure_new_artifacts, select_questions, write_new
from payment_ops.knowledge.index import CachedEmbeddings, LocalVectorIndex
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import BM25Retriever, DenseRetriever, reciprocal_rank_fusion


MODEL = "Qwen/Qwen3-Embedding-8B"

DEFINITIONS = """## Metric definitions

Only answerable questions enter macro averages. Relevance is binary at the
document/section level, not document-only or chunk level. Top five chunk slots
are retained in their original ranking: repeated sections earn gain only once
and still consume a slot. Fewer than five hits leaves the other slots empty.

- Recall@5: distinct relevant sections retrieved / all gold relevant sections.
- Precision@5: distinct relevant sections retrieved / 5.
- MRR@5: reciprocal rank of the first relevant section, or zero when none appear.
- NDCG@5: binary unique-section gain discounted by log2(rank + 1), divided by
  ideal gain for min(5, number of relevant sections).
- Evidence-group coverage: fraction of required groups satisfied; all groups
  are required (AND), any listed alternative satisfies a group (OR).
- Multi-document evidence coverage: evidence-group coverage macro-averaged only
  over questions requiring evidence from at least two unavoidable documents.
  Report its question count separately. Document presence alone is insufficient.
- Required-document coverage: fraction of unavoidable documents represented by
  a relevant hit. Complete evidence rate: fraction with every evidence group met.

Alternative sources remain separately relevant for Recall/NDCG: retrieving only
one alternative can satisfy a group without obtaining perfect section recall.
An empty relevance set is undefined (null), never a scored zero or perfect score.
Unsupported, ambiguous, and fixture-dependent cases are excluded from all these
averages. Context sections are never scored as direct answer evidence.
"""


def render_report(result: dict, records: list[dict]) -> str:
    """Render both a truthful pending report and the completed live comparison."""
    lines = ["# Week 2 retrieval evaluation", "", f"Status: **{result['status']}**.", "",
             "## Configuration", "", "```json", json.dumps(result["configuration"], indent=2), "```", "",
             "The project owner reports a successful Qwen smoke test (4096 dimensions) and three live inspections. "
             "That history is separate from measurements produced by this runner.", "",
             "Gold labels are derived from corpus procedures, not prior rankings. Original question text and categories "
             "are preserved in `evaluation/week2/golden_questions.json`. Each record states its relevance justification "
             "and required groups. Supporting context is distinguished from directly relevant evidence.", "",
             "## Question eligibility", "", "| Classification | Count |", "| --- | --- |"]
    for status, count in sorted(Counter(r["classification"] for r in records).items()):
        lines.append(f"| {status} | {count} |")
    lines += ["", "Q09/Q10 require clarification and have no definitive answer labels. Q13/Q14/Q15/Q19 "
              "are unsupported (unknown code, live data, legal rule, historical version). Q17/Q18 require "
              "archived/conflicting fixtures and are not retrieved or scored in this baseline.", "", DEFINITIONS,
              "## Method comparison", "", "| Method | Evaluated | Recall@5 | Precision@5 | MRR@5 | NDCG@5 | Multi-doc evidence coverage | Complete evidence rate |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    methods = result["methods"]
    for name in ("Dense", "BM25", "Hybrid"):
        if name not in methods:
            lines.append(f"| {name} | Pending | Pending | Pending | Pending | Pending | Pending | Pending |")
        else:
            item = methods[name]
            metrics = item["macro_metrics"]
            values = [metrics.get(key) for key in ("recall_at_5", "precision_at_5", "mrr_at_5", "ndcg_at_5", "multi_document_evidence_coverage", "complete_evidence")]
            lines.append(f"| {name} | {item['evaluated_questions']} | " + " | ".join("N/A" if v is None else f"{v:.4f}" for v in values) + " |")
    lines += ["", "## Per-question results and evidence gaps", ""]
    for record in records:
        qid = record["question_id"]
        lines += [f"### {qid}: {record['question']}", "", f"Classification: {record['classification']}. {record['justification']}", "",
                  "Relevant sections: " + (", ".join(f"`{s}`" for s in record["relevant_sections"]) or "None (unscored)."), ""]
        if record["classification"] == "fixture-dependent":
            lines += ["Deferred until isolated evaluation fixtures exist.", ""]
            continue
        if not methods:
            lines += ["Dense / BM25 / Hybrid results pending a complete real-embedding baseline run.", ""]
            continue
        for name, item in methods.items():
            row = next(row for row in item["questions"] if row["question_id"] == qid)
            lines += [f"**{name}**", "", "| Rank | Document | Section | Chunk ID | Score |", "| --- | --- | --- | --- | --- |"]
            for hit in row["hits"]:
                lines.append(f"| {hit['rank']} | {hit['document_title']} | {hit['section_id']} | `{hit['chunk_id']}` | {hit['score']:.6f} |")
            if not row["hits"]:
                lines.append("| — | No hits | — | — | — |")
            lines.append("")
            if row["scoring"] is not None:
                scoring = row["scoring"]
                lines += ["Metrics: `" + json.dumps(scoring["metrics"], sort_keys=True) + "`", "",
                          "Missing sections: " + (", ".join(scoring["missing_sections"]) or "None"), "",
                          "Missing required groups: " + (", ".join(scoring["missing_evidence_groups"]) or "None"), "",
                          "Nonrelevant sections occupying top-five slots: " + (", ".join(scoring["nonrelevant_sections"]) or "None"), ""]
            else:
                lines += ["Observation only: returned passages are not evidence that this question is answerable. "
                          "Retrieval ranking cannot measure abstention or clarification accuracy.", ""]
    lines += ["## Multi-document coverage", ""]
    for name, item in methods.items():
        coverage = item["macro_metrics"].get("multi_document_evidence_coverage")
        lines.append(f"- {name}: {item['multi_document_questions']} multi-document questions; "
                     f"group coverage {coverage if coverage is not None else 'N/A'}. "
                     "Per-question missing groups are listed above.")
    if not methods:
        count = sum(r["classification"] == "answerable" and len(mandatory_documents(r)) > 1 for r in records)
        lines.append(f"Pending for {count} multi-document questions. No measured coverage claimed.")
    lines += ["", "## Unsupported and ambiguous observations", "",
              "Q13 asks for an undocumented code, Q14 needs live account access, Q15 asks for a universal legal rule, "
              "and Q19 needs a missing historical version. None has direct answer evidence. Q09/Q10 require clarification. "
              "Their per-question rankings above are observations only; thematic overlap is not answerability. "
              + ("Actual rankings are available above; no abstention accuracy is inferred." if methods else
                 "Actual retrieval observations remain pending the live run."), "",
              "## Does hybrid improve retrieval?", ""]
    if all(name in methods for name in ("Dense", "BM25", "Hybrid")):
        for key in ("recall_at_5", "precision_at_5", "mrr_at_5", "ndcg_at_5", "multi_document_evidence_coverage"):
            hybrid = methods["Hybrid"]["macro_metrics"].get(key)
            if hybrid is None:
                lines.append(f"- {key}: N/A for the selected questions.")
                continue
            lines.append(f"- {key}: Hybrid minus Dense = {hybrid - methods['Dense']['macro_metrics'][key]:+.4f}; "
                         f"Hybrid minus BM25 = {hybrid - methods['BM25']['macro_metrics'][key]:+.4f}.")
        lines += ["", "Positive deltas are metric-specific improvements, not proof of overall superiority or answer quality. "
                  "Review regressions and missing evidence in each question before changing parameters."]
    else:
        lines.append("Pending. Previous three-question inspections do not establish a 20-question baseline advantage.")
    lines += ["", "## Recommended follow-up and limitations", ""]
    if methods:
        lines.append("Review measured missing groups and nonrelevant top-five slots before a separate tuning experiment. "
                     "If group coverage is incomplete, test candidate depth or section-context expansion only after preserving "
                     "this baseline. Do not assume fusion benefits every question. No retriever parameters were changed here.")
    else:
        lines.append("Run the live baseline first; measured-result-based tuning recommendations remain pending. "
                     f"Blocker: {result.get('blocker', 'live run not requested')}.")
    lines += ["", "This is a small development set, not a held-out benchmark. Binary section labels credit any chunk from "
              "a relevant section, which can overstate evidence completeness when that section spans chunks. Required-group "
              "coverage mitigates alternative-source interpretation but is still section-level, not claim-level. "
              "Model alias stability is provider-controlled; hashes and package versions enable comparison but do not guarantee "
              "identical future embeddings. No answer faithfulness, abstention accuracy, legal correctness, or latency target "
              "is evaluated. Unsupported questions may retrieve thematically similar text without becoming supported.", "",
              "## Reproduce", "", "From the repository root, with NEBIUS_API_KEY available in the terminal:", "",
              "```powershell", "uv run python -m payment_ops.knowledge.evaluate_retrieval --live" +
              (f" --profile {result['configuration']['selection']['profile_path']}" if result["configuration"].get("selection", {}).get("profile_path") else ""), "```", "",
              "The model is explicitly Qwen/Qwen3-Embedding-8B; the runner requires 4096 dimensions. "
              "It reuses .cache/payment_ops/embeddings, embeds each query once, and reuses those dense/sparse candidates "
              "for existing RRF fusion. It writes secret-free machine-readable configuration, hashes, scores, ranks, "
              "and evidence gaps into a unique run directory; existing artifacts are never overwritten. "
              "No source passages, credentials, headers, or raw provider errors are serialized. "
              "No --live flag creates only a pending report and performs no provider calls.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--documents", type=Path, default=Path("data/knowledge/documents"))
    parser.add_argument("--gold", type=Path, default=Path("evaluation/week2/golden_questions.json"))
    parser.add_argument("--cache", type=Path, default=Path(".cache/payment_ops/embeddings"))
    parser.add_argument("--profile", type=Path, help="ID selection profile; omit for all original questions")
    parser.add_argument("--output-root", type=Path, default=Path("evaluation/week2/results/retrieval"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    documents = load_documents(args.documents)
    dataset, records = load_dataset(args.gold, documents)
    try:
        records, selection = select_questions(records, args.gold, args.profile)
        run = args.output_root / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        args.output = args.output or run / "results.json"
        args.report = args.report or run / "report.md"
        ensure_new_artifacts(args.output, args.report)
    except EvaluationError as exc:
        parser.error(str(exc))
    chunks = chunk_documents(documents)
    configuration = {
        "selection": selection, "retrieval_stage": "initial top-5 only; no service context expansion",
        "model": MODEL, "provider": "Nebius", "expected_dimensions": 4096, "actual_dimensions": None,
        "top_k": 5, "candidate_k_per_method": 5, "rrf_constant": 60, "rrf_weights": "equal",
        "bm25_k1": 1.5, "bm25_b": 0.75, "dense_similarity": "cosine",
        "document_count": len(documents), "section_count": sum(len(d.sections) for d in documents),
        "chunk_count": len(chunks), "chunker_version": CHUNKER_VERSION,
        "dataset_version": dataset["dataset_version"], "gold_sha256": sha256(args.gold.read_bytes()).hexdigest(),
        "corpus_sha256": {d.document_id: sha256(d.raw_text.encode("utf-8")).hexdigest() for d in documents},
        "chunk_ids": [c.chunk_id for c in chunks], "python": platform.python_version(),
        "packages": {p: version(p) for p in ("langchain-core", "numpy", "rank-bm25", "httpx")},
        "code_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob("*.py"))},
    }
    result = {"schema_version": 1, "run_time_utc": datetime.now(timezone.utc).isoformat(),
              "status": "pending", "configuration": configuration, "methods": {}}
    provider = None
    failed = False
    try:
        if args.live:
            provider = NebiusEmbeddings(model=MODEL)
            provider.verify_model()
            cached = CachedEmbeddings(provider, identity=provider.cache_identity, directory=args.cache)
            index = LocalVectorIndex(chunks, cached)
            if index.dimensions != 4096:
                raise EmbeddingError("Expected 4096 dimensions for this verified baseline model")
            configuration["actual_dimensions"] = index.dimensions
            dense, sparse = DenseRetriever(index), BM25Retriever(chunks)
            rankings = {name: {} for name in ("Dense", "BM25", "Hybrid")}
            for record in records:
                if record["classification"] == "fixture-dependent":
                    continue
                qid, query = record["question_id"], record["question"]
                dense_hits, sparse_hits = dense.retrieve(query, 5), sparse.retrieve(query, 5)
                rankings["Dense"][qid], rankings["BM25"][qid] = dense_hits, sparse_hits
                rankings["Hybrid"][qid] = reciprocal_rank_fusion(dense_hits, sparse_hits, k=5, rank_constant=60)
            result["methods"] = evaluate_rankings(records, rankings)
            result["status"] = "complete-real-embeddings"
        else:
            result["blocker"] = "Live evaluation not requested; no official baseline metrics calculated"
    except EmbeddingError as exc:
        result["blocker"] = str(exc)
        failed = True
    finally:
        if provider is not None:
            provider.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    write_new(args.output, json.dumps(result, indent=2, allow_nan=False) + "\n")
    write_new(args.report, render_report(result, records))
    print(f"Evaluation {result['status']}; {len(records)} gold questions; report: {args.report}; JSON: {args.output}")
    if failed:
        print(f"Live baseline pending: {result['blocker']}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
