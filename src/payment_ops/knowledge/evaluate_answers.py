"""Development-set comparison against preserved Baseline V1. Run --live, then --review RUN_DIRECTORY."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
from time import perf_counter

from payment_ops.knowledge.answer_evaluation import (
    candidate_claims, citation_checks, disposition_correct, gold_evidence_gaps,
    read_human_review, summarize, write_review_files,
)
from payment_ops.knowledge.chunking import CHUNKER_VERSION, chunk_documents
from payment_ops.knowledge.embeddings import EmbeddingError, NebiusEmbeddings
from payment_ops.knowledge.evaluation import EvaluationError, load_dataset
from payment_ops.knowledge.evaluation_selection import ensure_new_artifacts, expected_dispositions, select_questions, write_new
from payment_ops.knowledge.generation import GenerationDiagnostic, GenerationError, create_generation_provider
from payment_ops.knowledge.index import CachedEmbeddings, LocalVectorIndex
from payment_ops.knowledge.ingestion import IngestionError, load_documents
from payment_ops.knowledge.retrieval import DenseRetriever
from payment_ops.knowledge.service import AnswerResult, DISCLOSURE, KnowledgeService, PROMPT_VERSION


EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"
GENERATION_MODEL = "Qwen/Qwen3-30B-A3B-Instruct-2507"


def run_questions(service, records: list[dict], chunks: tuple, *, clock=perf_counter) -> list[dict]:
    """Only question text crosses the production service boundary; label afterward."""
    by_id = {c.chunk_id: c for c in chunks}
    rows = []
    for record in records:
        if record["classification"] == "fixture-dependent":
            continue
        start = clock()
        try:
            answer = service.ask(record["question"])
        except Exception:
            answer = AnswerResult("unavailable", DISCLOSURE + "\n\nEvaluation service call failed.", (),
                                  "dense", (), "evaluation_service_failure",
                                  diagnostics=(GenerationDiagnostic("evaluation", "service_failure"),))
        elapsed = clock() - start
        ids = list(answer.retrieved_chunk_ids)
        row = {"question_id": record["question_id"], "question": record["question"],
               "category": record["category"], "classification": record["classification"],
               "answer": answer.answer, "status": answer.status, "reason_code": answer.reason_code,
               "retrieval_method": answer.retrieval_method, "prompt_version": answer.prompt_version,
               "embedding_model": EMBEDDING_MODEL, "generation_model": GENERATION_MODEL,
               "retrieved_chunk_ids": ids,
               "reference_expansions": list(answer.reference_expansions),
               "retrieved_sources": [{"source_id": f"S{i}", "chunk_id": cid,
                                      "document_id": by_id[cid].document_id,
                                      "section_id": by_id[cid].section_id,
                                      "document_version": by_id[cid].document_version,
                                      "effective_date": by_id[cid].effective_date.isoformat(),
                                      "retrieval_origin": (("explicit_reference" if dict(answer.reference_expansions)[cid] is not None else "requested_section")
                                                           if cid in dict(answer.reference_expansions) else "ranked"),
                                      "linked_from_chunk_id": dict(answer.reference_expansions).get(cid)}
                                     for i, cid in enumerate(dict.fromkeys(ids), 1) if cid in by_id],
               "citations": [asdict(c) for c in answer.citations],
               "diagnostics": [asdict(d) for d in answer.diagnostics],
               "missing_evidence_declarations": sorted({s for d in answer.diagnostics for s in d.missing_sections}),
               "elapsed_seconds": elapsed,
               "gold_required_evidence_groups": record["required_evidence_groups"],
               "gold_evidence": gold_evidence_gaps(record, ids, by_id)}
        row["expected_dispositions"] = expected_dispositions(record)
        row["expected_behavior"] = record["expected_behavior"]
        row["expected_document_ids"] = sorted({ref.split("/")[0] for ref in record["relevant_sections"]})
        expansions = dict(answer.reference_expansions)
        seeds = [cid for cid in ids if cid not in expansions]
        row["ranked_seed_chunk_ids"] = seeds
        row["expanded_chunk_ids"] = [cid for cid in ids if cid in expansions]
        row["ranked_seed_gold_evidence"] = gold_evidence_gaps(record, seeds, by_id) if seeds else None
        row["citation_checks"] = citation_checks(row, by_id)
        row["correct_disposition"] = disposition_correct(row)
        rows.append(row)
    return rows


REVIEW_CRITERIA = """## Methodology and human review

