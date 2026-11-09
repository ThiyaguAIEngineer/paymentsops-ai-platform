# PaymentOps Knowledge Assistant

**Mastering Agentic AI — Gen Academy Week 2 RAG Submission**
**Project:** PaymentOps AI Platform
**Branch:** `feat/week2-knowledge-assistant`
**Evidence checkpoint:** `9f9e04a` — Week 2 implementation and evaluations
**Submission documentation prepared:** November 2, 2026

## 1. Executive Summary

The PaymentOps Knowledge Assistant is a Retrieval-Augmented Generation (RAG)
application that answers payment procedure, exception-handling, troubleshooting,
and synthetic error-code questions from six curated operational documents. It
serves payment operations analysts, support analysts, reconciliation analysts, and
supervisors who need to locate guidance and inspect the evidence behind an answer.

The business problem is fragmented operational knowledge: related instructions can
span a status guide, an error catalog, and a procedure. Finding one relevant passage
does not necessarily establish every prerequisite or review gate. RAG was selected
to connect natural-language questions to a controlled, versioned corpus and make
the supporting sources visible, while allowing clarification or abstention when
the evidence is insufficient.

The implementation combines local retrieval, Nebius-hosted Qwen embeddings and
generation, strict response validation, and a Streamlit interface. The saved
15-question development evaluation achieved the expected disposition on 15/15
questions, with 27/27 structurally valid citations and 47/47 exact supporting
passages. These results demonstrate automated behavior and source checks;
human claim faithfulness and procedural completeness remain unmeasured. Formal
Week 2 sign-off is pending, and observed P95 latency exceeds the target.

## 2. Problem Statement and Use Case

Payment operations questions often require distinctions that generic answers can
blur: acceptance versus settlement, recall versus cancellation, name mismatch
versus account-format failure, or a delayed update versus a confirmed rejection.
Procedural guidance must also preserve stop conditions, evidence requirements,
ownership, and supervisor review.

Representative questions include:

- “What details are required to open a wire recall request?”
- “Does ACCEPTED mean a payment has settled?”
- “What does SYN-BEN-301 mean, and what should I do first?”
- “A status update is delayed and the analyst wants to resend. What checks and escalation apply?”
- “Which evidence is required to close a suspected duplicate case?”

A generic LLM has no reliable basis for knowing this project's fictional codes,
document versions, or local procedures. Fluent answers could invent deadlines,
assume transaction facts, or replace an undocumented identifier with a similar
code. The assistant instead retrieves approved demonstration text and requires
source-linked evidence for substantive generated statements.

This is a synthetic educational demonstration for fictional Northstar Demo
Payments. It provides guidance, not live transaction investigation or payment
execution. It cannot access accounts, release or settle payments, establish actual
bank policies or legal requirements, or change the Week 1 validation decisions.
Week 1 dashboard records are not automatically passed to the LLM.

## 3. RAG Framework

**Gen Academy RAG one-liner:** My RAG app helps payment operations analysts answer
payment procedure, exception-handling, troubleshooting, and error-code questions
from six curated synthetic PaymentOps operational documents through a Streamlit
Knowledge Assistant, targeting at least 90% human-reviewed answer faithfulness.

The 90% threshold is a target for supported substantive claims on answerable
questions. Human-reviewed faithfulness is currently unmeasured; the target has
not been demonstrated as achieved.

