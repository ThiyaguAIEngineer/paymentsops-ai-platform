"""Shared ID-profile selection and non-overwriting artifacts for existing runners."""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from payment_ops.knowledge.evaluation import EvaluationError


def select_questions(records: list[dict], gold: Path, profile: Path | None = None) -> tuple[list[dict], dict]:
    """Select unchanged gold records; annotations never cross the inference boundary."""
    ids = [r["question_id"] for r in records]
    metadata = {"profile_id": "original-full", "profile_path": None, "profile_sha256": None, "acceptance": {}}
    if profile is not None:
        try:
            raw = profile.read_bytes()
            data = json.loads(raw)
        except (OSError, ValueError) as exc:
            raise EvaluationError("Cannot read selection profile") from exc
        required = {"schema_version", "profile_id", "gold_sha256", "question_ids", "expected_distribution", "acceptance"}
        if (not isinstance(data, dict) or set(data) != required
                or type(data["schema_version"]) is not int or data["schema_version"] != 1):
            raise EvaluationError("Malformed selection profile")
        ids = data["question_ids"]
        if (not isinstance(ids, list) or not ids or any(not isinstance(i, str) for i in ids)
                or len(ids) != len(set(ids)) or not set(ids) <= {r["question_id"] for r in records}):
            raise EvaluationError("Profile IDs must be distinct known questions")
        if not isinstance(data["profile_id"], str) or not data["profile_id"].strip():
            raise EvaluationError("Missing profile ID")
        if data["gold_sha256"] != sha256(gold.read_bytes()).hexdigest():
            raise EvaluationError("Profile does not match the frozen original gold dataset")
        acceptance = data["acceptance"]
        if not isinstance(acceptance, dict) or set(acceptance) != set(ids):
            raise EvaluationError("Acceptance notes must cover exactly the selected IDs")
        for notes in acceptance.values():
            if not isinstance(notes, dict) or set(notes) != {"criteria", "safety_restrictions"}:
                raise EvaluationError("Malformed acceptance notes")
            if any(not isinstance(v, list) or not v or any(not isinstance(s, str) or not s.strip() for s in v) for v in notes.values()):
                raise EvaluationError("Acceptance criteria and restrictions must be nonempty string lists")
        metadata.update(profile_id=data["profile_id"], profile_path=profile.as_posix(), profile_sha256=sha256(raw).hexdigest(), acceptance=acceptance)
    by_id = {r["question_id"]: r for r in records}
    selected = [by_id[qid] for qid in ids]
    distribution = dict(sorted(Counter(r["classification"] for r in selected).items()))
    if profile is not None and data["expected_distribution"] != distribution:
        raise EvaluationError("Profile disposition distribution does not match gold")
    metadata.update(
        selected_ids=ids, executed_ids=[r["question_id"] for r in selected if r["classification"] != "fixture-dependent"],
        excluded_ids=[r["question_id"] for r in records if r["question_id"] not in ids],
        deferred_ids=[r["question_id"] for r in records if r["classification"] == "fixture-dependent"],
        distribution=distribution,
        selected_records_sha256=sha256(json.dumps(selected, sort_keys=True).encode()).hexdigest(),
        expectations={r["question_id"]: {
            "question": r["question"], "category": r["category"], "classification": r["classification"],
            "expected_dispositions": expected_dispositions(r), "expected_behavior": r["expected_behavior"],
            "expected_document_ids": sorted({s.split("/")[0] for s in r["relevant_sections"]}),
            "relevant_sections": r["relevant_sections"], "required_evidence_groups": r["required_evidence_groups"],
            "multiple_evidence_groups_required": len(r["required_evidence_groups"]) > 1,
            "multiple_sections_required": r["multiple_sections_required"],
            "context_sections_not_positive_labels": r["context_sections"],
        } for r in selected},
    )
    return selected, metadata


def expected_dispositions(record: dict) -> list[str]:
    return {"answerable": ["answered", "limited_answer"], "ambiguous": ["clarification"],
            "unsupported": ["insufficient_evidence"], "fixture-dependent": []}[record["classification"]]


def ensure_new_artifacts(*paths: Path) -> None:
    resolved = [p.resolve() for p in paths]
    if len(set(resolved)) != len(resolved) or any(p.exists() for p in resolved):
        raise EvaluationError("Output already exists or paths overlap; choose new artifact paths")


def write_new(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)