All 20 original questions remain in the gold dataset. The live runner executes
the selected eligible questions (counts/IDs in configuration.selection). Without a
profile the original 12 answerable, four unsupported and two ambiguous are used. Q17/Q18 are deferred
until archived/conflicting-source fixtures exist. Labels and expected evidence
groups are consulted only AFTER KnowledgeService.ask(question_text) returns.
No gold answer, expected section, or evaluation category is sent to inference.

Automatic checks are structural, not semantic:

- Answerable disposition matches answered/limited_answer; unsupported matches a
  genuine evidence abstention, not invalid_response; ambiguous matches clarification.
  A matching status does not prove an answer is correct or complete.
- Successful generation rate = substantive answered/limited_answer responses /
  all eligible questions. It is NOT an API transport success metric. Also report
  answerable response coverage; guard-generated clarifications make no LLM call.
- Citation membership checks exact retrieved chunk, document/section/version/path,
  source slot, and unique citation number. Quote verification checks the exact
  original substring at stored offsets for every passage. Zero citations/passages
  gives N/A, never a perfect score. All candidate claims must have known inline IDs.
- Invalid-response and incomplete-evidence frequencies use all evaluated questions
  as denominator; unavailability is reported separately. Gold evidence-group gaps
  assess current retrieved sections, not semantic completeness of generated claims.
- Latency is wall time around the normal service call, including query embedding,
  retrieval, generation, validation and fallbacks. Startup/corpus embedding/index
  time is separate. P50/P95 use nearest-rank ceil(p*N); failures and fast guard
  paths remain in the overall distribution. Model-path timings exclude guards and
  pre-generation failures/empty retrieval, but retain provider errors. A single
  18-question run is not the 100-query warm latency benchmark or target proof.

The run directory contains results.json, sources.json, claims.csv, completeness.csv,
and report.md. Source snapshots preserve review context by chunk ID and hash.
Only accepted answers/fallbacks and allowlisted diagnostics are saved; rejected
model payloads, authorization headers, keys, and sensitive provider settings are
not recorded. Keep generated artifacts in the ignored results directory.

### Faithfulness review criteria

claims.csv starts with BLANK assessments, reviewer and segmentation confirmation.
Mechanical sentence candidates inherit their original statement's citations. They
are NOT guaranteed atomic facts: reviewers must inspect the full generated answer,
split compound assertions into separate rows, and verify no substantive claim was
omitted. To split, copy a row, keep original_claim_id and immutable answer/evidence
fields, assign a unique claim_id, and edit claim_text into individual assertions.
Set segmentation_confirmed=yes only after checking coverage and citation mapping.
Every original candidate must remain covered; every child row must be reviewed.

- Supported: the claim's meaning, conditions, sequence, and scope follow from the
  cited source text. A quote merely mentioning the topic is insufficient.
- Unsupported: meaning is absent, contradicted, invented, or an unretrieved
  procedure is represented as verified. Valid IDs/quotes do not rescue such a claim.
- Partially supported: only part of a compound assertion or procedure is justified,
  or an essential condition is missing. Split where possible; do not give full credit.

