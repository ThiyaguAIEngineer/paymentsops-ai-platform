# Week 2 PaymentOps Knowledge Assistant: final evaluation

**Acceptance status: pending sign-off.** Functional implementation and saved live
development evaluations are complete. Human quality review is incomplete, observed
latency exceeds the target, and procedural completeness findings remain open.
**100% disposition accuracy is not 100% answer correctness or faithfulness.**

## 1. Objective, artifacts and verification method

Evaluate whether the existing RAG backend retrieves relevant operational evidence,
chooses the expected answer/clarify/abstain disposition, validates citations and
quotations, and supplies complete, faithful guidance within the requested scope.
This report uses saved results; no Nebius evaluation was rerun for Task 17D.

| Evidence | Saved location under `evaluation/week2/results/` | Status |
| --- | --- | --- |
| Task 17B retrieval, primary/latest completed run | `retrieval/20261029T180407869874Z/results.json` and `report.md` | complete-real-embeddings |
| Earlier completed retrieval run | `retrieval/20261029T175736627946Z/results.json` and `report.md` | Same aggregate metrics |
| Task 17C answer evaluation | `answers_development/20261029T181352053697Z/results.json`, `sources.json`, `report.md` | complete-real-qa; 15 questions |
| Official claim-review export | `answers_development/20261029T181352053697Z/claims.csv` | Assessments incomplete |
| Official procedural review export | `answers_development/20261029T181352053697Z/completeness.csv` | Assessments incomplete |

Both completed retrieval runs use the same curated profile and produce identical
aggregate metrics; neither is treated as independent validation. The earlier
`retrieval/20261029T175715579764Z` run is pending and is not a metric source.

Verification was read-only: validate the original gold dataset/profile against the
actual corpus; check profile, gold and corpus hashes; reconstruct saved rankings
and recompute metrics with `evaluate_rankings`; recompute answer summaries,
dispositions and citation checks with the existing helpers; compare source
snapshots to the 32 actual chunks; inspect review files using `read_human_review`.
Recomputed values match saved results. No reviewer labels or result files were
changed. Baseline V1 remains preserved separately with its original denominator.

## 2. Corpus, architecture and frozen profile

The active corpus contains six fictional Northstar Demo Payments documents:
Wire Recall SOP, ACH Returns Guide, Payment Error-Code Catalog, Beneficiary
Validation Runbook, Payment Exception Handling SOP, and Settlement and Payment
Status Guide. It contains 31 sections and 32 structural-v1 chunks, version 1.0.0,
effective 2026-10-28, with document/section/version/source metadata and stable IDs.
These are synthetic educational procedures, not actual bank or regulatory policy.

One repository and one Streamlit application provide Wire Validation (Week 1) and
Knowledge Assistant (Week 2). The independently testable knowledge backend uses
ingestion/structural chunking, Nebius adapters, a content-addressed document-vector
cache, a LangChain local cosine index, BM25, and equal-weight RRF. Dense top-5 is
the production baseline, with existing bounded explicit-reference/requested-scope
evidence expansion. Grounded generation enforces schema, source membership and
exact source quotations; historical applicability, clarification, unknown-code
abstention and fail-closed behavior remain in place. No payment records are sent
automatically from Week 1 to the LLM, and there is no payment execution.

The frozen profile is `evaluation/week2/profiles/curated15_v1.json`, profile ID
`week2-curated15-v1`, SHA-256
`8abfd23d4caf35bca61c2c50b9b8de8b1088ee155ec42076547c0b215fcd0504`.
It references the unchanged 20-question `evaluation/week2/golden_questions.json`,
SHA-256 `6b229d92923a1737f34a7fe3704f40cba8a78bc9e0680e3724e308a89cf1132d`.

Selected IDs: Q01, Q02, Q03, Q04, Q05, Q07, Q08, Q09, Q10, Q11, Q12, Q13, Q15,
Q19, Q20: **10 answerable, 2 ambiguous, 3 unsupported**. Q06/Q14/Q16 remain in the
original dataset but are unselected. Q17/Q18 remain deferred; no archived/conflict
fixtures were introduced. Gold criteria and labels are applied after inference,
never supplied as answer context or instructions to KnowledgeService.

