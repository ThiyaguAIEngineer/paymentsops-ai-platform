# Payment Operations Intelligence Platform — project state

## Current phase

Week 2 implementation and curated live development evaluation are complete.
Final report prepared: `docs/WEEK2_FINAL_EVALUATION.md`. Human quality review and
formal sign-off are pending. The Task 17D checkpoint records current results;
earlier checkpoints retain historical metrics with their original denominators.
Week 1 Commercial Wire Payment Validation Simulator implementation and manual
acceptance are complete and committed as 04f29e2; Week 1 is frozen.
This document reflects requirements supplied during development;
the original approved PRD and project handoff are not available locally.

## Completed functionality

- Immutable Payment model with eight required instruction fields, optional
  missing values, Decimal amounts, and Python date values.
- Input validation collecting all errors without mutating instructions.
- Four vendor-neutral connector Protocols and deterministic mock implementations:
  Core Banking, Limits, Fraud, and Sanctions.
- Deterministic evaluation of six areas: payment input, active/wire-enabled
  account, available balance, single-wire limit, fraud, and sanctions.
- Dependency-injected PaymentService orchestrating validation, independent
  connector lookups, error normalization, and decision evaluation.
- Twenty synthetic instructions spanning successful, rejected, review, boundary,
  invalid-input, and connector-outage scenarios.
- Streamlit dashboard with dynamic metrics, decision filtering, payment
  selection, all control findings, and read-only connector evidence.
- Complete DecisionResult with retained findings and deterministic primary reason.
- Immutable PaymentProcessingResult and ConnectorEvidence; compatible legacy
  process_payment() consumers continue receiving DecisionResult.

### Week 2 progress

- Six synthetic operational documents, 31 sections, and 32 deterministic chunks.
- Immutable document/section/chunk models, validated ingestion, safe cleaning,
  and heading-aware structural chunking independent of Streamlit.
- Nebius embedding adapter, reusable local vector cache, LangChain in-memory
  cosine index, BM25, and equal-weight RRF hybrid retrieval (top 5 each; constant 60).
- Project owner reports real Qwen/Qwen3-Embedding-8B verification, 4096 dimensions,
  and three successful live retrieval inspections. This is owner-reported live
  verification, distinct from Codex's offline tests and current evaluation results.
- Reproducible golden dataset preserves all 20 original questions: 12 answerable,
  4 unsupported, 2 ambiguous, and 2 fixture-dependent. Labels reference the actual
  corpus; planning/evaluation data remain outside the ingestion directory.
- Evaluation runner compares unchanged Dense/BM25/Hybrid implementations with
  Recall@5, Precision@5, MRR@5, NDCG@5, and required evidence-group coverage.
  Unsupported/ambiguous cases are unscored observations; Q17/Q18 are deferred.
  Saved results now report complete-real-embeddings with Qwen/Qwen3-Embedding-8B,
  4096 dimensions: Dense Recall@5 83.3%, BM25 62.5%, Hybrid 68.1%; complete
  evidence rates 75.0%, 58.3%, and 66.7%, respectively. See
  docs/WEEK2_RETRIEVAL_EVALUATION.md and evaluation/week2/results/latest.json.
- Dense top-5 is the initial generation default based on those measured results;
  BM25 and Hybrid remain configurable, unchanged alternatives. Dense still misses
  required evidence on Q06/Q07/Q08; generation must not fill these gaps by guessing.
- Grounded KnowledgeService, vendor-neutral generation Protocol, Nebius chat
  adapter, statement-level citations and quote validation, and live inspection CLI
  are implemented. No golden labels are accessed during normal questions.
- Generation model: Qwen/Qwen3-30B-A3B-Instruct-2507, verified by the owner's live
  API run. Factual and paraphrase scenarios answered; unsupported abstained;
  ambiguous clarified. SYN-BEN-301 and delayed-status scenarios returned
  invalid_response. Original model payloads were not saved, so exact original
  validation causes remain unknown; no root-cause guess is treated as confirmed.
- Diagnostic revision: explicit safe stage/category failures, exact quote-passage
  offsets, and one citation number per document/section/version retaining all
  supporting passages. grounded-v2 exposes missing linked sections as non-evidence
  context and distinguishes declared incomplete evidence from malformed output.
  No quote matching, source validation, or retrieval settings have been relaxed.
  See docs/WEEK2_GENERATION_DIAGNOSTICS.md. A real rerun is still required.
- Latest saved grounded-v2 diagnostics: factual invalid_required_sections;
  exact-code missing BV-NAME; recall overdeclared six follow-up/related sections;
  delayed-status answered; unsupported abstained; ambiguous incorrectly answered.
  Diagnostics retain categories and source manifests, not raw model values or
  answers, so factual field shape and delayed-status answer faithfulness are unknown.
- grounded-v3 makes required_sections mandatory and explicitly typed as full
  document/section strings, with safe field/type/index diagnostics. It separates
  requested-scope evidence from related/future stages and adds explicitly labeled
  limited_answer responses. Missing essential evidence still blocks an answer.
