# Week 2 synthetic corpus and evaluation design

Planning only: the six knowledge documents do not exist yet. All source mappings,
section IDs, codes, and expected behaviors below are provisional until corpus review.
The proposed fictional operator is Northstar Demo Payments. Its procedures, codes,
and identifiers are synthetic educational examples, not real bank policies,
payment-network standards, or regulatory requirements. Example cases use identifiers
such as `SYN-WIRE-1001`, `SYN-ACH-2001`, and `SYN-CASE-3001`; no real customer data.

## Metadata contract

| Field | Scope and convention |
| --- | --- |
| document_id | Stable unique ID, e.g. `SYN-WIRE-RECALL`; independent of title changes. |
| title | Human-readable canonical document title. |
| version | Semantic version; initially proposed `1.0.0`. |
| effective_date | ISO `YYYY-MM-DD`; initially proposed `2026-10-28`, reviewed before release. |
| document_type | Controlled value: `sop`, `guide`, `catalog`, or `runbook`. |
| source_path | Repository-relative canonical Markdown path listed below. |
| section_id | Stable explicit section identifier attached to each section and inherited by chunks. |

Document fields live in front matter; sections carry explicit IDs, not IDs derived
from heading order. A chunk inherits all seven fields. Additional derived metadata:
chunk ID, source content hash, chunker version, and any exact error codes present.
The corpus manifest records approval/review dates and supersession relationships.

Generate deterministic chunk IDs from document ID, document version, section ID,
chunker version, and a digest of canonical chunk text. Identical input/configuration
must reproduce the same ID; changed text/version intentionally produces new IDs.
Reject duplicate sections or duplicate generated IDs rather than overwriting them.
Keep explicit section IDs stable so citations can be traced across revisions.

Each document should include a synthetic-data notice, scope, glossary, prerequisites,
numbered actions, stop/escalation conditions, worked synthetic examples, and version
history. Preserve literal codes, synonyms, question-like headings, and cross-references
as document ID plus section ID to support exact and semantic search.

## 1. Wire Recall SOP

- **ID/title/type:** `SYN-WIRE-RECALL` / Wire Recall SOP / `sop`.
- **Source:** `data/knowledge/documents/wire_recall_sop.md`.
- **Purpose:** Explain requests to recover a released synthetic wire, including
  status checks and uncertain outcomes; distinguish recall from pre-release cancellation.
- **Audience:** Wire operations analysts and exception supervisors.
- **Sections:** `WR-SCOPE` recall versus cancellation; `WR-ELIGIBILITY` status and
  prerequisites; `WR-REQUEST` request details and case creation; `WR-TRACK` follow-up
  states; `WR-ESCALATE` unresolved cases and communications.
- **Questions:** Can this status enter the recall workflow? What details are required?
  Does a recall acknowledgment mean funds were recovered? When should a case escalate?
- **Cross-references:** `SYN-STATUS/SS-STATES`, `SYN-EXCEPTION/EX-ESCALATE`,
  `SYN-ERROR-CATALOG/EC-WIRE`.
- **Codes:** `SYN-WR-101` recall prerequisites missing; `SYN-WR-102` recall response
  pending. The catalog owns definitions; this SOP owns the detailed procedure.

## 2. ACH Returns Guide

- **ID/title/type:** `SYN-ACH-RETURNS` / ACH Returns Guide / `guide`.
- **Source:** `data/knowledge/documents/ach_returns_guide.md`.
- **Purpose:** Explain classification, investigation, and permitted next steps for
  fictional ACH return cases. No real return codes or regulatory deadlines implied.
- **Audience:** ACH operations and reconciliation analysts.
- **Sections:** `AR-SCOPE` return versus recall; `AR-CLASSIFY` synthetic return reasons;
  `AR-INVESTIGATE` evidence and case details; `AR-NEXT` correction and retry gates;
  `AR-ESCALATE` unresolved or duplicate-risk cases.
- **Questions:** What does a synthetic account-closed return mean? Is immediate retry
  allowed? What evidence supports correction? Who handles an unresolved return?
