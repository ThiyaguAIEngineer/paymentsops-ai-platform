# Week 3 MVP PRD: Payment Investigation Agent

**Status:** proposed design for owner review; no implementation authorized by this document.
**Prepared:** November 9, 2026 (America/New_York).
**Course deadline:** November 11, 2026; exact upload cutoff/timezone is unconfirmed.

## 1. Goal, boundaries and acceptance

**One-line definition:** My agent helps payment operations analysts replace manual
cross-control evidence gathering for an existing synthetic commercial wire with
stateful investigation through read-only payment lookup, Core, Limits, Fraud and
Sanctions tools, targeting correct evidence-backed outcomes on all three MVP demo
scenarios with zero payment mutations and recommendation-only human review.
This measurable MVP success target is unverified, not an achieved result.

Build one bounded LangGraph agent inside the existing Streamlit application.
The LLM chooses the next evidence tool from an allowlist based on the selected
payment, observations and remaining work. Deterministic code validates actions,
executes tools, evaluates controls, enforces limits and manages review/resume.
This is more than a fixed sequence of checks: the trace must expose actual
model-selected actions and subsequent state-dependent choices. Fixed-order
fallback behavior must be labeled degraded, not presented as successful LLM planning.

The owner declares Weeks 1 and 2 complete for course progression. Historical Week 2
records still show outstanding human quality review and formal latency benchmarking;
this PRD neither changes those results nor makes them Week 3 implementation work.

Acceptance requires:

- Select an existing synthetic payment; start an independent investigation.
- Invoke actual mock connector methods, one tool at a time; retain observations,
  completed/failed attempts, remaining work and bounded planner decisions.
- Have the model choose among multiple eligible tools on a normal run; show that
  different valid plans can reach the same deterministic control findings.
- Continue independent checks after a connector failure and produce an explicit
  incomplete-evidence escalation rather than inventing a passing result.
- Pause with a versioned recommendation, accept human review, and resume either
  to completion or one bounded further-investigation cycle and another review.
- Display unambiguous investigation outcomes and preserve all payment inputs.

Human acceptance concerns the **investigation recommendation only**. There are no
release, reject, cancel, settle, repair, transmit or payment-update actions.
Existing engine labels describe simulated control findings, never a payment action.

## 2. Source-of-truth inspection and repository checkpoint

Reviewed in the requested order: search for the current PRD; search for
`PaymentOps_AI_Project_Handoff.md`; inspect project state; inspect implementation;
review architecture/decision documentation; review Week 2 submission/evaluation.
No original PRD or separate handoff was found in the repository or its parent
directory. No claim is made to have inspected unavailable artifacts. The supplied
Week 3 requirements govern the proposal; older Week 2 exclusions of agents applied
to that week's scope, not this new task.

| Inspected component | Existing capability / integration implication |
| --- | --- |
| `services/payment_service.py` | `PaymentService(core, limits, fraud, sanctions)`; `process_payment(payment)` returns `DecisionResult`; `process_payment_with_evidence(payment)` returns immutable `PaymentProcessingResult`. Valid input triggers all four connector lookups in a fixed order; invalid input skips them. Do not use this method as the agent's tool dispatcher. |
| `samples/payments.py` | `SYNTHETIC_PAYMENTS` is a tuple of 20 immutable `Payment` instructions with unique synthetic scenario IDs. There is no dedicated public payment-ID lookup service; add a Week 3 lookup wrapper over this tuple. UI lookup currently uses selection plus a generator expression. |
| `connectors/base.py` | Read-only Protocols and frozen response dataclasses for Core, Limits, Fraud and Sanctions; failures use `ConnectorError`/`RecordNotFoundError`. |
| `services/decision_engine.py` | Pure `evaluate_payment(payment, *, account=None, limits=None, fraud=None, sanctions=None)` returns ordered checks and deterministic severity/primary reason. Rejection takes precedence over review; unavailable controls require review unless an available rejection dominates. |
| `services/results.py` | `ConnectorEvidence` and `PaymentProcessingResult` retain frozen responses separately from decisions. Preserve these contracts. |
| `knowledge/service.py` | `KnowledgeService.ask(question, *, method=None) -> AnswerResult`; statuses include answered, limited_answer, clarification, insufficient_evidence and unavailable; reason codes and citations remain significant. Normal inference does not consume gold labels. |
| `knowledge/runtime.py` | `create_knowledge_service()` composes existing Dense retrieval, local cache/index and Nebius adapters; initialize lazily only if optional guidance is enabled. |
| `knowledge/generation.py` | `GenerationProvider.generate(system_prompt, user_prompt) -> str`; Nebius JSON chat adapter with model verification, temperature zero and configurable timeout/output limit. It rejects native model `tool_calls`, so reuse JSON action selection plus application dispatch rather than claiming native function calling. |
| `ui/app.py`, `ui/knowledge_view.py` | Sidebar `Workspace` radio currently offers Wire Validation (default) and Knowledge Assistant. Knowledge resources initialize on Ask and are session cached. Future integration adds a third view with a lazy import, preserving both current views. |
| `pyproject.toml`, `uv.lock`, local environment | Python 3.13; `langchain-core`, Streamlit, httpx, NumPy and rank-bm25 exist. Neither full `langchain` nor `langgraph` is declared/locked; local import discovery confirms LangGraph is absent. No dependency changes made for this task. |
| `tests/` | pytest fixtures, parametrization and `unittest.mock` connector/provider doubles; Streamlit `AppTest` for UI, cache isolation and submission-only calls. Existing tests avoid live APIs. |

