# Week 2 grounded answer-generation backend

## Status and model selection

Implemented backend and offline contract tests. The latest saved grounded-v2 live
diagnostics show factual required_sections validation failure, exact-code/recall
abstention due to declared missing sections, delayed-status answered, unsupported
abstained, and ambiguous incorrectly answered. The model's raw values/answer text
were not retained by those diagnostics. grounded-v3 corrects contract and scope
weaknesses below, but Codex lacks NEBIUS_API_KEY and has not confirmed a live v3
rerun. No fake response is a real model result.

Initial provider: Nebius. Owner-verified generation model:
`Qwen/Qwen3-30B-A3B-Instruct-2507`. Nebius's official
[Qwen catalog](https://nebius.com/services/token-factory/models/qwen-models-inference)
lists this model for text inference; its
[API reference](https://api.tokenfactory.nebius.com/docs) documents chat completions.
Catalog listing is not proof of account access or this application's JSON-response
compatibility. The adapter checks the configured exact model against `/models`,
then verifies a nonempty completed assistant response from `/chat/completions`.
Grounded JSON/schema validation occurs separately. API compatibility is established
by the owner's run; correctness across scenarios is not. See
[the failure investigation](WEEK2_GENERATION_DIAGNOSTICS.md).

Generation model is explicit via `--model` or NEBIUS_GENERATION_MODEL. Provider
selection uses KNOWLEDGE_GENERATION_PROVIDER (initially `nebius` only); other
implementations can be injected through the vendor-neutral GenerationProvider
Protocol without changing KnowledgeService. No fake provider ships in runtime code.
NEBIUS_API_KEY comes only from the environment. Optional NEBIUS_BASE_URL defaults
to `https://api.tokenfactory.nebius.com/v1`. Keys and headers are never printed,
serialized, or included in errors. Timeouts and transport errors are sanitized.

## Architecture and measured retrieval decision

```text
Question -> KnowledgeService -> selected existing retriever (top 5)
         -> JSON context with text + source metadata
         -> GenerationProvider -> structured grounded response
         -> schema, source-ID and quote checks -> AnswerResult + citations
```

Dense is the initial default. The saved real-embedding baseline in
`evaluation/week2/results/latest.json` reports, over 12 answerable questions:

| Method | Recall@5 | Complete evidence rate |
| --- | --- | --- |
| Dense | 83.3% | 75.0% |
| BM25 | 62.5% | 58.3% |
| Hybrid | 68.1% | 66.7% |

See [the full evaluation](WEEK2_RETRIEVAL_EVALUATION.md). Dense's two-question
multi-document evidence-group coverage is 50%, versus Hybrid's 33.3%. Dense
misses required correction evidence on Q06, duplicate investigation on Q07,
and correction/common case evidence on Q08. These gaps are reasons to test
abstention, not permission to invent omitted procedure steps.

BM25 and Hybrid remain selectable alternatives. Existing retrievers, ingestion,
chunking, and source documents are reused unchanged. Scores are omitted from the
generation prompt; no confidence threshold or reranker is introduced. Normal
queries do not import or read the golden dataset or expected-source labels.

## Prompt and response contract

Prompt version: `grounded-v3`. The system prompt identifies the assistant as
educational, prohibits external policy invention and payment execution, and
requires sufficient evidence for the complete requested scope. It explicitly
instructs the model to preserve prerequisites, review gates, ordered steps,
stop conditions, and uncertainty. A cross-reference does not supply the referenced
section's contents. Conflicting current guidance requires abstention.

The user message is a JSON data object containing question and retrieved sources.
Every source includes a local ID (S1-S5), title, document ID, section ID, version,
effective date, chunk ID, source path, and text. Source IDs refer only to this
request. Retrieved instructions and user requests to override the system are
untrusted data. No tools or executable workflows are available to the model.
JSON encoding and instruction priority reduce delimiter confusion; they are not
a proof of resistance to prompt injection.

Each source also supplies its complete `section_reference` string, for example
`SYN-STATUS/SS-STATES`. `required_sections` is mandatory, always an array of these
complete strings or explicit linked references. [] is valid for a direct factual
answer without further procedural dependencies. Missing fields, null, a scalar,
objects, bare section IDs, and source IDs such as S1 are rejected, never repaired.
Safe diagnostics identify the field, JSON type, and invalid element index without
printing the model's value. The v2 error established an invalid value, but its exact
shape was not retained, so no particular shape is claimed as its confirmed cause.

Required sections mean essential evidence for the specific requested scope, not
all related reading or every linked lifecycle stage. A getting-started answer does
not automatically need closure/tracking evidence. Necessary missing evidence still
causes incomplete_evidence; the model's list is not independently verified proof
that an answer is complete.

The provider must return exactly:

```json
{
  "status": "answered",
  "statements": [
    {
      "text": "A supported claim or coherent procedure segment",
      "evidence": [{"source_id": "S1", "quote": "verbatim supporting excerpt"}]
    }
  ],
  "clarification_question": null,
  "required_sections": []
}
```

This is a schema example, not a live generated answer. Each substantive answered
statement must include evidence. Unknown source IDs, invented quotes, uncited
statements, duplicate JSON fields, malformed output, and incomplete responses are
rejected. Quote comparison normalizes whitespace only. Token truncation or a tool
request is not accepted as a completed chat response. Initial generation settings
are temperature 0, maximum 1800 output tokens, nonstreaming, JSON-object response
format, and a 45-second request timeout; these do not establish latency targets.

`limited_answer` is also valid with the same mandatory fields and strict per-claim
evidence. It is explicitly labeled as limited guidance rather than a complete
end-to-end procedure; the model must state the boundary in its cited answer.
It cannot silently omit a critical requested step. If an essential part of the
requested scope is missing, the response must abstain rather than relabel itself
as limited. Related references are not automatically mandatory dependencies.

## Citations and result types

The application appends numbered citations to each validated statement, with one
bibliography number per document/section/version. A citation
contains document title, document ID, section ID, version, exact chunk ID, source
path, and all supporting passages with exact retrieved-chunk offsets. Display format:

```text
[1] Document title | DOCUMENT-ID/SECTION-ID | v1.0.0
    Chunk: exact retrieved chunk ID
    Evidence: quoted retrieved excerpt
```

Citation metadata comes from the retrieved KnowledgeChunk, not model-supplied
metadata. A valid citation and quote prove membership/extraction only: the claim
may still misinterpret the quote or omit a prerequisite. Independent faithfulness,
completeness, and safety evaluation remains required before claiming the 90% goal.

AnswerResult is immutable and includes status, readable answer, immutable citation
tuple, retrieval method, retrieved chunk IDs, reason code, and prompt version.
Every result, including clarification and errors, starts with:
“Synthetic educational material — not an actual bank policy.”

## Abstention and clarification

- Empty questions produce a clarification request without retrieval or generation.
- Empty retrieval produces insufficient_evidence without a generation call.
- For ambiguous rail/status/intent, the prompted model must return clarification
  with an explicit question and no procedural answer statements.
- A small action-intent guard asks for rail/current confirmed status before
  retrieval when a request to reverse, undo, cancel, recall, recover, return,
  stop, retry, or resend a particular payment lacks that context. It handles
  varied phrasing, not a fixed question string. Definitions/comparisons bypass
  the guard; provided rail/status permits normal retrieval. This conservative
  lexical guard has false-positive/negative limitations; remaining ambiguity is
  still model-assessed and no procedure is selected by the guard.
- For unsupported codes, live account questions, legal/historical facts absent
  from context, conflicts, or incomplete procedures, the model must return
  insufficient_evidence with no answer statements. The application uses a fixed
  abstention message rather than displaying an unsupported partial answer.
- Malformed output or invalid citations produce a safe insufficient_evidence
  result with reason `invalid_response`; rejected model text is not displayed.
- Declared necessary sections missing from retrieved context produce reason
  `incomplete_evidence`, separate from parsing/schema/citation failures. Context
  inventories absent linked sections, without supplying their contents or gold labels.
- Provider and retrieval failures produce unavailable, not an assertion that
  the corpus contains no answer. Raw exception details are not returned.

Apart from the clarification guard, empty question/retrieval and structural validation,
evidence-sufficiency and remaining ambiguity decisions are model judgments. Offline tests exercise
the contracts using explicit fake responses; they do not establish that the real
model reliably makes those judgments. No gold-dependent routing or arbitrary
similarity threshold is used.

## Live inspection from authenticated PowerShell

From the repository root, with NEBIUS_API_KEY available in that terminal:

```powershell
uv run python -m payment_ops.knowledge.inspect_generation --model "Qwen/Qwen3-30B-A3B-Instruct-2507" --diagnostics --diagnostics-json "evaluation/week2/results/generation_diagnostics_v3.json"
```

This tests the verified model with the revised prompt/validator. The utility
checks account visibility, reuses real Qwen/Qwen3-Embedding-8B document vectors
from the existing cache, and generates answers for six questions: factual,
exact-code, paraphrase, multi-document, unsupported, and ambiguous. It displays
answer status, retrieval method, citations, chunk IDs, and supporting quotes.
Allowlisted stage/category diagnostics distinguish parse, schema, grounding,
evidence-sufficiency, and provider failures. No raw model output is persisted;
the optional diagnostics JSON contains statuses and source manifests only.
No fake fallback exists. Missing
credentials/access, transport incompatibility, malformed output, and invalid
citations produce a nonzero exit code. Review statuses as well as wording.

Use `--method bm25` or `--method hybrid` for the existing alternatives. BM25 mode
does not require embeddings. `--embedding-model` is configurable; keep the
verified model for baseline comparisons. To configure the model without a CLI
argument, set NEBIUS_GENERATION_MODEL in the terminal and omit `--model`.
Do not paste keys into chat or command arguments. A separately started terminal
may have credentials unavailable to the Codex process.

## Remaining verification

Repeat live inspection with diagnostics to investigate recurring failures, then assess actual
claim faithfulness, complete-procedure coverage, clarification, abstention, and
prompt-injection behavior independently. Preserve the frozen retrieval baseline;
do not present golden-dataset tuning as held-out validation. Q17/Q18 archived and
conflicting fixtures remain deferred. No Streamlit integration, payment execution,
agents, hosted vector database, or reranking is implemented.
