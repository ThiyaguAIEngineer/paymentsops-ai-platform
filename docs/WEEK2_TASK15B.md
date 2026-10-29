# Task 15B: final backend stabilization

Reference: `evaluation/week2/results/answers_development/20261029T011211499185Z`
and `docs/WEEK2_TASK15_COMPARISON.md`: all 18 eligible questions executed,
17/18 correct dispositions. Baseline V1, this run, earlier runs, source SOPs and
gold labels remain unchanged. Reference hashes are recorded in
`evaluation/week2/task15b_reference_manifest.json`. This remains a development-set
comparison, not independent validation.

## Q07: failed exact quotation

The latest failure is grounding_validation/quote_not_found at statement 5,
evidence 1, source S2 (EC-STATUS), 87 characters. All gold evidence groups were
retrieved, including duplicate-risk and escalation sections. No matching source
was found for the rejected quotation. Its text was intentionally not retained;
only a hash, length and location are available. Therefore no exact punctuation,
Markdown or wording error can be reconstructed safely from these artifacts.

Q07 succeeded in the preceding grounded-v5 run and failed in other saved runs at
different sources/positions/quote lengths. This is consistent with intermittent
invalid model-generated excerpts. No deterministic source-ID or validator defect
was reproduced. It does not conclusively isolate the generation cause, nor show
that all future failures will be transient. Exact source excerpts continue to pass
and simulated rewritten/wrong-source excerpts fail offline.

The service now permits one fresh regeneration ONLY after an initial
grounding_validation/quote_not_found. Limits and safeguards:

- At most two total generation calls per question; no additional retrieval or
  query embedding. Source text, source IDs, question and context are unchanged.
- The second system instruction reinforces exact copying; the rejected answer or
  quote is not supplied, repaired, logged, or accepted. No alternate source is
  substituted. Every second response receives the full original validation.
- Schema/parsing errors, unknown source IDs, quotes belonging to another source,
  missing essential evidence and provider failures do not initiate recovery.
- A second failure stops safely. Provider failure during recovery is unavailable,
  not an answer. A valid abstention/clarification remains such, rather than being
  converted into an answer. Diagnostics retain the initial rejection plus the
  final failure or quote_retry_validated marker; recovery is not hidden.

This can add a full generation request to latency/cost. The existing 45-second
provider timeout and 1,800-token output cap apply to each call, not a shared
deadline; no claim is made that the 12-second warm-query target is met. No new
model, agent, infrastructure, database, reranker or repair workflow was added.

## Q08: common case-field coverage

The new run retrieves EX-EVIDENCE, but the accepted model answer again summarizes
correction/validation/reconciliation/review instead of the separate common record.
Its citations cover EC-ACH, BV-CORRECT and AR-NEXT, not the missing common checklist.
This is a completeness weakness in model summarization, not a remaining retrieval
gap. A correct disposition and valid quotes do not establish procedural completeness.

For case-evidence questions with an initially valid substantive response, the
service now appends the exact field table and adjacent missing-value/history/
prerequisite warning from the actually retrieved EX-EVIDENCE source. The generated
summary remains intact and fully validated. The combined response is revalidated
with the same source-membership, exact-quote and citation-numbering logic, preserving
all original citations. No evaluation labels or invented field/value list is used.

The table includes identity, instruction context, observed condition, evidence
provenance, request context, work performed, ownership and follow-up because those
are the SOP's actual rows. Output explicitly identifies them as requirements, not
populated case values. The prompt asks the model to focus on rail-specific guidance
and gates rather than duplicate this application-rendered checklist.

If the section/table is absent or unusable, the response is explicitly limited and
states that complete common case requirements are unavailable. Model abstentions,
clarifications and invalid responses are not turned into answered procedures by
appending a table. Existing missing-essential-evidence checks still stop the answer.
This guarantees inclusion of the current retrieved table, not semantic accuracy or
completeness of the model's other procedural claims.

## Q13: presentation only

The unsupported-code evidence decision is unchanged. The displayed guidance removes
the SOP instruction number, collapses wrapping whitespace and labels the paragraph
as documented escalation guidance. The supporting quotation retains the original
numbered source passage and exact offsets. No meaning, owner or action is invented.

## Verification and readiness

Targeted scripted tests cover one valid recovery, repeated invalid quotes, unchanged
context/single retrieval, ineligible errors, recovery provider/schema failures,
source membership, Q07's no-resend/duplicate context, Q08 omission reproduction and
all eight actual rows/warning with exact citation offsets, unavailable tables,
and Q13 presentation/classification. Focused tests: 84 passed. Full suite: 563
passed (18 new regressions). `git diff --check` passed.

The current Codex process has no NEBIUS_API_KEY. No live calls were attempted and
no new score is claimed. Offline tests establish bounded behavior and deterministic
table inclusion; they do not establish live quotation reliability, semantic
faithfulness, complete procedures, or independent generalization. Human review
remains necessary. Backend contracts are ready for controlled UI integration, but
live stabilization acceptance is pending authenticated verification before release.
No Streamlit changes or commit/push are part of this task.

```powershell
uv run python -m payment_ops.knowledge.evaluate_answers --live --report docs/WEEK2_TASK15B_COMPARISON.md
```

The new report path and unique run directory preserve the Task 15 reference. Inspect
Q07 diagnostics/recovery and latency, Q08 actual checklist and procedural claims,
Q13 presentation, and all other questions. Then perform human claim/completeness
review on a separate copy of preserved artifacts before final UI acceptance.
