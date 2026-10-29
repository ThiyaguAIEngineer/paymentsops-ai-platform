---
document_id: SYN-ERROR-CATALOG
title: Payment Error-Code Catalog
version: 1.0.0
effective_date: 2026-10-28
document_type: catalog
source_path: data/knowledge/documents/payment_error_code_catalog.md
---

# Payment Error-Code Catalog

Synthetic educational material — not an actual bank policy.

Audience: operations analysts and first-line support at Northstar Demo Payments,
the payments operations unit of fictional Northstar Demo Regional Bank, a U.S.
regional bank. Version 1.0.0 is the initial current corpus version. This catalog
owns the eight canonical code meanings below. Detailed actions belong to the
referenced procedures. These are invented local codes, not real ACH return codes,
network responses, regulatory requirements, or authority to execute payments.

## EC-LOOKUP — Exact identifiers and unknown codes

**section_id: EC-LOOKUP**

Prerequisites: capture the literal code, rail/component, payment or case reference,
status, event timestamp, and evidence source. A code describes a condition, not
the complete payment outcome. “Retry” means preparing a proposed new attempt,
not authorization to transmit, release, or settle it.

1. Compare the complete identifier to this catalog, preserving digits and hyphens.
2. Read its meaning, restrictions, and governing procedure together.
3. If rail or status is unknown, obtain it before recommending an action.
4. For an undocumented identifier, state that its meaning is not established,
   preserve the received text, and route to the relevant operations owner using
   `SYN-EXCEPTION/EX-TRIAGE`. Do not guess from a neighboring code or external code set.
5. If this catalog and an equally current procedure conflict, stop the disputed
   action and request owner review; do not silently select one instruction.

Example: `SYN-BEN-301` in case `SYN-CASE-3003` identifies a name mismatch. It does
not establish the payment's settlement status or mean account format is invalid.

## EC-WIRE — Wire recall codes

**section_id: EC-WIRE**

| Code | Meaning | Impact | Initial action | Retry restriction | Owner | Governing section |
| --- | --- | --- | --- | --- | --- | --- |
| SYN-WR-101 | Recall prerequisites missing | Recall request preparation blocked | Obtain missing request details or verification | Do not prepare a duplicate request or resend the payment | Wire Operations | SYN-WIRE-RECALL/WR-ELIGIBILITY |
| SYN-WR-102 | Recall response pending | Recovery outcome unresolved | Check request reference and record follow-up checkpoint | Do not resend the original wire to resolve pending recall | Wire Operations | SYN-WIRE-RECALL/WR-TRACK |

A pending response is neither a decline nor proof of recovery. Request receipt
and recovered funds require different evidence.

## EC-ACH — ACH return codes

**section_id: EC-ACH**

| Code | Meaning | Impact | Initial action | Retry restriction | Owner | Governing section |
| --- | --- | --- | --- | --- | --- | --- |
| SYN-ACH-201 | Account closed | Original destination cannot be reused for retry | Obtain verified replacement details and review | No immediate retry; correction, reconciliation, duplicate checks, and supervisor review required | ACH Operations | SYN-ACH-RETURNS/AR-NEXT |
| SYN-ACH-202 | Account details invalid | Supplied destination details require correction | Identify invalid field and obtain verified correction | No immediate retry; revalidation, reconciliation, duplicate checks, and supervisor review required | ACH Operations | SYN-ACH-RETURNS/AR-NEXT |

Neither identifier is an actual network return code. A corrected field does not
prove that an account previously reported closed has reopened.

## EC-BENEFICIARY — Beneficiary validation codes

**section_id: EC-BENEFICIARY**

| Code | Meaning | Impact | Initial action | Retry restriction | Owner | Governing section |
| --- | --- | --- | --- | --- | --- | --- |
| SYN-BEN-301 | Name mismatch | Beneficiary identity/detail discrepancy unresolved | Compare submitted name with verified beneficiary record | Do not bypass validation; verified correction and revalidation required | Beneficiary Maintenance | SYN-BENEFICIARY/BV-NAME |
| SYN-BEN-302 | Account format invalid | Account-reference syntax fails synthetic format check | Identify format failure against the fictional reference convention | Do not bypass validation; verified correction and revalidation required | Beneficiary Maintenance | SYN-BENEFICIARY/BV-FORMAT |

These checks differ: a well-formed account reference may still have a name
mismatch. Passing either check alone establishes neither payment approval nor settlement.

## EC-STATUS — Status integration codes

**section_id: EC-STATUS**

| Code | Meaning | Impact | Initial action | Retry restriction | Owner | Governing section |
| --- | --- | --- | --- | --- | --- | --- |
| SYN-STS-401 | Status update delayed | Current lifecycle state uncertain | Inspect last confirmed event and matching evidence; request reconciliation review | No resend while status or duplicate risk remains unresolved | Reconciliation | SYN-STATUS/SS-DELAY |

Delayed communication is not rejection. Do not replace the last confirmed state
with SETTLED or REJECTED based on elapsed time alone.

## EC-EXCEPTION — Case-handling codes

**section_id: EC-EXCEPTION**

| Code | Meaning | Impact | Initial action | Retry restriction | Owner | Governing section |
| --- | --- | --- | --- | --- | --- | --- |
| SYN-EXC-501 | Duplicate suspected | More than one instruction may represent the same obligation | Link candidate instructions and investigate distinctness | Hold retry preparation until duplicate risk is resolved and reviewed | Payment Exceptions | SYN-EXCEPTION/EX-DUPLICATE |

Matching amounts alone do not prove a duplicate. Closure requires documented
comparison, outcomes, and review under `SYN-EXCEPTION/EX-CLOSE`. Escalate unresolved
or contradictory evidence via `SYN-EXCEPTION/EX-ESCALATE`.

This catalog supplies no live status, legal deadlines, fraud thresholds, sanctions
treatments, or meanings for identifiers not listed above. Version history: 1.0.0,
2026-10-28, initial eight-code catalog; no superseded definitions are included.