Saved model/configuration: Nebius `Qwen/Qwen3-Embedding-8B`, 4096 dimensions;
generation `Qwen/Qwen3-30B-A3B-Instruct-2507`; prompt grounded-v7-development;
temperature 0; 1,800 output tokens; 45-second generation timeout per call. Only an
initial quote_not_found can trigger one fresh generation using unchanged sources
and full revalidation. Task 17D changes none of these settings.

## 3. Initial retrieval comparison

Metrics below are macro averages over **10 answerable questions**, using binary
unique-section relevance in the initial five chunk slots. Repeated sections still
consume slots. Required groups are AND across groups and OR within alternatives;
group completeness is not claim-level or procedural completeness. The five
ambiguous/unsupported questions have observation-only retrieval, with metrics N/A.
Multi-document coverage uses only **Q07/Q08 (2 questions)**.

| Metric | Dense | BM25 | Hybrid RRF |
| --- | ---: | ---: | ---: |
| Recall@5 | 0.8500 | 0.6000 | 0.6667 |
| Precision@5 | 0.3000 | 0.2200 | 0.2200 |
| MRR@5 | 0.7083 | 0.5250 | 0.7200 |
| NDCG@5 | 0.6831 | 0.4962 | 0.6009 |
| Required evidence-group coverage | 0.9000 | 0.7000 | 0.7667 |
| Multi-document evidence coverage | 0.5000 | 0.5000 | 0.3333 |
| Required-document coverage | 0.9048 | 0.5952 | 0.6905 |
| All-required-groups satisfied | 8/10 (80%) | 6/10 (60%) | 7/10 (70%) |

RRF uses rank constant 60 and equal weights; BM25 uses k1=1.5, b=0.75. Hybrid's
MRR is slightly higher than Dense's, but its recall, precision, NDCG and group
coverage are lower. These results support retaining the current Dense baseline;
they do not establish that Hybrid generally underperforms on unseen questions.

The answer run's retained seed evidence had group coverage 2/3 for Q07 and 1/3 for
Q08. Expanded final context reached 3/3 for each; all ten answerable questions had
their required groups represented in final context. This is **retrieval evidence
availability**, not proof that the answer used all that evidence. Seed IDs exposed
by AnswerResult are post-applicability-filter context, not a raw pre-filter trace;
the standalone retrieval evaluation remains authoritative for initial rankings.

## 4. Generation and refusal results

| Measure | Verified result |
| --- | ---: |
| Eligible questions executed | 15/15 |
| Expected response disposition | 15/15 (100%) |
| Answerable questions with substantive responses | 10/10 |
| Ambiguous questions clarified (Q09/Q10) | 2/2 |
| Unsupported questions abstained (Q13/Q15/Q19) | 3/3 |
| Final invalid responses | 0/15 |
| Final incomplete-evidence dispositions | 0/15 |
| Unavailable responses | 0/15 |
| Substantive response rate, all questions | 10/15 (66.7%) |
| Structural citation membership | 27/27 (100%) |
| Exact supporting-passage verification | 47/47 (100%) |
| Answered responses with cited mechanical claim candidates | 10/10 |

Q13 preserves the undocumented identifier and does not invent its meaning. Q15
abstains on universal legal requirements. Q19 returns policy_period_unsupported
instead of projecting the current SOP backward into 2024. These observations cover
only the selected questions, not broad refusal/safety reliability.

Q05 initially failed quote_not_found, then passed after the single bounded retry;
its saved diagnostics preserve both events. Zero **final** invalid responses does
not mean zero initial validation failures. No rejected quotation was accepted or
automatically repaired. The 27 citations/47 passages include Q13's supported
escalation guidance; clarification and empty-evidence fallbacks receive no perfect
quotation score by default.

## 5. Human quality review: unmeasured

The saved result has `human_review: null` and `answer_relevance: null`.
Read-only verification of the official exports found:

| Review requirement | Current state |
| --- | --- |
| Mechanical claim candidates / exported rows | 52 / 52 |
| Rows with assessment, reviewer and confirmed segmentation | 0/52 |
| Assessment/reviewer/segmentation fields | All blank |
| Answerable procedural-review rows | 10 |
| Completeness assessments with reviewer | 0/10 |
| Verified faithfulness score | **Unmeasured** |
| Verified procedural completeness score | **Unmeasured** |
| Answer relevance | **Unmeasured** |
| Semantic citation correctness / claim entailment | **Unmeasured** |

The 52 candidates are mechanical sentence segments, not reviewer-confirmed atomic
substantive claims. Reviewers must split compound claims, confirm every original
candidate remains covered, verify citation association and record reviewer identity,
assessment and segmentation_confirmed=yes. Existing exports cover answered claims;
abstention/clarification guidance also needs manual inspection.

Once all substantive claims are reviewed, faithfulness is **Supported claims /
all reviewed substantive claims**. Partially supported and Unsupported receive no
full-support numerator credit and remain in the denominator. Report answerable
claim faithfulness separately from all-generated-answer claim faithfulness; the
>=90% target applies to answerable claims. Do not compute a favorable score from
a partially reviewed subset or count abstentions as perfect faithfulness.

For procedural review, assess all ten answerable cases using the existing categories
(complete supported, appropriately bounded, missing essential procedure,
unsupported additional instruction, unnecessary abstention). After full review,
report category counts, complete_supported_answer / 10 and, separately,
appropriately_bounded_answer / 10; do not equate bounded guidance with a full
procedure. No such ratings
are currently present; **0% review coverage is not a 0% quality score**. No Partial
or Unsupported labels were removed or recast; no claim labels exist yet to score.
Answer relevance and semantic citation correctness need explicit human assessment;
the current exports do not contain separate completed ratings for those dimensions.

## 6. Q05, Q07 and Q20 completeness findings

These are artifact/source inspection findings for reviewer attention, **not official
human assessments or new gold labels**. Their answered disposition does not settle
whether the requested guidance is complete or adequately bounded.

| Question | Supported content visible in saved answer | Outstanding completeness issue |
| --- | --- | --- |
| Q05, where to start a released-wire recall | Release/prerequisite checks, required details, requester verification outcome, duplicate avoidance and supervisor review | Recovery uncertainty is not stated explicitly. The answer lists a proposed owner but omits assigning an owner and recording the next checkpoint; requester-verification reviewer is not explicitly listed alongside the outcome. Review against WR-ELIGIBILITY/WR-REQUEST and the getting-started scope, rather than requiring unrelated later closure stages. |
| Q07, delayed status/resend checks and escalation | Last confirmed state, uncertainty, event matching, no-resend hold, Reconciliation/rail routing and escalation checkpoint | EX-DUPLICATE was retrieved, but the answer references it without explaining its candidate comparison and Payment Exceptions supervisor-review gate. Its actual citations cover SS-DELAY, EC-STATUS and EX-ESCALATE, not EX-DUPLICATE. Available context and a cross-reference do not establish delivered procedural coverage. |
| Q20, duplicate-case closure evidence | Candidate comparison, distinct-obligation/duplicate determination, known outcomes, reconciliation findings, supervisor review, retry decision and closure metadata; missing evidence keeps case open | EX-CLOSE's explicit final disposition with evidence references and conditional matched confirmation for claimed funds movement are not clearly spelled out. Reconciliation findings are mentioned; reviewers must decide whether the wording is sufficient for the requested closure scope. |

Q08's final answer includes the application-rendered EX-EVIDENCE table and its
warning, with citations to the retrieved SOP. That addresses the prior common-field
omission but does not automatically validate its remaining generated procedural
claims. Any omissions or partially supported claims found in review must remain in
the official assessments; they must not be waived to preserve a disposition score.

## 7. Citation-validation boundaries

Membership and literal quote checks verify source identity, metadata and exact
stored passage offsets. They do not prove that a quoted passage entails the whole
claim, that a sequence/gate is complete, that a related procedure was actually
explained, or that synthetic procedures are real policy. Mechanical inline-citation
coverage likewise does not establish atomic claim coverage. Q07 illustrates this
boundary: all checked citations are structurally valid while a requested procedure
may still be incompletely explained. Semantic citation correctness remains a
human-review obligation. The fail-closed validator is not weakened for this report.

