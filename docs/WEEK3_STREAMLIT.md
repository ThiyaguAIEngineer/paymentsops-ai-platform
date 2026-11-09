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
