---
document_id: SYN-STATUS
title: Settlement and Payment Status Guide
version: 1.0.0
effective_date: 2026-10-28
document_type: guide
source_path: data/knowledge/documents/settlement_payment_status_guide.md
---

# Settlement and Payment Status Guide

Synthetic educational material — not an actual bank policy.

Audience: payment monitoring, reconciliation, and support analysts at Northstar
Demo Payments, the payments operations unit of fictional Northstar Demo Regional
Bank, a U.S. regional bank. Version 1.0.0 is the initial current corpus version.
Settlement, ACH, and wire are domain terms; this lifecycle and its evidence rules
are fictional local conventions, not network guarantees or regulatory requirements.
The guide describes evidence interpretation and cannot execute, release, or settle
payments. Week 1 validation decisions are separate from these lifecycle states.

## SS-STATES — Lifecycle glossary and permitted transitions

**section_id: SS-STATES**

| State | Meaning in this simulation | Possible next recorded state |
| --- | --- | --- |
| RECEIVED | Instruction captured; acceptance not yet established | ACCEPTED or REJECTED |
| ACCEPTED | Initial intake accepted; release and settlement not established | RELEASED or REJECTED |
| RELEASED | Instruction crossed the fictional processing release boundary | SETTLED or REJECTED, with matched outcome evidence |
| SETTLED | Matched settlement confirmation and reconciliation evidence recorded | RETURNED where a matched later return is evidenced |
| REJECTED | Definitive rejection event matched to the instruction | No automatic transition for the same instruction |
| RETURNED | Matched return outcome recorded against the original instruction | Reconciliation follow-up; no automatic replacement |

These transitions are a simplified educational model, not a representation of
every payment network. Events must have supporting references; do not advance a
state simply because enough time elapsed. ACCEPTED does not mean SETTLED.
Validation success, approval readiness, and a recipient's acknowledgment are not
settlement confirmation. RELEASED or SETTLED wire recovery requests use
`SYN-WIRE-RECALL/WR-ELIGIBILITY`; pre-release cancellation assessment is separate.

## SS-EVIDENCE — What establishes a confirmed status?

**section_id: SS-EVIDENCE**

Prerequisites: payment ID, rail, original reference, amount/currency, last confirmed
state, and event provenance. Preserve each event's reference, timestamp, source,
and relation to the instruction. The synthetic event journal supports intake and
release events; a matched settlement confirmation plus Reconciliation's matched
record supports SETTLED. A return notice supports a matched return outcome,
with reconciliation tracked separately under `SYN-STATUS/SS-RETURNS`.

1. Match payment/reference, rail, amount/currency, and synthetic counterparties.
2. Inspect the event type and evidence source; retain the last confirmed event.
3. For a settlement claim, obtain both settlement confirmation and matched
   reconciliation record. Missing one leaves settlement unconfirmed.
4. For contradictory events or unmatched references, preserve both records and
   escalate; do not choose whichever has the latest displayed timestamp.

Example: `SYN-WIRE-1004` has an ACCEPTED event but no release or settlement
confirmation. The analyst may report accepted, settlement unconfirmed. The
analyst cannot report settled because the dashboard has stopped refreshing.

## SS-DELAY — Delayed or unknown status updates

**section_id: SS-DELAY**

`SYN-STS-401` means status update delayed, as defined by
`SYN-ERROR-CATALOG/EC-STATUS`. A delayed update is a communication/evidence
condition, not a lifecycle rejection. Unknown current status means evidence is
insufficient; it is not permission to resend.

1. Preserve the last confirmed state and timestamp; mark current status uncertain.
2. Inspect the synthetic event journal for matching release/outcome references,
   then ask Reconciliation to match available confirmation records.
3. Check related instructions and cases for a possible replacement or duplicate.
   Hold retry preparation while status or duplicate risk is unresolved, following
   `SYN-EXCEPTION/EX-DUPLICATE`.
4. Record missing evidence and route to Reconciliation and the relevant rail
   owner using `SYN-EXCEPTION/EX-ESCALATE`. Escalate conflicting evidence immediately
   and any unresolved case at its owner-recorded follow-up checkpoint.
5. Update the case only when matched evidence supports a new conclusion. If
   uncertainty remains, report it explicitly and maintain the hold.

Example: delayed update for `SYN-ACH-2002` leaves ACCEPTED as the last confirmed
state. The analyst gathers event references and opens a reconciliation case;
the analyst does not send another entry to test whether the first one succeeded.
No fixed elapsed-time threshold or automatic retry allowance is defined.

## SS-RETURNS — Returns, recall acknowledgments, and recovery

**section_id: SS-RETURNS**

An ACH return is an outcome notice matched to an original entry, not a wire recall
request. A matched notice can establish RETURNED while return-accounting
reconciliation remains open. Follow `SYN-ACH-RETURNS/AR-CLASSIFY` for reason handling
and its correction/review gates before preparing a replacement proposal.

A wire recall acknowledgment confirms receipt of a recovery request only. It
does not establish returned funds, invalidate earlier settlement evidence, or
guarantee recovery. Recall case states and required outcome evidence are defined
in `SYN-WIRE-RECALL/WR-TRACK`. Confirmed recovery requires a matched recovery
confirmation and reconciliation evidence; report only the confirmed amount.
Do not force recall case states into the payment-state table or infer RETURNED
from an acknowledgment. Preserve the original payment and link later recovery
evidence as a separate case outcome.

## SS-ESCALATE — Reconciliation and limits of evidence

**section_id: SS-ESCALATE**

Escalate mismatched payment references, disputed amounts, incompatible lifecycle
events, missing settlement evidence, or delayed outcomes still unresolved at the
recorded checkpoint. Reconciliation owns evidence matching; the rail owner owns
the operational follow-up. Use `SYN-EXCEPTION/EX-EVIDENCE` for the case record and
`SYN-EXCEPTION/EX-ESCALATE` for handoff. Do not close as settled, recovered, or
resolved without the respective evidence and review.

Current guidance is version 1.0.0 effective 2026-10-28. No earlier approved
version is provided; historical procedures cannot be reconstructed from this
guide. If equally current excerpts conflict, surface both and obtain owner review
instead of treating recency alone as authority. This guide provides no live
transaction access, external-bank status guarantees, or universal legal deadline.
Version history: 1.0.0, 2026-10-28, initial synthetic guide.
