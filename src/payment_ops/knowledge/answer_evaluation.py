"""Offline checks and human review artifacts, independent of production inference."""

from collections import Counter
import csv
import json
import math
from pathlib import Path
import re

from payment_ops.knowledge.evaluation import EvaluationError
from payment_ops.knowledge.service import DISCLOSURE


ANSWER_STATUSES = {"answered", "limited_answer"}
ASSESSMENTS = {"Supported", "Unsupported", "Partially supported"}
COMPLETENESS = {"complete_supported_answer", "appropriately_bounded_answer",
                "missing_essential_procedure", "unsupported_additional_instruction", "unnecessary_abstention"}
CLAIM_FIELDS = ["question_id", "claim_id", "original_claim_id", "generated_answer", "claim_text",
                "citation_numbers", "evidence_quotes", "assessment", "reviewer", "segmentation_confirmed", "notes"]
PROCEDURE_FIELDS = ["question_id", "question", "generated_answer", "response_status", "required_evidence_groups",
                    "missing_evidence_groups", "assessment", "reviewer", "notes"]


def candidate_claims(row: dict) -> list[dict]:
    """Mechanical sentence candidates, not a semantic claim extractor.

Each candidate inherits its original statement's citations. Reviewers must verify
association and split compound assertions before confirming segmentation.
"""
    if row["status"] not in ANSWER_STATUSES:
        return []
    text = row["answer"]
    if text.startswith(DISCLOSURE + "\n\n"):
        text = text[len(DISCLOSURE) + 2:]
    prefix = "Limited guidance for the requested scope; this is not a complete end-to-end procedure.\n\n"
    if text.startswith(prefix):
        text = text[len(prefix):]
    output = []
    for segment in text.split("\n\n"):
        numbers = list(dict.fromkeys(int(n) for n in re.findall(r"\[(\d+)\]", segment)))
        clean = re.sub(r"\[\d+\]", "", segment).strip()
        for claim in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])|\n(?=\s*(?:\d+[.)]|[-*])\s)", clean):
            if not claim.strip():
                continue
            identity = f"{row['question_id']}.C{len(output) + 1:02}"
            evidence = [c for c in row["citations"] if c["number"] in numbers]
            output.append({"question_id": row["question_id"], "claim_id": identity,
                           "original_claim_id": identity, "generated_answer": row["answer"],
                           "claim_text": claim.strip(), "citation_numbers": json.dumps(numbers),
                           "evidence_quotes": json.dumps(evidence, ensure_ascii=False),
                           "assessment": "", "reviewer": "", "segmentation_confirmed": "", "notes": ""})
    return output


def citation_checks(row: dict, chunks: dict) -> dict:
    """Independently check metadata, request membership, source slots and offsets."""
    retrieved = list(dict.fromkeys(row["retrieved_chunk_ids"]))
    slot_map = {f"S{i}": cid for i, cid in enumerate(retrieved, 1)}
    numbers = [c["number"] for c in row["citations"]]
    checks = []
    passages = []
    for citation in row["citations"]:
        chunk = chunks.get(citation["chunk_id"])
        member = (chunk is not None and citation["chunk_id"] in retrieved
                  and type(citation["number"]) is int and citation["number"] > 0)
        if member:
            member = all(citation[field] == getattr(chunk, field) for field in
                         ("document_title", "document_id", "section_id", "document_version", "source_path"))
        for passage in citation["passages"]:
            source = chunks.get(passage["chunk_id"])
            in_context = (source is not None and passage["chunk_id"] in retrieved
                          and slot_map.get(passage["source_id"]) == passage["chunk_id"])
            if in_context:
                in_context = all(citation[field] == getattr(source, field) for field in
                                 ("document_title", "document_id", "section_id", "document_version", "source_path"))
            member = member and in_context
            start, end = passage["start"], passage["end"]
            verified = (in_context and type(start) is int and type(end) is int and
                        0 <= start < end <= len(source.content) and
                        isinstance(passage["quote"], str) and bool(passage["quote"].strip())
                        and source.content[start:end] == passage["quote"])
            passages.append(bool(verified))
        checks.append(bool(member and citation["passages"] and numbers.count(citation["number"]) == 1))
    candidates = candidate_claims(row)
    referenced = [json.loads(c["citation_numbers"]) for c in candidates]
    cited = bool(candidates) and all(ns and set(ns) <= set(numbers) for ns in referenced)
    return {"citation_count": len(checks), "valid_citation_count": sum(checks),
            "passage_count": len(passages), "verified_passage_count": sum(passages),
            "all_claim_candidates_cited": cited if row["status"] in ANSWER_STATUSES else None,
            "issues": (["invalid_citation_membership"] if not all(checks) else []) +
                      (["invalid_supporting_passage"] if not all(passages) else []) +
                      (["missing_or_unknown_inline_citation"] if row["status"] in ANSWER_STATUSES and not cited else [])}


