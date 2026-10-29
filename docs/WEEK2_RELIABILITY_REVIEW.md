# Week 2 reliability review

The latest completed run is
`evaluation/week2/results/answers_development/20261029T002845632511Z`:
18/18 eligible questions, grounded-v4-development, Dense top-5 plus the existing
bounded one-hop reference follow-up. Its report, results, sources and review sheets
remain unchanged, as do Baseline V1 and the gold dataset. Preservation hashes are
in `evaluation/week2/reliability_artifacts_manifest.json`.

This review uses existing live outputs and offline tests. No live calls were made:
NEBIUS_API_KEY is unavailable. The grounded-v5-development prompt is a candidate,
not a live-verified improvement. These questions are a development set, not
independent validation. Human faithfulness and procedural completeness remain
unmeasured.

## Historical abstention scoring

Q19 correctly abstained with `insufficient_evidence/policy_period_unsupported`.
The evaluator's allowlist omitted that evidence-decision reason. It now accepts
that reason only with insufficient_evidence for an unsupported question. Invalid
responses, retrieval/provider/application failures, unknown reasons, and an
answered response with the same reason do not receive abstention credit.

Offline rescoring of the saved outputs changes only Q19: 14/18 correct dispositions
(77.8%) becomes 15/18 (83.3%). This is an evaluator correction, not improved model
inference or a faithfulness measurement. Reproducible derived data, including the
source results hash and corrected summary, is saved separately in
`evaluation/week2/reliability_review.json`; original row flags/summaries stay intact.

The model-path latency filter also now excludes temporal-gate abstentions and
policy-period clarifications, which do not invoke generation. Overall latency still
includes them; no slow requests are removed from the overall P95.

## Quote failures

| Question | Rejected evidence | Diagnostic |
|---|---|---|
| Q03 | Statement 2, evidence 1, S1 EC-BENEFICIARY, 72 characters | quote_not_found |
| Q04 | Statement 2, evidence 3, S4 AR-NEXT, 199 characters | quote_not_found |
| Q07 | Statement 1, evidence 1, S1 SS-DELAY, 255 characters | quote_not_found |

All three had full gold evidence-group coverage in the retrieved context. The
validator found none of the rejected quotations in their specified sources after
whitespace-only normalization; matching_source_ids was also empty. The diagnostics
retain hashes, lengths and locations, not rejected model payloads. Exact causes
such as removed Markdown, changed punctuation, combined list steps or paraphrasing
cannot be determined from those hashes. These are plausible failure mechanisms,
not reconstructed facts about the rejected text.

The existing contract supplied raw Markdown in JSON text fields and requested
verbatim quotations. Catalog tables and ordered, wrapped procedural steps create
opportunities for a model to rewrite formatting while composing an explanation.
The v5 prompt explicitly separates explanatory statement text from copy-only
quotations: copy a sufficient contiguous substring from the cited source's decoded
text, preserve Markdown/punctuation/case, use separate evidence items for
nonadjacent excerpts, and never synthesize a quote by joining cells/steps or adding
ellipses. Short excerpts must still substantively support their associated claims.

The quote validator, source membership, source offsets and citation grouping are
unchanged. There is no repair, source substitution, second model or retry pipeline.
Offline tests accept exact table/list excerpts and reject simulated rewritten,
joined, missing and wrong-source quotations. These tests establish validation
behavior, not live quotation reliability or semantic entailment.

## Q08 completeness

Q08 asks for both correction evidence and case evidence. Its answer gives the
invalid-field correction and selected BV-CORRECT evidence/reviewer details. It
does not supply the common case record, state that this portion is missing, or
label its guidance limited. It also does not enumerate all correction/revalidation
records present in BV-CORRECT. Structural citation success and an answered status
do not establish completeness.