- A general transaction-action clarification guard requests missing rail/status
  before retrieving or generating procedures; definitions/comparisons bypass it.
  Source IDs, exact quotes, passage offsets, and citation checks remain strict;
  neither required_sections nor quote membership proves semantic completeness.
  Dense top-5, source documents, and retrieval configurations remain unchanged.
- Latest owner-run grounded-v3 inspection is recorded in the saved diagnostics:
  factual answered, SYN-BEN-301 incomplete_evidence, recall answered, delayed-status
  answered, unsupported abstained, and ambiguous clarified. These dispositions
  establish functioning generation, not semantic faithfulness or completeness.
- End-to-end evaluation CLI now executes the 18 eligible original questions through
  the unchanged KnowledgeService with real Qwen embeddings/generation and Dense
  top-5. Gold labels are applied only after inference; Q17/Q18 remain deferred.
- Evaluation captures accepted answers/fallbacks, sources, citations/quotes,
  diagnostic missing-section declarations, configuration hashes, and service
  latency. Structural checks and response-disposition metrics are separated from
  human claim faithfulness and scope/completeness review. No favorable labels or
  achievement claims are generated automatically. Full live QA metrics are pending.

## Architecture

The Payment Service coordinates components; this is a logical flow rather than
a chain in which connectors invoke the Decision Engine:

```text
Streamlit UI
    |
    v
Payment Service
    |-- Payment Input Validation
    |      `-- Invalid input: skip connector lookups
    |-- Valid input: Vendor-Neutral Connector Interfaces
    |      `-- Mock Core / Limits / Fraud / Sanctions
    |-- Deterministic Decision Engine (input + normalized responses/errors)
    `-- PaymentProcessingResult
           |-- DecisionResult
           `-- ConnectorEvidence (exact retrieved response objects)
                   |
                   v
              Streamlit UI
```

Domain models and input validation live under domain/, connector contracts and
mock data under connectors/, orchestration and evaluation under services/,
synthetic instructions under samples/, and presentation under ui/. The UI
composes injected mock dependencies but performs no screening lookups or banking
rule evaluation. Cached service results supply both findings and evidence.

## Architectural decisions

- Synthetic payment data only; no real bank integrations or payment execution.
- Domain logic separated from UI; vendor-neutral interfaces and constructor
  dependency injection keep orchestration independent of mock implementations.
- Deterministic business rules: rejection takes precedence over review; all
  failed/review findings remain available and primary reasons use fixed ordering.
- Unavailable mandatory controls never silently pass. Safe review treatment
  preserves available rejections. Invalid input produces skipped downstream checks.
- Immutable connector evidence reuses normalized frozen response types. No
  fabricated zero balances, PASS decisions, or raw exceptions are exposed.
- Decimal monetary values; read-only mock records; privacy-conscious logging.
- Shared processing workflow retrieves each connector once per valid instruction.
- One evolving repository and one unified Streamlit application will expose Wire
  Validation and Knowledge Assistant through shared navigation; no separate app.
- Week 2 backend will live separately under payment_ops/knowledge/, independently
  testable without Streamlit and without changing Week 1 validation logic.
- Week 2 backend now implements ingestion -> structural chunks -> cached real
  embeddings/local cosine index plus independent BM25 -> RRF. Evaluation is a
  separate CLI over the same pipeline. Grounded answer generation consumes these
  retrievers through injection, validates citations against retrieved chunks, and
  returns answered/limited_answer/insufficient_evidence/clarification/unavailable results. No UI integration.
- Week 2 planning is documented in docs/WEEK2_FRAMEWORK.md and
  docs/WEEK2_CORPUS_DESIGN.md. Quality and latency goals are targets, not results.

## Verification

The final Week 1 suite contains 273 tests covering domain validation, connectors,
decision boundaries and precedence, service interactions, evidence identity,
compatibility, all 20 scenarios, UI metrics/filtering/selection, error presentation,
and a temporary localhost Streamlit startup health check.

Final checkpoint verification: uv run pytest passed all 273 tests; git diff --check
passed. The project owner confirmed successful manual dashboard launch, correctly
displayed evidence, and all important manual scenarios.

Baseline metrics: 20 payments; $300,107.02 total finite positive instruction value;
4 ready, 6 manual review, 10 rejected. Three invalid amounts are excluded from
value, while all instructions remain included in counts and the table.

Week 2 evaluation checkpoint: `uv run pytest` passed 371 tests (including 25
offline evaluation tests); `git diff --check` passed. Week 1 source and its
273-test baseline remain unchanged. The full live evaluation was subsequently
completed in the owner's authenticated terminal; its saved results are recorded
above. Retrieval evidence coverage is not answer faithfulness or abstention accuracy.

Grounded-generation checkpoint: `uv run pytest` passed 403 tests, including 32
new offline generation tests; whitespace checks passed. Ingestion, chunking,
embeddings, index, retrieval, and all six corpus content hashes match the saved
live retrieval baseline. Live generation inspection stopped safely because the
Codex process lacks credentials; no actual generated answers are claimed.

