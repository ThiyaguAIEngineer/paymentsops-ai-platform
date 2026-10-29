# Live generation failure investigation

Historical grounded-v2 investigation and contract below. A later saved live v2
run confirmed invalid_required_sections, overdeclared procedural dependencies,
and an ambiguous request answered. Current grounded-v3 behavior and strict schema
are documented in [WEEK2_GENERATION.md](WEEK2_GENERATION.md); the old optional-field
compatibility described below no longer applies. Live v3 verification is pending.

## Confirmed facts and unresolved causes

The project owner verified Qwen/Qwen3-30B-A3B-Instruct-2507 chat inference and
ran six scenarios. Factual and wire-recall questions answered, the unsupported
question abstained, and the ambiguous question requested clarification. The
SYN-BEN-301 and delayed-status scenarios returned invalid_response.

The original model payloads were not saved by the old CLI. This Codex process
does not have NEBIUS_API_KEY. Consequently the exact failing validation branch
for either original live response cannot be reconstructed from those statuses.
The regression payloads in tests are explicitly simulated categories, not captured
live responses. Neither problem is claimed solved until live diagnostics confirm it.

Confirmed implementation issues:

1. KnowledgeService caught parsing/schema/grounding exceptions and discarded their
   details, collapsing all of them into invalid_response. This prevented diagnosis.
2. Citation identity was (source ID, quote). Different valid quotes from one source
   section created multiple bibliography numbers, explaining the reported clutter.

No demonstrated reason exists to relax JSON, source-ID, or quote requirements.
Fenced JSON, invented text, fuzzy quote matches, and incorrect source assignments
remain rejected. There is no retry, response repair, citation remapping, or fallback
to a neighboring section.

## Evidence for the two scenarios

The saved complete-real-embeddings retrieval baseline contains:

| Scenario | Dense top-five sections in rank order | Evidence assessment |
| --- | --- | --- |
| SYN-BEN-301 / Q03 | EC-BENEFICIARY, BV-FORMAT, EC-LOOKUP, AR-CLASSIFY, BV-CHECKS | The catalog entry provides the code meaning and first action. BV-NAME is missing, but the narrow question's required evidence group is satisfied by the catalog. |
| Delayed status / Q07 | SS-DELAY, EC-STATUS, WR-ESCALATE, EX-ESCALATE, SS-ESCALATE | EX-DUPLICATE is missing. The three-group evidence coverage is 2/3. SS-DELAY links that procedure but does not supply all its investigation/review details. |

These are saved baseline results, not a rerun of the owner's six generation
requests. Retrieval ranks can vary with provider/model revisions. Gold labels were
used for this offline assessment only; the service never reads them or supplies
missing procedures from them.

For either invalid_response, the old code could have failed on JSON parsing,
duplicate fields, schema shape, status/statement consistency, generated citation
markers, absent evidence, unknown source IDs, or a quote not contained in its
referenced source. The response is needed to choose among these possibilities.
Provider transport/truncation errors follow provider_failure rather than the old
invalid_response branch, so they do not explain those statuses under the inspected
implementation. The new diagnostics distinguish these paths explicitly.

In particular, a table-entry paraphrase is not an exact quote. A real quote assigned
to the wrong source ID must also fail even when another retrieved source contains
it. Those cases are covered by simulated SYN-BEN-301 regression tests, not asserted
as the original live cause. The delayed-status evidence gap is established, but it
does not prove that the original invalid_response was an evidence-sufficiency error.

## Safe diagnostics

AnswerResult now carries immutable diagnostics. Each failure includes a stage and
category. Validation reports the first failed condition in deterministic order;
it does not silently erase that failure or expose rejected model text.

| Stage | Example categories |
| --- | --- |
| configuration | missing_credentials, missing_model, model_unavailable, invalid_endpoint |
| provider_communication | timeout, authentication_failed, http_error, transport_error, invalid_provider_json, truncated_response, malformed_chat_response |
| parsing | invalid_json, duplicate_json_field |
| schema_validation | invalid_response_fields, invalid_statement_fields, invalid_status_combination, invalid_citation_fields |
| grounding_validation | uncited_statement, unknown_source_id, empty_or_invalid_quote, quote_not_found, quote_in_different_source, unknown_required_reference |
| evidence_sufficiency | incomplete_retrieval_evidence, model_abstention, empty_retrieval |
| retrieval | retrieval_failure |

