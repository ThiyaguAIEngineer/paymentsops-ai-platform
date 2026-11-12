# PaymentOps Intelligence Console: Streamlit guide

The existing application now has a third **Workspace** option,
**Payment Investigation Agent**. Wire Validation remains the default; Knowledge
Assistant keeps its existing interface and backend.

## Console presentation (Task 9C)

The shared shell is now branded **Payment Operations Intelligence Console** with a
clearly visible **SYNTHETIC DEMONSTRATION ENVIRONMENT** notice, three unchanged
workspace choices and read-only mock-integration boundaries. Native Streamlit theme
settings live in `.streamlit/config.toml`; repository-owned scoped CSS lives in
`src/payment_ops/ui/console.css`. Small `presentation.py` helpers provide page
headers, metric cards and native status/check rows. No frontend build system,
custom JavaScript, external font/CDN or new runtime dependency is introduced.

The light navy/slate/white palette uses readable labels with every status color:
green Passed, amber Needs review, red Rejected/blocked and gray Unavailable/Not
performed/Unknown. The theme sets typography and borders; CSS handles long-reference
wrapping, responsive KPI rows and visible keyboard focus. Selectors use application-
owned container keys and a few native component test IDs, not generated hash
classes. Those native selectors should be rechecked when Streamlit is upgraded.
All data/model/reviewer content remains in native text, code or HTML-disabled
Markdown. Only the trusted local stylesheet enters `st.html`.

Investigation layout now follows selection -> overview -> control findings ->
recommendation/review -> report -> optional guidance -> detailed activity/evidence.
Overview metrics show only stored facts: selected run amount, simulator finding,
investigation lifecycle, usable mandatory controls and gaps. Evidence progress is
not payment approval. The recommendation and dedicated review panel retain all
three actions, revision/session validation and check-budget explanations.
**Investigation report** states provisional versus a final recorded outcome.
**Operational Guidance** remains a separate opt-in panel.

Open **Agent activity and evidence** for the actual ordered AI-selected/fallback
cards, linked execution outcome/evidence/error, comparison tables, connector results
and recorded failures. Table detail may scroll within its native container. Unknown
or unavailable screening never becomes a passing badge. Wire Validation keeps its
same counts, filter and selected-payment behavior, with KPI cards, a filter panel,
control rows and an expandable comparison table. Knowledge Assistant keeps its
existing form/result/citation contracts, with consistent headings and clearer
supporting-source scope notes. Expanding sources never requests another answer.

Restart Streamlit after changing theme configuration. Launch from the repository
root with the existing command below. No new environment variables are required.

### Visual and owner acceptance

Task 9C used an ignored, explicitly labeled offline fixture entry point with real
UI/graph/mocks and scripted model/service doubles, blocking external HTTP. Headless
Chrome captured all eight states below at 1440, 1024 and 768 pixels: 24 viewport/state
checks detected no page-level horizontal overflow. Representative screenshots and
section details were visually inspected; a clipped environment badge and KPI labels
were corrected. Keyboard focus was inspected as a visible 3px outline. These are
offline layout checks, not a live Nebius rehearsal or a full accessibility audit.

| Owner check | Acceptance expectation |
| --- | --- |
| Wire Validation | Same KPIs/filter/selection; readable table and recorded control explanations |
| Knowledge answer with citations | Answer/refusal status distinct; expand source/version and original passage without another call |
| Investigation before start | Selected details and explicit Investigate Payment; no automatic model/tool activity |
| Completed investigation | Stored completed lifecycle distinct from simulator readiness; final recorded-outcome PDF label |
| Awaiting review | Recommendation/revision and three bounded review actions; provisional PDF label |
| Fraud-unavailable escalation | Gray unavailable control, explicit missing Fraud evidence and recorded connector failure |
| Supported operational guidance | Explicit request, bounded topic, status and verified passages separate from payment evidence |
| Insufficient guidance | Exact no-supported-procedure message; investigation/review/evidence unchanged |

Before recording, repeat these checks in the owner's browser at all three widths,
including sidebar open/closed at tablet width. Tab through native controls and
check focus, readable wrapped labels, no clipping/overlap, and table-local scrolling.
Exercise acceptance, one eligible recheck/second review, End and Escalate, guidance
and PDF download on the actual session; compare tool/planner counts before and
after non-investigation actions. No payment action is available. Live response
latency, browser differences, zoom/screen-reader use and formal accessibility
conformance remain unqualified. Below 768 pixels is outside the tested range.

