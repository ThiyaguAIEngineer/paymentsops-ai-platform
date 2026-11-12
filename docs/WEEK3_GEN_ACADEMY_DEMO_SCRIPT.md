# Gen Academy Week 3: final Payment Investigation Agent demo

**Target: 4:30; acceptable range 4:15-4:40. Final recording must be under 5:00.**
Prioritize one successful investigation and its enhanced features. Reserve about
40 seconds within the schedule for model latency, navigation and review. Do not
run Scenarios B and C again for the recording; discuss their recorded limitations.

## Preparation

- Launch from the repository root:

  ```powershell
  uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
  ```

- Configure credentials securely outside the capture. Planner uses
  `INVESTIGATION_GENERATION_MODEL` or fallback `NEBIUS_GENERATION_MODEL`;
  optional guidance also needs the existing Week 2 `NEBIUS_GENERATION_MODEL` and
  `NEBIUS_EMBEDDING_MODEL`. `NEBIUS_API_KEY` is required for live provider access;
  `NEBIUS_BASE_URL` is optional. Restart after environment/theme changes.
- Open the [submission report](WEEK3_GEN_ACADEMY_SUBMISSION.md) architecture diagram
  and limitations in a second tab. Keep credentials, terminals and unrelated tabs
  off-screen. Use readable browser zoom and silence notifications.
- Use one browser session throughout investigation and review. Precheck the generic
  guidance topic and PDF download destination. Do not refresh or restart while
  paused for review. A prior accepted run must be identified as **Previous recorded
  result** both on screen and in narration; it is never a newly executed live run.
- Rehearse with a timer. A new run requires actual provider execution; never imply
  that a scripted offline fixture is live. If using an edited recording, label
  removed waits as **Elapsed wait removed**, and preserve the actual run's outcome.

## Timed narration and navigation

Read the actual trace before describing counts, order or outcome. The successful
owner-accepted reference has five planning decisions and five tool attempts; a
fresh model run may differ. This is a speaking guide, not a promised execution.

| Time | Navigation/action | Concise narration |
| --- | --- | --- |
| 0:00-0:25 | Show console title, synthetic notice and three Workspaces. | ?Payment analysts gather account, limits, fraud and sanctions evidence across systems. Missing evidence must never look like a passing control. PaymentOps combines Week 1 deterministic validation, Week 2 knowledge retrieval and this Week 3 investigation agent, using synthetic data.? |
| 0:25-0:50 | Show report architecture diagram, then return to Payment Investigation Agent. | ?One LangGraph agent lets the model choose eligible read-only tools. Code validates the choice, binds the payment, executes mock connectors and records state. The existing rules engine determines findings. A genuine graph interrupt waits for human review.? |
| 0:50-1:25 | Select `SYNTHETIC-WIRE-001`; click **Investigate Payment** once. Keep spinner visible; this segment includes about 25 seconds of wait allowance. | ?I am starting this investigation. The planner uses Nebius; the banking connectors are mocks. Tool order is model-selected, while payment rules and safety limits stay deterministic.? Pause while execution finishes. |
| 1:25-2:00 | Show overview and control findings; expand **Agent activity and evidence**. Show action sources, attempts and one evidence reference. | ?This trace records what actually ran. In the accepted successful run, five model decisions were four connector choices and finish. Lookup plus those four connectors made five tool attempts. All four mandatory controls had evidence. Finish is a decision, not another tool dispatch.? Use this run's actual counts if newly executed. |
| 2:00-2:30 | Collapse detail; show recommendation/revision and review panel. Accept only a complete, nondegraded run awaiting review. Show **Completed and reviewed** and unchanged attempts. | ?READY FOR PROCESSING is a simulator finding. Acceptance reviews the investigation recommendation; it never authorizes a payment. Resume keeps the same thread and records the human decision without rerunning the connectors.? |
| 2:30-3:15 | In **Operational Guidance**, choose an available general topic and click **Find Operational Guidance** once. Show actual status, source/version and one supporting passage. Includes about 10 seconds of wait allowance. | ?This optional analyst request reuses the Week 2 KnowledgeService. Only a fixed generic question is sent, without payment data. The answer preserves source citations and passages. Source, version and quote checks are mechanical checks; semantic correctness still needs review. There is no balance, fraud or sanctions-specific remedy SOP.? |
| 3:15-3:40 | Click **Download Investigation Report**; open the downloaded PDF. Show lifecycle and accepted human-review history. | ?The PDF projects the stored snapshot: findings, evidence, action history and accepted review. Pending-review reports are provisional. Export makes no model or connector call and changes no investigation state. This final record does not authorize moving money.? |
| 3:40-4:05 | Show report development/test section. | ?Codex assisted incremental tool, graph, interrupt, PDF, guidance and UI development. The final offline regression has 878 passing tests with injected providers and real graph/mock execution. These are regression tests, not 878 live-model trials.? |
| 4:05-4:30 | Show report Scenarios B/C and limitations; finish on console or report title. | ?Earlier rehearsals recorded a planner timeout with visible bounded fallback, and unavailable Fraud evidence with escalation. Those limitations remain. This synthetic MVP has session-only memory, unauthenticated reviewer labels and no real bank access or payment execution. The next step is course submission.? |

## Latency and unexpected outcomes

The schedule totals 4:30 and includes roughly 35 seconds of provider waiting plus
brief navigation/review allowance. Speak naturally; do not fill waits with repeated
clicks. If execution or guidance exceeds the budget, stop and rerecord, or use a
clearly disclosed cut of the elapsed wait or a clearly labeled previous genuine
result. Do not accelerate into unreadable scrolling to meet the deadline.

If a fresh run degrades, show its actual source/error/status. Do not describe fallback
as autonomous success or accept incomplete evidence as successful completion.
A previously captured successful investigation can support this enhanced-feature
demo only when explicitly labeled as a previous result. Show a guidance failure
honestly; its safe message leaves the investigation unchanged. Do not alter code,
policies or configuration to manufacture a successful recording.

## Final delivery checks

- Inspect exported duration: target 4:15-4:40, strictly under five minutes.
- Confirm readable payment ID, action provenance, evidence, real review transition,
  displayed citations and final PDF accepted-review history. Verify disclosed cuts
  and prior-result labels, audible narration and no secrets in any frame.
- Upload and test reviewer access to the actual Week 3 video and any required shared
  report. The Week 2 video does not establish a Week 3 recording/upload.
- Submit by **November 11, 2026, 11:50 PM PST** and retain confirmation. Actual course
  submission remains pending until confirmed by the owner.