Where relevant, diagnostics include one-based statement/evidence indexes, an
already validated local source ID, quote character count and SHA-256 fingerprint,
other retrieved local source IDs containing the exact quote, missing referenced
section IDs, or an HTTP status integer. They never include raw exceptions, provider
bodies, unknown model-supplied IDs, quote text, headers, keys, or endpoint settings.
The retrieved-source manifest maps S1-S5 to exact chunk/document/section/version.
No raw model response logging has been added.

The CLI always displays failure stage/category. --diagnostics adds structured
details and the source manifest. --diagnostics-json writes only allowlisted
scenario status, reason, prompt version, method, diagnostics, and source metadata.
Use the already ignored results directory for this generated artifact.

## Exact passage validation and readable citations

Quote matching still normalizes whitespace only. A normalized character map now
locates the original exact substring in the referenced chunk; every supporting
EvidencePassage retains chunk ID, local source ID, original quote, and start/end
character offsets. No case, punctuation, table-cell, or semantic normalization is
performed. A quote found only in another source is diagnosed but not reassigned.

Bibliography numbers are now unique per document ID / section ID / version. Every
distinct supporting passage remains available under that number, including quotes
from different retrieved chunks of the same section. Inline citations still attach
to each statement; only the repeated source entries are consolidated. The legacy
Citation.chunk_id/evidence_quote fields identify the first passage; consumers must
use Citation.passages for the complete evidence record.

The grounded-v2 prompt asks for 2-4 coherent concise segments where practical,
without dropping critical steps, prerequisites, or warnings. There is no destructive
post-generation truncation, and the synthetic educational disclaimer is retained.

## Incomplete evidence versus invalid output

Context now explicitly lists referenced sections absent from retrieved text. This
is a generic inventory derived from the current chunks, not gold data or a command
to fetch extra evidence. Missing references are not a blanket abstention rule:
a complete catalog entry can answer a narrow question without a full runbook.

The prompt asks the model to name sections necessary for the requested scope in
required_sections. This additive field is accepted alongside the original three
fields for compatibility; malformed values or fabricated references fail validation.
Only references present in the context or its explicit links are allowed.
When a declared necessary reference is absent, the service returns
insufficient_evidence with reason incomplete_evidence and lists the absent section
in diagnostics. It never renders a partial answer as complete and does not fetch
or fill the missing content. A valid insufficient_evidence response is not malformed
generation. Invalid statement/quote structures remain invalid_response even when
the context also contains unresolved links.

Determining which sources are necessary is still a model judgment. A model that
fails to recognize a necessary omitted section could still return a well-formed but
incomplete answer. Citation membership and exact passage checks cannot establish
semantic entailment, procedural completeness, or reliable prompt-injection resistance.
These remain explicit live-evaluation limitations; no score threshold was introduced.

## Repeat the six scenarios from authenticated PowerShell

```powershell
uv run python -m payment_ops.knowledge.inspect_generation --model "Qwen/Qwen3-30B-A3B-Instruct-2507" --diagnostics --diagnostics-json "evaluation/week2/results/generation_diagnostics.json"
```

NEBIUS_API_KEY must already be available in that terminal. The CLI uses unchanged
Dense top-5 by default and reuses the existing embedding cache. It shows generated
answers, section-level citations, all validated evidence passages and offsets, and
safe validation diagnostics. The JSON file omits model text and credentials.
The runner exits nonzero if a scenario has invalid_response or provider/retrieval
failure; a genuine insufficient-evidence outcome is a valid inspection result.

Review the exact-code failure's stage/category and source/quote checks; confirm
whether the delayed-status case abstains for missing EX-DUPLICATE or produces a
different structural failure. Keep prompt versions with comparisons. A new run
cannot prove the exact cause of an unsaved earlier response, but it can diagnose
any recurring failure and verify current behavior. No successful rerun is claimed
by this offline investigation.
