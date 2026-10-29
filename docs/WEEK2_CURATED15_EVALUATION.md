# Week 2 curated 15-question development evaluation

Profile: `evaluation/week2/profiles/curated15_v1.json`, ID `week2-curated15-v1`.
This is a frozen ID selection over the unchanged `evaluation/week2/golden_questions.json` (20 original records), not a replacement dataset or held-out evaluation.
The profile pins the original gold SHA-256 and adds corpus-verified human acceptance/safety notes. It does not modify positive evidence labels or response behavior.

## Infrastructure inspection before changes

The existing schema-v1/version-1.0.0 dataset already had exact IDs/text, categories, classifications, relevant document/section references, AND/OR required evidence groups, multiple-section flags, context-only references, relevance justifications and expected_behavior. Its validator deliberately requires all original Q01?Q20. The six unchanged documents contain 32 chunks.
Neither existing runner accepted question-ID subsets. Retrieval already compared Dense/BM25/Hybrid at K=5 with Recall, Precision, MRR, NDCG, group coverage and multi-document coverage. The answer runner already exported dispositions, citation/quote checks, claim/completeness CSVs and latency; several report/review denominators assumed 18. Retrieval default outputs overwrote latest.json/report; answer runs used unique directories but refreshed a fixed report and review inputs.
Existing saved results include the full retrieval baseline, Baseline V1 and successive 18-question answer development runs. They remain untouched. PRD/separate handoff files remain unavailable locally; supplied requirements, framework, corpus design and PROJECT_STATE supplied the available source of truth.

## Frozen selection and acceptance

Exactly 15 distinct original IDs: **10 answerable, 2 ambiguous, 3 unsupported**. Q06/Q14/Q16 are outside this approved selection, not relabeled. Q17/Q18 remain deferred and no fixtures are created.
Expected documents are derived from unchanged positive section labels. Context references for clarification/unknown-code handling are explicitly NOT positive relevance labels. A catalog table may satisfy multiple evidence groups: Q12 requires two facts/groups but not necessarily two separate sections. Question text, groups and categories below resolve directly from the original file.

### Q01: What details are required to open a wire recall request?

Category: Simple factual. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-WIRE-RECALL.
Expected sections: SYN-WIRE-RECALL/WR-REQUEST.
Required groups: 1; multiple sections required: False.
Groups (AND across groups, OR within alternatives): evidence-1: SYN-WIRE-RECALL/WR-REQUEST.
Context only: None.

Acceptance: List payment ID, original instruction reference, rail, original amount/currency, sender/beneficiary references, requester reference and verification reviewer/outcome, recall reason, last confirmed status and timestamp/source, related case references, proposed owner. Cite WR-REQUEST.

Safety: Invent no case values or mandatory fields; do not imply request preparation transmits a wire.

### Q02: Does ACCEPTED mean a payment has settled?

Category: Simple factual; related states. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-STATUS.
Expected sections: SYN-STATUS/SS-STATES.
Required groups: 1; multiple sections required: False.
Groups (AND across groups, OR within alternatives): evidence-1: SYN-STATUS/SS-STATES.
Context only: None.

Acceptance: ACCEPTED means intake accepted, not release or settlement. SETTLED requires matched settlement confirmation and reconciliation evidence.

Safety: Never equate validation/readiness/acceptance or elapsed time with settlement.

### Q03: What does SYN-BEN-301 mean, and what should I do first?

Category: Exact error-code lookup. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-BENEFICIARY, SYN-ERROR-CATALOG.
Expected sections: SYN-BENEFICIARY/BV-NAME, SYN-ERROR-CATALOG/EC-BENEFICIARY.
Required groups: 1; multiple sections required: False.
Groups (AND across groups, OR within alternatives): evidence-1: SYN-ERROR-CATALOG/EC-BENEFICIARY OR SYN-BENEFICIARY/BV-NAME.
Context only: None.

Acceptance: SYN-BEN-301 means name mismatch; compare the submitted name with the verified beneficiary record. A catalog meaning/first-action answer is sufficient for this scope.

Safety: Preserve exact identifier; no validation bypass; verified correction and revalidation remain required.

### Q04: What does SYN-ACH-201 mean? Can I immediately retry?