- **Cross-references:** `SYN-ERROR-CATALOG/EC-ACH`, `SYN-BENEFICIARY/BV-CORRECT`,
  `SYN-EXCEPTION/EX-ESCALATE`, `SYN-STATUS/SS-RETURNS`.
- **Codes:** `SYN-ACH-201` account closed; `SYN-ACH-202` account details invalid.
  Proposed procedure requires correction/review before any retry, not automatic retry.

## 3. Payment Error-Code Catalog

- **ID/title/type:** `SYN-ERROR-CATALOG` / Payment Error-Code Catalog / `catalog`.
- **Source:** `data/knowledge/documents/payment_error_code_catalog.md`.
- **Purpose:** Canonical exact-code lookup, with meaning, rail/component, impact,
  initial action, retry restriction, owner, and link to the governing procedure.
- **Audience:** All operations analysts and first-line support.
- **Sections:** `EC-LOOKUP` identifier matching and unknown codes; `EC-WIRE` recall;
  `EC-ACH` returns; `EC-BENEFICIARY` validation; `EC-STATUS` status integration;
  `EC-EXCEPTION` case handling.
- **Questions:** What does this exact code mean? Is it retryable? Which runbook applies?
  How does one similar code differ from another?
- **Cross-references:** Every entry points to its owning procedure section in one
  of the other five documents. Catalog summaries must agree with those procedures.
- **Codes:** `SYN-WR-101`, `SYN-WR-102`, `SYN-ACH-201`, `SYN-ACH-202`,
  `SYN-BEN-301` name mismatch, `SYN-BEN-302` account format invalid,
  `SYN-STS-401` status update delayed, `SYN-EXC-501` duplicate suspected.
  All are invented identifiers. Preserve spelling and punctuation; an unknown
  identifier must not inherit a neighboring code's meaning.

## 4. Beneficiary Validation Runbook

- **ID/title/type:** `SYN-BENEFICIARY` / Beneficiary Validation Runbook / `runbook`.
- **Source:** `data/knowledge/documents/beneficiary_validation_runbook.md`.
- **Purpose:** Triage fictional beneficiary name/account validation failures without
  overriding controls or treating a corrected field as payment approval.
- **Audience:** Payment initiation support and beneficiary maintenance analysts.
- **Sections:** `BV-CHECKS` scope and required fields; `BV-NAME` name mismatch;
  `BV-FORMAT` account format issues; `BV-CORRECT` verified correction and revalidation;
  `BV-ESCALATE` unresolved discrepancies.
- **Questions:** What if the payee name does not match? How does format failure differ?
  What must happen after correcting details? Does validation prove settlement?
- **Cross-references:** `SYN-ERROR-CATALOG/EC-BENEFICIARY`,
  `SYN-EXCEPTION/EX-TRIAGE`, `SYN-STATUS/SS-STATES`.
- **Codes:** `SYN-BEN-301`, `SYN-BEN-302`. Never bypass checks to resolve these codes.

## 5. Payment Exception Handling SOP

- **ID/title/type:** `SYN-EXCEPTION` / Payment Exception Handling SOP / `sop`.
- **Source:** `data/knowledge/documents/payment_exception_handling_sop.md`.
- **Purpose:** Own common triage, evidence collection, case routing, escalation,
  duplicate prevention, and closure; defer rail-specific actions to their owners.
- **Audience:** Cross-rail operations analysts and supervisors.
- **Sections:** `EX-TRIAGE` identify rail/status/error; `EX-EVIDENCE` required case
  fields; `EX-DUPLICATE` duplicate suspicion and retry stop; `EX-ESCALATE` owner
  routing and unresolved cases; `EX-CLOSE` closure evidence and audit notes.
- **Questions:** What belongs in an escalation? What if two payments appear identical?
  Can I retry while status is unknown? What evidence supports case closure?
- **Cross-references:** `SYN-WIRE-RECALL/WR-REQUEST`, `SYN-ACH-RETURNS/AR-NEXT`,
  `SYN-BENEFICIARY/BV-CORRECT`, `SYN-STATUS/SS-DELAY`,
  `SYN-ERROR-CATALOG/EC-EXCEPTION`.
- **Codes:** `SYN-EXC-501`. Propose holding retry while duplicate risk is unresolved.