After owner visual/live acceptance, refresh final submission screenshots, navigation
instructions, PDF/guidance architecture claims and test counts, and rehearse the
video timing. The finalized Gen Academy submission report and demo script remain
unchanged in Task 9C; no course submission is claimed.

## Launch and model configuration

Run from the repository root, with the locked environment installed:

```powershell
uv sync --locked
uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
```

Configure `NEBIUS_API_KEY` securely in the launching process before authenticated
rehearsal. Never place its value in source, the question/reviewer-note fields,
recorded terminal commands or screenshots. The existing `NEBIUS_GENERATION_MODEL`
can supply the planner model; `INVESTIGATION_GENERATION_MODEL` overrides it for
Week 3. The saved Week 2 generation model is
`Qwen/Qwen3-30B-A3B-Instruct-2507`; account access and live planner behavior still
need rehearsal. `NEBIUS_BASE_URL` remains the adapter's optional endpoint setting.
No embedding model or RAG initialization is needed for this view. Restart the app
after changing environment settings.

The UI calls `investigation/runtime.py` only on **Investigate Payment**. It creates
unique run/thread IDs, the existing four mock connectors and the real controller.
The graph lazily creates the existing Nebius JSON generation adapter with Week 3
settings (15-second call timeout, 400 output tokens). Production has no scripted
provider. Missing credentials/model access cause visible degraded planning and
bounded deterministic fallback; they do not establish autonomous success.

## Run and review

1. Select an existing synthetic wire. Selection and navigation perform no agent I/O.
2. Click **Investigate Payment**. A spinner covers execution through the real
   LangGraph review interrupt. Inspect overview, control findings and recommendation;
   open Agent activity and evidence for model/fallback sequence, normalized results,
   attempt/evidence IDs and recorded errors. Gaps and simulator findings remain distinct.
3. **Accept Investigation Recommendation** resumes the same thread. Missing
   evidence or degraded planning permits acknowledgment only and remains escalated.
4. To recheck, select an eligible connector, enter a short note and click
   **Request Further Investigation**. The controller validates the request and
   shared extra-attempt budget. One connector runs, the recommendation revision
   increases, and the graph pauses again. No planner loop restarts.
5. **End and Escalate** records the decision and ends without more tool calls.
6. To replace the trace, choose the desired payment, click **Start New
   Investigation**, then **Investigate Payment**. Arming a new run alone retains
   the current trace. Changing selection hides review controls for a different
   active payment; switching back makes its current review available again.

The demo payments are `SYNTHETIC-WIRE-001`, `SYNTHETIC-WIRE-LOW-BALANCE` and
`SYNTHETIC-WIRE-UNAVAILABLE`. Expected fixture behavior is documented in the
[MVP PRD](WEEK3_MVP_PRD.md). Every UI trace comes from actual graph state and mock
method calls. An engine finding such as REJECTED is a simulator observation;
investigation acceptance never executes, releases, rejects, settles or changes a payment.

## Optional operational guidance (Task 9B)

After starting an investigation, the matching retained payment has an **Operational
Guidance** section. Choose a bounded procedure topic, then explicitly click **Find
Operational Guidance**. Merely investigating, reviewing, navigating or rerendering
never calls RAG. Results and failures are retained for the active run/topic;
repeated requests reuse the saved result. Another topic needs its own explicit
request. A new run, lost controller or different payment selection clears displayed
guidance. No investigation-linked results use a global shared cache.

| Topic | Coverage and applicability boundary |
| --- | --- |
| General exception triage/case evidence | EX-TRIAGE and EX-EVIDENCE. Suggested for recorded REJECTED/REVIEW/UNAVAILABLE checks; general record requirements, not a control-specific remedy |
| General beneficiary correction/revalidation | BV-CORRECT. Manual educational lookup only; no beneficiary-name/format failure is inferred from Week 1 fields |
| General wire recall prerequisites | WR-SCOPE and WR-ELIGIBILITY. Manual only; no release evidence or recall eligibility is inferred |
| General status interpretation | SS-STATES. Manual only; engine readiness/rejection does not establish a lifecycle event or settlement |

There is no balance-remediation, fraud-treatment or sanctions-specific SOP in the
six-document corpus. Unsupported topics are refused without initializing RAG.
For missing applicable support the UI states: "No sufficiently supported operational
procedure was found in the available synthetic knowledge base." General educational
lookups remain clearly labeled and cannot substitute for missing control evidence.