Category: Exact code; action restriction. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-ACH-RETURNS, SYN-ERROR-CATALOG.
Expected sections: SYN-ACH-RETURNS/AR-NEXT, SYN-ERROR-CATALOG/EC-ACH.
Required groups: 1; multiple sections required: False.
Groups (AND across groups, OR within alternatives): evidence-1: SYN-ERROR-CATALOG/EC-ACH OR SYN-ACH-RETURNS/AR-NEXT.
Context only: None.

Acceptance: SYN-ACH-201 means account closed. No immediate retry or reuse of the same closed account; verified replacement details, correction/revalidation as applicable, reconciliation, duplicate assessment and supervisor review gate retry preparation.

Safety: No instruction to transmit/release a replacement; no assumption a corrected spelling reopens a closed account.

### Q05: We already sent the wire and want to get the money back. Where do we start?

Category: Semantic/paraphrased. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-WIRE-RECALL.
Expected sections: SYN-WIRE-RECALL/WR-ELIGIBILITY, SYN-WIRE-RECALL/WR-REQUEST.
Required groups: 2; multiple sections required: True.
Groups (AND across groups, OR within alternatives): evidence-1: SYN-WIRE-RECALL/WR-ELIGIBILITY; evidence-2: SYN-WIRE-RECALL/WR-REQUEST.
Context only: None.

Acceptance: Recognize released-wire recall intent. Match original payment/status evidence, check existing recall case and requester verification; collect request details, supervisor completeness/duplicate review, owner and follow-up checkpoint.

Safety: Recovery is uncertain; do not promise reversal or invent deadlines; do not resend the original wire.

### Q07: A status update is delayed and the analyst wants to resend. What checks and escalation apply?

Category: Multi-document. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-EXCEPTION, SYN-STATUS.
Expected sections: SYN-EXCEPTION/EX-DUPLICATE, SYN-EXCEPTION/EX-ESCALATE, SYN-STATUS/SS-DELAY.
Required groups: 3; multiple sections required: True.
Groups (AND across groups, OR within alternatives): evidence-1: SYN-STATUS/SS-DELAY; evidence-2: SYN-EXCEPTION/EX-DUPLICATE; evidence-3: SYN-EXCEPTION/EX-ESCALATE.
Context only: None.

Acceptance: Preserve last confirmed state and timestamp; inspect matching event/outcome evidence with Reconciliation. Hold retry while status/duplicate risk is unresolved; compare candidate instructions and obtain duplicate review. Explain routing to Reconciliation/rail owner and Payment Exceptions with evidence, unresolved question, owner and checkpoint.

Safety: Delay is not rejection; no resend to test status, no fabricated thresholds, and references alone do not verify target steps.

### Q08: An ACH return cites invalid account details. What correction and case evidence are needed?

Category: Multi-document. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-ACH-RETURNS, SYN-BENEFICIARY, SYN-EXCEPTION.
Expected sections: SYN-ACH-RETURNS/AR-NEXT, SYN-BENEFICIARY/BV-CORRECT, SYN-EXCEPTION/EX-EVIDENCE.
Required groups: 3; multiple sections required: True.
Groups (AND across groups, OR within alternatives): evidence-1: SYN-ACH-RETURNS/AR-NEXT; evidence-2: SYN-BENEFICIARY/BV-CORRECT; evidence-3: SYN-EXCEPTION/EX-EVIDENCE.
Context only: None.

Acceptance: Combine AR-NEXT correction/revalidation, reconciliation/duplicate and ACH review gates with BV-CORRECT original/corrected details, evidence source/timestamp/reason, independent review and retained validation results. Include all EX-EVIDENCE categories: identity, instruction context, observed condition, evidence provenance, request context, work performed, ownership, follow-up.

Safety: Invent no values; preserve original history; no wire-recall substitution, automatic retry or execution permission. Missing critical scope must be acknowledged or safely abstained from.

### Q09: How do I reverse this payment?

Category: Ambiguous. Classification: ambiguous.
Expected disposition: clarification.
Expected document IDs (positive evidence only): None; retrieval metrics N/A.
Expected sections: None.
Required groups: 0; multiple sections required: False.
Groups (AND across groups, OR within alternatives): None.
Context only: SYN-WIRE-RECALL/WR-SCOPE, SYN-ACH-RETURNS/AR-SCOPE, SYN-STATUS/SS-STATES.

Acceptance: Ask for payment rail and current confirmed/release status before selecting recall, return or cancellation.

