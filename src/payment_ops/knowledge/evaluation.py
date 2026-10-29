"""Section-level gold validation and offline retrieval metrics; no provider calls."""

import json
import math
from pathlib import Path

from payment_ops.knowledge.models import KnowledgeDocument
from payment_ops.knowledge.retrieval import RetrievalHit


class EvaluationError(ValueError):
    """Invalid gold data or evaluation input."""


def validate_dataset(dataset: dict, documents: tuple[KnowledgeDocument, ...]) -> list[dict]:
    """Validate all 20 labels before ranking; context refs never count as gold gain."""
    if (not isinstance(dataset, dict) or type(dataset.get("schema_version")) is not int
            or dataset["schema_version"] != 1):
        raise EvaluationError("Unsupported golden dataset schema")
    if not isinstance(dataset.get("dataset_version"), str) or not dataset["dataset_version"].strip():
        raise EvaluationError("Missing dataset_version")
    records = dataset.get("questions")
    if not isinstance(records, list) or len(records) != 20:
        raise EvaluationError("Golden dataset must contain the original 20 questions")
    available = {f"{d.document_id}/{s.section_id}" for d in documents for s in d.sections}
    seen = set()
    required = {"question_id", "question", "category", "classification", "relevant_sections",
                "required_evidence_groups", "multiple_sections_required", "context_sections",
                "justification", "expected_behavior"}
    for record in records:
        if not isinstance(record, dict) or set(record) != required:
            raise EvaluationError("Malformed evaluation record fields")
        qid = record["question_id"]
        for field in ("question_id", "question", "category", "justification", "expected_behavior"):
            if not isinstance(record[field], str) or not record[field].strip():
                raise EvaluationError(f"Invalid {field}")
        if qid in seen:
            raise EvaluationError(f"Duplicate question ID: {qid}")
        seen.add(qid)
        status = record["classification"]
        if not isinstance(status, str) or status not in {"answerable", "unsupported", "ambiguous", "fixture-dependent"}:
            raise EvaluationError(f"{qid}: invalid classification")
        for field in ("relevant_sections", "context_sections"):
            refs = record[field]
            if not isinstance(refs, list) or any(not isinstance(r, str) for r in refs):
                raise EvaluationError(f"{qid}: invalid {field}")
            if len(set(refs)) != len(refs) or not set(refs) <= available:
                raise EvaluationError(f"{qid}: duplicate or unknown section reference")
        groups = record["required_evidence_groups"]
        if not isinstance(groups, list):
            raise EvaluationError(f"{qid}: invalid evidence groups")
        group_ids, alternatives = set(), set()
        for group in groups:
            if not isinstance(group, dict) or set(group) != {"group_id", "alternatives"}:
                raise EvaluationError(f"{qid}: malformed evidence group")
            gid, refs = group["group_id"], group["alternatives"]
            if not isinstance(gid, str) or not gid.strip() or gid in group_ids:
                raise EvaluationError(f"{qid}: invalid evidence group ID")
            group_ids.add(gid)
            if (not isinstance(refs, list) or not refs or any(not isinstance(r, str) for r in refs)
                    or len(set(refs)) != len(refs) or not set(refs) <= set(record["relevant_sections"])):
                raise EvaluationError(f"{qid}: invalid evidence group alternatives")
            alternatives.update(refs)
        if alternatives != set(record["relevant_sections"]):
            raise EvaluationError(f"{qid}: relevance and evidence groups disagree")
        # One section may support multiple facts/groups (e.g. a comparison table).
        needs_multiple = bool(groups) and not set.intersection(*(set(g["alternatives"]) for g in groups))
        if type(record["multiple_sections_required"]) is not bool or record["multiple_sections_required"] != needs_multiple:
            raise EvaluationError(f"{qid}: multiple_sections_required disagrees with groups")
        if (status == "answerable") != bool(groups):
            raise EvaluationError(f"{qid}: only answerable records may have scored evidence")
    if seen != {f"Q{i:02}" for i in range(1, 21)}:
        raise EvaluationError("Question IDs must be Q01 through Q20")
    return sorted(records, key=lambda record: record["question_id"])