Generation-diagnostics checkpoint: `uv run pytest` passed 424 tests, including 21
new simulated diagnostic/regression cases; whitespace checks passed. A local
inspection reports configuration/missing_credentials. The owner-confirmed live
milestone and two unresolved live validation failures are recorded above. No
successful live confirmation of the diagnostic/presentation changes is claimed.

grounded-v3 checkpoint: `uv run pytest` passed 452 tests, including 28 new schema,
scope, source-boundary, and clarification regressions. `git diff --check` passed.
Week 1 is unchanged; ingestion/chunking/embedding/index/retrieval and all six
corpus hashes still match the saved live baseline. NEBIUS_API_KEY is unavailable
to this Codex process, so no live v3 correction is claimed. The lexical guard can
over- or under-detect context, and model scope/essential-evidence judgments still
require real-inference review; required_sections is not a completeness certificate.

Answer-evaluation checkpoint: `uv run pytest` passed 477 tests, including 25 new
offline evaluation/review tests; whitespace checks passed. The live runner stopped
at configuration/missing_credentials with 0/18 questions executed, so the report
contains pending measurements, not fake scores. Week 1 and the normal RAG pipeline
were not changed. The >=90% human-reviewed answerable-claim faithfulness target
remains unmeasured; CSV assessments start blank and partial support receives no
full-support credit. Human completeness is reviewed separately from dispositions.

## Task 13: Baseline V1 safety and answer-coverage corrections

Baseline V1 is the completed grounded-v3, Dense top-5 live run
`evaluation/week2/results/answers/20261028T202702213394Z`: 18/18 executed,
12/18 correct response dispositions (66.7%), 100% structural citation membership
and quote verification. Human faithfulness remains unmeasured. The original report,
run, gold labels and a hash-verified snapshot are preserved; hashes/configuration
are recorded in `evaluation/week2/baseline_v1_manifest.json`. These are development
questions, not independent validation. This section supersedes earlier statements
that the full baseline was pending.

Safety finding: Q19 incorrectly described a current 2026 SOP as a 2024 procedure.
Valid citations/quotes did not establish historical applicability. Q01/Q08 were
blocked by an overly broad transaction-context guard; Q10's pronoun-only retry
request escaped it. Q03's catalog entry contains meaning, first action and stop
conditions; the model unnecessarily demanded the downstream runbook. Q06 lacked
BV-CORRECT despite an explicit reference in the retrieved BV-NAME section.

Interrupted-change regression: `period` initialization was unreachable after an
unconditional return in KnowledgeService.ask. Its earlier use raised NameError,
which the broad retrieval fallback converted into retrieval_failure. Moving the
initialization before retrieval restored all original 477 tests (81 focused
generation tests). No retriever capability or provider change was needed.

Implemented grounded-v4-development corrections:
- A pre-generation metadata gate checks requested ISO dates/years/relative previous
  years against effective dates and known document versions. Missing historical
  evidence abstains; unclear/open-ended periods clarify. Current policy is never
  substituted for a requested unsupported period. Known supersession bounds older
  evidence. Metadata is retained in prompts and saved source provenance.
- General SOP questions reach retrieval; transaction-action decisions require
  missing rail/status context, including pronoun-only retry decisions.
- Narrow catalog meaning/first-action scope is explicit in the prompt, preserving
  stop/revalidation rules and conservative handling of missing essential evidence.
- Dense seeds remain top-5. An optional injected corpus catalog resolves at most
  ONE explicitly linked section, at most two chunks, one hop. Original ranks remain;
  linked chunks carry their parent ID and origin, not a fictitious dense score.
  This is a development candidate, not a measured retrieval improvement.
- Existing retrieve(query, k) doubles/callers still work without the optional catalog.
  Citation membership, exact source quote offsets, required-evidence checks, safe
  fallbacks and the synthetic disclosure remain. Retrieval diagnostics expose only
  an allowlisted exception class, never exception messages/secrets.

The live development comparison was attempted but stopped safely with
configuration/missing_credentials: 0/18 executed, no new metrics. Results go to
`evaluation/week2/results/answers_development/` and the separate report
`docs/WEEK2_ANSWER_DEVELOPMENT_COMPARISON.md`. The runner rejects writes/reviews
against Baseline V1 and validates its hashes. Offline regressions cover generalized
periods, action intent, optional retrieval compatibility, provenance/bounds,
missing evidence and catalog scope. Week 1, UI and synthetic corpus are untouched.

Limitations: temporal language parsing is deliberately bounded; the corpus lacks
archived/conflicting-source fixtures and cannot establish an exhaustive policy
history. Intent detection and scope judgments are not complete semantic validators.
One-hop expansion may add irrelevant context or leave other essential sections
missing. No live answer-coverage improvement or semantic faithfulness is claimed.
Human completeness/faithfulness review and held-out questions remain necessary.