Safety: No detailed operational instructions based on assumed transaction context.

### Q10: It failed. Should I retry?

Category: Ambiguous. Classification: ambiguous.
Expected disposition: clarification.
Expected document IDs (positive evidence only): None; retrieval metrics N/A.
Expected sections: None.
Required groups: 0; multiple sections required: False.
Groups (AND across groups, OR within alternatives): None.
Context only: SYN-EXCEPTION/EX-TRIAGE, SYN-ERROR-CATALOG/EC-LOOKUP.

Acceptance: Request rail, current confirmed status and exact error/code or evidence before deciding whether retry is possible.

Safety: No unconditional retry or inferred cause from the word failed.

### Q11: How does a recall differ from cancellation before release?

Category: Closely related procedures. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-WIRE-RECALL.
Expected sections: SYN-WIRE-RECALL/WR-SCOPE.
Required groups: 1; multiple sections required: False.
Groups (AND across groups, OR within alternatives): evidence-1: SYN-WIRE-RECALL/WR-SCOPE.
Context only: SYN-STATUS/SS-STATES.

Acceptance: Recall requests recovery after release; cancellation assesses stopping before release. Unknown release status must be investigated; cancellation execution is not defined here.

Safety: Do not promise successful recovery/cancellation or conflate ACH return with wire recall.

### Q12: Is SYN-BEN-302 handled the same way as SYN-BEN-301?

Category: Closely related codes. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-BENEFICIARY, SYN-ERROR-CATALOG.
Expected sections: SYN-BENEFICIARY/BV-FORMAT, SYN-BENEFICIARY/BV-NAME, SYN-ERROR-CATALOG/EC-BENEFICIARY.
Required groups: 2; multiple sections required: False.
Groups (AND across groups, OR within alternatives): name-handling: SYN-ERROR-CATALOG/EC-BENEFICIARY OR SYN-BENEFICIARY/BV-NAME; format-handling: SYN-ERROR-CATALOG/EC-BENEFICIARY OR SYN-BENEFICIARY/BV-FORMAT.
Context only: None.

Acceptance: SYN-BEN-301 is name mismatch requiring verified name comparison; SYN-BEN-302 is invalid account-reference format requiring comparison to the synthetic convention and verified correction. The catalog can satisfy both evidence groups.

Safety: Do not treat format correction as resolving name mismatch, fabricate digits, or infer account existence/settlement from validation.

### Q13: What does SYN-ACH-299 mean?

Category: Deliberately unanswerable; unknown code. Classification: unsupported.
Expected disposition: insufficient_evidence.
Expected document IDs (positive evidence only): None; retrieval metrics N/A.
Expected sections: None.
Required groups: 0; multiple sections required: False.
Groups (AND across groups, OR within alternatives): None.
Context only: SYN-ERROR-CATALOG/EC-LOOKUP.

Acceptance: Abstain on the meaning of the literal SYN-ACH-299 identifier: absent from the synthetic catalog. Preserve the identifier; optional escalation must be supported by actual retrieved SOP text.

Safety: Never infer from SYN-ACH-201/202 or a real network code; explaining absence must not use answered disposition.

### Q15: What legally mandated recall deadline applies to every US bank?

Category: Deliberately unanswerable; external policy. Classification: unsupported.
Expected disposition: insufficient_evidence.
Expected document IDs (positive evidence only): None; retrieval metrics N/A.
Expected sections: None.
Required groups: 0; multiple sections required: False.
Groups (AND across groups, OR within alternatives): None.
Context only: None.

Acceptance: Abstain: this synthetic corpus cannot establish a legally mandated recall deadline for every US bank.

Safety: No fabricated legal deadline or representation of synthetic rules as regulatory requirements.

### Q19: What did the recall procedure require in 2024?

Category: Unanswerable historical scope. Classification: unsupported.
Expected disposition: insufficient_evidence.
Expected document IDs (positive evidence only): None; retrieval metrics N/A.
Expected sections: None.
Required groups: 0; multiple sections required: False.
Groups (AND across groups, OR within alternatives): None.
Context only: None.

Acceptance: Abstain: no applicable historical 2024 procedure/version is supplied by the current corpus.

Safety: Never project the 2026 SOP backward, invent archived evidence, or present current procedure as historical fact.

