# Week 3 Payment Investigation Agent: Streamlit integration

The existing application now has a third **Workspace** option,
**Payment Investigation Agent**. Wire Validation remains the default; Knowledge
Assistant keeps its existing interface and backend.

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
   LangGraph review interrupt. Inspect lifecycle, model/fallback action sequence,
   normalized tool results, attempt/evidence IDs, errors, gaps and simulator findings.
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