Current branch: `feat/week2-knowledge-assistant`; HEAD `cdea169` (Week 2 submission
documentation). Tracked working files were clean at inspection. Two untracked
local exports exist: `PaymentOps_Week2_Demo_Script_and_Screen_Guide.docx` and
`PaymentOps_Week2_Submission_Formatted.docx`; preserve and exclude them.

**Branch recommendation:** after approval, create
`feat/week3-payment-investigation-agent` from `cdea169`/the current Week 2 tip.
The local default branch is named `master`, not `main`, and is not a reliable
Week 2 implementation base. Do not merge or rename branches to begin this MVP.
If Week 2 is not merged upstream, describe Week 3 as depending on the Week 2 branch
and use a stacked review/base until repository integration is deliberately resolved.
Do not reset the worktree or stage the DOCX exports. No branch is created here.

## 3. Smallest architecture and workflow

Use `StateGraph` with serial nodes, a session-local `InMemorySaver` and explicit
conditional edges. Existing `langchain-core` tools wrap mock connectors; a small
Week 3 planner calls the existing Nebius generation adapter with its own JSON
contract. No full LangChain agent framework or additional model adapter is needed.
Summary rendering is deterministic; defer an LLM-written narrative to avoid a
second source of unsupported financial claims.

```text
START -> load_payment_and_validate
            | unknown ID -> safe_failure -> END
            | invalid input -> evaluate_and_summarize
            v
         plan_next <------------------------+
            | allowlisted action            |
            v                               |
         execute_one_tool -> record_result -+
            | finish / invalid plan / budget exhausted
            v
         evaluate_and_summarize
            v
         human_review [interrupt: recommendation only]
            | accept -> finalize -> END
            | request one further check, eligible and within budget
            +-> plan_next -> execute_one_tool -> evaluate_and_summarize
                                 -> human_review again
            | stop / impossible request / review limit -> finalize escalation -> END
```

`record_result` may be part of `execute_one_tool`; the diagram separates its
responsibility, not a required extra module. Conditional edges must distinguish
initial collection from the single requested recheck: after that recheck, return
to summarization, not another unrestricted collection loop.

### Proposed state schema

One typed state per run; use JSON-safe records for checkpoint and interrupt data.
Serialize Decimal amounts as strings, dates as ISO strings and enums as values;
rehydrate trusted existing dataclasses at tool/engine boundaries. Keep provider
clients/tool objects in runtime dependencies, not in graph state.

| Field/group | Type and invariant |
| --- | --- |
| Identity | `run_id`, session-owned `thread_id`, `payment_id`; immutable after start. One payment per run. |
| Payment | Canonical serialized `Payment` snapshot and `input_errors`; selection must resolve to existing data, never model-created instruction fields. |
| Lifecycle | `phase`: loading, collecting, summarizing, awaiting_review, completed, escalated, failed. Separate `outcome_reason`; no payment-status field is writable. |
| Work | Required controls `{core, limits, fraud, sanctions}`, attempted/succeeded/failed sets, computed remaining controls, and pending action. Attempted is not the same as successfully evidenced. |
| Evidence | Current response per control plus append-only attempt records: attempt/evidence ID, tool name, bound input reference, normalized result or sanitized error category, sequence and elapsed time. Rechecks retain previous evidence and mark which attempt is current. |
| Planner | Validated `{action, reason}`; reason is a short display explanation, not private chain-of-thought. Append bounded action history with `source=model` or `source=fallback`. Never store raw rejected provider responses. |
| Limits | Tool-attempt count, planner-call count, extra-check-used, guidance-used, review-round count and active-execution elapsed time. Counters never reset on resume. |
| Findings | Serialized engine `DecisionResult`, unresolved evidence gaps, deterministic recommendation and evidence references; optionally separate procedure guidance and original citations. |
| Review | Recommendation revision, pending review ID, decision/note, reviewer label, requested control and review event history. Reviewer label is not authenticated identity. |

