# Week 2: PaymentOps Knowledge Assistant framework

Status: design targets only; no corpus, RAG implementation, or measured results yet.

## Official project definition

"My RAG app helps payment operations analysts answer payment procedure, exception-handling, troubleshooting, and error-code questions from six curated synthetic PaymentOps operational documents through a Streamlit Knowledge Assistant, targeting at least 90% answer faithfulness."

## 1. Use case and intended users

Payment operations analysts and support analysts need cited explanations of
procedures, exception triage, status interpretation, and synthetic error codes.
The assistant provides educational operational guidance. It cannot inspect live
transactions, execute payments, or change Week 1 validation decisions.

## 2. Knowledge corpus

Exactly six curated synthetic documents: Wire Recall SOP, ACH Returns Guide,
Payment Error-Code Catalog, Beneficiary Validation Runbook, Payment Exception
Handling SOP, and Settlement and Payment Status Guide. See
[the corpus design](WEEK2_CORPUS_DESIGN.md) for ownership and provisional evaluation.
Use fictional Northstar Demo Payments operations, synthetic identifiers, and
invented procedures explicitly labeled as educational. No invented rule is a
real bank policy, network rule, or regulatory requirement.

Only approved corpus files under `data/knowledge/documents/` will be indexed.
Planning documents, evaluation questions, expected answers, and tests are excluded.

## 3. Ingestion and cleaning approach

Begin with UTF-8 Markdown and structured metadata. Validate required metadata,
unique document/section IDs, cross-references, and synthetic-only content before
indexing. Normalize whitespace and line endings, remove redundant presentation
markup, and preserve headings, ordered steps, code spellings, tables, and negation.
Retain source text and content hashes for reproducibility. Reject malformed files
with explicit diagnostics; never silently drop procedure steps or table headers.

## 4. Document freshness and versioning

Use explicit semantic versions and ISO effective dates; the initial proposed
release is version `1.0.0`, effective `2026-10-28`, subject to corpus review.
Track review dates, supersession relationships, and content hashes in a corpus
manifest. Document ownership and section IDs remain stable across revisions.
Default retrieval includes only the approved effective version per document.
Archive prior versions outside the active index; historical questions require an
explicitly supported version scope or an insufficient-evidence response.
Rebuild affected index content when source, chunker, or embedding configuration
changes. Do not combine incompatible embedding versions in one index.

## 5. Chunking and embedding strategy

Start with section-aware chunks of approximately 400-600 tokens and 50-100 tokens
of overlap within a section. These are tuning hypotheses, not fixed requirements.
Keep an error-code entry and its meaning/action together; keep short procedures
whole where possible. Repeat necessary heading and table-header context.
Carry document/version/section metadata and deterministic chunk IDs into retrieval.
Embed titles, section headings, and content; preserve exact codes for BM25.
Choose an embedding model only after checking Python 3.13 compatibility, quality,
latency, cost, and provider data handling. No model is selected by this document.

## 6. Retrieval architecture and top-k strategy

Use a deterministic RAG pipeline with separately testable ingestion, retrieval,
and generation. Proposed backend: `src/payment_ops/knowledge/`, independent of
Streamlit and the Week 1 payment modules, using injected provider interfaces.
Python and uv remain the foundation. LangChain is preferred for useful adapters;
BM25 supplies lexical retrieval. Consider Pinecone only if hosted persistence is
justified; neither a vector database nor a provider is selected yet.

Initial experiment: retrieve top 10 vector hits and top 10 BM25 hits, fuse with
reciprocal rank fusion, deduplicate, then supply up to 5 chunks within a context
budget. Tune candidate and final k using Recall@k and multi-document coverage.
Filter effective versions before ranking. Detect exact synthetic codes without
discarding semantic retrieval; never substitute a similar code for an unknown one.
Empty hits and inadequate coverage trigger abstention. Ranking scores are not
calibrated confidence; evidence sufficiency also requires relevant, nonconflicting
support for the requested answer.

