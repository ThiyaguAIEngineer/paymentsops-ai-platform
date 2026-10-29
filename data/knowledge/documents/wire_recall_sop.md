---
document_id: SYN-WIRE-RECALL
title: Wire Recall SOP
version: 1.0.0
effective_date: 2026-10-28
document_type: sop
source_path: data/knowledge/documents/wire_recall_sop.md
---

# Wire Recall SOP

Synthetic educational material — not an actual bank policy.

Northstar Demo Payments is the fictional payments operations unit of fictional
Northstar Demo Regional Bank, a U.S. regional bank used only for this simulation.
Audience: wire operations analysts and exception supervisors. Version 1.0.0 is
the initial current corpus version; no earlier approved procedure is supplied.
Wire, recall, and settlement are payment-domain terms; all workflow rules below
are invented local procedures, not network rules or regulatory requirements.
This document grants no authority to execute, release, or settle a payment.

## WR-SCOPE — Recall versus cancellation

**section_id: WR-SCOPE**

A recall is a request to recover a wire already released from the fictional
operator's processing boundary. It is a request, not a reversal guarantee.
Cancellation is a request to stop an instruction before release. Do not use
these terms interchangeably when someone asks to “reverse” or “get back” a payment.
For RECEIVED or ACCEPTED instructions, route a cancellation assessment to Wire
Operations; this SOP does not define cancellation execution. For RELEASED or
SETTLED wires, assess recall prerequisites. For an uncertain release status,
investigate before selecting either procedure. ACH returns follow
`SYN-ACH-RETURNS/AR-SCOPE`, not this wire workflow.

## WR-ELIGIBILITY — Confirm status and prerequisites

**section_id: WR-ELIGIBILITY**

Prerequisites: an identifiable synthetic wire, a documented request from a
verified fictional requester, and current release evidence. Read status meanings
in `SYN-STATUS/SS-STATES` and evidence requirements in `SYN-STATUS/SS-EVIDENCE`.

1. Match the request to its payment ID and original instruction reference.
2. Check rail, last confirmed status, status timestamp, and evidence source.
3. Check for an existing recall case to avoid duplicate requests.
4. Verify requester authority through the simulation's recorded requester review;
   record the reviewer and outcome rather than accepting an unverified message.
5. If mandatory details or verification are missing, record `SYN-WR-101`
   (recall prerequisites missing), stop request preparation, and obtain them.
6. If released or settled evidence is available and prerequisites are complete,
   prepare the recall case. Recovery remains uncertain even for a settled wire.

A rejected wire without release evidence does not become recall-eligible merely
because the requester wants a refund. Contradictory evidence requires escalation.

## WR-REQUEST — Prepare the recall request and case

**section_id: WR-REQUEST**

Required details: payment ID, original instruction reference, rail, original
amount and currency, synthetic sender and beneficiary references, requester
reference, requester-verification reviewer/outcome, reason for recall, last
confirmed payment status, status timestamp/source, related case references, and
the proposed case owner. Record these using `SYN-EXCEPTION/EX-EVIDENCE`.

1. Create or link one recall case and preserve the original instruction unchanged.
2. Record the required details and supporting evidence; identify missing items.
3. Ask the Wire Operations supervisor to review completeness and duplicate risk.
4. Record a simulated request reference only when that review is complete.
   This is an educational case record, not transmission to a bank or network.
5. Assign an owner and record the next follow-up checkpoint agreed by that owner.
   This SOP establishes no universal elapsed-time deadline.

Example: fictional requester `SYN-REQUESTER-11` asks to recover `SYN-WIRE-1001`
for USD 125.00 after release. Case `SYN-CASE-3001` links the release event and
requester verification. The analyst prepares a recall request; no recovery is
booked and no payment is executed by this procedure.

## WR-TRACK — Track acknowledgment separately from recovery

**section_id: WR-TRACK**

| Recall case state | Required evidence | Interpretation |
| --- | --- | --- |
| REQUEST_PREPARED | Complete reviewed case | Request is ready for simulated follow-up. |
| ACKNOWLEDGED | Response referencing the request | Receipt acknowledged; recovery not established. |
| RESPONSE_PENDING | No definitive outcome | Record `SYN-WR-102`: recall response pending. |
| RECOVERED | Matched recovery confirmation and reconciliation evidence | Recovery supported for the confirmed amount only. |
| DECLINED | Definitive response with reference | Recovery request declined; preserve reason. |

These are case states, separate from payment lifecycle states. An acknowledgment
does not undo SETTLED or prove recovered funds. Record response timestamps,
references, and any confirmed partial amount; do not infer full recovery from a
partial confirmation. See `SYN-STATUS/SS-RETURNS`. Never resubmit the original
wire as a way to resolve a pending recall.

## WR-ESCALATE — Escalation, communication, and boundaries

**section_id: WR-ESCALATE**

Escalate missing prerequisites that cannot be verified, inconsistent payment or
response references, disputed amounts, duplicate requests, and an outcome still
unresolved at the recorded follow-up checkpoint. Route to the Wire Operations
supervisor using `SYN-EXCEPTION/EX-ESCALATE`; provide the request, evidence,
actions already taken, and precise unresolved question. Update the case owner
and next checkpoint after review.

Communicate “request acknowledged; recovery not confirmed” when that is all the
evidence supports. Close only with a documented outcome and reconciliation for
any claimed recovery, following `SYN-EXCEPTION/EX-CLOSE`. The catalog owns exact
code definitions in `SYN-ERROR-CATALOG/EC-WIRE`.

No recall success rate, legal deadline, external-bank policy, live payment result,
or historical 2024 procedure is established here. Version history: 1.0.0,
2026-10-28, initial synthetic procedure; no superseded text is included.