No final score is computed until all claim rows are labeled with a reviewer and
segmentation confirmed. Faithfulness = Supported / all reviewed substantive claims;
Partially supported and Unsupported receive zero full-support credit. Report both
answerable-question claim faithfulness (the >=90% target's scope) and all-generated-
claim faithfulness. No claims/abstentions is N/A, never 100%. Response coverage is
separate; selective abstention cannot establish overall quality. Human segmentation
and ratings are judgments, not automatically verified ground truth. The runner
never assigns favorable labels or declares the 90% target achieved automatically.

### Procedural completeness review criteria

completeness.csv covers ALL selected answerable questions, including abstentions. Assign
one primary category and record additional issues in notes:

- complete_supported_answer: all information necessary for the requested scope,
  including relevant prerequisites, stop rules and review gates, is supported.
- appropriately_bounded_answer: supported guidance meets the requested limited
  scope and explicitly excludes unverified later stages without hiding a critical gap.
- missing_essential_procedure: a required step/condition/evidence source is absent;
  safe abstention due to a retrieval gap can belong here, rather than being unsafe.
- unsupported_additional_instruction: answer adds an unjustified action, deadline,
  policy, or permission beyond what sources support.
- unnecessary_abstention: available retrieved text was sufficient for the actual
  question, yet the system declined. Inspect the text, not merely the gold labels.

These are human labels, NOT inferred from model status or required_sections. Review
the recurring SYN-BEN-301 case (Q03) for narrow catalog sufficiency versus genuine
missing procedural evidence; no workaround or hardcoded answer is introduced.
Citation matching cannot establish faithfulness, and faithfulness does not establish
requested-scope completeness. Unsupported/ambiguous disposition accuracy is separate.
"""


def render_report(result: dict) -> str:
    lines = ["# Week 2 development-set answer comparison",
             "", "Baseline V1 remains unchanged: 12/18 correct dispositions (66.7%); 100% structural citation and quote verification; human faithfulness unmeasured.",
             "This reuses the development questions and is not independent validation.", "", f"Status: **{result['status']}**.", "",
             "## Configuration", "", "```json", json.dumps(result["configuration"], indent=2), "```", "",
             "Latest six-case grounded-v3 inspection: factual answered; SYN-BEN-301 incomplete_evidence; "
             "recall answered; delayed-status answered; unsupported abstained; ambiguous clarified. "
             "Those historical status-only inspections are not this selected run and do not establish faithfulness.", "",
             "## Eligibility", "", f"Selection: {result['configuration'].get('selection', {}).get('profile_id', 'original-full')}; "
             f"eligible: {result.get('eligibility', {}).get('eligible', 18)}. Original 20 questions preserved; "
             "Q17/Q18 fixture-dependent and excluded. Original PRD/separate handoff were not found locally; "
             "repository state, framework, corpus and golden dataset define this evaluation.", "", REVIEW_CRITERIA,
             "## Observed dispositions and deterministic metrics", ""]
    if result.get("summary") is None:
        lines += ["Pending: no full live QA baseline measured. " + result.get("blocker", "Live execution not requested."), "",
                  "Disposition rates, citation/quote findings, evidence gaps, and P50/P95 latency are pending."]
        if result.get("safe_diagnostics"):
            lines += ["", "Safe initialization diagnostics: `" + json.dumps(result["safe_diagnostics"]) + "`"]
    else:
        lines += ["```json", json.dumps(result["summary"], indent=2), "```", ""]
    review = result.get("human_review")
    lines += ["", "## Human faithfulness and procedural completeness", ""]
    lines += ["Answer relevance remains unmeasured; no automatic relevance judge or labels are supplied.", ""]
    if review is None:
        lines += ["Human assessments pending. **90% faithfulness target: not measured.** "
                  "No completeness categories have been assigned automatically."]
    else:
        lines += ["```json", json.dumps(review, indent=2), "```", "",
                  "These scores require explicit human ratings; no automatic claim of target achievement is made. "
                  "Incomplete reviews keep final scores null. Review coverage and abstentions alongside any score."]
    lines += ["", "## Per-question results, evidence gaps, and failure analysis", ""]
    for row in result["questions"]:
        lines += [f"### {row['question_id']}: {row['question']}", "",
                  f"Category: {row['category']}; class: {row['classification']}; status: {row['status']}; reason: {row['reason_code']}.", "",
                  f"Service latency: {row['elapsed_seconds']:.3f} seconds. Correct disposition: {row['correct_disposition']} (status only).", "",
                  row["answer"], "", "Retrieved sources: `" + json.dumps(row["retrieved_sources"]) + "`", "",
                  "Expected dispositions: `" + json.dumps(row.get("expected_dispositions")) + "`", "",
                  "Profile acceptance/safety criteria: `" + json.dumps(row.get("profile_acceptance")) + "`", "",
                  "Ranked seed IDs (before expansion, after service filtering): `" + json.dumps(row.get("ranked_seed_chunk_ids")) + "`", "",
                  "Expanded IDs: `" + json.dumps(row.get("expanded_chunk_ids")) + "`", "",
                  "Seed evidence coverage: `" + json.dumps(row.get("ranked_seed_gold_evidence")) + "`", "",
                  "Citation checks: `" + json.dumps(row["citation_checks"]) + "`", "",
                  "Current gold evidence gaps: `" + json.dumps(row["gold_evidence"]) + "`", "",
                  "Prior Dense retrieval baseline gaps: `" + json.dumps(row.get("prior_retrieval_gaps")) + "`", "",
                  "Missing-evidence declarations exposed by the service: `" + json.dumps(row["missing_evidence_declarations"]) + "`", "",
                  "Safe diagnostics: `" + json.dumps(row["diagnostics"]) + "`", ""]
        for citation in row["citations"]:
            lines += [f"[{citation['number']}] {citation['document_title']} | {citation['document_id']}/{citation['section_id']} | v{citation['document_version']}", ""]
            for passage in citation["passages"]:
                lines += [f"Chunk `{passage['chunk_id']}`; offsets {passage['start']}:{passage['end']}.", "",
                          "> " + passage["quote"].replace("\n", "\n> "), ""]
    if not result["questions"]:
        lines.append("All selected answers and human review rows await a real run; no synthetic answers substituted.")
    lines += ["", "## Recurring SYN-BEN-301 analysis and next actions", ""]
    q03 = next((r for r in result["questions"] if r["question_id"] == "Q03"), None)
    if q03:
        lines.append(f"Q03 observed status: {q03['status']}; reason: {q03['reason_code']}. "
                     "Compare its current gold gaps, declared missing sections and retrieved catalog text above. "
                     "Only human scope/completeness review can establish whether abstention was unnecessary.")
    else:
        lines.append("The six-case inspection reported incomplete_evidence for Q03. Full baseline and human catalog/scope review remain pending; no workaround is added.")
    if result["questions"]:
        failures = [r["question_id"] for r in result["questions"] if not r["correct_disposition"]]
        lines.append("Status-disposition mismatches: " + (", ".join(failures) or "None") + ". These are review priorities, not automatic faithfulness judgments.")
    lines += ["", "Complete human claim and completeness sheets before drawing quality conclusions. "
              "Preserve this frozen development-set run before any separate prompt/retrieval experiment. "
              "Check unsupported instructions, incomplete procedures, unnecessary abstentions and bounded answers. "
              "Do not treat this reused development set as held-out validation.", "",
              "## Limitations", "", "No automatic semantic judge is used. Sentence candidates can contain multiple claims; "
              "citation inheritance needs review. A matching quote can be misinterpreted. Missing-evidence declarations "
              "include only missing sections exposed by AnswerResult diagnostics, not the raw model's complete "
              "required_sections list. Guard clarifications can skip retrieval, correctly resulting in no source hits. "
              "Seed IDs are the service's retained ranked context after metadata filtering, not a raw pre-filter search trace. "
              "When seed IDs are not exposed, seed coverage is N/A; standalone retrieval metrics remain authoritative. "
              "Model aliases/provider behavior can change despite frozen code; run hashes identify local inputs only. "
              "A small selected run at concurrency one does not establish P95 performance under load or the formal warm-query target. "
              "Fixture-dependent cases, held-out paraphrases and broader safety evaluation remain outstanding.", "",
              "## Commands", "", "From an authenticated PowerShell terminal at repository root:", "",
              "```powershell", "uv run python -m payment_ops.knowledge.evaluate_answers --live" +
              (f" --profile {result['configuration']['selection']['profile_path']}" if result["configuration"].get("selection", {}).get("profile_path") else ""), "```", "",
              "The command prints a unique ignored run directory. Review its claims.csv and completeness.csv, then:", "",
              "```powershell", 'uv run python -m payment_ops.knowledge.evaluate_answers --review "evaluation/week2/results/answers_development/RUN_DIRECTORY"', "```", "",
              "--review reads saved data only and makes no API calls. It writes a separate reviewed run and report; inputs stay unchanged. "
              "Without --live/--review, only a pending report is prepared. Credentials remain in the environment.", ""]
    baseline = result["configuration"].get("baseline")
    if baseline:
        lines.extend(["", "## Baseline V1 comparison", "",
                      "Different profiles have different denominators and are not directly comparable to the full Baseline V1 aggregate. No independent validation; human faithfulness requires review.", "",
                      "| Measure | Baseline V1 | Development run |", "|---|---:|---:|"])
        summary = result.get("summary")
        baseline_correct = sum(v["correct_dispositions"] for v in baseline["summary"]["disposition_by_class"].values())
        development_correct = sum(v["correct_dispositions"] for v in summary["disposition_by_class"].values()) if summary else "Pending"
        lines.append(f"| correct dispositions / evaluated | {baseline_correct}/18 | {development_correct}/{result.get('eligibility', {}).get('eligible', 18)} |")
        for key, value in baseline["summary"].items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                current = summary.get(key, "Pending") if summary else "Pending"
                lines.append(f"| {key} | {value} | {current} |")
    return "\n".join(lines)


def _prior_gaps(path: Path, gold_hash: str, corpus_hashes: dict) -> dict:
    if not path.exists():
        return {}
    try:
        baseline = json.loads(path.read_text(encoding="utf-8"))
        cfg = baseline["configuration"]
        if (baseline["status"] != "complete-real-embeddings" or cfg["gold_sha256"] != gold_hash
                or cfg["corpus_sha256"] != corpus_hashes or cfg["model"] != EMBEDDING_MODEL):
            return {}
        return {r["question_id"]: r["scoring"] for r in baseline["methods"]["Dense"]["questions"]}
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true")
    mode.add_argument("--review", type=Path)
    parser.add_argument("--documents", type=Path, default=Path("data/knowledge/documents"))
    parser.add_argument("--gold", type=Path, default=Path("evaluation/week2/golden_questions.json"))
    parser.add_argument("--cache", type=Path, default=Path(".cache/payment_ops/embeddings"))
    parser.add_argument("--output-root", type=Path, default=Path("evaluation/week2/results/answers_development"))
    parser.add_argument("--profile", type=Path, help="ID selection profile; omit for original full eligible set")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.review and args.profile:
        parser.error("Review uses the saved run selection; do not supply --profile")
    directory = args.output_root / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    args.report = args.report or directory / "report.md"
    try:
        ensure_new_artifacts(args.report, directory / "results.json")
    except EvaluationError as exc:
        parser.error(str(exc))
    manifest = json.loads(Path("evaluation/week2/baseline_v1_manifest.json").read_text(encoding="utf-8"))
    protected = [Path(manifest[k]).resolve() for k in ("original_run", "snapshot")]
    preservation = Path("evaluation/week2/reliability_artifacts_manifest.json")
    if preservation.exists():
        frozen = json.loads(preservation.read_text(encoding="utf-8"))
        # New live runs get unique child directories; never review saved originals
        # in place. Human review can operate on a separate copy of a saved run.
        frozen_runs = {Path(p).parent.resolve() for p in frozen["files_sha256"] if Path(p).name == "results.json"}
        if (args.report.resolve() in {Path(p).resolve() for p in frozen["protected_reports"]}
                or any(root == path or root in path.parents for root in frozen_runs
                       for path in (args.report.resolve(), args.output_root.resolve(),
                                    *([args.review.resolve()] if args.review else [])))):
            parser.error("Saved evaluation artifacts are immutable; use a new report or separate human-review copy")
    if (args.report.resolve() == Path("docs/WEEK2_ANSWER_EVALUATION.md").resolve()
            or any(root == path or root in path.parents
                   for root in protected
                   for path in (args.report.resolve(), args.output_root.resolve(), *([args.review.resolve()] if args.review else [])))):
        parser.error("Baseline V1 is immutable; use a separate development output/report or review copy")
    for root in protected:
        for name, digest in manifest["files_sha256"].items():
            if sha256((root / name).read_bytes()).hexdigest() != digest:
                parser.error("Baseline V1 snapshot integrity check failed")
    if sha256(Path("docs/WEEK2_ANSWER_EVALUATION.md").read_bytes()).hexdigest() != manifest["report_sha256"]:
        parser.error("Original Baseline V1 report integrity check failed")
    if sha256(args.gold.read_bytes()).hexdigest() != manifest["gold_sha256"]:
        parser.error("Development comparison requires the unchanged Baseline V1 gold dataset")
    if args.review:
        try:
            path = args.review / "results.json"
            result = json.loads(path.read_text(encoding="utf-8"))
            eligible = result.get("eligibility", {}).get("eligible", 18)
            rows = result.get("questions", [])
            expected_ids = result["configuration"].get("selection", {}).get("executed_ids")
            if (result.get("status") != "complete-real-qa" or len(rows) != eligible
                    or (expected_ids is not None and [r["question_id"] for r in rows] != expected_ids)):
                raise EvaluationError("Human review requires a completed run matching its saved selection")
            result["human_review"] = read_human_review(result, args.review)
            directory.mkdir(parents=True, exist_ok=False)
            write_new(directory / "results.json", json.dumps(result, indent=2, allow_nan=False) + "\n")
            report = render_report(result)
            write_new(directory / "report.md", report)
            if args.report.resolve() != (directory / "report.md").resolve():
                write_new(args.report, report)
            for name in ("claims.csv", "completeness.csv"):
                shutil.copy2(args.review / name, directory / name)
        except (EvaluationError, OSError, ValueError, KeyError, TypeError):
            print("Human review failed validation; check run files, review identities, fields and labels. No scores published.")
            return 1
        print(f"Human review read without API calls: {args.review}; new results: {directory}")
        return 0
    documents = load_documents(args.documents)
    dataset, records = load_dataset(args.gold, documents)
    try:
        records, selection = select_questions(records, args.gold, args.profile)
    except EvaluationError as exc:
        parser.error(str(exc))
    chunks = chunk_documents(documents)
    corpus_hashes = {d.document_id: sha256(d.raw_text.encode()).hexdigest() for d in documents}
    gold_hash = sha256(args.gold.read_bytes()).hexdigest()
    config = {"selection": selection, "embedding_model": EMBEDDING_MODEL, "generation_model": GENERATION_MODEL,
              "embedding_dimensions_expected": 4096, "embedding_dimensions_actual": None,
              "evaluation_role": "Development-set comparison; not independent validation",
              "disposition_rule_version": "evidence-abstention-v2",
              "quote_recovery": "one fresh generation only for quote_not_found; unchanged sources; full revalidation",
              "case_record_rendering": "exact retrieved SOP table and warning appended by service",
              "baseline": manifest, "reference_expansion": "one explicit section (at most two chunks), plus one complete requested-scope section",
              "provider": "Nebius", "prompt_version": PROMPT_VERSION, "retrieval_method": "dense", "top_k": 5,
              "temperature": 0, "max_output_tokens": 1800, "generation_timeout_seconds": 45,
              "chunk_count": len(chunks), "chunker_version": CHUNKER_VERSION,
              "gold_version": dataset["dataset_version"], "gold_sha256": gold_hash, "corpus_sha256": corpus_hashes,
              "python": platform.python_version(), "concurrency": 1,
              "packages": {p: version(p) for p in ("langchain-core", "httpx", "numpy", "rank-bm25")},
              "code_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob("*.py"))}}
    result = {"schema_version": 1, "status": "pending", "configuration": config, "questions": [],
              "summary": None, "human_review": None, "answer_relevance": None,
              "eligibility": {"total": 20, "selected": len(records), "eligible": len(selection["executed_ids"]), "deferred": selection["deferred_ids"]},
              "started_utc": datetime.now(timezone.utc).isoformat(), "startup_seconds": None}
    failed = False
    generation = embedding = None
    directory.mkdir(parents=True, exist_ok=False)
    try:
        if args.live:
            start = perf_counter()
            generation = create_generation_provider(provider="nebius", model=GENERATION_MODEL)
            generation.verify_model()
            embedding = NebiusEmbeddings(model=EMBEDDING_MODEL)
            cached = CachedEmbeddings(embedding, identity=embedding.cache_identity, directory=args.cache)
            index = LocalVectorIndex(chunks, cached)
            if index.dimensions != 4096:
                raise EmbeddingError("Unexpected embedding dimensions")
            config["embedding_dimensions_actual"] = index.dimensions
            service = KnowledgeService({"dense": DenseRetriever(index)}, generation, section_catalog=chunks)
            result["startup_seconds"] = perf_counter() - start
            result["questions"] = run_questions(service, records, chunks)
            previous = _prior_gaps(Path("evaluation/week2/results/latest.json"), gold_hash, corpus_hashes)
            for row in result["questions"]:
                row["profile_acceptance"] = selection["acceptance"].get(row["question_id"])
                row["prior_retrieval_gaps"] = previous.get(row["question_id"])
            result["summary"] = summarize(result["questions"])
            result["status"] = "complete-real-qa"
            snapshots = {c.chunk_id: asdict(c) for c in chunks}
            (directory / "sources.json").write_text(json.dumps(snapshots, indent=2, default=str) + "\n", encoding="utf-8")
            write_review_files(result, directory)
        else:
            result["blocker"] = "Live QA evaluation not requested; real measurements and human review pending."
    except (GenerationError, EmbeddingError, IngestionError, EvaluationError, OSError) as exc:
        result["status"] = "incomplete" if result["questions"] else "pending"
        result["blocker"] = "Live QA baseline could not initialize or persist; check credentials, model access, corpus and output paths."
        if isinstance(exc, GenerationError):
            result["safe_diagnostics"] = [asdict(exc.diagnostic)]
        failed = True
    finally:
        if generation is not None:
            generation.close()
        if embedding is not None:
            embedding.close()
    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report = render_report(result)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    write_new(args.report, report)
    if directory is not None:
        write_new(directory / "results.json", json.dumps(result, indent=2, allow_nan=False) + "\n")
        if args.report.resolve() != (directory / "report.md").resolve():
            write_new(directory / "report.md", report)
        print(f"Run directory: {directory}")
    print(f"QA baseline: {result['status']}; {len(result['questions'])}/{result['eligibility']['eligible']} questions executed; report: {args.report}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