## 7. Grounded generation and citations

Consider Nebius or Fireworks after evaluating available models and operational
tradeoffs; no LLM provider/model is locked. Generate only from retrieved evidence.
Treat source content as data, never as instructions that override assistant rules.
Attach citations to substantive procedural claims using document title/ID,
version, section ID, and chunk ID, with a readable source excerpt in the UI.
Validate citation membership against retrieved chunks; evaluate whether cited text
actually supports each claim. Do not invent deadlines, code meanings, outcomes,
or live transaction facts. Separate cited guidance from clarification requests.

## 8. Insufficient-evidence behavior

Return an explicit status and concise explanation when the corpus cannot support
an answer. Ask for the missing rail, status, or exact code when clarification can
resolve ambiguity. Surface conflicting current evidence and abstain on the disputed
instruction; do not choose a convenient rule. Do not imply that recall guarantees
recovery or that accepted means settled. Provider/index failure produces a safe
unavailable response, tracked separately from evidence-based abstention.

## 9. Evaluation strategy

Maintain evaluation fixtures outside the indexed corpus. The preliminary matrix
in the corpus design is provisional until actual sections are authored and reviewed.
Then freeze source mappings, required answer facts, forbidden unsupported claims,
and expected answer/clarify/abstain labels. Reserve a held-out paraphrase set before
retrieval tuning; report results by category and sample size.

- Retrieval: Recall@5 against expected supporting sections, exact-code accuracy,
  and coverage of all required documents for multi-document questions.
- Faithfulness: human reviewers split substantive answers into verifiable factual
  claims. Score supported claims / all factual claims across answers to answerable
  questions; target at least 90%. Unsupported and contradicted claims both fail.
  Report per-question scores too. Empty answers/abstentions do not count as perfect
  faithfulness; report answer coverage and expected-fact completeness separately.
- Citations: measure valid references, claim support, and citation coverage.
- Abstention: separately measure correct abstentions on unanswerable cases,
  false abstentions on answerable cases, and clarification accuracy on ambiguous
  cases. Report confusion counts; no abstention target has been agreed yet.
- Version safety: superseded text must not override current instructions. Inject
  controlled conflict/version fixtures only in isolated evaluation indexes; do not
  contaminate the six active documents with deliberately false guidance.
- Reproducibility: record corpus/index hashes, chunking, retrieval settings,
  model/provider identifiers, prompt version, and run date. Use deterministic
  doubles for unit tests; keep optional live-provider evaluation separate.

## 10. Performance objectives

Targets, not achieved metrics:

- At least 90% answer faithfulness on answerable evaluation questions, using the
  claim-support definition above alongside answer coverage/completeness.
- P95 warm-query latency at most 12 seconds, measured from backend question
  submission through answer and citation validation, including query embedding,
  retrieval, and generation. Exclude ingestion, initial index loading, and UI
  rendering; report cold-start timing separately.
- Benchmark at least 100 uncached answer executions after warm-up, initially at
  concurrency one, with documented environment, prompt mix, token limits, sample
  count, percentile method, and error rate. Repeated questions must not use cached
  generated answers to inflate performance. Report provider failures separately.
- Evaluate abstention accuracy separately; select its target after corpus review.

## Architecture boundaries and open decisions

One repository and one Streamlit application will expose Wire Validation and
Knowledge Assistant through shared navigation and presentation. Week 1 backend
code, tests, and validation behavior remain frozen. Navigation is future work.
The knowledge backend must run and be testable without Streamlit for a standalone
course submission. No agents, LangGraph, API server, or payment execution is needed.

Open decisions: embedding and generation models/providers, local versus hosted
vector storage, LangChain adapter scope, final chunk/k settings, evidence gate,
abstention target, and benchmark environment. Resolve these through measured
experiments after corpus creation, not by adding dependencies during planning.