Update state by returning validated patches. Compute derived sets from recorded
attempts rather than trusting model-written state. Record unique event IDs to
avoid duplicating history during reruns/resume. Keep old attempts for audit;
recommendations cite current evidence IDs and explicitly identify unresolved errors.

### Read-only tools

All model-exposed tools take no arbitrary payment/account argument: the runtime
binds the selected run's validated payment. Use LangChain `StructuredTool` or
equivalent `langchain-core` wrappers, invoked by the dispatcher; this is actual
tool invocation through Python, not simulated tool text.

| Tool | Wrapper behavior / underlying interface |
| --- | --- |
| `lookup_payment(payment_id)` | Deterministic initial node/tool resolves exactly one item from `SYNTHETIC_PAYMENTS`. Invalid/unknown ID fails safely; not exposed for model-driven switching to another payment. |
| `get_core_evidence()` | Calls `CoreBankingConnector.get_account(payment.sender_account_id)`; one response supplies both account and balance checks. |
| `get_limit_evidence()` | Calls `LimitsConnector.get_limit(payment.sender_account_id)`; returns configured single-wire limit, not live usage. |
| `get_fraud_evidence()` | Calls `FraudConnector.screen(payment.payment_id)`; synthetic score/decision, not a newly computed fraud model result. |
| `get_sanctions_evidence()` | Calls `SanctionsConnector.screen(payment)`; predetermined synthetic screening, not real sanctions matching. |
| `get_procedure_guidance()` (optional, disabled by default) | Calls existing `KnowledgeService.ask` with a bounded generic question derived from a finding/approved topic, without payment identifiers, names or account fields. Keep guidance separate from payment evidence. |

`evaluate_payment` is a deterministic internal function, not an LLM-choice tool.
Use public connector Protocols and constructor injection; do not import the
private `_lookup` helper from PaymentService or change its behavior. New wrappers
must normalize exceptions and response types equivalently. RAG nonanswers,
rejected-response reason codes and provider failures never count as usable guidance.
Copy accepted citation structures unchanged; do not invent new citations or let
procedure text establish account balance, screening or settlement facts.

### LLM and deterministic responsibilities

- Model sees synthetic amount/ID as necessary, normalized findings, completed/error
  indicators and eligible action names; omit beneficiary/account details and secrets.
  It selects one eligible next tool, a permitted recheck, or `finish`, with a short
  reason. Initial planning offers all four unattempted controls; subsequent plans
  include observed results. Optional guidance is offered only when enabled.
- Code binds inputs, validates the exact action schema/allowlist, enforces all
  budgets, dispatches tools and supplies their real results. No dynamic imports,
  executable model code, arbitrary URLs or arbitrary tool names are accepted.
- All four controls must be attempted on valid input before a complete recommendation;
  model `finish` before this is invalid. Control order remains model-selected.
  A known adverse finding does not suppress the other independent checks.
- Code runs `evaluate_payment` on collected typed responses; failed/unattempted
  controls become sanitized `ConnectorError`/missing evidence, never fabricated
  PASS facts. Preserve available adverse findings and the engine's precedence.
- Code builds a fixed summary: instruction reference, facts/evidence IDs, each
  control status, unresolved gaps, engine finding and proposed review/escalation.
  Even READY FOR PROCESSING is displayed as an existing simulator finding, not
  authorization to release funds. Acceptance changes only investigation metadata.

## 4. Failure policy, limits and outcomes

**Bounds per investigation, including resume:** at most 7 dispatched tool attempts
(1 lookup + 4 initial connectors + 1 extra connector attempt + 1 optional guidance),
at most 8 planner generation calls, and 1 additional-investigation review cycle
(maximum 2 review pauses). All failed attempts count. The one extra connector
attempt may be consumed by one explicitly selected bounded transient recovery or
one human-requested recheck, not both. Permanent configuration errors and invalid
requests are not automatically retried. Every dispatched attempt, including failed
lookup and connector calls, counts toward the seven-attempt maximum. Rejected
pre-dispatch requests and idempotent replay of a recorded invocation do not dispatch
another tool. No automatic infinite retry; a persistent fixture failure remains failed.

