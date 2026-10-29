"""Conservative policy-date applicability using existing version metadata only."""

from dataclasses import dataclass
from datetime import date
import re


@dataclass(frozen=True)
class PolicyPeriod:
    start: date
    end: date
    version: str | None = None


def requested_policy_period(question: str, today: date) -> tuple[PolicyPeriod | None, str | None]:
    """Parse ISO as-of dates, whole years, last year, and explicit versions.

Ambiguous temporal language asks for clarification, never invents a period.
Years mean the whole year; metadata must cover the entire requested interval.
"""
    text = question.lower()
    policy_intent = re.search(r"\b(polic\w*|procedur\w*|sop|rules?|require\w*|runbook|guide|version|as of)\b", text)
    temporal_intent = re.search(r"\b(?:in|during|before|after|until|since)\s+\d{4}\b|\b(?:last|previous) year\b", text)
    if not policy_intent and not temporal_intent:
        return None, None
    if re.search(r"\b(?:before|after|until|since)\s+\d{4}\b", text):
        return None, "Please specify the policy as-of date; an open-ended period cannot be verified from a single version."
    version_match = re.search(r"\b(?:version\s*|v)(\d+\.\d+(?:\.\d+)?)\b", text)
    version = version_match.group(1) if version_match else None
    dates = re.findall(r"(?<![\w-])\d{4}-\d{2}-\d{2}(?![\w-])", text)
    years = re.findall(r"(?<![\w-])\d{4}(?![\w-])", re.sub(r"\d{4}-\d{2}-\d{2}", "", text))
    if len(dates) + len(set(years)) > 1:
        return None, "Please specify one policy as-of date or year; comparisons across periods require separate evidence."
    try:
        if dates:
            day = date.fromisoformat(dates[0])
            return PolicyPeriod(day, day, version), None
        if years:
            year = int(years[0])
            return PolicyPeriod(date(year, 1, 1), date(year, 12, 31), version), None
        if re.search(r"\b(last|previous) year\b", text):
            return PolicyPeriod(date(today.year - 1, 1, 1), date(today.year - 1, 12, 31), version), None
    except ValueError:
        return None, "Please provide a valid policy as-of date in YYYY-MM-DD format."
    if re.search(r"\b(historical|formerly|old|earlier|past|previous|prior)\b", text) and not version:
        return None, "Which policy as-of date or explicit document version do you need?"
    # Current-policy and named-version questions still exclude future evidence.
    return PolicyPeriod(today, today, version), None


def applicable_chunk(chunk, period: PolicyPeriod, catalog: tuple, today: date) -> bool:
    """Latest known version must cover the whole interval, without extrapolation.

No valid-through date exists in this corpus: the next known version bounds the
previous one. This is applicability within the provided corpus, not proof that
the archive is historically exhaustive. Future-period assertions are disallowed.
"""
    if period.end > today or chunk.effective_date > period.start:
        return False
    if period.version is not None and chunk.document_version != period.version:
        return False
    versions = {(c.document_version, c.effective_date) for c in catalog if c.document_id == chunk.document_id}
    if any(effective > chunk.effective_date and effective <= period.end for _, effective in versions):
        return False
    if len({v for v, effective in versions if effective == chunk.effective_date}) > 1:
        return False
    return True
