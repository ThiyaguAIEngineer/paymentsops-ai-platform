# Week 2 unified Streamlit integration

One repository, one application and the existing entry point remain:

```powershell
uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
```

The sidebar Workspace radio selects Wire Validation (default) or Knowledge
Assistant. The Week 1 dashboard body, sample data, filters, decisions, metrics,
connector evidence and backend remain unchanged. Navigation does not introduce a
second application or send dashboard records to the knowledge service.

## Source of truth and scope

The original/current PRD and PaymentOps_AI_Project_Handoff.md are not present in
the repository or its parent directory. The supplied Task 16 requirements,
docs/WEEK2_FRAMEWORK.md, PROJECT_STATE.md and existing code/tests supplied the
available requirements and architecture decisions. The framework's initial model
and retrieval proposals are historical; current composition follows the verified
implementation, not those superseded planning hypotheses.

The latest live reference is
`evaluation/week2/results/answers_development/20261029T012444697570Z`,
grounded-v7-development, 17/18 correct development dispositions. Q20 safely returns
invalid_response after quote_in_different_source. This integration does not modify
that behavior, the reliability logic, SOPs, gold labels, or frozen evaluation
artifacts. Human faithfulness/completeness remains unmeasured; same-set disposition
accuracy is not independent validation or a faithfulness score.

## Configuration and initialization

The existing adapters read configuration from the environment of the process
launching Streamlit. Make NEBIUS_API_KEY available securely in that terminal; do
not enter it in the question box or commit it. Set the verified model IDs:

```powershell
$env:NEBIUS_EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"
$env:NEBIUS_GENERATION_MODEL = "Qwen/Qwen3-30B-A3B-Instruct-2507"
uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
```

KNOWLEDGE_GENERATION_PROVIDER defaults to nebius through the existing adapter.
The existing optional NEBIUS_BASE_URL setting remains supported by the adapters.
There is no new UI credential store, .env loader, provider or dependency. Restart
the app after changing configuration; session-cached clients retain their initial
configuration until released.

`knowledge/runtime.py` is a composition function, independent of Streamlit. It
loads/chunks the existing corpus, constructs the existing Nebius adapters, reuses
CachedEmbeddings and LocalVectorIndex, and returns the existing KnowledgeService
with Dense retrieval and the complete section_catalog. Corpus/cache paths are
anchored to the repository rather than the working directory. No reliability
algorithm or service response model is changed. Partial initialization closes
clients on failure; a finalizer closes clients when the service is released.

`ui/knowledge_view.py` uses Streamlit's session-scoped cache_resource (the installed
and locked Streamlit 1.65 supports this API). The first nonempty Ask submission
initializes the service/index. Subsequent reruns and submissions in that browser
session reuse it. Other sessions build their own in-memory resources while reusing
the existing on-disk document embedding cache. The session cache is removed on
disconnect; resources are reclaimed when no longer referenced. It is not persistent
conversation storage.

Opening either view, editing an unsubmitted draft, expanding evidence or ordinary
reruns do not invoke the service. Only a submitted nonempty question calls
`KnowledgeService.ask(question)`. No payment object or Week 1 session data is passed.
The latest submitted question and AnswerResult are held in that browser session;
generated answers are not globally cached or substituted with canned responses.

## Presentation and safety

| Existing response | Presentation |
| --- | --- |
| answered | Answered status and validated Markdown body |
| limited_answer | Scope warning and validated limited guidance |
| clarification | Clarification required and the service's follow-up question |
| insufficient_evidence | Evidence warning; supported escalation citations retained if present |
| reason invalid_response/unvalidated_response, or unknown status | Rejected-response notice; body and citations hidden |
| unavailable | Service-unavailable message; body and citations hidden |
| Initialization/call exception | Sanitized operator/configuration/connectivity message; no raw exception |

Document title, document ID, section and version appear for each citation. Expand
Supporting evidence to inspect the exact supporting passages, source slot and chunk
ID. Quotations render as literal text/code, not executable HTML. The answer renders
with Streamlit Markdown and unsafe HTML disabled. A presentation-only formatter
adds blank lines around pipe tables so the service's required case-evidence table
and following warnings render separately. It does not modify stored AnswerResult,
source passages or citation offsets.

The synthetic educational disclaimer is always visible. Empty submissions and
errors clear the previous result to avoid showing a stale answer as the new result.
Unsubmitted edits leave the last answer labeled with its actual submitted question.
Session navigation can redisplay that answer without another provider call.

## Verification and limitations

Tests use AppTest and service/provider doubles, covering successful answers,
sources/quotes, structured Markdown, clarification, evidence abstention, limited
guidance, invalid/unavailable envelopes, initialization failures, cache reuse,
submission-only execution, navigation and unchanged Week 1 interactions. Offline
runtime tests verify the composition, cache identity/paths and cleanup. AppTest
uses the same literal session ID across instances, so test fixtures clear resource
caches between tests while verifying reuse across reruns within a test.

No real provider calls were made for UI verification; live end-to-end UI acceptance
requires the operator's configured environment. First submission may take longer
for initialization; the existing bounded quote retry can add generation latency.
This integration makes no new latency or faithfulness claim and does not repair the
remaining Q20 attribution failure. Human review remains necessary. There is no
authentication, deployment, payment execution, persistent chat, agent or new
database in this task.

Verification: 61 focused UI/runtime/Week 1 tests passed; full suite: 585 passed
(22 new tests). `git diff --check` and the local Streamlit health/startup test
passed. Existing RAG module and preserved artifact hashes remain unchanged.
See PROJECT_STATE.md for the next acceptance milestone. No commit
or push is performed automatically.