| Design area | Implemented decision |
| --- | --- |
| Users and questions | Operations/support users asking factual, procedural, exact-code, paraphrased, comparison, and multi-document questions; ambiguous and unsupported requests are handled explicitly. |
| Knowledge corpus | Six UTF-8 Markdown documents under `data/knowledge/documents/`; 31 sections and 32 chunks. Planning, evaluation labels, reports, and tests are outside ingestion. |
| Application interface | One Streamlit application with Wire Validation and Knowledge Assistant navigation; an independently testable Python knowledge backend and inspection/evaluation CLIs. |
| Ingestion and cleaning | Parse the corpus's flat front matter and explicit section format; validate metadata, IDs and cross-references. Normalize line endings and trailing whitespace while retaining meaningful Markdown, tables, ordered steps and negation. Malformed inputs fail explicitly. |
| Freshness | Active documents are version `1.0.0`, effective `2026-10-28`. Version/date provenance is retained; historical applicability is checked before generation. Unsupported historical requests abstain. There is no scheduled document refresh or implemented archive collection. |
| Chunking | `structural-v1`, section-aware, with a 450 approximate-token soft maximum measured as `ceil(characters/4)`. Preserve indivisible tables, lists, code blocks and paragraphs, even if oversized; repeat section headings for split chunks. No token overlap is added. |
| Embeddings | Nebius `Qwen/Qwen3-Embedding-8B`, 4096 dimensions in saved live runs; document vectors cached locally by provider/model/preprocessing identity and input content. Query vectors are not persisted. |
| Retrieval | Dense cosine top-5 is the generation baseline; BM25 and equal-weight RRF are implemented comparison alternatives. Bounded source-reference/requested-scope expansion can add evidence to the generation context. |
| Faithfulness target | At least 90% human-reviewed supported substantive claims on answerable questions, alongside separate coverage/completeness measures. Achievement remains unmeasured. |
| Latency target | Warm-query P95 at most 12 seconds, including query embedding through validation, excluding startup and UI rendering. The planned benchmark requires at least 100 uncached executions after warm-up at concurrency one; it remains outstanding. |

The framework document records earlier planning hypotheses, including overlap and
different candidate counts. The table above describes the actual implementation,
rather than treating those proposals as completed features.

## 4. Knowledge Corpus

| Synthetic document | ID | Purpose |
| --- | --- | --- |
| Wire Recall SOP | `SYN-WIRE-RECALL` | Released-wire recall prerequisites, request records, tracking, escalation, and uncertain recovery outcomes. |
| ACH Returns Guide | `SYN-ACH-RETURNS` | Fictional return classification, investigation, correction and review gates before retry preparation. |
| Payment Error-Code Catalog | `SYN-ERROR-CATALOG` | Canonical exact-code meanings, first actions, restrictions, ownership and links to governing procedures. |
| Beneficiary Validation Runbook | `SYN-BENEFICIARY` | Name mismatch, account-reference format failures, verified correction, revalidation and escalation. |
| Payment Exception Handling SOP | `SYN-EXCEPTION` | Common triage, case evidence, duplicate prevention, routing, escalation and closure requirements. |
| Settlement and Payment Status Guide | `SYN-STATUS` | Lifecycle definitions, confirmation evidence, delayed updates, returns and reconciliation. |

Synthetic data enables a reproducible course exercise without real customer
records, confidential bank procedures, or production-system access. It also allows
explicit ownership boundaries: the catalog owns code meanings, procedure documents
own detailed actions, the status guide owns lifecycle definitions, and the
exception SOP owns common case handling. Synthetic procedures and identifiers
must not be interpreted as real network standards or regulatory obligations.

Each chunk retains document title/ID, section, version, effective date, source path,
and deterministic chunk identity. Stable provenance supports inspection and
reproduction; it does not independently establish that a procedure is correct for
a real institution.

## 5. Technical Architecture

The main answer path is:

```text
Six synthetic Markdown documents
    -> Validated ingestion and conservative cleaning
    -> Structural section-aware chunks
    -> Nebius embeddings -> local document-vector cache
    -> LangChain in-memory cosine index

Submitted question
    -> Clarification / policy-period guards
    -> Query embedding and Dense top-5 retrieval
    -> Applicable-source filtering and bounded evidence expansion
    -> JSON context with source IDs, text and provenance
    -> Nebius LLM generation
    -> Schema, source, exact-quote and declared-dependency validation
    -> Cited answer / explicitly limited answer
       OR clarification / evidence abstention / safe unavailable response
```

BM25 and Hybrid RRF provide alternative retrieval paths in the comparison runner.
Some guards return before generation, including transaction-context clarification,
unsupported historical scope, and deterministic unknown-code handling. Thus every
submission does not necessarily produce an LLM completion.