## 6. Settlement and Payment Status Guide

- **ID/title/type:** `SYN-STATUS` / Settlement and Payment Status Guide / `guide`.
- **Source:** `data/knowledge/documents/settlement_payment_status_guide.md`.
- **Purpose:** Define fictional lifecycle states and evidence needed to distinguish
  acceptance, release, settlement, return, and recall outcomes.
- **Audience:** Payment monitoring, reconciliation, and support analysts.
- **Sections:** `SS-STATES` state glossary and transition table; `SS-EVIDENCE`
  confirmation sources; `SS-DELAY` delayed/unknown updates; `SS-RETURNS` return and
  recall relationships; `SS-ESCALATE` unresolved reconciliation.
- **Questions:** Does ACCEPTED mean SETTLED? What if an update is delayed? Can an
  unknown status safely be retried? How do recall acknowledgment and recovery differ?
- **Cross-references:** `SYN-EXCEPTION/EX-DUPLICATE`, `SYN-WIRE-RECALL/WR-TRACK`,
  `SYN-ACH-RETURNS/AR-CLASSIFY`, `SYN-ERROR-CATALOG/EC-STATUS`.
- **Codes:** `SYN-STS-401`. Proposed states include RECEIVED, ACCEPTED, RELEASED,
  SETTLED, REJECTED, and RETURNED; a delayed update is not proof of rejection.

## Consistency and retrieval design

The error catalog owns code meanings; procedure documents own detailed actions;
the status guide owns lifecycle definitions; the exception SOP owns common routing.
Review cross-references together before release. Do not resolve inconsistent
instructions merely by choosing the newest date across unrelated documents.

Include exact identifiers alongside natural language synonyms such as payee /
beneficiary, send back / return, and recover a released wire / recall. Distinguish
closely related concepts explicitly: recall versus cancellation, ACH return versus
wire recall, name mismatch versus format failure, and accepted versus settled.
Define synthetic deadlines only if needed for a coherent example, with explicit
scope and units; do not import real-world policy assumptions.

## Preliminary evaluation matrix

Expected sources below are provisional. Full document IDs are defined above;
short source labels in this table map to those titles. Answerability assumes the
planned content is authored; it is not a claim about documents that exist today.
Clarification and abstention are distinct expected outcomes.