def gold_evidence_gaps(record: dict, retrieved_ids: list[str], chunks: dict) -> dict | None:
    """Gold is consulted only after the service call; no evidence is injected."""
    if record["classification"] != "answerable":
        return None
    refs = {f"{chunks[cid].document_id}/{chunks[cid].section_id}" for cid in retrieved_ids if cid in chunks}
    missing = [g["group_id"] for g in record["required_evidence_groups"] if not set(g["alternatives"]) & refs]
    return {"retrieved_sections": sorted(refs),
            "missing_relevant_sections": sorted(set(record["relevant_sections"]) - refs),
            "missing_evidence_groups": missing,
            "group_coverage": (len(record["required_evidence_groups"]) - len(missing)) / len(record["required_evidence_groups"])}


def disposition_correct(row: dict) -> bool:
    classification = row["classification"]
    if classification == "answerable":
        return row["status"] in ANSWER_STATUSES
    if classification == "unsupported":
        # Rejecting malformed output is safe, but not a correct evidence decision.
        return row["status"] == "insufficient_evidence" and row["reason_code"] in {
            "insufficient_evidence", "incomplete_evidence", "empty_retrieval", "policy_period_unsupported",
        }
    return classification == "ambiguous" and row["status"] == "clarification"


def percentile(values: list[float], fraction: float) -> float | None:
    """Nearest-rank percentile; no interpolation or hidden outlier removal."""
    if not 0 < fraction <= 1:
        raise EvaluationError("Percentile fraction must be in (0, 1]")
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) or v < 0 for v in values):
        raise EvaluationError("Latency values must be finite and nonnegative")
    return sorted(values)[math.ceil(fraction * len(values)) - 1] if values else None


def summarize(rows: list[dict]) -> dict:
    def rate(numerator, denominator):
        return numerator / denominator if denominator else None
    classes = {}
    for classification in ("answerable", "unsupported", "ambiguous"):
        group = [r for r in rows if r["classification"] == classification]
        classes[classification] = {"count": len(group), "correct_dispositions": sum(disposition_correct(r) for r in group),
                                   "disposition_accuracy": rate(sum(disposition_correct(r) for r in group), len(group))}
    checks = [r["citation_checks"] for r in rows]
    times = [r["elapsed_seconds"] for r in rows]
    answers = [r for r in rows if r["status"] in ANSWER_STATUSES]
    # Model-path latency excludes guard/empty-retrieval shortcuts, but retains errors.
    model_path = [r["elapsed_seconds"] for r in rows if r["reason_code"] not in
                  {"empty_question", "missing_transaction_context", "ambiguous_policy_period",
                   "policy_period_unsupported", "empty_retrieval", "retrieval_failure"}]
    return {"evaluated_questions": len(rows), "status_counts": dict(sorted(Counter(r["status"] for r in rows).items())),
            "disposition_by_class": classes,
            "successful_generation_rate": rate(len(answers), len(rows)),
            "answerable_response_coverage": rate(sum(r["classification"] == "answerable" for r in answers), classes["answerable"]["count"]),
            "invalid_response_count": sum(r["reason_code"] == "invalid_response" for r in rows),
            "invalid_response_frequency": rate(sum(r["reason_code"] == "invalid_response" for r in rows), len(rows)),
            "incomplete_evidence_count": sum(r["reason_code"] == "incomplete_evidence" for r in rows),
            "incomplete_evidence_frequency": rate(sum(r["reason_code"] == "incomplete_evidence" for r in rows), len(rows)),
            "unavailable_count": sum(r["status"] == "unavailable" for r in rows),
            "citation_membership_validity": rate(sum(c["valid_citation_count"] for c in checks), sum(c["citation_count"] for c in checks)),
            "quote_verification_rate": rate(sum(c["verified_passage_count"] for c in checks), sum(c["passage_count"] for c in checks)),
            "answers_with_all_claim_candidates_cited": rate(sum(c["all_claim_candidates_cited"] is True for c in checks), len(answers)),
            "latency": {"count": len(times), "p50_seconds": percentile(times, .5), "p95_seconds": percentile(times, .95),
                        "model_path_count": len(model_path), "model_path_p50_seconds": percentile(model_path, .5),
                        "model_path_p95_seconds": percentile(model_path, .95)}}