Retrieved AR-NEXT and BV-CORRECT support correction/revalidation and review gates.
The unretrieved EX-EVIDENCE section supplies the distinct common checklist:
identity, instruction context, observed condition, evidence provenance, request
context, work performed, ownership and follow-up. This list is a corpus inspection
finding, not evidence added to normal inference. Gold labels remain evaluation-only.

The prompt now requires checking each requested scope separately. Independently
safe correction guidance may be a limited_answer only if it explicitly names the
unavailable common case-record requirements and does not imply completeness or
permission to retry. If missing evidence is a prerequisite to the guidance itself,
abstain. No additional retrieval expansion or top-k increase was made. The model's
scope declaration remains unverified semantically and needs human review.

## Latency investigation

| Observation | Baseline V1 | Latest development run |
|---|---:|---:|
| Questions | 18 | 18 |
| Overall P50, seconds | 1.478 | 5.930 |
| Overall P95, seconds | 4.296 | 17.510 |
| Median retrieved source text, characters | 5,619 | 6,697 |
| Mean retrieved source text, characters | 5,616.8 | 6,809.7 |

With nearest-rank P95 and only 18 samples, P95 is the maximum: Q07 in V1 and Q20
in the latest run. Q20 rose from 2.351 to 17.510 seconds; Q04 rose from 2.445 to
5.867, and Q07 from 4.296 to 12.178. This is a small sequential sample, not a stable
warm-query performance benchmark. The latest run exceeds the 12-second target.

Implementation evidence and likely contributors:

- Reference follow-up is local: one explicit section, no new embedding/generation
  request. All latest nonempty contexts contain six chunks versus five seeds in
  V1. Mean source text is about 21% larger, which can add provider input-processing
  and generation overhead. Prompt/output differences also confound comparison;
  token usage and decoding durations were not retained.
- An offline 1,000-iteration probe of metadata filtering plus the existing one-hop
  resolver on Q08's saved seeds/32-chunk corpus averaged about 0.135 milliseconds
  per iteration on this machine. This narrow local probe excludes embedding,
  cosine search, context serialization, quote validation and generation; it is not
  a live latency measurement. It does not explain a multi-second increase by itself.
- Query embeddings are not cached: each Dense query calls the embedding provider.
  Q19 took 7.742 seconds despite the temporal gate preventing generation, showing
  that generation is not the only possible contributor. Its retrieval includes a
  live query embedding before metadata filtering. This does not isolate network
  time from provider embedding time or local retrieval.
- Q01/Q08 now invoke retrieval/generation instead of fast guard clarifications;
  this changes the latency population. Q10 now takes a fast clarification path.
- Provider/network/load variation, larger context and different generated output
  lengths are plausible contributors. Only total service-call durations were
  recorded, so their relative contributions cannot be established. No causal
  percentage or provider fault is asserted. There are no new resolver API calls,
  automated repairs or generation retries to explain the difference.

No speculative performance infrastructure or retrieval tuning was introduced.
Preserve end-to-end timings and reassess on the next authenticated run; investigate
stage timings only if the limitation persists. The prompt-only changes do not
establish that latency will improve.

## Verification and next steps

Offline coverage includes the historical disposition allowlist, rejection of
application errors, exact and malformed quotations, wrong-source membership,
bounded case-evidence presentation, temporal model-path accounting and artifact
preservation. See PROJECT_STATE.md for final test counts.

Run from an authenticated PowerShell terminal at repository root:

```powershell
uv run python -m payment_ops.knowledge.evaluate_answers --live --report docs/WEEK2_ANSWER_RELIABILITY_COMPARISON.md
```

The runner creates a unique results directory and uses the existing document
embedding cache. The original development report is protected from overwrite.
Review all generated claims and scope/completeness, particularly Q03/Q04/Q07/Q08
and Q19. To annotate a preserved run, copy it to a separate review directory first
and use --review on the copy with a new report path. No human labels are assigned
automatically. Next: human evaluation review, then unified Streamlit integration;
Week 1 and synthetic SOP documents remain frozen.
