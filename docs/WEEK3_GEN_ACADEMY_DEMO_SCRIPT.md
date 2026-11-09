# Gen Academy Week 3: Payment Investigation Agent demo

**Target:** 4:30 including navigation, scrolling and approximately 35 seconds of
visible execution/wait allowance. Hard maximum: five minutes. Rehearse with a timer;
model latency is variable and the target is not a runtime guarantee.

Use the actual Streamlit application and real Nebius planner for newly executed
actions. The banking connectors are synthetic mocks. The main demonstration covers
A and C; discuss B briefly using the owner's confirmed rehearsal observations.
Do not rerun all three just to fill the recording.

## Preparation and recording checklist

- From the repository root, install the locked environment if necessary with
  `uv sync --locked`. Launch in PowerShell:

  ```powershell
  uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
  ```

- Securely configure `NEBIUS_API_KEY` and either
  `INVESTIGATION_GENERATION_MODEL` (preferred override) or
  `NEBIUS_GENERATION_MODEL` (fallback) in the launching process. Optional
  `NEBIUS_BASE_URL` defaults to `https://api.tokenfactory.nebius.com/v1`.
  Model access and network connectivity are required. Restart after changes.
  No embedding configuration is needed for the agent workspace.
- Confirm all three Workspace choices render. Inspect the existing owner-run
  acceptance record in the [submission report](WEEK3_GEN_ACADEMY_SUBMISSION.md).
  Additional authenticated rehearsals are owner actions, not part of documentation preparation.
- Record browser content and microphone, with readable text and notifications off.
  Keep terminals, environment listings, `.env` files, credential settings, account
  consoles and unrelated tabs outside the capture. Never paste a key into the UI.
- Use one browser session for A, then explicitly start a new investigation for C.
  Do not refresh/restart between interrupt and review. Confirm payment ID before
  each review; keep the action table, history, finding and review buttons accessible.
- Budget time for scrolling and waiting. If latency threatens five minutes, stop
  and record again, or use clearly disclosed edited segments from actual runs.
  Label any wait cut as elapsed time removed; label any prior-run capture as a
  recorded run. Never narrate saved/static evidence as newly executed live calls.
- For timeout or unexpected output, show **Recorded failures** and the degraded
  banner honestly. Do not repeatedly click Investigate or call fallback autonomous
  success. End and Escalate when appropriate, then rerecord a concise explanation
  if needed. Do not change safety checks or credentials on camera.

## Timed narration and screen sequence

The wording below is a speaking guide, not a guarantee of identical model actions.
Read the actual trace before describing it. The historical A/C counts are expected
from owner rehearsal, not promised output for a fresh run.