## 8. Latency and target gap

| Timing | Saved answer-run result |
| --- | ---: |
| Overall P50 | 4.592 seconds |
| Overall P95 | 12.775 seconds |
| Model-path P50 / P95 | 4.592 / 12.775 seconds (12 classified model-path rows) |
| Startup/index initialization, separately recorded | 1.221 seconds |
| Warm-query target | P95 <=12 seconds |
| Observed excess over 12 seconds | 0.775 seconds (about 6.46%) |

These are service-call wall times, including query embeddings, retrieval,
generation/any recovery, validation and fallbacks, excluding separately measured
startup and UI rendering. The saved model-path label is the evaluator's reason-code
classification, not a network request trace: in particular Q13's deterministic
catalog response does not generate an LLM completion. Overall timings retain all
15 questions, including fast clarifications.

With 15 observations and nearest-rank percentiles, P95 is the maximum: Q04 at
12.7747635000851 seconds. Its row has no recovery diagnostic. The sample does not
isolate provider/network, embedding, generation or local processing time; it cannot
establish a causal explanation or a stable workload percentile. The framework's
>=100-query, warmed, concurrency-one benchmark has not been completed. Thus the
observed run exceeds 12 seconds and the formal warm-query target is **not met or
established**. No speculative performance changes or new API calls were made here.

## 9. Development-set and scope limitations

The same small corpus/questions informed development, scope fixes and evidence
expansion. The curated 15 are not held out, and their denominator differs from
the original 18-eligible Baseline V1. Aggregate score changes must not be called
independent generalization or compared as if question populations were identical.
There are only two multi-document questions, three unsupported cases and two
clarifications. Section-level relevance can overstate actual claim completeness;
Q17/Q18 historical/conflict fixtures, held-out paraphrases and broader adversarial
evaluation remain deferred. Model aliases/provider behavior and latency can vary.

The original PRD/separate handoff and an authoritative next-week specification
remain unavailable locally. Existing supplied requirements, framework, corpus,
profile and saved results define this report's scope. No claim is made about real
bank compliance, live payment access/execution or production deployment readiness.

## 10. Acceptance and next milestone

**Pending sign-off; Week 2 is not ready for formal closure on the available evidence.**

Completed: six-document synthetic corpus, ingestion/chunking, real embeddings and
cache/index, Dense/BM25/RRF retrieval, grounded generation/strict validation and
safe fallback, bounded recovery, exact common-case checklist rendering, frozen
profile/evaluation runners/review exports, and integration into the unified
Streamlit application. Offline integration is verified; these evaluations are
backend evaluations, not authenticated end-to-end UI acceptance evidence.

Closure requires:

1. Complete reviewer-confirmed atomic segmentation, claim support and procedural
   assessments on a separate review copy; calculate the >=90% answerable faithfulness
   metric without discarding partial/unsupported claims.
2. Record answer-relevance and semantic citation assessments, and adjudicate Q05,
   Q07 and Q20 completeness findings against the frozen criteria. Any proposed
   behavior change is a separate task, not part of this documentation update.
3. Address or explicitly accept the latency gap and qualify the warm-query benchmark;
   record the owner/reviewer's acceptance decision rather than inventing sign-off.
4. Record authenticated UI acceptance and formal Week 2 sign-off, then confirm the
   next roadmap stage with the project owner. No undocumented Week 3 feature or
   agent implementation is inferred from the current repository.

Week 1 completion history and frozen evaluation/source artifacts remain intact.
Task 17D modifies documentation only; nothing is committed or pushed automatically.

## 11. Offline documentation verification

Task 17D's focused evaluation/profile/human-review tests passed: **67 tests**.
`git diff --check` passed. Saved metrics were recomputed offline as described above;
all 115 captured source, corpus, frozen profile and evaluation files were verified
unchanged.
No Nebius calls, new judgments, CSV edits or application changes were made.