Use a 15-second planner-call timeout and approximately 400 output tokens by
constructing a separate existing Nebius adapter instance for Week 3; leave Week 2
defaults unchanged. Target an active execution budget of 180 seconds, excluding
time waiting for human review; check remaining budget before each new operation.
Synchronous network calls already in flight may overrun that soft budget; do not
claim hard cancellation. Add graph recursion limit 40 per invocation as a last
guard, catch exhaustion at the controller and render a safe diagnostic. This is
a bounded demo design, not a promised performance benchmark.

| Event | Required behavior |
| --- | --- |
| Unknown ID | Fail with `invalid_selection`; no connector or model call. |
| Invalid payment fields | Retain input errors, skip connectors and planner, summarize deterministic input findings for review. Never convert into a corrected payment. |
| Connector exception, wrong type or invalid response fields | Record sanitized unavailable evidence; continue eligible independent controls. Engine checks still validate semantic field values. Allow at most the shared extra attempt. |
| Invalid/duplicate/premature-finish planner action or planner timeout | Record planner failure; switch once to a visibly labeled deterministic fallback that attempts outstanding controls in fixed order without further planner calls. Mark run degraded and require escalation review. Do not describe this as a successful autonomous plan. |
| Required evidence remains missing after attempts | Summary must say incomplete evidence / escalation required, regardless of a separate known rejection. Human acceptance cannot turn missing evidence into success. |
| Further investigation has no eligible action/budget | Retain review request; terminate with escalation and explicit limit reason, not a loop or fabricated new evidence. |
| Optional RAG unavailable or unsupported | Record guidance unavailable; preserve control findings. Do not make unsupported procedural recommendations. |

**Terminal outcomes:** `completed_reviewed` only after all required evidence is
usable, planning is not degraded, and a reviewer accepts the current recommendation;
adverse control findings can still be a successfully completed investigation.
`escalated` denotes unresolved evidence, planner degradation, rejected/unfinished
recommendation or exhausted limits. Reviewer acceptance of an escalation is stored
as acknowledgment, not `completed_reviewed`. `failed` denotes invalid selection
or unrecoverable orchestration error. `awaiting_review` is explicitly nonterminal.
No outcome denotes executed, approved, rejected or settled payments.

## 5. Human review, resume and Streamlit lifecycle

Compile the graph with a per-browser-session `InMemorySaver`. Assign a new opaque
thread ID per run and retain graph/checkpointer/controller in session state.
Do not use a global shared investigation cache. Start only on an explicit
**Investigate** submission; passive reruns/navigation do not rerun tools. A changed
payment selection requires a new run; old review controls must not apply to it.

Build the recommendation in a node before review. The review node calls
`interrupt()` with JSON-safe run/review IDs, recommendation revision, findings,
gaps and legal choices. Show **Accept investigation recommendation**, **Request
further investigation** (one specific connector plus a short note), and **End and
escalate**. Notes are data, not new executable instructions. The reviewer may
request a recheck only within the shared extra-attempt budget; it does not edit facts.

Resume with `Command(resume=payload)` using the same session-owned `thread_id`.
Validate run/review ID and revision before invoking and again in the graph;
duplicate/stale submissions must not replay tools. Record the review event after
`interrupt` returns. The review node must perform no tools/model calls before
the interrupt: LangGraph restarts that node on resume. Do not swallow its
interrupt signal in broad exception handling. Rebuild a new recommendation
revision after a further check and pause again for review.