| ID | Question | Category | Expected source document(s) / section(s) | Answerable? | Expected behavior |
| --- | --- | --- | --- | --- | --- |
| Q01 | What details are required to open a wire recall request? | Simple factual | Wire Recall / WR-REQUEST | Yes | List required details with a citation; invent no fields. |
| Q02 | Does ACCEPTED mean a payment has settled? | Simple factual; related states | Status / SS-STATES | Yes | Explain the distinction and required settlement evidence. |
| Q03 | What does SYN-BEN-301 mean, and what should I do first? | Exact error-code lookup | Catalog / EC-BENEFICIARY; Beneficiary / BV-NAME | Yes | Match the exact code and cite meaning and first action. |
| Q04 | What does SYN-ACH-201 mean? Can I immediately retry? | Exact code; action restriction | Catalog / EC-ACH; ACH Returns / AR-NEXT | Yes | Explain account-closed meaning and correction/review gate. |
| Q05 | We already sent the wire and want to get the money back. Where do we start? | Semantic/paraphrased | Wire Recall / WR-ELIGIBILITY, WR-REQUEST | Yes | Recognize recall intent and prerequisites; promise no recovery. |
| Q06 | The payee label differs from the account holder. How do I resolve it? | Semantic/paraphrased | Beneficiary / BV-NAME, BV-CORRECT | Yes | Retrieve name-mismatch guidance despite different wording. |
| Q07 | A status update is delayed and the analyst wants to resend. What checks and escalation apply? | Multi-document | Status / SS-DELAY; Exception / EX-DUPLICATE, EX-ESCALATE | Yes | Combine status uncertainty and duplicate prevention with both sources. |
| Q08 | An ACH return cites invalid account details. What correction and case evidence are needed? | Multi-document | ACH Returns / AR-NEXT; Beneficiary / BV-CORRECT; Exception / EX-EVIDENCE | Yes | Combine relevant steps; do not substitute wire recall instructions. |
| Q09 | How do I reverse this payment? | Ambiguous | Wire Recall / WR-SCOPE; ACH Returns / AR-SCOPE; Status / SS-STATES | No, needs context | Ask rail and current status before prescribing a procedure. |
| Q10 | It failed. Should I retry? | Ambiguous | Exception / EX-TRIAGE; Catalog / EC-LOOKUP | No, needs context | Request exact error, rail, and status; avoid unconditional retry. |
| Q11 | How does a recall differ from cancellation before release? | Closely related procedures | Wire Recall / WR-SCOPE; Status / SS-STATES | Yes | Explain the boundary and status prerequisite. |
| Q12 | Is SYN-BEN-302 handled the same way as SYN-BEN-301? | Closely related codes | Catalog / EC-BENEFICIARY; Beneficiary / BV-NAME, BV-FORMAT | Yes | Distinguish format failure from name mismatch. |
| Q13 | What does SYN-ACH-299 mean? | Deliberately unanswerable; unknown code | No supporting source; Catalog / EC-LOOKUP for unknown-code handling | No | State the code is undocumented; never infer from SYN-ACH-201/202. |
| Q14 | Has real customer account 123456 received its payment today? | Deliberately unanswerable; live data | None | No | Explain lack of live transaction access; invent no status. |
| Q15 | What legally mandated recall deadline applies to every US bank? | Deliberately unanswerable; external policy | None | No | State synthetic corpus cannot establish legal requirements. |
| Q16 | Does an acknowledgment of my recall request guarantee recovery? | Factual; related outcomes | Wire Recall / WR-TRACK; Status / SS-RETURNS | Yes | Distinguish acknowledgment from confirmed recovery. |
| Q17 | An archived v0.9 draft says delayed status permits immediate retry; what applies now? | Superseded information | Current Status / SS-DELAY; Exception / EX-DUPLICATE; isolated archived fixture | Yes for current guidance | Use current approved guidance; identify archived fixture as superseded. |
| Q18 | Two equally current approved excerpts disagree on whether SYN-EXC-501 permits retry. Which should I follow? | Conflicting information | Isolated conflicting fixtures for Catalog / EC-EXCEPTION and Exception / EX-DUPLICATE | No definitive instruction | Cite the conflict, abstain on disputed action, and request owner review. |
| Q19 | What did the recall procedure require in 2024? | Unanswerable historical scope | None in initial active corpus | No | Explain historical version unavailable; do not project current steps backward. |
| Q20 | Which evidence is required to close a suspected duplicate case? | Simple factual | Exception / EX-CLOSE, EX-DUPLICATE | Yes | List closure requirements grounded in authored sections. |

Q17's v0.9 rule and Q18's contradiction are deliberate test fixtures, not planned
operating instructions. Create them only in isolated evaluation data later. For Q17,
test active-version exclusion and a controlled mixed-version retrieval scenario.
For Q18, inject both current conflicting excerpts to test conflict handling; do not
introduce a seventh active corpus document or contradictory approved production text.

## Evaluation execution and corpus acceptance

Keep future evaluation questions, gold facts, source IDs, and fixture excerpts under
`tests/knowledge/fixtures/` or a separate evaluation directory excluded from ingestion.
The present design document must also remain outside the index. A question alone
is not a gold answer: after authoring, reviewers must confirm required supporting
sections, expected facts, prohibited claims, and answerability for every case.

Use this matrix as the development set. Create and hold out additional paraphrases
before tuning chunk sizes, fusion, top-k, and evidence gates. Score retrieval before
generation to distinguish missing evidence from unsupported generation. Apply the
faithfulness, completeness, citation, abstention, and latency definitions in
[the framework](WEEK2_FRAMEWORK.md). Track correct clarification separately from
unanswerable-case abstention and service failures. Report denominators and category
results; the 90% faithfulness and 12-second P95 goals have not been achieved yet.

Corpus creation is the next milestone: author exactly these six documents, validate
metadata and references, review synthetic-only labeling and consistency, and freeze
the initial approved corpus plus verified evaluation sources. Only afterward select
providers/dependencies and implement ingestion, chunking, retrieval, and generation.