The implementation uses Python 3.13, uv, Streamlit, `langchain-core`, NumPy,
`rank-bm25`, and `httpx`. `LocalVectorIndex` wraps LangChain's
`InMemoryVectorStore` for cosine ranking. The persistent local JSON cache stores
document embeddings; it is not a hosted vector database or a persisted search index.
Nebius adapters use injectable embedding/generation interfaces, and
`KnowledgeService.ask(question)` coordinates the answer workflow independently
of Streamlit. The saved generation model is
`Qwen/Qwen3-30B-A3B-Instruct-2507`, with temperature 0, a 1,800-output-token limit,
and a 45-second generation timeout per call.

The UI initializes the service on the first nonempty Ask submission and reuses
resources within the browser session. Sources expose document/section/version
metadata and expandable exact supporting passages. Credentials are read from the
launching process environment. No API key is entered into the question box or
included in this document.

Implementation evidence: `src/payment_ops/knowledge/ingestion.py`, `chunking.py`,
`embeddings.py`, `index.py`, `retrieval.py`, `runtime.py`, `generation.py`, and
`service.py`; presentation is in `src/payment_ops/ui/knowledge_view.py`.

## 6. Retrieval Strategy

**Dense retrieval.** The query is embedded with the configured embedding model and
ranked against local chunk vectors by cosine similarity. This supports semantic
matches when users paraphrase the documents. Stable chunk IDs break score ties;
the initial baseline returns five chunks.

**BM25 retrieval.** `BM25Okapi` uses `k1=1.5` and `b=0.75`. Tokenization retains
hyphenated identifiers such as `SYN-BEN-301` as whole tokens, supporting exact
lexical matches. Chunks with no query-term overlap are not returned merely to fill
the five slots.

**Hybrid RRF.** Dense and BM25 each contribute their top five candidates. Equal
weights combine ranks using `sum(1 / (60 + rank))`, deduplicated by chunk identity,
and return the top five fused hits. RRF combines rank positions rather than
assuming that cosine and BM25 scores have comparable scales. No reranker or cloud
vector database was implemented.

**Comparison method.** The retrieval runner uses the same corpus, chunks, frozen
questions and section-level gold definitions for each method. It reports Recall@5,
Precision@5, MRR@5, NDCG@5 and required evidence-group coverage. Only answerable
questions receive relevance scores; ambiguous/unsupported cases are observations.
Repeated sections still occupy chunk slots. Required evidence groups use AND
across groups and OR within allowed alternatives.

**Baseline selection.** Earlier original-set evaluation favored Dense, and the
final curated evaluation supports retaining it: Dense has higher recall, precision,
NDCG and evidence-group coverage than BM25 or Hybrid. Hybrid's slightly higher
MRR does not compensate for its lower evidence coverage for this application.
This is a dataset-specific decision, not a general claim that hybrid search is worse.

Generation context is broader than the initial five ranked chunks when bounded
expansion applies. Explicit-reference following adds at most one linked section,
up to two chunks, in one hop. Requested-scope inclusion uses exact metadata lookup
for a complete single-chunk, single-version section. Added sources retain distinct
provenance; they are not reranked semantic hits. Initial retrieval metrics and
final-context evidence availability are reported separately.

## 7. Prompt Engineering and Grounded Generation

The active prompt version is `grounded-v7-development` in
`src/payment_ops/knowledge/service.py`. It constrains generation to the supplied
synthetic evidence and prohibits invented policies, deadlines, transaction facts,
code meanings, or execution capabilities. Questions and source text are treated
as untrusted data. Retrieval scores are omitted from the prompt because they are
ranking signals, not calibrated answer confidence.

Representative verbatim excerpts from `SYSTEM_PROMPT` in
[`service.py`](../src/payment_ops/knowledge/service.py):

```text
First decide whether the requested answer is supported by the supplied text.
Use clarification when rail, status, code, or intent is materially ambiguous; ask
a concise question instead of guessing. Use insufficient_evidence when a code or
fact is undocumented, live data or legal/historical evidence is unavailable, current
sources conflict, or required procedure steps/evidence are missing.
```

```text
For answered or limited_answer: include nonempty statements; every statement must have supporting
evidence from the supplied source IDs with exact nonempty quotes. Include all
material steps for the requested scope, never infer missing steps. Do not insert
your own numbered citation markers; the application adds them.
```