def load_dataset(path: Path | str, documents: tuple[KnowledgeDocument, ...]) -> tuple[dict, list[dict]]:
    try:
        dataset = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise EvaluationError("Cannot read golden dataset JSON") from exc
    return dataset, validate_dataset(dataset, documents)


def mandatory_documents(record: dict) -> set[str]:
    """Documents unavoidable across the OR alternatives of each required group."""
    return {next(iter(documents)) for group in record["required_evidence_groups"]
            if len(documents := {ref.split("/")[0] for ref in group["alternatives"]}) == 1}


def score_ranking(record: dict, hits: tuple[RetrievalHit, ...], k: int = 5) -> dict:
    """Score top-k chunk slots against unique document/section gold labels.

Duplicate sections occupy their rank slots but gain zero after first occurrence.
Precision denominator is always k; no-hit/missing ranks contribute zero.
Empty relevance returns null metrics (undefined), never a perfect or zero score.
Evidence groups are AND across groups, OR within a group's alternatives.
"""
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise EvaluationError("k must be a positive integer")
    relevant = set(record["relevant_sections"])
    ranked = [f"{h.chunk.document_id}/{h.chunk.section_id}" for h in hits[:k]]
    found = set(ranked) & relevant
    groups = record["required_evidence_groups"]
    missing_groups = [g["group_id"] for g in groups if not set(g["alternatives"]) & set(ranked)]
    metrics = dict.fromkeys(("recall_at_5", "precision_at_5", "mrr_at_5", "ndcg_at_5",
                            "evidence_group_coverage", "multi_document_evidence_coverage",
                            "required_document_coverage", "complete_evidence"))
    if relevant:
        seen = set()
        gains = []
        for ref in ranked:
            gains.append(int(ref in relevant and ref not in seen))
            seen.add(ref)
        dcg = sum(gain / math.log2(rank + 1) for rank, gain in enumerate(gains, 1))
        ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(k, len(relevant)) + 1))
        coverage = (len(groups) - len(missing_groups)) / len(groups)
        required_docs = mandatory_documents(record)
        retrieved_docs = {ref.split("/")[0] for ref in found}
        metrics.update(
            recall_at_5=len(found) / len(relevant), precision_at_5=len(found) / k,
            mrr_at_5=next((1 / rank for rank, gain in enumerate(gains, 1) if gain), 0.0),
            ndcg_at_5=dcg / ideal, evidence_group_coverage=coverage,
            multi_document_evidence_coverage=coverage if len(required_docs) > 1 else None,
            required_document_coverage=len(required_docs & retrieved_docs) / len(required_docs) if required_docs else None,
            complete_evidence=not missing_groups,
        )
    return {"metrics": metrics, "missing_sections": sorted(relevant - found),
            "missing_evidence_groups": missing_groups,
            "nonrelevant_sections": sorted(set(ranked) - relevant)}


def evaluate_rankings(records: list[dict], rankings: dict[str, dict[str, tuple[RetrievalHit, ...]]]) -> dict:
    """Evaluate only answerable records; retain other rankings as unscored observations."""
    output = {}
    for method, questions in rankings.items():
        rows = []
        for record in records:
            qid = record["question_id"]
            if record["classification"] == "fixture-dependent":
                continue
            if qid not in questions:
                raise EvaluationError(f"{method}: missing results for {qid}")
            hits = questions[qid]
            scored = score_ranking(record, hits) if record["classification"] == "answerable" else None
            rows.append({"question_id": qid, "classification": record["classification"],
                         "scoring": scored, "hits": [
                             {"rank": i, "chunk_id": h.chunk.chunk_id,
                              "document_id": h.chunk.document_id, "document_title": h.chunk.document_title,
                              "section_id": h.chunk.section_id, "score": h.score}
                             for i, h in enumerate(hits[:5], 1)]})
        measured = [row["scoring"]["metrics"] for row in rows if row["scoring"] is not None]
        averages = {}
        if measured:
            for name in measured[0]:
                values = [m[name] for m in measured if m[name] is not None]
                averages[name] = sum(values) / len(values) if values else None
        output[method] = {"evaluated_questions": len(measured),
                          "multi_document_questions": sum(m["multi_document_evidence_coverage"] is not None for m in measured),
                          "macro_metrics": averages, "questions": rows}
    return output