Final offline verification: 507 tests passed, including all 477 original tests
and 30 new generalized regressions. Focused generation verification: 81 passed.
`git diff --check` passed. Baseline V1 original/snapshot/report and gold hashes
were rechecked unchanged. No commit or push was performed.

## Post-Task 13 reliability review

The latest completed real Nebius run is
`evaluation/week2/results/answers_development/20261029T002845632511Z` (18/18),
superseding the earlier pending-live statements. It used grounded-v4-development,
Dense top-5 plus bounded one-hop follow-up. Baseline V1 remains unchanged at
12/18 dispositions (66.7%); structural citation/quote checks were 100% for accepted
outputs in both runs, not proof of faithfulness or success for rejected outputs.
Human faithfulness/completeness remains unmeasured.

Findings and corrections:
- Q19 safely abstains with policy_period_unsupported. The evaluator omitted that
  reason from its unsupported-question evidence-abstention allowlist. It is now
  accepted only with insufficient_evidence; invalid responses and application,
  retrieval/provider failures remain incorrect dispositions. Offline rescoring
  changes only Q19: saved 14/18 (77.8%) becomes 15/18 (83.3%). This is a scoring
  correction on existing live outputs, not a new inference improvement. Separate
  derived results are in `evaluation/week2/reliability_review.json`.
- Q03/Q04/Q07 failed quote_not_found despite full retrieved evidence-group
  coverage. Saved diagnostics have locations, lengths and hashes only; exact
  rejected wording cannot be reconstructed. Markdown stripping, paraphrasing and
  joined excerpts are possible mechanisms, not established exact causes.
- grounded-v5-development adds a copy-only quotation contract: decoded source text,
  contiguous sufficient excerpts, preserved Markdown/case/punctuation, separate
  evidence items for nonadjacent excerpts. Exact quote validation, membership,
  provenance, fail-closed behavior and disclosure are unchanged; no repair or
  alternate-source substitution is introduced.
- Q08's accepted answer covers selected correction evidence but does not address
  the missing EX-EVIDENCE common case record or disclose the gap. The prompt now
  distinguishes every requested scope; independently safe partial guidance must
  be explicitly limited and name the unavailable portion. Missing prerequisites
  still require abstention. Scope compliance remains a human-review judgment.
  Retrieval configuration and source documents are unchanged.
- Overall P95 rose from 4.296 to 17.510 seconds; with 18 samples it is the maximum
  request (latest Q20). Mean retrieved source text grew about 21%. A local 1,000-
  iteration metadata/reference probe averaged about 0.135 ms per iteration, not
  an end-to-end performance measurement. Query embeddings are uncached; Q19 took
  7.742 seconds without generation. Context/output changes, provider/network/load
  variation and newly unblocked model paths may contribute. Stage timings/token
  usage were not retained, so causation cannot be separated. The 12-second target
  remains unmet for this run. Model-path summaries now exclude temporal gates;
  overall latency still includes them. No performance infrastructure was added.

All previous Baseline V1 and development artifacts/reports/gold are protected via
`evaluation/week2/reliability_artifacts_manifest.json`; all 29 file hashes and six
corpus hashes were verified unchanged. New live reports default to
`docs/WEEK2_ANSWER_RELIABILITY_COMPARISON.md`. Human review of a preserved run must
use a separate copy. Full findings: `docs/WEEK2_RELIABILITY_REVIEW.md`.

Verification: 95 focused regression tests passed; full `uv run pytest`: 528 passed
(all previous 507 plus 21 new offline cases); `git diff --check` passed. No live
calls were attempted because NEBIUS_API_KEY is absent. Prompt improvements remain
unverified by real inference. Week 1, UI, SOPs, gold labels and retrieval are frozen;
no commit/push. These same-question comparisons are not independent validation.

## Task 15: unknown identifiers and common case evidence

Inspected the unified-platform/backend architecture, service/retrieval contracts,
offline tests and latest real run before changes. Reference:
`evaluation/week2/results/answers_development/20261029T004007182456Z`,
grounded-v5-development, 17/18 correct dispositions (94.4%). This supersedes the
previous v5 pending-live note; the new v6 candidate remains pending live verification.
The reference run/report hashes are in `evaluation/week2/task15_reference_manifest.json`.

Q13 root cause: the model correctly described absence of a catalog definition but
selected answered; structural validation did not enforce definition membership.
The service now checks exact code identifiers against applicable canonical catalog
table rows for code-meaning requests when a complete corpus catalog is injected.
Unknown identifiers return insufficient_evidence, preserve received spelling, and
state their meaning cannot be established from the available synthetic catalog.
No identifier or evaluation-question-specific answer is hardcoded. Optional
escalation is extracted verbatim from retrieved EC-LOOKUP and passes the existing
citation/quote validator. Missing guidance is not invented; validation errors
remain invalid_response diagnostics. Documented codes retain normal generation.
Legacy callers without a full catalog retain model-based handling rather than
claiming global absence from incomplete top-five evidence.

