---
document_id: SYN-ACH-RETURNS
title: ACH Returns Guide
version: 1.0.0
effective_date: 2026-10-28
document_type: guide
source_path: data/knowledge/documents/ach_returns_guide.md
---

# ACH Returns Guide

Synthetic educational material — not an actual bank policy.

Audience: ACH operations and reconciliation analysts at Northstar Demo Payments,
the payments operations unit of fictional Northstar Demo Regional Bank, a U.S.
regional bank. Version 1.0.0 is the initial current corpus version. ACH is a
payment-network term; the codes, evidence gates, and workflows here are fictional
local conventions, not actual network return rules or regulatory requirements.
This guide authorizes no payment execution, release, or settlement.

## AR-SCOPE — ACH return versus wire recall

**section_id: AR-SCOPE**

A return is a recorded outcome associated with an original synthetic ACH entry.
A return notice must identify that entry; a caller saying “send it back” is not
itself return evidence. A wire recall requests recovery of a released wire and
belongs to `SYN-WIRE-RECALL/WR-SCOPE`. Ask for rail and current status when the
request is ambiguous. Do not apply wire recall steps to an ACH return.

Prerequisites for return handling are the original entry reference, a matched
return notice, its exact synthetic code, and a case owner. RETURNED has the
meaning in `SYN-STATUS/SS-RETURNS`; a notice does not by itself prove internal
reconciliation or authorize a replacement payment.

## AR-CLASSIFY — Classify the synthetic return reason

**section_id: AR-CLASSIFY**

| Exact code | Meaning | Initial handling |
| --- | --- | --- |
| SYN-ACH-201 | Account closed | Stop retry preparation; obtain verified replacement details and review. |
| SYN-ACH-202 | Account details invalid | Identify the invalid field, obtain verified correction, and revalidate. |

The canonical meanings and ownership are in `SYN-ERROR-CATALOG/EC-ACH`.
Neither code means a simple temporary timeout. Neither permits immediate retry.
Do not translate a real-world return code or an undocumented synthetic code into
one of these meanings. Preserve the literal received identifier and escalate an
unrecognized reason for classification.

## AR-INVESTIGATE — Collect and match evidence

**section_id: AR-INVESTIGATE**

1. Match return notice reference, original entry ID, rail, amount, currency, and
   synthetic beneficiary reference to the original instruction.
2. Record the exact code, notice timestamp, source, and last confirmed status.
3. Preserve the original details and identify the specific disputed or invalid
   field. Do not overwrite the original entry to hide the cause.
4. Check related cases and candidate replacements for duplicate risk.
5. Record reconciliation evidence separately from the notice; if a notice amount
   does not match the entry, stop classification and ask ACH Operations to review.

Use the full common case fields in `SYN-EXCEPTION/EX-EVIDENCE`, including owner,
actions, unresolved question, and next checkpoint. A screenshot without a matching
entry reference is insufficient to establish the returned entry's identity.

Example: notice `SYN-RETURN-2101` identifies `SYN-ACH-2001`, USD 240.00, with
`SYN-ACH-202`. Analyst `SYN-ANALYST-21` records the invalid account-reference
field and opens `SYN-CASE-3002`; the analyst does not label a different entry
returned simply because its amount matches.

## AR-NEXT — Correction, revalidation, and retry gates

**section_id: AR-NEXT**

1. For `SYN-ACH-201`, do not retry to the same closed account. Obtain verified
   replacement beneficiary details from the fictional beneficiary-maintenance
   workflow; absence of replacement details keeps the case unresolved.
2. For `SYN-ACH-202`, obtain verified correction of the identified invalid field.
   Follow `SYN-BENEFICIARY/BV-CORRECT` for evidence, change history, and revalidation.
3. Confirm the return is matched and reconciled, check for pending replacements,
   and resolve duplicate suspicion under `SYN-EXCEPTION/EX-DUPLICATE`.
4. Have the ACH Operations supervisor review corrected details, revalidation
   result, return evidence, and duplicate assessment. Record the review outcome.
5. Only a complete favorable review permits preparing a replacement proposal for
   the separate simulated approval workflow. This guide does not authorize
   sending, releasing, or settling it. Link a distinct proposed instruction to
   the original case; preserve the original returned entry.

Failed revalidation, unresolved reconciliation, or missing review blocks further
retry preparation. Corrected spelling alone is not evidence that a closed
account is usable. Return closure and replacement approval are separate outcomes.

## AR-ESCALATE — Unresolved and duplicate-risk cases

**section_id: AR-ESCALATE**

Route unknown codes, unmatched notices, unavailable correction evidence, disputed
amounts, and failed revalidation to ACH Operations. Involve Beneficiary Maintenance
for detail corrections and Reconciliation for unmatched return accounting. If a
replacement may already exist, stop retries and apply the duplicate workflow.
Use `SYN-EXCEPTION/EX-ESCALATE` for routing and handoff records.

At the owner-recorded follow-up checkpoint, document outstanding evidence and
escalate unresolved cases to the ACH Operations supervisor. No universal return
deadline or retry limit is supplied. Close with matched outcome, reconciliation,
and correction/review evidence where applicable under `SYN-EXCEPTION/EX-CLOSE`.

This guide cannot identify a live return, define undocumented codes, state real
network deadlines, or establish legal obligations. Version history: 1.0.0,
2026-10-28, initial synthetic guide; no prior approved version supplied.