The model returns a strict JSON object containing status, statements, a
clarification question, and `required_sections`. Each substantive statement must
reference supplied source IDs and exact supporting quotations. The application
validates the schema, source membership, declared dependencies, and literal quote
occurrence in the specified source. It records passage offsets and renders
numbered citations grouped by document/section/version while retaining supporting
passages. A quote from another source does not pass merely because it exists
somewhere in the context.

Safe behavior distinguishes four situations: request missing transaction context;
abstain when evidence is unsupported or essential guidance is missing; provide
explicitly bounded guidance when independently safe; or return unavailable when
configuration/provider/retrieval fails. Historical requests are checked against
effective-date/version metadata. Unknown codes retain their exact identifier and
do not inherit a neighboring code's meaning. Conflict abstention is instructed,
but dedicated conflicting-source fixtures remain deferred.

Important iterations addressed observed failures:

- Early diagnostics exposed schema/type failures, quote mismatches and missing
  linked evidence instead of hiding every failure behind a generic result.
- Grounded-v3 made `required_sections` mandatory and typed, distinguished essential
  scope from optional follow-up, and introduced explicit limited guidance.
- Grounded-v4 development added policy-period safety and refined clarification
  so general SOP questions were not blocked while underspecified retry actions
  requested context. Bounded evidence expansion addressed referenced-section gaps.
- Later scope and quotation refinements led to grounded-v7's explicit copying
  contract and common-case evidence rendering. When requested and retrieved, the
  application appends the actual EX-EVIDENCE table and warning with a citation,
  rather than relying on a generated summary to reproduce every common field.

Only an initial `quote_not_found` permits one fresh generation with unchanged
sources and full revalidation. Other failures do not receive this recovery. Quotes
are never silently repaired or assigned to a different source. In the final saved
run, Q05 used this bounded retry successfully.

These checks establish structural membership and literal quotation, not semantic
entailment. A model's `required_sections` declaration is not a completeness
certificate, and a valid short quote may still fail to support the entire claim.
See `docs/WEEK2_GENERATION_DIAGNOSTICS.md`,
`docs/WEEK2_ANSWER_DEVELOPMENT_COMPARISON.md`, and
`docs/WEEK2_FINAL_EVALUATION.md` for the recorded progression and limits.

## 8. Development Process and Iterations

Codex assisted with incremental implementation, offline tests, diagnostic tooling,
evaluation infrastructure, and evidence-based documentation. Project records
distinguish Codex's offline verification from owner-executed authenticated live
provider runs; automated assistance did not supply human quality judgments or sign-off.

Development progressed from framework/corpus design to validated ingestion and
structural chunking, then provider adapters, cached embeddings and retrieval
comparison. Grounded generation and diagnostics followed. Evaluation-driven scope,
historical-safety, evidence-expansion and quotation changes preceded integration
into the existing Streamlit application and the final curated evaluation report.

Recorded problems included excessive clarification on general questions,
unnecessary demands for downstream runbooks on narrow catalog questions, missing
cross-document evidence, historical misuse of current policy, malformed model
output, and quotations copied inaccurately or attributed to another source. A
service initialization bug also converted an internal `NameError` into a retrieval
failure; correcting the initialization restored regression tests without changing
the retrieval provider. These findings show why pipeline stages and diagnostics
must be inspected separately.

Engineering tradeoffs favored structural preservation over fixed-size splitting,
a small local index over hosted infrastructure, measured Dense performance over
assuming Hybrid superiority, and strict rejection over accepting plausible but
unverifiable text. Bounded expansion increases context coverage without unrestricted
link traversal; a single quote retry improves recovery while adding possible latency.
The Week 1 backend remained frozen and separate from the knowledge backend.

Git history records Week 1 completion at `04f29e2` and the consolidated Week 2
checkpoint at `9f9e04a`. Fine-grained iteration evidence comes from project state,
diagnostics and preserved evaluation artifacts, rather than an invented sequence
of separate commits.

## 9. Evaluation Methodology and Results