Q08 root cause: the one-hop resolver supplied BV-CORRECT but not the distinct common
case checklist EX-EVIDENCE. A bounded requested-section lookup now adds that exact
metadata section for general case-evidence/record/field intent. Dense top-5 order
and ordinary one-hop behavior remain unchanged. Actual Q08 context is seven chunks
(five seeds plus BV-CORRECT plus EX-EVIDENCE). Requested sections have honest
requested_section origin and no fabricated link parent, including saved evaluation
provenance. Only complete single-chunk targets are admitted; metadata applicability
filtering still precedes inclusion. The grounded-v6-development prompt asks for all
required common case fields alongside correction records, without inserting SOP
facts into inference from gold labels. Unknown-code requests use the scoped lookup
for EC-LOOKUP instead; at most one requested section is added per question.

Existing source-membership/quote verification, exact passage offsets, disclosure,
Q09/Q10 clarification and Q07 duplicate-risk stops remain. Frozen Baseline V1,
preserved development runs/reports, all gold labels and six SOP hashes were checked
unchanged. Week 1 and UI are untouched; no framework/database/provider/agent added.
Details and authenticated command: `docs/WEEK2_TASK15.md`.

Verification: 132 focused tests passed; full `uv run pytest`: 545 passed
(all previous 528 plus 17 new regressions). `git diff --check` passed.

NEBIUS_API_KEY is absent, so no live calls were attempted. No updated v6 score is
available; 17/18 remains the v5 reference, not a claim about this candidate. Scripted
offline case-field coverage proves retrieval/validation behavior, not live model
completeness. Human faithfulness remains unmeasured. Requested-section intent
recognition is lexical and single-chunk lookup is deliberately bounded. Same-set
comparisons do not establish independent generalization. No commit/push.

## Task 15B: bounded quote recovery and deterministic common record

Read the saved Task 15 run/report before implementation:
`evaluation/week2/results/answers_development/20261029T011211499185Z`,
grounded-v6-development, 18/18 executed, 17/18 correct dispositions. Q13's evidence
abstention is confirmed live. Q07 failed quote_not_found at statement 5/evidence 1,
S2 EC-STATUS, 87 characters, despite full evidence-group coverage. Q08 retrieved
EX-EVIDENCE but omitted its common fields, citing correction/rail guidance instead.
This supersedes the previous v6 pending-live statement, not the current v7 status.
Reference run/report hashes: `evaluation/week2/task15b_reference_manifest.json`.

Q07 succeeded in an earlier run and failed at different quote locations in others.
No deterministic source-ID or literal-validation bug was reproduced. Rejected
quote text was not retained, so its exact rewriting error and whether a fresh
attempt will succeed cannot be established. Pattern is consistent with intermittent
invalid model excerpts; no definitive provider/root-generation cause is claimed.

Changes in grounded-v7-development:
- At most ONE fresh regeneration after initial grounding_validation/quote_not_found.
  Same question/context/source IDs, no new retrieval/embedding, no rejected payload
  feedback, no repair or substitution. Full validation applies again. Other errors
  do not initiate retry. A second failure stops safely; provider failures remain
  unavailable and valid abstentions/clarifications are respected. Diagnostics
  preserve the initial failure and final outcome, including quote_retry_validated.
- For requested case-evidence scope and an initially valid substantive answer,
  append the actual retrieved EX-EVIDENCE field table and adjacent warning using
  exact source quotes, then revalidate/rebuild all citations with the existing
  validator. This avoids model omission of common fields without adding facts or
  gold labels. Records are explicitly requirements, not populated transaction data.
  Unavailable/unusable tables force explicitly limited guidance, never a complete
  common checklist claim. This does not prove other procedural claims complete.
- Q13's displayed guidance removes its instruction number and wrapping whitespace;
  original numbered quote/offsets and insufficient_evidence classification remain.
- Evaluation configuration records recovery/rendering behavior; new reports default
  to `docs/WEEK2_TASK15B_COMPARISON.md` to preserve the previous report. Retrieval,
  SOPs, gold, Week 1 and Streamlit UI are unchanged. No new architecture/dependencies.

Verification: 84 focused tests passed; full `uv run pytest`: 563 passed (all prior
545 plus 18 stabilization regressions). `git diff --check` passed. Preserved
Baseline V1/development artifacts and six source hashes were verified unchanged.
No live calls were attempted: this process lacks NEBIUS_API_KEY. No new live score,
faithfulness or independent-generalization result is claimed. No commit or push.
Details and limits: `docs/WEEK2_TASK15B.md`.

Readiness: backend contracts are offline-ready for controlled UI integration.
Final live stabilization acceptance and human procedural/claim review are still
pending before release. One retry can add a full provider call; the existing
45-second timeout and 1,800-token cap apply PER call, not a shared deadline. The
12-second warm-query target is not established. Intent recognition remains lexical;
rendering all common fields does not semantically verify generated rail procedures.

## Task 16: unified Streamlit Knowledge Assistant

