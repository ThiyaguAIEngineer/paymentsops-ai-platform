# Task 15: unknown codes and requested case evidence

Reference run: `evaluation/week2/results/answers_development/20261029T004007182456Z`,
grounded-v5-development, 17/18 correct dispositions (94.4%). This task does not
overwrite that run, its report, Baseline V1, corpus or gold labels. Its hashes are
recorded separately in `evaluation/week2/task15_reference_manifest.json`.

## Q13 root cause and correction

The model's answer accurately said SYN-ACH-299 was undocumented but labeled that
explanation answered. The service verified citations/quotes but did not enforce
code-definition membership or distinguish explaining absence from defining a code.

With the complete injected corpus catalog, code-meaning requests now compare exact
received identifiers to canonical catalog table entries. Prose/example mentions
are not definitions. Undocumented identifiers return insufficient_evidence with
their original spelling and a clear statement that their meaning cannot be
established from the available synthetic catalog. There is no code-specific list
or question matching, and the model cannot override this disposition.

If retrieved, the catalog's EC-LOOKUP undocumented-identifier instruction supplies
escalation guidance. The application copies that actual passage and runs it through
the existing quote/citation validator before including it. It does not invent an
owner, infer from a nearby code or substitute a different source. If the passage
is unavailable, only the evidence abstention is returned. Validation failures
remain diagnostic invalid_response failures, not successful evidence decisions.

Documented codes, including SYN-ACH-201, continue through normal generation with
their restrictions. Legacy callers without a complete catalog retain model-driven
handling: absence cannot be proven from an arbitrary top-five subset. The live
evaluation and inspection compositions already supply the complete corpus catalog.

## Q08 root cause and correction

Dense top-5 and the first explicit reference supplied BV-CORRECT, but not the
separate common case checklist EX-EVIDENCE. The generated correction/reconciliation/
review answer therefore omitted mandatory common case fields.

The existing retrieval module now supports a bounded exact-metadata lookup for an
explicitly requested knowledge scope. Case-evidence/record/field questions add
SYN-EXCEPTION/EX-EVIDENCE if absent, alongside the existing BV-CORRECT follow-up.
This uses operational section identifiers, not evaluation labels or Q08's wording.
Dense top-5 ordering and ordinary one-hop reference resolution are unchanged.

The scoped lookup adds only a complete single-chunk section. Missing, multi-chunk
or conflicting-version targets are not silently truncated or merged. Temporal
filtering applies before selection. Its origin is requested_section, score is a
placeholder rather than cosine confidence, and it has no fabricated link parent.
The actual Q08 context is seven chunks: five seeds, BV-CORRECT and EX-EVIDENCE.
At most one requested-scope lookup is applied per question; unknown-code requests
prioritize the catalog's unknown-code instruction instead of procedural expansion.

The grounded-v6-development prompt explicitly requests every common case field
when that checklist is supplied: identity, instruction context, observed condition,
evidence provenance, request context, work performed, ownership and follow-up.
These fields remain sourced from the SOP text, not injected as generated facts.
Quote validation, source membership, version/path provenance, limited guidance,
clarification, duplicate-risk stops and the educational disclosure remain intact.

## Verification and limits

Offline tests cover multiple undocumented identifiers, exact identifier preservation,
supported codes, absence versus prose mentions, all eight case-field categories
with exact citations, requested-section bounds/deduplication, Q09/Q10 guard
clarification and Q07 duplicate-risk context. Scripted valid answers demonstrate
service acceptance and citation coverage, not that a live model will include every
field. Human completeness and faithfulness remain unmeasured.

Verification: 132 focused tests passed; full suite: 545 passed (17 new regressions).
`git diff --check` passed.

No live run was attempted because this process has no NEBIUS_API_KEY. No updated
inference score is available; 17/18 is the preserved reference, not a v6 result.
No generalization claim follows from this development set.

From an authenticated PowerShell terminal:

```powershell
uv run python -m payment_ops.knowledge.evaluate_answers --live --report docs/WEEK2_TASK15_COMPARISON.md
```

Compare Q13 disposition and Q08 evidence/answer completeness against the reference
run, as well as all remaining questions. The runner creates a unique result
directory and reuses document embeddings. It records requested-section provenance.
The new report path preserves the previous 17/18 report. No UI, new framework,
database, provider or agent was introduced. Nothing is committed or pushed.
