"""Bounded analyst procedure lookup, separate from investigation facts and graph."""

from dataclasses import dataclass
from typing import Callable

from payment_ops.knowledge.service import AnswerResult, Citation, EvidencePassage, KnowledgeService
from payment_ops.investigation.state import InvestigationState
from payment_ops.services.decision_engine import CheckStatus


NO_PROCEDURE = "No sufficiently supported operational procedure was found in the available synthetic knowledge base."


@dataclass(frozen=True)
class ProcedureTopic:
    topic_id: str
    label: str
    question: str
    corpus_scope: str


TOPICS = (
    ProcedureTopic("exception", "General exception triage and case evidence",
                   "What common case evidence and initial triage does the synthetic Payment Exception Handling SOP require?",
                   "SYN-EXCEPTION / EX-TRIAGE and EX-EVIDENCE"),
    ProcedureTopic("beneficiary", "General beneficiary validation and correction",
                   "What verified correction and revalidation evidence does the synthetic Beneficiary Validation Runbook require?",
                   "SYN-BENEFICIARY / BV-CORRECT"),
    ProcedureTopic("recall", "General wire recall prerequisites",
                   "What are the synthetic wire recall prerequisites, and how does recall differ from cancellation?",
                   "SYN-WIRE-RECALL / WR-SCOPE and WR-ELIGIBILITY"),
    ProcedureTopic("status", "General payment status interpretation",
                   "What does ACCEPTED mean in the synthetic payment status guide, and does it establish settlement?",
                   "SYN-STATUS / SS-STATES"),
)
_TOPICS = {topic.topic_id: topic for topic in TOPICS}
STATUSES = {"answered", "limited_answer", "clarification", "insufficient_evidence", "unavailable"}
_REASONS = STATUSES | {"empty_question", "ambiguous_policy_period", "missing_transaction_context",
                       "policy_period_unsupported", "retrieval_failure", "empty_retrieval",
                       "provider_failure", "incomplete_evidence", "invalid_response", "unvalidated_response"}


@dataclass(frozen=True)
class GuidanceResult:
    topic_id: str
    answer: AnswerResult | None
    error_category: str | None = None


def finding_related_topics(snapshot: InvestigationState) -> tuple[str, ...]:
    """Suggest general triage from actual adverse checks, never a specific remedy.

    The validation engine does not perform corpus beneficiary-name/format checks
    or record release/settlement events. Those topics therefore remain manual
    educational lookups; simulator REJECTED is not a matched rejection event.
    """
    findings = snapshot.get("findings") or {}
    adverse = any(check.get("status") in {CheckStatus.REJECTED, CheckStatus.REVIEW, CheckStatus.UNAVAILABLE}
                  for check in findings.get("checks", []))
    return ("exception",) if adverse else ()


def _valid_envelope(answer) -> bool:
    """Check the public return contract, not a second RAG/citation validator.

    Grounding is established by KnowledgeService.ask. No raw provider response is
    accepted here. Non-answer bodies and rejected validation envelopes are hidden
    by presentation; accepted citations are preserved without rewriting passages.
    """
    if (not isinstance(answer, AnswerResult) or answer.status not in STATUSES
            or not isinstance(answer.answer, str) or answer.reason_code not in _REASONS
            or not isinstance(answer.citations, tuple)):
        return False
    if answer.status in {"answered", "limited_answer"} and (
        answer.reason_code != answer.status or not answer.answer.strip() or not answer.citations
    ):
        return False
    return all(isinstance(c, Citation) and type(c.number) is int and c.number > 0
               and all(isinstance(getattr(c, field), str) and getattr(c, field).strip()
                       for field in ("document_title", "document_id", "section_id", "document_version", "chunk_id", "source_path", "evidence_quote"))
               and isinstance(c.passages, tuple) and bool(c.passages)
               and all(isinstance(p, EvidencePassage) and isinstance(p.quote, str) and bool(p.quote.strip())
                       and isinstance(p.chunk_id, str) and isinstance(p.source_id, str)
                       and type(p.start) is int and type(p.end) is int and 0 <= p.start < p.end
                       for p in c.passages)
               for c in answer.citations)


def find_operational_guidance(topic_id: str, *,
                              service_factory: Callable[[], KnowledgeService]) -> GuidanceResult:
    """Only a fixed generic question crosses the existing public service boundary.

    No snapshot or transaction fields are accepted by this lookup function. Caller
    owns explicit-request gating and per-run/topic caching. Exceptions never expose
    provider messages or change investigation status.
    """
    topic = _TOPICS.get(topic_id)
    if topic is None:
        return GuidanceResult(topic_id, None, "unsupported_topic")
    try:
        answer = service_factory().ask(topic.question)
        if not _valid_envelope(answer):
            return GuidanceResult(topic_id, None, "malformed_response")
        return GuidanceResult(topic_id, answer)
    except Exception:
        return GuidanceResult(topic_id, None, "knowledge_unavailable")