The current PRD and PaymentOps_AI_Project_Handoff.md remain unavailable in the
repository/parent directory. Used the supplied requirements, Week 2 framework,
existing architecture decisions, PROJECT_STATE and public backend contracts.
Latest owner-executed live reference is
`evaluation/week2/results/answers_development/20261029T012444697570Z`,
grounded-v7-development, 17/18 correct dispositions. The remaining Q20 failure is
safely rejected quote_in_different_source, not a UI defect. Human faithfulness and
procedural completeness remain unmeasured; this is development-set performance.

Integrated one existing app with a sidebar Workspace radio: Wire Validation is
the default; Knowledge Assistant is a separate view. The original Week 1 dashboard
body is moved intact into render_wire_validation; filters, metrics, selection,
connector evidence, PaymentService and Decision Engine behavior are unchanged.

The new ui/knowledge_view.py uses the existing KnowledgeService.ask(question) and
AnswerResult/Citation/EvidencePassage contracts. A form provides Question/Ask;
only a nonempty explicit submission calls the service. Opening the view, draft
edits and ordinary reruns do not initialize or call providers. The latest submitted
question/result remains session-local and labeled with its actual question.
No Week 1 payment records or state are passed to the LLM.

knowledge/runtime.py is application composition, not new reliability logic: the
existing adapters read credentials/model settings from the process environment;
the existing ingestion, chunker, document embedding cache, local index and Dense
retriever are reused with the complete section_catalog. Paths are repository-
anchored. Streamlit cache_resource(scope="session") reuses the service/index across
reruns/submissions for that browser session; document embeddings remain shared via
the existing disk cache. Partial initialization closes clients; finalization closes
clients when the resource is released. No configuration/keys are collected in UI.

The view distinguishes answered, limited guidance, clarification, evidence
abstention, invalid/unvalidated response and unavailability. Rejected/unavailable
bodies and citations are hidden; exceptions are sanitized. Validated Markdown
(including the common case-field table) renders with HTML disabled. Sources show
title/document/section/version; expanders display exact literal quotations and
source/chunk identifiers. Formatting only adds table-block whitespace in the UI;
original AnswerResult and evidence offsets are unchanged. Synthetic disclosure is
always visible. No fabricated fallback answers, agents, databases or frameworks.

Verification: 61 focused UI/runtime/Week 1 tests passed; full `uv run pytest`:
585 passed (all prior 563 plus 22 new integration/composition tests).
`git diff --check` passed; local Streamlit server health/startup test passed.
All preexisting knowledge module hashes match the latest live reference; preserved
baseline/development artifact hashes were checked unchanged. No backend RAG
reliability logic, SOPs, gold labels or frozen baseline were changed. No new live
provider/UI inference was attempted; tests use doubles and a missing-key check.
No commit/push. Setup/limitations: `docs/WEEK2_STREAMLIT.md` and README.md.

## Task 17A: curated 15-question golden development profile

Inspected the available Week 2 framework/requirements, corpus design, project
state, six actual SOPs, original gold schema, runners/helpers/tests and saved result
directories before changes. PRD/separate handoff remain unavailable locally.
Existing evaluation already had 20 validated original records, binary section
labels/AND-OR evidence groups, retrieval metrics, disposition/citation/quote checks,
human claim/completeness exports and latency. Neither runner accepted ID subsets;
answer eligibility/review assumed 18, and some output/report paths overwrote files.

Frozen profile: `evaluation/week2/profiles/curated15_v1.json`, profile ID
week2-curated15-v1. IDs: Q01,Q02,Q03,Q04,Q05,Q07,Q08,Q09,Q10,Q11,Q12,Q13,Q15,Q19,Q20.
Exactly 10 answerable, 2 ambiguous and 3 unsupported. It pins the original gold
SHA-256 and adds corpus-verified human acceptance/safety notes. Original text,
classifications, relevant/context sections and evidence groups are unchanged in
`evaluation/week2/golden_questions.json` (all 20 retained). Q17/Q18 remain deferred;
no historical/conflict fixtures created. Q06/Q14/Q16 are unselected, not relabeled.
Full per-question acceptance/source/disposition review is documented in
`docs/WEEK2_CURATED15_EVALUATION.md` and resolved into output selection metadata.

Both existing runners now accept --profile PATH via shared evaluation_selection.py.
Omitting the flag retains the original full 20 definitions / 18 eligible questions.
Metadata records profile ID/path/hash, selected/executed/excluded/deferred IDs,
distribution, selected-record hash and resolved expectations. Review uses the saved
selection, supporting both 15- and 18-question runs. Only literal original question
text crosses KnowledgeService.ask; gold/criteria/labels are attached after response.
No prompt, retriever, generation, corpus or UI behavior was changed.