**Evaluation evidence:** See the [final evaluation report](WEEK2_FINAL_EVALUATION.md)
for verified metrics and known findings, and [Appendix A](#appendix-a---frozen-15-question-evaluation-evidence)
for all 15 question-level dispositions. The report contains selected question
findings rather than a complete question-by-question table.

The frozen profile `evaluation/week2/profiles/curated15_v1.json`, ID
`week2-curated15-v1`, selects unchanged records from the original 20-question gold
dataset. The selected IDs are Q01–Q05, Q07–Q13, Q15, Q19 and Q20: **10 answerable,
2 ambiguous and 3 unsupported** questions. Categories include factual lookup,
exact codes, semantic paraphrases, related concepts, multi-document procedures,
clarification, unknown codes, external legal requirements and historical scope.
Q06/Q14/Q16 are unselected; Q17/Q18 remain deferred fixture-dependent cases.

Evaluation annotations and expected dispositions are applied after inference;
they are never answer context for `KnowledgeService`. Runs retain model/prompt
configuration, corpus/profile hashes, sources, diagnostics and timings. The
retrieval and answer runners reuse the implemented pipeline; offline helpers
compute metrics and produce blank human-review exports.

**Initial retrieval — macro averages over 10 answerable questions:**

| Metric | Dense | BM25 | Hybrid RRF |
| --- | ---: | ---: | ---: |
| Recall@5 | 85.0% | 60.0% | 66.7% |
| Evidence-group coverage | 90.0% | 70.0% | 76.7% |
| Precision@5 | 30.0% | 22.0% | 22.0% |
| MRR@5 | 0.7083 | 0.5250 | 0.7200 |
| NDCG@5 | 0.6831 | 0.4962 | 0.6009 |
| All required groups satisfied | 8/10 | 6/10 | 7/10 |

Q07/Q08 are the only two multi-document questions. Final expanded generation
context contains all required groups for all ten answerable questions; evidence
availability does not prove that the answer delivered each required step.

**Generation and validation — 15-question saved live development run:**

| Measure | Result |
| --- | ---: |
| Questions executed | 15/15 |
| Correct response dispositions | 15/15 (100%) |
| Answerable questions with substantive responses | 10/10 |
| Ambiguous questions clarified | 2/2 |
| Unsupported questions abstained | 3/3 |
| Valid structural citations | 27/27 |
| Verified exact quotation passages | 47/47 |
| Final invalid / incomplete-evidence / unavailable responses | 0 / 0 / 0 |
| P50 service latency | 4.592 seconds |
| P95 service latency | 12.775 seconds |
| Startup/index initialization, measured separately | 1.221 seconds |

The citation/passage totals include supported escalation guidance in Q13's
unknown-code abstention. Zero final invalid responses does not erase Q05's initial
quote failure and recovery. Disposition accuracy measures whether the service
answered, clarified or abstained as expected; it does not measure whether every
generated claim or procedure is complete and faithful.

Official review exports contain 52 mechanical claim candidates and ten procedural
review rows, with no completed assessments. Human faithfulness, procedural
completeness, answer relevance, and semantic citation correctness remain unmeasured.
The faithfulness formula is supported substantive claims divided by all reviewed
substantive claims; partial/unsupported claims receive no full-support credit.
Review requires confirmed atomic segmentation and complete coverage, not a
favorable subset. Abstentions do not count as perfectly faithful answers.

Service latency includes query embeddings, retrieval, generation/recovery,
validation and fallbacks, excluding startup and UI rendering. P95 exceeds the
12-second target by 0.775 seconds. With 15 observations and nearest-rank
percentiles, P95 is the maximum observed time; this is not the required 100-query
warm benchmark. No causal performance breakdown was established.

Metric sources are the saved retrieval run
`evaluation/week2/results/retrieval/20261029T180407869874Z/` and answer run
`evaluation/week2/results/answers_development/20261029T181352053697Z/`.
The final evaluation report records offline recomputation matching saved metrics.
No live evaluation was rerun for this submission documentation.

## 10. Challenges and Limitations

- **Retrieval completeness:** Dense initially satisfies all required groups for
  8/10 answerable questions. Expansion improves available context but cannot
  guarantee semantic relevance or use of every essential procedure.
- **Q05, recall initiation:** The saved answer does not explicitly state recovery
  uncertainty, owner/next-checkpoint assignment, or the requester-verification reviewer.
- **Q07, delayed status/resend:** EX-DUPLICATE is retrieved, but the answer references
  it without explaining candidate comparison and the Payment Exceptions supervisor
  review gate. Its citations do not establish that those steps were delivered.
- **Q20, duplicate closure:** Final disposition with evidence references and
  conditional matched confirmation for claimed funds movement are not clearly
  stated. Reviewers must assess whether the reconciliation wording is sufficient.
- **Human review:** Those concerns are inspection findings awaiting adjudication,
  not completed official ratings. Claim faithfulness, procedural completeness,
  relevance and semantic citation correctness have not been formally measured.
- **Latency:** Observed P95 is above target; the formal warm benchmark is outstanding.
- **Development-set reuse:** These questions informed implementation and tuning.
  The 15 are not held out; comparison to the original 18-eligible baseline must
  acknowledge the changed denominator. Two multi-document, two ambiguous and three
  unsupported cases do not establish broad generalization or safety reliability.
- **Synthetic and operational boundaries:** No real banking integration,
  authentication, payment execution, production deployment readiness or actual
  regulatory compliance is demonstrated. Archived/conflicting-source fixtures and
  authenticated end-to-end UI acceptance remain outstanding.

## 11. Key Engineering Learnings

1. **Chunking preserves procedural meaning.** Keeping ordered steps, tables and
   stop conditions together is more useful than enforcing a hard token size.
   Character estimates must be labeled as estimates, and stable IDs enable traceability.
2. **Embeddings require reproducible configuration.** Model identity, dimensions,
   preprocessing and content belong in cache/validation decisions. Reusing document
   vectors reduces repeated ingestion work without implying cached answers.
3. **Dense versus sparse is an empirical choice.** Exact-code tokenization helps
   lexical retrieval, but this corpus's measured coverage favors Dense. Fusion
   cannot be assumed to improve every metric or evidence requirement.
4. **Grounding has multiple layers.** Source membership and literal quotes are
   necessary checks; semantic support and procedural completeness need separate
   review. A linked section is not evidence until its text is actually supplied.
5. **Safe refusal is part of the interface.** Clarification, unsupported evidence,
   limited guidance and service failure need distinct outcomes. Historical safety
   requires applicability checks, not just a valid citation to a current document.
6. **Retrieval and generation failures differ.** Missing context calls for retrieval
   investigation; omitted steps despite available context call for generation and
   completeness review; schema/quote failures require validation diagnostics.
7. **Evaluation should constrain claims.** Frozen definitions, preserved artifacts,
   explicit denominators and separate human review prevent disposition scores from
   being mistaken for full answer quality. Documentation must retain open findings
   even when automated metrics improve.

## 12. Future Improvements

- Complete human atomic-claim and procedural review on a separate review copy,
  including Q05/Q07/Q20 adjudication, relevance and semantic citation assessments.
- Address confirmed omissions in a separate implementation task while preserving
  the frozen evaluation evidence and strict validation rules.
- Add held-out paraphrases and isolated historical/conflict fixtures to test
  generalization and version safety without contaminating the active corpus.
- Run the documented 100-query warm benchmark and investigate measured latency
  before selecting performance changes or explicitly accepting the gap.
- Record authenticated UI acceptance and the owner's formal Week 2 sign-off.

These are proposed next steps, not implemented features. Week 3 agentic
capabilities are outside this submission.

## 13. GitHub Repository

[PaymentOps AI Platform — Week 2 Knowledge Assistant branch](https://github.com/ThiyaguAIEngineer/paymentsops-ai-platform/tree/feat/week2-knowledge-assistant)

Before launching authenticated functionality, securely configure `NEBIUS_API_KEY`
in the environment of the terminal that will launch Streamlit. Do not enter the
key in the question box or commit it to the repository. No key value is shown here.
Then launch the existing application with the verified model settings:

```powershell
uv sync --locked
$env:NEBIUS_EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"
$env:NEBIUS_GENERATION_MODEL = "Qwen/Qwen3-30B-A3B-Instruct-2507"
uv run streamlit run src/payment_ops/ui/app.py --browser.gatherUsageStats=false
```

Select **Knowledge Assistant** and submit a synthetic procedure question. The
repository's README contains inspection and evaluation commands; launching with
configured credentials can invoke the provider, whereas this documentation task
made no provider calls.

**Source provenance.** This submission is based on the repository implementation,
[`PROJECT_STATE.md`](../PROJECT_STATE.md), frozen evaluation definitions and saved
runs, and the [final evaluation report](WEEK2_FINAL_EVALUATION.md). The
[framework](WEEK2_FRAMEWORK.md) and [corpus design](WEEK2_CORPUS_DESIGN.md) provide
planning context; current behavior and results take precedence over earlier
proposals. Setup and interface details are documented in the
[README](../README.md) and [Streamlit integration guide](WEEK2_STREAMLIT.md).
The original PRD and separate handoff were unavailable and were not inspected.
The repository URL and pushed status are owner-supplied; local Git history was
reviewed. Human quality review and formal acceptance remain pending.

## Appendix A - Frozen 15-Question Evaluation Evidence

Source: the unchanged local answer run
`evaluation/week2/results/answers_development/20261029T181352053697Z/results.json`
for `week2-curated15-v1`, documented in the tracked
[final evaluation report](WEEK2_FINAL_EVALUATION.md). Generated run files are
ignored by Git and are not distributed through this link. Categories and observed
statuses below are copied from that run. Completeness observations come from the
[final evaluation report](WEEK2_FINAL_EVALUATION.md#6-q05-q07-and-q20-completeness-findings)
and await human adjudication. "No validation failure recorded" describes saved
diagnostics, not a completed human quality assessment. Clarification and abstention
rows are expected safe outcomes, not evaluation failures.

| Question ID | Category | Observed disposition | Relevant observations |
| --- | --- | --- | --- |
| Q01 | Simple factual | `answered` | No validation failure recorded; human quality review pending. |
| Q02 | Simple factual; related states | `answered` | No validation failure recorded; human quality review pending. |
| Q03 | Exact error-code lookup | `answered` | No validation failure recorded; human quality review pending. |
| Q04 | Exact code; action restriction | `answered` | No validation failure recorded; slowest observed service call (12.775 s), with no recovery diagnostic. |
| Q05 | Semantic/paraphrased | `answered` | Initial `quote_not_found`; one fresh retry passed (`quote_retry_validated`). Recovery uncertainty, owner/checkpoint assignment and verification-reviewer completeness concerns remain. |
| Q07 | Multi-document | `answered` | No validation failure recorded. Retrieved EX-DUPLICATE is referenced without explaining candidate comparison and the Payment Exceptions supervisor-review gate. |
| Q08 | Multi-document | `answered` | No validation failure recorded. Exact EX-EVIDENCE table/warning included; remaining procedural claims still require review. |
| Q09 | Ambiguous | `clarification` | `missing_transaction_context`; clarification guard detected missing rail/status. |
| Q10 | Ambiguous | `clarification` | `missing_transaction_context`; clarification guard detected missing rail/status. |
| Q11 | Closely related procedures | `answered` | No validation failure recorded; human quality review pending. |
| Q12 | Closely related codes | `answered` | No validation failure recorded; human quality review pending. |
| Q13 | Deliberately unanswerable; unknown code | `insufficient_evidence` | `undocumented_identifier`; abstained on unknown SYN-ACH-299 and retained supported escalation guidance. |
| Q15 | Deliberately unanswerable; external policy | `insufficient_evidence` | `model_abstention`; synthetic evidence cannot establish universal legal requirements. |
| Q19 | Unanswerable historical scope | `insufficient_evidence` | `policy_period_unsupported` / `no_applicable_version`; current evidence was not substituted for 2024 policy. |
| Q20 | Simple factual | `answered` | No validation failure recorded. Final disposition/evidence references and conditional matched confirmation for claimed funds movement are not clearly stated. |