| Time | Screen and action | Natural narration |
| --- | --- | --- |
| 0:00-0:25 | Show app title and Workspace choices, Wire Validation initially visible. | “This is PaymentOps, my synthetic payment operations platform. Analysts need to gather evidence across account, limits, fraud and sanctions checks without confusing missing evidence with a passing result. Week 1 supplied deterministic wire validation. Week 2 added a separate RAG Knowledge Assistant. Week 3 adds a stateful investigation agent.” |
| 0:25-0:55 | Show the workflow diagram in the submission report, then return to the app. | “One LangGraph agent asks the Nebius model which eligible read-only connector to call next. Code validates the JSON action, binds it to the selected payment, executes the mock tool and records the result. The existing decision engine evaluates findings. The graph then interrupts for human review. The model never controls payment execution.” |
| 0:55-1:15 | Select Payment Investigation Agent, `SYNTHETIC-WIRE-001`; click **Investigate Payment** once. Leave spinner visible. Allow about 10 seconds of quiet waiting. | “I’m starting the actual Nebius planner. The model chooses tools; those tools execute mock connectors, not real banking services.” |
| 1:15-1:50 | When ready, show lifecycle/counts, **Action sequence**, then **Tool execution history**. Expand one result only. | “Here is the recorded sequence and its source. For the successful rehearsal, there were five model decisions: four connector selections and finish. Lookup plus the four connectors made five tool attempts. Each observation has an evidence reference. I’m checking this run’s actual counts and sources rather than assuming the same order.” |
| 1:50-2:20 | Scroll to engine finding/recommendation and human review. Click **Accept Investigation Recommendation** only if complete, nondegraded and awaiting review. Show resulting lifecycle and counts. | “The expected simulator finding here is READY FOR PROCESSING. That is a finding, not authorization to move money. This pause is a genuine LangGraph interrupt. Acceptance resumes the same investigation thread and completes the reviewed investigation without repeating the connector calls. I verify that the attempt count stays unchanged.” |
| 2:20-2:40 | Select `SYNTHETIC-WIRE-UNAVAILABLE`, click **Start New Investigation**, then **Investigate Payment**. Allow about 10 seconds quiet waiting. | “This new investigation has its own identity and state. Its synthetic Fraud connector is deliberately unavailable.” |
| 2:40-3:15 | Show C action/history, Fraud failure, **Recorded failures**, missing evidence and MANUAL REVIEW finding. Scroll deliberately; no need to expand every result. | “The prior live rehearsal completed the other controls and recorded connector_unavailable for Fraud. Missing Fraud evidence stayed visible; it was never converted to PASS. The simulator finding was MANUAL REVIEW. I’m confirming those observations in this trace. A successful planner sequence can still produce an investigation that needs escalation because evidence is incomplete.” |
| 3:15-3:35 | Click **End and Escalate** at C review; show escalated lifecycle and unchanged tool count. Allow about five seconds for scrolling/resume. | “End and Escalate resumes the graph without another connector call. The prior run ended escalated: five attempts, one review. The payment remains unchanged.” |
| 3:35-3:55 | Show submission report Scenario B row, explicitly presented as prior rehearsal evidence. | “In the low-balance rehearsal, the second planning attempt recorded planner_timeout. Bounded fallback collected the remaining controls, and the deterministic finding correctly remained REJECTED. A human Core recheck retained state, increased attempts to six and revision to two, then reached a second review. That was degraded planning, not fully autonomous success; its final terminal outcome is unconfirmed.” |
| 3:55-4:15 | Show state/workflow sections or code filenames and current offline test result in the report. | “Codex helped me build this incrementally: read-only tools, bounded planning, real interrupt and resume, then Streamlit. The offline suite now has 824 passing tests, using injected test providers rather than live model calls. The key lesson is to separate model choice from deterministic rules, retain evidence and make degradation explicit.” |
| 4:15-4:30 | Return to app title or report limitations. | “This synthetic MVP has no payment execution, real bank access, authenticated reviewer or persistent memory. The timeout demonstrates why bounded failure handling and human review matter. These examples establish no reliability percentage.” |

## Timing and unexpected-result rules

The two start segments reserve roughly 20 seconds of waiting; scrolling/resume and
brief pauses bring total non-speaking allowance to about 35 seconds. Practice at a
natural pace, shorten wording if necessary and inspect the exported recording's
actual duration. If a fresh A or C run degrades, narrate its actual status and error
category, not the historical expected outcome. Do not accept a degraded run as a
completed autonomous investigation. A clearly labeled prior genuine run can be used
in a later edited recording, with its provenance stated.

## Final checks and submission

- Export near 4:30 and strictly under 5:00; inspect start/end, audible narration,
  readable evidence/counts, clean scrolling and any disclosed edits.
- Confirm the recording shows actual selected payment IDs, model/fallback sources,
  genuine review transitions and no credentials or private model reasoning.
- Upload to an accessible destination and test the reviewer link. Final Week 3
  recording/upload is not confirmed by the Week 2 4:58 video.
- Review/share any required Google Doc, finalize the authorized GitHub branch,
  verify course requirements and November 11 cutoff timezone, submit and retain
  confirmation. Do not mark the course submission complete before owner confirmation.