Retrieval retains initial K=5 Dense/BM25/Hybrid metrics unchanged. Ambiguous and
unsupported rows remain unscored/null/N/A. Answer outputs separate retained ranked
seed IDs/coverage from expansions and final context coverage. These seeds are
post-applicability context; raw pre-filter ranks discarded by the unchanged service
cannot be reconstructed and are not invented. Missing seed observations are N/A.
Citation/quote checks, human review exports and latency remain separate; answer
relevance is explicitly unmeasured, and faithfulness needs human review. No LLM judge.

Every run defaults to unique timestamped results/report paths. Explicit existing
output/report paths are refused; exclusive writes protect files. Human --review
writes a NEW reviewed run/report and copies review sheets instead of modifying
its input. Existing latest.json and reports are no longer refreshed. Preservation
manifest: `evaluation/week2/task17a_preservation_manifest.json` (65 prior artifacts,
including original gold and six SOPs); hashes verified unchanged. Non-runner RAG
module hashes also match the latest live reference.

Verification: 67 focused tests passed; full `uv run pytest`: 602 passed (all prior
585 plus 17 selection/runner/review tests). `git diff --check` passed. Tests cover
exact IDs/distribution, gold preservation, malformed profiles, full-set fallback,
N/A unsupported metrics, inference leakage, expansion separation, exports/review
for 15 and 18 questions, and non-overwriting outputs. No live Nebius calls were
made during implementation. Scripted test outputs are not measured model quality.
No commit/push, tuning, UI/product features, new framework, SOP or gold edits.

## Task 17D: final Week 2 evaluation report and closure status

**Acceptance status: pending sign-off. Week 2 is not formally closed.**
Final report: `docs/WEEK2_FINAL_EVALUATION.md`. This checkpoint supersedes earlier
pending-live statements for Task 17B/17C; it does not imply human quality approval.

Verified saved artifacts (no Nebius rerun):
- Task 17B: `evaluation/week2/results/retrieval/20261029T180407869874Z` is the
  latest completed curated15 retrieval run. The earlier completed
  `20261029T175736627946Z` has identical aggregate metrics. The pending
  `20261029T175715579764Z` run is not used for scores.
- Task 17C: `evaluation/week2/results/answers_development/20261029T181352053697Z`
  completed 15/15 curated questions. Profile ID/hash, original gold and six corpus
  hashes match current frozen inputs; sources.json matches all 32 actual chunks.
- Reconstructed rankings match evaluate_rankings output. Recomputed answer
  summaries, dispositions and citation checks match saved data. Human-review
  verification reads the official run CSVs without modifying them.

Current architecture/components: one repository and one Streamlit application
with separate Wire Validation and Knowledge Assistant views, frozen Week 1 payment
logic and independently testable knowledge backend. Week 2 includes six synthetic
SOPs/guides/catalog, 31 sections/32 structural-v1 chunks, ingestion/cleaning/metadata,
Nebius embeddings, cached document vectors, LangChain local cosine index,
Dense/BM25/equal-weight RRF, grounded generation, exact citation/quote checks,
clarification/evidence abstention/historical applicability, bounded quote recovery,
retrieved common-case checklist rendering, session-cached UI composition, frozen
20-question gold plus curated15 profile, metrics and human-review exports.

Verified curated15 retrieval macro metrics (10 answerable questions):
- Dense: Recall@5 .8500, Precision@5 .3000, MRR@5 .7083, NDCG@5 .6831,
  group coverage .9000, multi-document coverage .5000, complete evidence 8/10.
- BM25: .6000, .2200, .5250, .4962, .7000, .5000, complete evidence 6/10.
- Hybrid: .6667, .2200, .7200, .6009, .7667, .3333, complete evidence 7/10.
Multi-document denominator is Q07/Q08 only. Ambiguous/unsupported retrieval is
unscored/N/A. Hybrid's slightly higher MRR does not overcome its lower recall and
evidence coverage on this development set; Dense remains the existing default.
Final expanded answer context covers all required groups on 10/10 answerable
questions; this does NOT establish that answers explain all required procedures.

Verified generation/refusal results: 15/15 correct dispositions (10 answered,
2 clarified, 3 evidence abstentions), 10/10 answerable response coverage, zero final
invalid/incomplete-evidence/unavailable responses. One Q05 initial unmatched quote
was rejected and its fresh bounded retry validated. Accepted structural citation
membership is 27/27 and supporting-passage verification 47/47. These are mechanical
checks, not 100% answer correctness, semantic citation quality or faithfulness.

Official human-review exports remain incomplete: claims.csv has 52 mechanical
candidate rows, all assessments/reviewers/segmentation confirmations blank;
completeness.csv has 10 rows, all assessments/reviewers blank. read_human_review
reports zero reviewed claims/procedures and null faithfulness. No completed
relevance or semantic-citation ratings are available. >=90% human answerable-claim
faithfulness is unmeasured; partial/unsupported claims must remain in the denominator
once reviewed, with no full-support numerator credit. Formal procedural completeness
and answer relevance are also unmeasured, not zero or perfect scores.