`investigation/guidance.py` sends only fixed generic questions through the existing
`KnowledgeService.ask` public interface. It accepts no transaction snapshot in its
lookup function. `ui/investigation_guidance.py` gates the request, lazily reuses the
existing session-scoped KnowledgeService resource and stores results outside graph
state. Existing Week 2 citation/quote checks and rendering remain unchanged.
Answered and limited answers retain verified source passages and metadata;
clarification stays a clarification. Insufficient/unavailable/rejected results show
safe status/no-support messages. Malformed responses and provider/retrieval failures
never expose raw exceptions or change the investigation outcome.

Live guidance additionally requires the existing Week 2 configuration:
`NEBIUS_API_KEY`, `NEBIUS_GENERATION_MODEL` and `NEBIUS_EMBEDDING_MODEL`; optional
`NEBIUS_BASE_URL` is shared. `INVESTIGATION_GENERATION_MODEL` overrides only the
agent planner, not KnowledgeService. Configure secrets securely before launch,
restart after changes, and keep them out of recordings. No new dependency is added.
First guidance lookup can take longer while models and the local embedding/index
composition initialize; missing configuration produces safe unavailable guidance.

This optional on-screen result does not enter payment evidence, recommendations,
human review or the Task 9A PDF. Guidance does not execute payment or case actions.
Authenticated live guidance acceptance remains a separate owner rehearsal. After
acceptance, revise the final submission's optional-RAG/deferred claims, architecture,
privacy boundary, test count, limitations and video sequence; those finalized files
are deliberately unchanged during Task 9B.

## Session and safety boundaries

### Downloadable investigation case report (Task 9A)

For the retained investigation's matching payment, **Download Investigation
Report** exports a PDF containing actual snapshot facts: payment/run references,
lifecycle, simulator checks, current and historical evidence, model versus fallback
actions, recorded failures/gaps, recommendation revision and human-review events.
Completed, escalated and failed snapshots are supported; an awaiting-review report
is clearly **provisional**, not a final outcome. No unrecorded event timestamp or
approval is inferred. Synthetic-data/no-payment-authorization notices appear in the
report, and reviewer labels are explicitly unauthenticated.

The pure Python entry point is
`payment_ops.investigation.report.generate_investigation_report(snapshot) -> bytes`.
Snapshot validation/projection is separate from ReportLab rendering. It uses only
the detached controller snapshot, never calls the graph/model/connectors, never
recalculates payment rules and never mutates state. Matching inputs with the locked
dependencies produce identical bytes (no generation timestamp; invariant PDF
metadata). Paragraphs escape model/reviewer text, use bundled fonts, wrap long
references and paginate tables. Download data stays in memory; no report database
or server-side file export is introduced.

`st.download_button(..., on_click="ignore")` downloads prepared bytes without a
script rerun. Even an unsolicited rerun reads state without restarting/resuming the
graph. The button is hidden during busy work, unavailable/invalid snapshots and a
different payment selection. Preparation errors show a sanitized message; they
never alter the investigation outcome. Install the updated lockfile with
`uv sync --locked`; no additional credentials/configuration are needed.

The finalized Gen Academy report/demo remain the historical `90f67fe` baseline.
After enhancement acceptance, review submission sections 6-8, 14, 18-19 and the
video's screen sequence/test-count narration before claiming the enhancement in a
new course delivery. Task 9A does not rewrite those finalized claims.

One current controller/checkpointer is retained in browser session state, never
in a global resource cache. Ordinary reruns, expanding evidence and workspace
navigation do not execute tools. Non-widget payment-choice state survives navigation.
Start-event tokens and explicit new-run arming prevent start replay. Review widgets
are keyed by run-scoped review ID/revision; the controller remains authoritative
for stale IDs, duplicates, budgets and concurrency. A busy flag gates UI actions
while synchronous requests execute. Notes are literal data, not planner instructions.

Checkpoint/controller objects stay outside JSON-safe graph state. Lost sessions,
checkpoints or process restart require a new run; no database or restart recovery
is introduced. UI errors use sanitized messages. It displays only validated action
explanations, normalized evidence and safe error categories, not raw provider
responses, credentials or private model reasoning. Reviewer labels are not
authenticated identities.

Offline AppTest coverage uses injected scripted test providers with the actual
runtime/controller/graph and existing mocks. It covers the three demo scenarios,
review/resume, navigation, isolation, loss, duplicate/stale events and missing
configuration. Authenticated end-to-end rehearsal and live latency/model adherence
are not established by these tests. No Nebius calls were made during preparation.