This is in-process checkpoint state across steps and Streamlit reruns, **not
persistent memory**. Process restart/session loss discards the run; show that it
cannot be resumed and require a new investigation. No cross-user sharing,
database, authenticated reviewer identity or restart recovery is claimed.
The selected APIs follow the official
[LangGraph interrupt/resume documentation](https://docs.langchain.com/oss/python/langgraph/interrupts).
Prefer basic `invoke`, `interrupt`, `Command` and `InMemorySaver`; avoid newer
streaming/typed-interrupt features until the resolved installed version is tested.

## 6. Three demo scenarios and minimum verification

Expected findings below are derived from existing fixtures, not new live runs.

| Scenario | Demonstration / acceptance evidence |
| --- | --- |
| `SYNTHETIC-WIRE-001` | Active wire-enabled account, balance 100000.00, amount 12500.50 within limit 50000.00, Fraud PASS, Sanctions CLEAR. Show four actual tool invocations, state changes, all-pass simulator finding, review interrupt and accepted investigation completion. |
| `SYNTHETIC-WIRE-LOW-BALANCE` | Balance 100.00 against amount 12500.50; other controls available. Show evidence-backed insufficient-balance finding without taking payment action. Request a core recheck, resume with history retained, show unchanged mock result, then accept the updated recommendation. Successful investigation does not mean a ready payment. |
| `SYNTHETIC-WIRE-UNAVAILABLE` | Fraud fixture raises `ConnectorError`; Core/Limits/Sanctions remain available. Show continued checks, one bounded recovery if chosen, persistent unavailable evidence, explicit escalation and reviewer acknowledgment. Never stage a fake recovery or claim missing fraud evidence passed. |

Minimum automated tests (behavior-focused, offline provider doubles):

1. Selected lookup and bound arguments match the immutable sample; unknown ID
   fails without downstream calls; invalid-input samples skip controls.
2. Scripted planners choose different valid tool orders; real wrapped mock methods
   are invoked and both orders produce identical deterministic findings.
3. Low-balance/blocked/review fixtures preserve engine severity and all findings;
   unavailable controls cannot become passing findings.
4. Exceptions, malformed responses and persistent fraud failure are retained in
   state; other checks continue; retries/budget limits terminate safely.
5. Malformed JSON, unlisted tools, payment-switch attempts, duplicate calls and
   premature finish cannot invoke arbitrary actions; fallback is visibly degraded.
6. Tool/planner/review counters and active budget survive resume; invalid/stale
   review payloads cannot accept a newer recommendation or replay evidence calls.
7. Graph pauses before completion; acceptance invokes no payment actions; further
   investigation performs only its bounded check, updates revision, and pauses again.
8. State/thread isolation and snapshot serialization preserve Decimal/date values
   and evidence IDs; payment snapshots and source fixtures remain unchanged.
9. Streamlit AppTest: lazy third navigation view, start-on-submit only, trace and
   gap display, review/resume, selection changes, duplicate-click protection and
   session loss; existing Wire Validation/Knowledge Assistant tests still pass.
10. Optional RAG, only if enabled: mock `ask` verifies generic question without
    transaction details; unavailable/rejected guidance is not rendered as valid
    evidence and citations of accepted guidance are retained.

Use deterministic scripted planner/provider doubles in tests, clearly labeled
test infrastructure. A live recorded demonstration must use the actual model for
tool choice and actual mocks for tool execution; no prewritten decision trace
should be presented as live reasoning. Owner-authorized model rehearsal belongs
to a later task, not this planning task.

## 7. Implementation tasks and deadline plan

Prioritize the mandatory agent, failure trace and real interrupt/resume path.
Optional RAG is the first cut if the November 11 deadline is threatened.

| Task | Small deliverable and exit check |
| --- | --- |
| W3-T2: branch/dependency spike | After review, create the recommended branch; add only compatible LangGraph dependency via uv and lock. Test Python 3.13 imports and minimal interrupt/resume with an in-memory saver. Run existing regressions if dependency resolution changes shared packages. Stop and resolve incompatibility before building UI. |
| W3-T3: state and tools | Implement typed state, sample lookup, four injected read-only wrappers, serialization and budget guards; focused offline tool/immutability tests. |
| W3-T4: planner and graph | Reuse Nebius JSON generation through a separate Week 3 adapter instance; allowlisted action validation, serial graph, deterministic engine summary and safe fallback. Verify distinct model-action sequences using doubles and failure fixture. |
| W3-T5: review/resume | Add recommendation revisions, real LangGraph interrupt, one further-check cycle and terminal outcomes. Test stale resumes, preserved limits and no pre-interrupt repeated I/O. |
| W3-T6: Streamlit integration | Third navigation view, selector, explicit start, visible tool history/evidence, review buttons and session isolation. Preserve the two existing views and pass their regression tests. |
| W3-T7: acceptance/docs/recording | Run focused plus full offline suite and whitespace checks. Owner rehearses three scenarios with actual planner model, records traces/results and video; update project state and submission guide. Verify course cutoff/upload requirements and leave upload buffer on November 11. Commit/push only when separately instructed. |
| Optional, after mandatory acceptance | Add the one bounded RAG guidance tool with lazy initialization and separate citations; otherwise document it as deferred, not implemented. |

Suggested pacing: November 9 review/dependency/tools; November 10 graph/review/UI
and regressions; November 11 early rehearsal, recording and submission buffer.
Do not add features on the submission day at the expense of recovery/review tests.
No effort estimate is a guarantee of provider availability or course acceptance.

## 8. Expected files and reuse boundary

Proposed new modules (combine rather than proliferate if small):

- `src/payment_ops/investigation/__init__.py`, `state.py`, `tools.py`, `planner.py`,
  `graph.py`, `runtime.py`; deterministic summarization can live in `graph.py`.
- `src/payment_ops/ui/investigation_view.py`.
- `tests/investigation/test_tools.py`, `test_planner.py`, `test_graph.py`, and
  `tests/test_investigation_dashboard.py`.
- Later `docs/WEEK3_DEMO_SCRIPT.md` and a compact Week 3 acceptance record.

Expected integration edits **in later authorized tasks only**: `pyproject.toml`
and `uv.lock` for LangGraph, `ui/app.py` for one new navigation option/lazy view,
and README/PROJECT_STATE for launch/status. Today creates this PRD only.

Reuse without changes: Payment and validation, sample tuple, all four connector
contracts/mocks, deterministic engine/results, PaymentService for existing Week 1
consumers, Week 2 generation adapter and knowledge service/runtime, existing views,
corpus, frozen gold/profile definitions and saved evaluation results. Do not call
the Week 1 dashboard's cached aggregate results to pretend agent-selected tools
were invoked. Keep Week 3 checkpoint state separate from Week 1/2 session keys.

## 9. Risks, blockers and explicit deferrals

- **Missing authoritative artifacts:** original PRD/handoff unavailable; this
  proposed scope needs owner review. Exact November 11 upload cutoff remains unknown.
- **Dependency:** LangGraph must be resolved and tested against current Python
  3.13/langchain-core/lock constraints. No version compatibility is assumed proven.
- **Provider:** existing Nebius model/configuration can be reused, but planner
  schema adherence, latency and model access need later owner-authorized rehearsal.
  Missing credentials must not break the two existing views.
- **Model decisions versus safety:** arbitrary actions are untrusted. Evidence
  completeness, engine precedence and approval boundaries remain code-enforced;
  a degraded fallback must not masquerade as agent success.
- **Synthetic data limits:** instructions have no real transaction lifecycle feed;
  wire selection does not prove release/settlement or support root-cause claims
  beyond the four mock controls. Repeated mock calls usually return unchanged data.
- **RAG cost/variability:** Week 2 Q08 variability and outstanding human review make
  guidance optional, separate and nonauthoritative for payment facts. Keep it off
  the critical path; do not use Week 2's 12-second target as a Week 3 guarantee.
- **Transient state:** in-memory review/resume works within a running session,
  not after restart; explicitly demonstrate and document this boundary.

Deferred: multiple agents, MCP, A2A, persistent memory/checkpoint storage,
cross-session investigation history, external APIs, payment execution/mutation,
real bank or legal policy claims, AWS/deployment, production authentication,
native provider function calling, streaming, autonomous remediation, free-form
task execution, broad root-cause diagnosis, LLM-written financial summaries,
new corpus/error-code fixtures, new Week 2 evaluation or retroactive score changes.

## Evidence references

- [Project state](../PROJECT_STATE.md), including owner-reported Week 2 demo.
- [Week 2 framework](WEEK2_FRAMEWORK.md) and
  [UI integration decisions](WEEK2_STREAMLIT.md): historical design/architecture,
  superseded where the final implementation differs.
- [Week 2 submission](WEEK2_GEN_ACADEMY_SUBMISSION.md) and
  [final evaluation](WEEK2_FINAL_EVALUATION.md): capability and quality boundaries.
- [PaymentService](../src/payment_ops/services/payment_service.py),
  [connector contracts](../src/payment_ops/connectors/base.py),
  [sample payments](../src/payment_ops/samples/payments.py), and
  [decision engine](../src/payment_ops/services/decision_engine.py).
- [Knowledge service](../src/payment_ops/knowledge/service.py),
  [generation adapter](../src/payment_ops/knowledge/generation.py),
  [UI entry point](../src/payment_ops/ui/app.py), and
  [dependency declarations](../pyproject.toml).

No application/dependency/branch changes, Nebius calls, evaluation changes,
commit or push were made for this PRD task.