Completeness observations requiring reviewer adjudication (not new gold labels or
human ratings): Q05 does not explicitly state recovery uncertainty or owner/next-
checkpoint assignment and does not explicitly list the requester-verification
reviewer; Q07 retrieves EX-DUPLICATE but references it without explaining candidate
comparison and Payment Exceptions supervisor review; Q20 does not clearly state
final disposition/evidence references and conditional matched confirmation for any
claimed funds movement. Other supported material in those answers is retained.
Q08 now includes the actual common-case table/warning, but all other procedural
claims still need human review. No ratings were invented or existing CSVs edited.

Latency: P50 4.592s; P95 12.775s (Q04, no retry), startup separately 1.221s. Observed
P95 is 0.775s above the 12s target. With N=15, nearest-rank P95 is the maximum;
the required >=100-query warm benchmark is outstanding, and no causal provider/
network/local breakdown is available. Saved model-path classification is not a
completion-call trace (Q13 is deterministic). Same-question reused development
results, small refusal/multi-document samples and section-level labels limit
conclusions. No independent-generalization or production-readiness claim is made.

Important decisions retained: synthetic corpus only; one app/separate backends;
Dense top-5 plus bounded evidence expansion; model/provider settings in environment;
no dashboard records passed to LLM; strict fail-closed source/version/quote rules;
one fresh retry only for quote_not_found; no silent source substitution or repair;
gold labels used only after inference; original baseline/profile/results preserved.

Deferred/out of scope: Q17/Q18 archived/conflicting-source fixtures, held-out broader
paraphrases/adversarial evaluation, formal warm latency benchmark, completed human
quality review, authenticated end-to-end UI acceptance record, and formal closure.
No agents, new vector database, reranking, payment execution, real bank policies or
new framework are introduced. The authoritative next-week PRD/handoff is unavailable;
no Week 3 feature scope is inferred. The next agreed milestone is human review and
formal Week 2 sign-off, followed by owner confirmation of the next roadmap stage.

Task 17D verification: 67 focused offline evaluation/profile/review tests passed;
`git diff --check` passed. Read-only integrity checks confirmed all 115 captured source, corpus, frozen
profile and prior evaluation files unchanged. Only this document and the final report change.
No application, retrieval/generation, UI, SOP, gold/profile or result changes;
no live calls, commit or push. Existing Week 1 completion history remains intact.

## Dependencies and commands

- Python 3.13 (.python-version; project requires Python >=3.13).
- uv manages the environment and uv.lock.
- Runtime: Streamlit >=1.65.0 (locked to 1.65.0 plus transitive dependencies).
- Development: pytest >=9.1.1 (locked to 9.1.1).
- Week 2 runtime additions: langchain-core, httpx, rank-bm25, and numpy, managed
  by uv/uv.lock. Embeddings use NEBIUS_API_KEY from the process environment.
- Build backend: uv_build >=0.12.23,<0.13.0.

```powershell
uv sync --locked
uv run pytest
uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
```

## Remaining blockers and warnings

Week 1 remains complete and frozen at 04f29e2. Week 2 implementation and curated
live evaluations are complete; formal closure is pending human claim/procedural,
answer-relevance and semantic-citation review, Q05/Q07/Q20 completeness adjudication,
and latency-target qualification or explicit owner acceptance. See the final report.
Authenticated UI acceptance has not been recorded in the available artifacts.
Current Codex process credentials are not needed for this documentation-only task;
no new Nebius evaluation was run. Archived/conflict fixtures and held-out evaluation
remain deferred. Original PRD/separate handoff/next-week specification are unavailable
locally. No favorable reviewer judgment, achieved faithfulness target or next-week
feature scope is inferred from missing evidence. No commit/push without instruction.

Environment warnings encountered: an unrelated VIRTUAL_ENV is ignored by uv;
restricted uv cache access required elevated execution; Git may normalize LF
to CRLF on Windows. These did not prevent successful verification.
The scaffold console command payment-ops still prints a greeting; use the
documented Streamlit launch command. Project description metadata remains a
placeholder, with no effect on simulator operation.

Git review retains application files and excludes environments, bytecode,
pytest caches, .env files, and Streamlit secrets. No credentials were identified
in reviewed project files; secret-pattern inspection is not a formal security audit.

## Explicitly out of scope for Week 1

Real banking integrations, payment execution/release, authentication, databases,
API servers, AWS infrastructure, RAG, LLMs, and AI agents. No additional banking
rules, production controls, or Week 2 features were implemented.

## Next task

Complete the official Task 17C human claim/completeness review on a separate copy
of `evaluation/week2/results/answers_development/20261029T181352053697Z`.
Verify atomic segmentation, reviewer coverage and all supported/partial/unsupported
judgments; record relevance/semantic-citation assessments and adjudicate Q05/Q07/
Q20 omissions against the frozen profile. Do not alter gold/SOPs to improve scores.
Then resolve or explicitly accept the latency/UI-acceptance gaps and record formal
Week 2 sign-off before confirming the next roadmap stage with the owner. Task 17D
stops after documentation/reporting; no unnecessary live rerun or automatic commit.
