---
document_id: SYN-BENEFICIARY
title: Beneficiary Validation Runbook
version: 1.0.0
effective_date: 2026-10-28
document_type: runbook
source_path: data/knowledge/documents/beneficiary_validation_runbook.md
---

# Beneficiary Validation Runbook

Synthetic educational material — not an actual bank policy.

Audience: payment initiation support and beneficiary maintenance analysts at
Northstar Demo Payments, the payments operations unit of fictional Northstar Demo
Regional Bank, a U.S. regional bank. Version 1.0.0 is the initial current corpus
version. Beneficiary/payee are domain terms; the checks and format conventions
below are fictional local procedures, not actual banking or regulatory standards.
This runbook cannot authorize execution, release, settlement, or control overrides.

## BV-CHECKS — Scope, terms, and required fields

**section_id: BV-CHECKS**

Beneficiary and payee mean the intended recipient. A verified beneficiary record
is a synthetic maintenance record whose source and reviewer have been recorded;
a requester message alone is not such a record. Validation checks supplied details,
not available funds, sanctions clearance, payment approval, or receipt of money.

Prerequisites: payment/entry reference, rail, synthetic beneficiary reference,
submitted name and account reference, validation code, event timestamp/source,
and verified comparison record. Record the case fields in
`SYN-EXCEPTION/EX-EVIDENCE`. For “it failed” without these details, begin with
`SYN-EXCEPTION/EX-TRIAGE` rather than guessing a validation cause.

1. Preserve the submitted details and exact code.
2. Identify whether the issue is name comparison, account format, or both.
3. Follow the relevant branch; resolve each reported issue separately.
4. Revalidate corrected details and document review before further preparation.

## BV-NAME — Resolve a payee name mismatch

**section_id: BV-NAME**

`SYN-BEN-301` means name mismatch, as defined by
`SYN-ERROR-CATALOG/EC-BENEFICIARY`. A payee label differing from the verified
account-holder record needs investigation even if the account reference is well formed.

1. Compare the submitted name and verified record; record the discrepancy.
2. Ask Beneficiary Maintenance to verify the intended recipient through the
   recorded synthetic maintenance workflow. Do not assume a nickname or different
   company name is equivalent solely because it looks similar.
3. If the submitted detail is wrong, obtain verified correction under
   `SYN-BENEFICIARY/BV-CORRECT`. If the comparison record is disputed, stop and
   escalate instead of changing it to make the check pass.
4. Retain unresolved status until correction and revalidation evidence exist.

Do not bypass the name check, remove the code manually, or claim that resolving
the mismatch establishes ownership or settlement beyond the available evidence.

## BV-FORMAT — Resolve an invalid account-reference format

**section_id: BV-FORMAT**

`SYN-BEN-302` means account format invalid. For this corpus only, beneficiary
account references use `SYN-ACCT-` followed by four decimal digits, for example
`SYN-ACCT-4101`. This is a fictional identifier syntax, not a real account-number
or routing-number specification. It tests format, not whether an account exists.

1. Compare the supplied reference with this exact synthetic convention.
2. Identify the missing prefix, wrong digit count, or nondecimal suffix; do not
   fabricate digits, pad a number, or guess the destination.
3. Obtain the intended reference from verified maintenance evidence.
4. Apply `SYN-BENEFICIARY/BV-CORRECT` and revalidate both format and any outstanding
   name mismatch. A format correction cannot resolve a name mismatch by itself.

## BV-CORRECT — Verified correction and revalidation

**section_id: BV-CORRECT**

1. Link the original instruction and case; retain original field values.
2. Record the proposed corrected field, synthetic evidence reference, evidence
   source/timestamp, reason, and maintenance reviewer who verified the correction.
3. Have a second reviewer, distinct from the preparing analyst, confirm that
   the change matches the verified recipient record. Record reviewer and outcome.
4. Rerun the relevant synthetic validation checks on the proposed details and
   retain each result, timestamp, and reference, including remaining failures.
5. Link the original and corrected versions; never rewrite historical evidence.
6. Return the reviewed result to the rail-specific case owner. For ACH return
   correction, `SYN-ACH-RETURNS/AR-NEXT` adds reconciliation, duplicate checks, and
   ACH supervisor review. Validation alone does not satisfy those gates.

Example: `SYN-BENEFICIARY-41` in case `SYN-CASE-3003` has a name discrepancy
between fictional Cedar Lantern Demo Supplies and its verified maintenance
record. The preparer records the corrected name, independent reviewer, and new
validation result; the payment remains subject to its separate workflow.

## BV-ESCALATE — Unresolved discrepancies and boundaries

**section_id: BV-ESCALATE**

Stop and escalate missing verification, conflicting maintenance records, a
request to bypass checks, repeated validation failures, or unresolved name and
format issues. Route to Beneficiary Maintenance through
`SYN-EXCEPTION/EX-ESCALATE`, supplying original/corrected values, evidence,
review results, and the unresolved question. Record owner and next checkpoint.

Do not mark the case corrected while required evidence is absent. Report only
the supported validation outcome. Consult `SYN-STATUS/SS-STATES` for the separate
payment lifecycle: a validated beneficiary is not evidence that a payment settled.
Real account formats, fraud thresholds, sanctions decisions, and live recipient
identity cannot be established from this runbook. Version history: 1.0.0,
2026-10-28, initial synthetic runbook; no prior approved version supplied.