def write_review_files(result: dict, directory: Path | str) -> None:
    """Create blank review sheets once; never overwrite completed human work."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    claims = [claim for row in result["questions"] for claim in candidate_claims(row)]
    procedures = [{"question_id": row["question_id"], "question": row["question"],
                   "generated_answer": row["answer"], "response_status": row["status"],
                   "required_evidence_groups": json.dumps(row["gold_required_evidence_groups"]),
                   "missing_evidence_groups": json.dumps(row["gold_evidence"]["missing_evidence_groups"]),
                   "assessment": "", "reviewer": "", "notes": ""}
                  for row in result["questions"] if row["classification"] == "answerable"]
    for name, fields, records in (("claims.csv", CLAIM_FIELDS, claims), ("completeness.csv", PROCEDURE_FIELDS, procedures)):
        path = directory / name
        if path.exists():
            raise EvaluationError("Review sheet already exists; use another run directory")
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)


def read_human_review(result: dict, directory: Path | str) -> dict:
    """No favorable defaults; partial support gets zero full-support credit.

Every candidate must be covered, every child claim reviewed, and segmentation
explicitly confirmed before a final faithfulness score can be calculated.
"""
    directory = Path(directory)
    expected = {claim["claim_id"]: claim for row in result["questions"] for claim in candidate_claims(row)}
    by_question = {r["question_id"]: r for r in result["questions"]}
    try:
        with (directory / "claims.csv").open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != CLAIM_FIELDS:
                raise EvaluationError("Malformed claims review columns")
            claims = list(reader)
        with (directory / "completeness.csv").open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != PROCEDURE_FIELDS:
                raise EvaluationError("Malformed completeness review columns")
            procedures = list(reader)
    except OSError as exc:
        raise EvaluationError("Cannot read human review sheets") from exc
    if any(any(not isinstance(key, str) or not isinstance(value, str) for key, value in row.items())
           for row in [*claims, *procedures]):
        raise EvaluationError("Malformed human review row")
    covered, ids = set(), set()
    reviewed = []
    for claim in claims:
        original = expected.get(claim["original_claim_id"])
        if (original is None or claim["question_id"] != original["question_id"] or not claim["claim_id"].strip()
                or claim["claim_id"] in ids or not claim["claim_text"].strip()
                or any(claim[key] != original[key] for key in ("generated_answer", "citation_numbers", "evidence_quotes"))):
            raise EvaluationError("Claim review identity, evidence, or coverage is invalid")
        ids.add(claim["claim_id"])
        covered.add(claim["original_claim_id"])
        assessment = claim["assessment"].strip()
        if assessment and assessment not in ASSESSMENTS:
            raise EvaluationError("Unknown claim assessment")
        confirmed = claim["segmentation_confirmed"].strip().lower()
        if confirmed and confirmed not in {"yes", "no"}:
            raise EvaluationError("segmentation_confirmed must be yes/no or blank")
        if assessment and claim["reviewer"].strip() and confirmed == "yes":
            reviewed.append(claim)
    complete = bool(expected) and covered == set(expected) and len(reviewed) == len(claims)
    answerable = [c for c in reviewed if by_question[c["question_id"]]["classification"] == "answerable"]
    expected_procedures = {qid for qid, row in by_question.items() if row["classification"] == "answerable"}
    procedure_ids = set()
    procedure_counts = Counter()
    procedure_reviewed = 0
    for row in procedures:
        qid = row["question_id"]
        if qid not in expected_procedures or qid in procedure_ids:
            raise EvaluationError("Invalid completeness review question ID")
        procedure_ids.add(qid)
        original = by_question[qid]
        if (row["generated_answer"] != original["answer"] or row["response_status"] != original["status"]
                or row["question"] != original["question"]
                or row["required_evidence_groups"] != json.dumps(original["gold_required_evidence_groups"])
                or row["missing_evidence_groups"] != json.dumps(original["gold_evidence"]["missing_evidence_groups"])):
            raise EvaluationError("Completeness review does not match this run")
        assessment = row["assessment"].strip()
        if assessment and assessment not in COMPLETENESS:
            raise EvaluationError("Unknown completeness assessment")
        if assessment and row["reviewer"].strip():
            procedure_reviewed += 1
            procedure_counts[assessment] += 1
    procedures_complete = procedure_ids == expected_procedures and procedure_reviewed == len(expected_procedures) and bool(expected_procedures)
    return {"claim_review_complete": complete, "claim_candidates": len(expected), "reviewed_claim_rows": len(reviewed),
            "all_generated_claim_faithfulness": sum(c["assessment"].strip() == "Supported" for c in reviewed) / len(reviewed) if complete else None,
            "answerable_claim_faithfulness": sum(c["assessment"].strip() == "Supported" for c in answerable) / len(answerable) if complete and answerable else None,
            "answerable_reviewed_claims": len(answerable),
            "claim_assessment_counts": dict(Counter(c["assessment"].strip() for c in reviewed)),
            "completeness_review_complete": procedures_complete, "completeness_reviewed_questions": procedure_reviewed,
            "completeness_counts": dict(procedure_counts)}
