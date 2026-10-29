---
document_id: SYN-EXCEPTION
title: Payment Exception Handling SOP
version: 1.0.0
effective_date: 2026-10-28
document_type: sop
source_path: data/knowledge/documents/payment_exception_handling_sop.md
---

# Payment Exception Handling SOP

Synthetic educational material — not an actual bank policy.

Audience: cross-rail operations analysts and supervisors at Northstar Demo Payments,
the payments operations unit of fictional Northstar Demo Regional Bank, a U.S.
regional bank. Version 1.0.0 is the initial current corpus version. These case
handling rules are invented local workflows, not legal or network requirements.
An exception is a condition requiring investigation; a retry is preparation of a
proposed new attempt. This SOP authorizes no execution, release, or settlement.

## EX-TRIAGE — Identify rail, status, and error before action

**section_id: EX-TRIAGE**

1. Obtain the synthetic payment or entry reference, rail, last confirmed status,
   event timestamp/source, exact error code if present, and the analyst's question.
2. Determine whether evidence shows validation failure, an ACH return, a recall
   request, a delayed status update, or suspected duplication. Preserve uncertainty.
3. Check for an existing case and link related instructions before creating one.
4. Assign a case owner and follow the relevant specialist procedure. Do not
   infer “safe to retry” from the word failed or from a missing update.
5. If rail/status/code are missing, ask for them. “Reverse this payment” requires
   rail and release status before choosing return, recall, or cancellation review.

Consult `SYN-ERROR-CATALOG/EC-LOOKUP` for exact identifiers. A case open in an
analyst queue is not a payment lifecycle state. Use `SYN-STATUS/SS-STATES` for
lifecycle meanings and `SYN-STATUS/SS-DELAY` for delayed evidence.

## EX-EVIDENCE — Required case record and prerequisites

**section_id: EX-EVIDENCE**

| Case field | Required content |
| --- | --- |
| Identity | Case ID, payment/entry reference, rail, related case/instruction references |
| Instruction context | Original amount/currency and synthetic sender/beneficiary references |
| Observed condition | Exact code or explicit “no code supplied,” last confirmed status |
| Evidence provenance | Event/notice/request reference, timestamp, source, and preserved excerpt |
| Request context | Requester reference, requested outcome, verification record when applicable |
| Work performed | Actions taken, original and corrected details where relevant, results and reviewers |
| Ownership | Preparing analyst, current owner, escalation recipient if any |
| Follow-up | Unresolved question, missing evidence, next checkpoint and its owner |

Do not invent missing values. Record “not available” and seek evidence before an
action that depends on it. Retain original evidence and append corrections with
review history. Rail-specific prerequisites add to this common record: recall
request details in `SYN-WIRE-RECALL/WR-REQUEST`, return retry gates in
`SYN-ACH-RETURNS/AR-NEXT`, and correction evidence in `SYN-BENEFICIARY/BV-CORRECT`.

## EX-DUPLICATE — Hold retries while duplicate risk is unresolved

**section_id: EX-DUPLICATE**

`SYN-EXC-501` means duplicate suspected, per `SYN-ERROR-CATALOG/EC-EXCEPTION`.
A shared amount is a lead, not proof of duplication. A delayed status can hide
an already released payment, so do not resend merely to obtain a new status.

1. Hold retry preparation and identify all candidate instructions and cases.
2. Compare original obligation/reference, rail, amount/currency, synthetic payee,
   instruction timestamps, release references, and confirmed lifecycle outcomes.
3. Ask the rail owner and Reconciliation to resolve missing or inconsistent
   evidence. Record whether candidates are distinct obligations or possible repeats.
4. Obtain Payment Exceptions supervisor review of the comparison and outcome.
   Document the reviewer, decision, and supporting references.
5. Only after duplicate risk is resolved and reviewed may a separate replacement
   proposal proceed through its rail-specific gates. This does not approve payment.

Example: `SYN-WIRE-1002` and `SYN-WIRE-1003` both show USD 85.00 for fictional
Maple Kite Demo Services. Case `SYN-CASE-3004` links them. Distinct verified
obligation references may explain the match; absent those references, keep the
case unresolved rather than declaring a duplicate or resending either payment.

## EX-ESCALATE — Routing and unresolved cases

**section_id: EX-ESCALATE**

| Condition | Primary owner | Additional review |
| --- | --- | --- |
| Wire recall or cancellation assessment | Wire Operations | Wire Operations supervisor |
| ACH return classification or retry proposal | ACH Operations | ACH Operations supervisor |
| Beneficiary correction or verification conflict | Beneficiary Maintenance | Independent maintenance reviewer |
| Delayed or conflicting settlement evidence | Reconciliation | Relevant rail owner |
| Suspected duplicate across cases | Payment Exceptions | Rail owner and Reconciliation |

Escalate immediately within the simulation when evidence conflicts, an analyst
is asked to bypass a prerequisite, or duplicate risk blocks progress. Also
escalate any case unresolved at its recorded follow-up checkpoint. Supply the
common case record, actions attempted, precise unresolved question, and requested
owner decision. Record recipient acknowledgment, assigned owner, and next checkpoint;
do not treat handing off a case as proof that its condition is resolved.
No numerical service-level deadline is established by this corpus.

## EX-CLOSE — Closure evidence and audit notes

**section_id: EX-CLOSE**

1. Record the final disposition and its evidence references. Distinguish resolved,
   declined, or still unresolved; a queue transfer cannot be called resolution.
2. Reconcile any claimed funds movement with matched confirmation evidence.
3. For suspected duplicates, retain the candidate comparison, distinct-obligation
   or duplicate determination, each known payment outcome, reconciliation findings,
   supervisor review, and the recorded decision about further retry preparation.
4. For corrections, retain original/corrected values, verification, revalidation,
   and applicable rail review. For recall, retain acknowledgment separately from
   confirmed recovery or decline. Cite the governing procedure.
5. Record closure reviewer, timestamp, owner, related cases, and communication
   of the supported outcome. If material evidence or review is missing, keep the
   case open or escalated rather than recording resolved closure.

This SOP cannot determine live transaction facts, prescribe legal deadlines,
or resolve two equally authoritative contradictory instructions without owner
review. Version history: 1.0.0, 2026-10-28, initial synthetic SOP; no superseded
instructions are included.