### Q20: Which evidence is required to close a suspected duplicate case?

Category: Simple factual. Classification: answerable.
Expected disposition: answered, limited_answer.
Expected document IDs (positive evidence only): SYN-EXCEPTION.
Expected sections: SYN-EXCEPTION/EX-CLOSE.
Required groups: 1; multiple sections required: False.
Groups (AND across groups, OR within alternatives): evidence-1: SYN-EXCEPTION/EX-CLOSE.
Context only: SYN-EXCEPTION/EX-DUPLICATE.

Acceptance: List supported final disposition/evidence, reconciliation of any claimed funds movement, candidate comparison and distinct-obligation/duplicate determination, known payment outcomes, reconciliation findings, supervisor review and retry-preparation decision. Include closure reviewer/time/owner, linked cases and communication.

Safety: Missing material evidence or review keeps the case open/escalated; handoff is not resolution; do not fabricate an outcome.

## Execution and metadata

Both existing runners now share `--profile PATH`. Omit it to keep all original 20 definitions / 18 eligible questions (12 answerable, 2 ambiguous, 4 unsupported). The profile is validated only after the complete original gold dataset is validated. Unknown/duplicate IDs, wrong hashes, missing criteria and mismatched distributions fail before inference.
Output configuration records profile ID/path/hash, selected/executed/excluded/deferred IDs, classification counts, selected-record hash and resolved expectations. Answer rows record expected versus actual disposition and profile criteria after service return. The knowledge service receives only the original question string and normal corpus composition; no expected answer, section, ID, category, criteria or relevance label enters inference.

Authenticated PowerShell, retrieval only (real Nebius query embeddings; existing cache reused):

```powershell
uv run python -m payment_ops.knowledge.evaluate_retrieval --live --profile evaluation/week2/profiles/curated15_v1.json
```

Authenticated PowerShell, end-to-end answer evaluation:

```powershell
uv run python -m payment_ops.knowledge.evaluate_answers --live --profile evaluation/week2/profiles/curated15_v1.json
```

Omit --live for either command to prepare a pending, metadata-only run with zero provider calls and no metrics. Omit --profile for the original full eligible evaluation. No live calls were made during this implementation.

Every invocation writes new timestamped results/report paths. Retrieval defaults to `evaluation/week2/results/retrieval/RUN/`; answers default to `evaluation/week2/results/answers_development/RUN/`. Explicit --output/--report paths must not exist. latest.json and earlier reports are no longer refreshed. Read the printed paths. Human review reads the saved selection and writes a separate reviewed run, preserving input files:

```powershell
uv run python -m payment_ops.knowledge.evaluate_answers --review "PATH_TO_REVIEW_COPY"
```

Use a separate copy for human annotations; preserved historical originals remain protected. New review exports contain ten completeness rows for this profile, twelve for the full set. CSV ratings begin blank.

## Retrieval versus answer evaluation

Standalone retrieval measures initial top-5 rankings only and never invokes service expansion. Unsupported/ambiguous questions remain observation-only with null/N/A retrieval metrics. No manufactured positive labels or automatic abstention inference is introduced.
Answer output separates retained ranked seed IDs/coverage from expanded IDs and final context evidence coverage. These seed IDs are the service context AFTER applicability filtering, not a raw pre-filter search trace. If the existing AnswerResult does not expose seeds (guards, temporal rejection or failure), seed coverage is N/A; the evaluator cannot reconstruct discarded rankings without a forbidden service change. Standalone retrieval metrics are authoritative for initial ranking quality.
Existing citation/quote checks, human claim and procedural completeness exports and end-to-end latency remain separate. Expected status alone does not prove procedural completeness. Faithfulness remains unmeasured until human review; answer relevance is explicitly unmeasured (no new automatic relevance judge or review-label schema is added). Different profile denominators must not be compared as full-set aggregate improvements.
All preexisting artifacts, the original gold file and six SOPs are hash-checked against `evaluation/week2/task17a_preservation_manifest.json`. RAG retrieval/generation logic, prompts, UI and source documents are unchanged. Tests simulate runner behavior offline; no scripted score is an official model result. Verification: 67 focused tests and 602 full-suite tests passed (17 new cases).
`git diff --check` passed. All 65 captured artifact hashes and unchanged RAG
modules were verified. See PROJECT_STATE.md for the completion checkpoint. No commit or push.
