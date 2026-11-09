# Gen Academy Week 2: PaymentOps Knowledge Assistant Demo

**Recording target:** approximately 4 minutes 30 seconds; maximum 5 minutes.
**Prepared:** November 9, 2026.
**Branch inspected:** `feat/week2-knowledge-assistant`.

This is a presenter guide, not a transcript of a newly executed live run. Expected
behaviors come from the saved curated evaluation documented in the tracked
[final evaluation report](WEEK2_FINAL_EVALUATION.md) and the question-level appendix
in the [submission](WEEK2_GEN_ACADEMY_SUBMISSION.md#appendix-a---frozen-15-question-evaluation-evidence).
No Nebius calls or authenticated UI acceptance were performed during preparation.
Live wording, timing and dispositions can vary; narrate what actually appears.

## Timed narration and screen plan

Read the quoted narration naturally. Screen actions are directions, not spoken
text. The 270-second plan includes submission, provider waits and evidence scrolling;
it is not 270 seconds of continuous speech. Rehearse once with the recorder timer.

### 0:00-0:30 - Business problem and introduction

**Screen:** Streamlit application title, then sidebar **Workspace > Knowledge
Assistant**. Keep the synthetic-data disclaimer visible.

> This is the PaymentOps Knowledge Assistant, my Week 2 RAG project. Payment
> operations analysts often need several documents to answer one question about
> statuses, errors or exception handling. A generic answer can miss a prerequisite
> or review gate. This assistant retrieves evidence from six synthetic operational
> documents and presents guidance with inspectable sources. It cannot access live
> accounts or execute payments.

### 0:30-1:05 - RAG architecture

**Screen:** Submission Section 5 architecture in a rendered Markdown preview;
briefly show Section 4's six-document table, then return to the diagram.

> The pipeline validates Markdown documents, preserves their sections and tables
> during chunking, and embeds the text with a Qwen model through Nebius. Document
> vectors are cached locally, and a LangChain in-memory cosine index retrieves
> evidence. Dense top-five retrieval supplies the baseline, with bounded evidence
> expansion. A second Qwen model generates structured statements. The application
> checks source membership and exact quotations before displaying citations or a
> safe fallback. There is no hosted vector database or reranker.

### 1:05-1:25 - How Codex supported development

**Screen:** Repository tree at `src/payment_ops/knowledge/`, then submission
Section 8. Do not open environment files or terminal history.

> I used Codex to help implement separate ingestion, retrieval and generation
> components, write offline regression tests, and build diagnostics and evaluation
> tooling. I ran authenticated provider evaluations separately. Iterations addressed
> missing evidence, historical-policy scope and quote-copying failures. Codex's
> automated checks do not replace human answer-quality review.

### 1:25-1:55 - Q02: lifecycle distinction

**Screen:** Return to Streamlit. Paste Q02 into **Question**, click **Ask** once.
Show the status and answer, scroll to **Sources**, and expand one **Supporting
evidence [n]** panel. Use whichever citation number the live response supplies.

> First: does ACCEPTED mean a payment has settled? The saved run answered that
> acceptance is distinct from settlement, which requires matched confirmation and
> reconciliation evidence. Here I inspect the source section, version and exact
> supporting passage. This demonstrates a factual distinction with traceable evidence.

If the live result differs, replace the saved-result description with the actual
status and use the fallback guidance below; do not imply that expected text appeared.

### 1:55-2:25 - Q03: exact synthetic code

**Screen:** Replace the question with Q03; submit once. Show the exact identifier,
the answer, and its source metadata. Avoid reading the entire answer aloud.

> Next is SYN-BEN-301. In the saved run, it means a beneficiary-name mismatch;
> the initial action is to compare the submitted name with the verified beneficiary
> record and document the discrepancy. This demonstrates exact-code lookup and a
> narrow first-action question, rather than inventing a complete downstream workflow.

### 2:25-3:10 - Q08: correction plus common case evidence

**Screen:** Submit Q08. Scroll slowly through the correction guidance and the
rendered **Common case record requirements** table. Show the eight categories
and the warning below the table; briefly show multiple source documents.

> This question combines ACH correction with case evidence. The saved answer
> connected verified correction and revalidation with reconciliation, duplicate
> checks and supervisor review. It also included the common case-record table,
> covering identity, context, provenance, work, ownership and follow-up. The
> application renders that table from the actual retrieved SOP. These are required
> records, not populated transaction values. Having all the sources available still
> does not prove that every generated procedural claim is complete.

### 3:10-3:35 - Q13: unknown-code abstention

**Screen:** Submit Q13. Show **Insufficient evidence**, the preserved unknown code,
and any supported escalation citation. Do not expect an **Answered** badge.

> SYN-ACH-299 is not documented in this corpus. The saved run abstained on its
> meaning, preserved the exact identifier and supplied documented escalation
> guidance. It did not borrow a neighboring code's meaning. This path handles
> unknown codes deterministically; it does not require an LLM completion, although
> retrieval can still call the embedding provider.

### 3:35-4:05 - Retrieval comparison and evaluation

**Screen:** Tracked final evaluation report, Section 3 table, then Section 4
generation results and Section 8 latency. Use prepared bookmarks or search.
This is saved backend evaluation evidence, not a UI retrieval-mode switch.

> On ten answerable development questions, Dense recall was 85 percent, compared
> with 60 for BM25 and 66.7 for Hybrid. Evidence-group coverage also favored Dense,
> which is why it remained the baseline. Across the frozen fifteen-question profile,
> dispositions were correct in fifteen cases, with 27 valid structural citations
> and 47 exact passages. P50 latency was 4.592 seconds and P95 was 12.775 seconds.

### 4:05-4:30 - Learnings, limitations and close

**Screen:** Final evaluation Sections 5-6 and 10, or submission Sections 10-12;
finish on the repository link in submission Section 13.

> The main learning is that retrieval coverage, literal quotes and complete
> procedural guidance need separate evaluation. Human faithfulness, semantic
> citation correctness and completeness remain unmeasured; Q05, Q07 and Q20 have
> open completeness concerns. P95 exceeded the twelve-second target. This small,
> reused development set does not establish production readiness. Next steps are
> human review, a formal warm latency benchmark and recorded UI acceptance. Thank you.

## Question reference for rehearsal

Copy the wording exactly. These are existing evaluation questions, not new tests.
The observations below summarize the saved run; they are not promised live answers.

| ID and exact question | Demonstrates | Saved expected behavior |
| --- | --- | --- |
| Q02: Does ACCEPTED mean a payment has settled? | Lifecycle definitions and source-backed factual guidance | `answered`; acceptance is not settlement; matched settlement confirmation and reconciliation evidence are needed. |
| Q03: What does SYN-BEN-301 mean, and what should I do first? | Exact identifier matching and narrow first-action scope | `answered`; name mismatch; compare submitted name to the verified beneficiary record and document the discrepancy. |
| Q08: An ACH return cites invalid account details. What correction and case evidence are needed? | Multi-document procedure and common evidence checklist | `answered`; verified correction, retained revalidation evidence and review gates, plus the retrieved EX-EVIDENCE table/warning. Human procedural review remains pending. |
| Q13: What does SYN-ACH-299 mean? | Safe abstention on undocumented identifiers | `insufficient_evidence`; no invented meaning; exact identifier retained, with supported escalation guidance. |

The source run is locally recorded at
`evaluation/week2/results/answers_development/20261029T181352053697Z/results.json`.
Generated run artifacts are ignored by Git. Use the tracked report and submission
appendix for shareable evidence; do not add generated results to the repository.

## Recording checklist

### Before recording: environment and launch

- Confirm the repository root and branch using `git branch --show-current` and
  review `git status --short`. This preparation confirmed the Week 2 branch;
  it does not independently verify remote push status.
- Ensure Python 3.13, uv and the locked environment are available. Run
  `uv sync --locked` before the recording if setup is needed.
- Securely supply **NEBIUS_API_KEY** to the terminal that launches Streamlit,
  outside the recording. Required model variable names are
  **NEBIUS_EMBEDDING_MODEL** and **NEBIUS_GENERATION_MODEL**. Optional existing
  overrides are **NEBIUS_BASE_URL** and **KNOWLEDGE_GENERATION_PROVIDER**; retain
  the default Nebius provider unless deliberately configured otherwise.
- The startup command and model IDs below match README and the existing UI entry
  point. They were checked against repository evidence, not newly live-tested here:

```powershell
$env:NEBIUS_EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"
$env:NEBIUS_GENERATION_MODEL = "Qwen/Qwen3-30B-A3B-Instruct-2507"
uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
```

- Open the local URL printed by Streamlit. Select **Knowledge Assistant** from
  **Workspace**; the default view is **Wire Validation**. Restart Streamlit after
  environment-setting changes.
- In the owner's authenticated rehearsal, submit Q02 and confirm a response,
  sources and an expandable exact passage. Then rehearse Q03, Q08 and Q13; verify
  Q08's table/warning is readable and Q13's status is an abstention. These actions
  can invoke Nebius and were not performed as part of script preparation.
- First Ask initializes the service; later submissions reuse session resources and
  the document embedding cache. Answers are not cached as canned responses. Warm
  the service before recording, then explicitly resubmit the demonstration questions
  so the recorded answers correspond to actual submissions.

### Screen and capture sequence

1. Prepare rendered Markdown previews for the submission architecture and final
   evaluation tables, plus the repository tree. Prefer large readable text and
   hide editor side panels that crowd tables.
2. Capture only the app/docs window or a tightly selected screen area. Close email,
   notifications, unrelated tabs, secrets files and terminals containing credential
   setup. Never display environment-variable dumps, API headers or shell history.
3. Test microphone level and text readability with a short playback. Use 1080p
   capture where available; ensure the table and source excerpts remain legible.
4. Record in the timed order above: introduction, architecture, Codex, Q02, Q03,
   Q08, Q13, saved evaluation, limitations and repository link.
5. Paste one question at a time and click **Ask** only once. The UI retains the last
   submitted result; editing an unsubmitted draft does not produce a new answer.
   Keep **Response to:** visible when useful to establish which question was answered.

### Slow or unexpected responses

- Allow short waits while explaining the evidence checks. Initial resource setup,
  query embedding and a permitted quote retry can add time; Q13 is not guaranteed
  to be instant. The 45-second generation timeout is per call, not a whole-request
  latency guarantee, and one quote retry can cause another call.
- If a wait threatens the five-minute limit, pause the recording or trim dead time
  with a visible note such as **“Provider wait shortened”**. Do not claim an edited
  wait represents measured latency. Preserve the actual question/result pairing.
- If the UI returns **Response rejected**, **Knowledge service unavailable**,
  **Limited answer**, clarification or unexpected abstention, state the actual
  status. Do not read the expected saved behavior as though it appeared live.
- Pause to check configuration/connectivity off-screen. Avoid repeated clicking
  or weakening validation. If needed, switch to the submission appendix/final report
  and say: **“The live response did not complete as expected. This is the saved
  evaluated behavior, rather than a new live result.”** Re-record after fixing the
  environment if an uninterrupted live walkthrough is required by the course.
- Never replace a failed answer with fabricated UI text or present saved evidence
  as an authenticated live execution. Record unexpected behavior separately for
  later investigation; leave frozen results unchanged.

### Final playback and prerequisites still outstanding

- Aim for 4:30, allowing up to 30 seconds of contingency within a five-minute cap.
  Confirm the exported file duration, audible narration, readable tables/citations,
  visible question/status pairing and lack of credential or notification exposure.
- Confirm all four requested questions appear and that the recording distinguishes
  live outcomes from saved metrics. Do not claim 100% faithfulness from disposition
  accuracy or exact-quote checks; the 90% human faithfulness target is unmeasured.
- Before recording, the owner still needs working provider credentials/model access,
  network connectivity, an authenticated rehearsal, a recorder/microphone check,
  and confirmation of any course-specific upload/format requirements. Those course
  requirements are not available in the inspected repository.
- Human review/sign-off and the formal warm benchmark remain outstanding project
  acceptance work. An educational recording can describe those limits honestly;
  it does not itself resolve them or establish production readiness.

## Preparation evidence and scope

Reviewed: [project state](../PROJECT_STATE.md), [submission](WEEK2_GEN_ACADEMY_SUBMISSION.md),
[final evaluation](WEEK2_FINAL_EVALUATION.md), [README](../README.md),
`src/payment_ops/ui/app.py`, and `src/payment_ops/ui/knowledge_view.py`.
The README introduction and early project-state entries contain historical
pre-implementation wording; the implemented UI and latest evaluation checkpoint
establish the current Week 2 behavior.

The submission's clickable link to ignored local answer results was replaced with
the tracked final report; the local run path remains plain-text provenance.
Application code, corpus, gold labels and results are unchanged. Preparation made
no provider calls and did not commit or push documentation.
