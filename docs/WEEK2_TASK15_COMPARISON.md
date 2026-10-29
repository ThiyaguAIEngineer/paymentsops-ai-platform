# Week 2 development-set answer comparison

Baseline V1 remains unchanged: 12/18 correct dispositions (66.7%); 100% structural citation and quote verification; human faithfulness unmeasured.
This reuses the development questions and is not independent validation.

Status: **complete-real-qa**.

## Configuration

```json
{
  "embedding_model": "Qwen/Qwen3-Embedding-8B",
  "generation_model": "Qwen/Qwen3-30B-A3B-Instruct-2507",
  "embedding_dimensions_expected": 4096,
  "embedding_dimensions_actual": 4096,
  "evaluation_role": "Development-set comparison; not independent validation",
  "disposition_rule_version": "evidence-abstention-v2",
  "baseline": {
    "label": "Baseline V1",
    "original_run": "evaluation/week2/results/answers/20261028T202702213394Z",
    "snapshot": "evaluation/week2/results/baseline_v1",
    "files_sha256": {
      "claims.csv": "7920f5430655bd30ddda426152ca28b7505add472ab4c33407476637f0fca5d7",
      "completeness.csv": "6cd76470a3c1e393ac4674bf31427aeef09a33cdd7e7409f41d68353097a1dd7",
      "report.md": "9ea9659e1ca8719fd7937b9ab9b216154e4402132f01db8fa3cc3a8371d999e2",
      "results.json": "7a64fe87383e9acae9c05a46e75bc150613797b8547c9a621a4e6f93d6e7cafe",
      "sources.json": "97d7bcc1e54fdd31249e6dd8022dc0869a50fe416811684c713f21fa7bd45041"
    },
    "report_sha256": "9ea9659e1ca8719fd7937b9ab9b216154e4402132f01db8fa3cc3a8371d999e2",
    "gold_sha256": "6b229d92923a1737f34a7fe3704f40cba8a78bc9e0680e3724e308a89cf1132d",
    "configuration": {
      "embedding_model": "Qwen/Qwen3-Embedding-8B",
      "generation_model": "Qwen/Qwen3-30B-A3B-Instruct-2507",
      "embedding_dimensions_expected": 4096,
      "embedding_dimensions_actual": 4096,
      "provider": "Nebius",
      "prompt_version": "grounded-v3",
      "retrieval_method": "dense",
      "top_k": 5,
      "temperature": 0,
      "max_output_tokens": 1800,
      "generation_timeout_seconds": 45,
      "chunk_count": 32,
      "chunker_version": "structural-v1",
      "gold_version": "1.0.0",
      "gold_sha256": "6b229d92923a1737f34a7fe3704f40cba8a78bc9e0680e3724e308a89cf1132d",
      "corpus_sha256": {
        "SYN-ACH-RETURNS": "e8a647d4cc05b0065ac8e159ad4a82e7c50a39d961396966fdaa2f8e4b204a7c",
        "SYN-BENEFICIARY": "74649a098f59ad27f76124e85cc62bce97e61af041cdb17d548d0f18061cca6f",
        "SYN-ERROR-CATALOG": "0089f72ed4c5344b7b26284e793548650534eb79d91b3d2d1bea0eccc217944e",
        "SYN-EXCEPTION": "b1e934ac6a4f966b70e97676c67d13d2e9a0736271a6e647ba311de316fc5ef1",
        "SYN-STATUS": "7e6e4c838557a2409edfdd32e2635c84236dc155181e3c9dcdb1e8d883f57612",
        "SYN-WIRE-RECALL": "c8639fe6349e481e53abeb9324dd251237c98b3d279087997561860796751dc7"
      },
      "python": "3.13.14",
      "concurrency": 1,
      "packages": {
        "langchain-core": "1.7.1",
        "httpx": "0.28.1",
        "numpy": "2.5.4",
        "rank-bm25": "0.2.2"
      },
      "code_sha256": {
        "__init__.py": "428b64849b2962e1e57edee1ee4c2475d33034948ad746c8fd7a03f15afd363e",
        "answer_evaluation.py": "961cf2f5a4083a315fa0ce0a0a444ae684197f9b5b5afd7565a4c965eb92f564",
        "chunking.py": "81ac75d6878608a3f7ffe88957a14687f577c6513e2344cad52a044e94b3f62b",
        "embeddings.py": "31a82b5302dad5ca440a38dd382c649992b5731dfced42389aba90f84d896794",
        "evaluate_answers.py": "efe715fc4faf8877fa0c9d44b14e5f5716c130b51d9d8cbbb2f0957c1b284c1d",
        "evaluate_retrieval.py": "bad17f4d98acf5c35cdeb4e221c7f16aab6bb2b78d545050044fe94a9bd16b0a",
        "evaluation.py": "b28ddbc15384f08ddf3ed28ccfd96cfa6006afd489660e3d2e8f976b8137e698",
        "generation.py": "e71274a2352820ef129a32e50407534d276a636189b643a7be782175e57bd06e",
        "index.py": "c522f1209da3a5163481bd3e49227ef7ebb8aae7c8745bd0f4bb1129e0ff9c43",
        "ingestion.py": "bc97afcca02fc2e02ec821ce9cf4745e8d17cf3e72c001d3a8d4fbab51034901",
        "inspect_generation.py": "8822e00784aaa5770448c0302382d5b1ab76b3435592f486436cbe9cc5b086bb",
        "inspect_retrieval.py": "3181ac6c0266ef682edb94145fb370ed2b85e09d15a87134f3e4baf47b91cda0",
        "models.py": "2f343caaa92e046c21a34d52ec25e312871ed6546a152ba953fdfdc580b84446",
        "retrieval.py": "24dfd564eea6c6e303be70d8b17c5f2047e82e75d3e07ca0350de18bf68989de",
        "service.py": "5f008cdbbfc8376f0f858aa38fb743a5d7aa495deaa96425cba7f1672488c9ad"
      }
    },
    "summary": {
      "evaluated_questions": 18,
      "status_counts": {
        "answered": 9,
        "clarification": 3,
        "insufficient_evidence": 6
      },
      "disposition_by_class": {
        "answerable": {
          "count": 12,
          "correct_dispositions": 8,
          "disposition_accuracy": 0.6666666666666666
        },
        "unsupported": {
          "count": 4,
          "correct_dispositions": 3,
          "disposition_accuracy": 0.75
        },
        "ambiguous": {
          "count": 2,
          "correct_dispositions": 1,
          "disposition_accuracy": 0.5
        }
      },
      "successful_generation_rate": 0.5,
      "answerable_response_coverage": 0.6666666666666666,
      "invalid_response_count": 0,
      "invalid_response_frequency": 0.0,
      "incomplete_evidence_count": 2,
      "incomplete_evidence_frequency": 0.1111111111111111,
      "unavailable_count": 0,
      "citation_membership_validity": 1.0,
      "quote_verification_rate": 1.0,
      "answers_with_all_claim_candidates_cited": 1.0,
      "latency": {
        "count": 18,
        "p50_seconds": 1.4776595998555422,
        "p95_seconds": 4.29604859999381,
        "model_path_count": 15,
        "model_path_p50_seconds": 2.351238900097087,
        "model_path_p95_seconds": 4.29604859999381
      }
    },
    "human_faithfulness": "unmeasured"
  },
  "reference_expansion": "one explicit section (at most two chunks), plus one complete requested-scope section",
  "provider": "Nebius",
  "prompt_version": "grounded-v6-development",
  "retrieval_method": "dense",
  "top_k": 5,
  "temperature": 0,
  "max_output_tokens": 1800,
  "generation_timeout_seconds": 45,
  "chunk_count": 32,
  "chunker_version": "structural-v1",
  "gold_version": "1.0.0",
  "gold_sha256": "6b229d92923a1737f34a7fe3704f40cba8a78bc9e0680e3724e308a89cf1132d",
  "corpus_sha256": {
    "SYN-ACH-RETURNS": "e8a647d4cc05b0065ac8e159ad4a82e7c50a39d961396966fdaa2f8e4b204a7c",
    "SYN-BENEFICIARY": "74649a098f59ad27f76124e85cc62bce97e61af041cdb17d548d0f18061cca6f",
    "SYN-ERROR-CATALOG": "0089f72ed4c5344b7b26284e793548650534eb79d91b3d2d1bea0eccc217944e",
    "SYN-EXCEPTION": "b1e934ac6a4f966b70e97676c67d13d2e9a0736271a6e647ba311de316fc5ef1",
    "SYN-STATUS": "7e6e4c838557a2409edfdd32e2635c84236dc155181e3c9dcdb1e8d883f57612",
    "SYN-WIRE-RECALL": "c8639fe6349e481e53abeb9324dd251237c98b3d279087997561860796751dc7"
  },
  "python": "3.13.14",
  "concurrency": 1,
  "packages": {
    "langchain-core": "1.7.1",
    "httpx": "0.28.1",
    "numpy": "2.5.4",
    "rank-bm25": "0.2.2"
  },
  "code_sha256": {
    "__init__.py": "428b64849b2962e1e57edee1ee4c2475d33034948ad746c8fd7a03f15afd363e",
    "answer_evaluation.py": "906a6227aac22967952f0b99384141c0c30b74fd733c63c1239bef66112d9cb4",
    "chunking.py": "81ac75d6878608a3f7ffe88957a14687f577c6513e2344cad52a044e94b3f62b",
    "embeddings.py": "31a82b5302dad5ca440a38dd382c649992b5731dfced42389aba90f84d896794",
    "evaluate_answers.py": "ad82acd623bc200946b79296811aac3603fede193a16db0a079a29895486934b",
    "evaluate_retrieval.py": "bad17f4d98acf5c35cdeb4e221c7f16aab6bb2b78d545050044fe94a9bd16b0a",
    "evaluation.py": "b28ddbc15384f08ddf3ed28ccfd96cfa6006afd489660e3d2e8f976b8137e698",
    "generation.py": "80a1e51e9ad2a13f38db31bfbbf25a4393b7fd326b6b4e78522a2dab337f6b68",
    "index.py": "c522f1209da3a5163481bd3e49227ef7ebb8aae7c8745bd0f4bb1129e0ff9c43",
    "ingestion.py": "bc97afcca02fc2e02ec821ce9cf4745e8d17cf3e72c001d3a8d4fbab51034901",
    "inspect_generation.py": "4245881914e8a87eb308448d1eae35259166ed6e0849ac0e676c37a49f754879",
    "inspect_retrieval.py": "3181ac6c0266ef682edb94145fb370ed2b85e09d15a87134f3e4baf47b91cda0",
    "models.py": "2f343caaa92e046c21a34d52ec25e312871ed6546a152ba953fdfdc580b84446",
    "policy_period.py": "d3eb44b38bf1ac34953ec44429ad844f4617bd1cf3b1e416282bd5c48f10a96a",
    "retrieval.py": "ed7a4d5a5bc3b1ab5d977600eb016517238225b3c94f69dc95313360b59a38a4",
    "service.py": "09f18d2d4aab2d82677a5771572a7c5dc90457f2bb78573b5b00adac0ea1ce1b"
  }
}
```

Latest six-case grounded-v3 inspection: factual answered; SYN-BEN-301 incomplete_evidence; recall answered; delayed-status answered; unsupported abstained; ambiguous clarified. Those status-only inspections are not this 18-question baseline and do not establish faithfulness.

## Eligibility

20 preserved; 18 currently eligible (12 answerable, 4 unsupported, 2 ambiguous); Q17/Q18 fixture-dependent and excluded. Original PRD/separate handoff were not found locally; repository state, framework, corpus and golden dataset define this evaluation.

## Methodology and human review

All 20 original questions remain in the gold dataset. The live runner executes
12 answerable, four unsupported, and two ambiguous questions. Q17/Q18 are deferred
until archived/conflicting-source fixtures exist. Labels and expected evidence
groups are consulted only AFTER KnowledgeService.ask(question_text) returns.
No gold answer, expected section, or evaluation category is sent to inference.

Automatic checks are structural, not semantic:

- Answerable disposition matches answered/limited_answer; unsupported matches a
  genuine evidence abstention, not invalid_response; ambiguous matches clarification.
  A matching status does not prove an answer is correct or complete.
- Successful generation rate = substantive answered/limited_answer responses /
  all eligible questions. It is NOT an API transport success metric. Also report
  answerable response coverage; guard-generated clarifications make no LLM call.
- Citation membership checks exact retrieved chunk, document/section/version/path,
  source slot, and unique citation number. Quote verification checks the exact
  original substring at stored offsets for every passage. Zero citations/passages
  gives N/A, never a perfect score. All candidate claims must have known inline IDs.
- Invalid-response and incomplete-evidence frequencies use all evaluated questions
  as denominator; unavailability is reported separately. Gold evidence-group gaps
  assess current retrieved sections, not semantic completeness of generated claims.
- Latency is wall time around the normal service call, including query embedding,
  retrieval, generation, validation and fallbacks. Startup/corpus embedding/index
  time is separate. P50/P95 use nearest-rank ceil(p*N); failures and fast guard
  paths remain in the overall distribution. Model-path timings exclude guards and
  pre-generation failures/empty retrieval, but retain provider errors. A single
  18-question run is not the 100-query warm latency benchmark or target proof.

The run directory contains results.json, sources.json, claims.csv, completeness.csv,
and report.md. Source snapshots preserve review context by chunk ID and hash.
Only accepted answers/fallbacks and allowlisted diagnostics are saved; rejected
model payloads, authorization headers, keys, and sensitive provider settings are
not recorded. Keep generated artifacts in the ignored results directory.

### Faithfulness review criteria

claims.csv starts with BLANK assessments, reviewer and segmentation confirmation.
Mechanical sentence candidates inherit their original statement's citations. They
are NOT guaranteed atomic facts: reviewers must inspect the full generated answer,
split compound assertions into separate rows, and verify no substantive claim was
omitted. To split, copy a row, keep original_claim_id and immutable answer/evidence
fields, assign a unique claim_id, and edit claim_text into individual assertions.
Set segmentation_confirmed=yes only after checking coverage and citation mapping.
Every original candidate must remain covered; every child row must be reviewed.

- Supported: the claim's meaning, conditions, sequence, and scope follow from the
  cited source text. A quote merely mentioning the topic is insufficient.
- Unsupported: meaning is absent, contradicted, invented, or an unretrieved
  procedure is represented as verified. Valid IDs/quotes do not rescue such a claim.
- Partially supported: only part of a compound assertion or procedure is justified,
  or an essential condition is missing. Split where possible; do not give full credit.

No final score is computed until all claim rows are labeled with a reviewer and
segmentation confirmed. Faithfulness = Supported / all reviewed substantive claims;
Partially supported and Unsupported receive zero full-support credit. Report both
answerable-question claim faithfulness (the >=90% target's scope) and all-generated-
claim faithfulness. No claims/abstentions is N/A, never 100%. Response coverage is
separate; selective abstention cannot establish overall quality. Human segmentation
and ratings are judgments, not automatically verified ground truth. The runner
never assigns favorable labels or declares the 90% target achieved automatically.

### Procedural completeness review criteria

completeness.csv covers ALL 12 answerable questions, including abstentions. Assign
one primary category and record additional issues in notes:

- complete_supported_answer: all information necessary for the requested scope,
  including relevant prerequisites, stop rules and review gates, is supported.
- appropriately_bounded_answer: supported guidance meets the requested limited
  scope and explicitly excludes unverified later stages without hiding a critical gap.
- missing_essential_procedure: a required step/condition/evidence source is absent;
  safe abstention due to a retrieval gap can belong here, rather than being unsafe.
- unsupported_additional_instruction: answer adds an unjustified action, deadline,
  policy, or permission beyond what sources support.
- unnecessary_abstention: available retrieved text was sufficient for the actual
  question, yet the system declined. Inspect the text, not merely the gold labels.

These are human labels, NOT inferred from model status or required_sections. Review
the recurring SYN-BEN-301 case (Q03) for narrow catalog sufficiency versus genuine
missing procedural evidence; no workaround or hardcoded answer is introduced.
Citation matching cannot establish faithfulness, and faithfulness does not establish
requested-scope completeness. Unsupported/ambiguous disposition accuracy is separate.

## Observed dispositions and deterministic metrics

```json
{
  "evaluated_questions": 18,
  "status_counts": {
    "answered": 11,
    "clarification": 2,
    "insufficient_evidence": 5
  },
  "disposition_by_class": {
    "answerable": {
      "count": 12,
      "correct_dispositions": 11,
      "disposition_accuracy": 0.9166666666666666
    },
    "unsupported": {
      "count": 4,
      "correct_dispositions": 4,
      "disposition_accuracy": 1.0
    },
    "ambiguous": {
      "count": 2,
      "correct_dispositions": 2,
      "disposition_accuracy": 1.0
    }
  },
  "successful_generation_rate": 0.6111111111111112,
  "answerable_response_coverage": 0.9166666666666666,
  "invalid_response_count": 1,
  "invalid_response_frequency": 0.05555555555555555,
  "incomplete_evidence_count": 0,
  "incomplete_evidence_frequency": 0.0,
  "unavailable_count": 0,
  "citation_membership_validity": 1.0,
  "quote_verification_rate": 1.0,
  "answers_with_all_claim_candidates_cited": 1.0,
  "latency": {
    "count": 18,
    "p50_seconds": 5.352057100040838,
    "p95_seconds": 14.27836720016785,
    "model_path_count": 15,
    "model_path_p50_seconds": 5.99602449988015,
    "model_path_p95_seconds": 14.27836720016785
  }
}
```


## Human faithfulness and procedural completeness

Human assessments pending. **90% faithfulness target: not measured.** No completeness categories have been assigned automatically.

## Per-question results, evidence gaps, and failure analysis

### Q01: What details are required to open a wire recall request?

Category: Simple factual; class: answerable; status: answered; reason: answered.

Service latency: 5.352 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

To open a wire recall request, the required details include: payment ID, original instruction reference, rail, original amount and currency, synthetic sender and beneficiary references, requester reference, requester-verification reviewer and outcome, reason for recall, last confirmed payment status, status timestamp/source, related case references, and the proposed case owner. [1]

Before preparing the request, ensure that all prerequisites are met: the payment must be identifiable as a synthetic wire, the requester must be verified, and current release evidence must be documented. If any prerequisites are missing, record code SYN-WR-101 and stop preparation until they are obtained. [2]

After recording all required details and verifying completeness, the Wire Operations supervisor must review the request for completeness and duplicate risk before a simulated request reference is recorded. [1]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-WIRE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-REQUEST", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-ELIGIBILITY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-SCOPE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-ESCALATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-TRACK", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321"}]`

Citation checks: `{"citation_count": 2, "valid_citation_count": 2, "passage_count": 4, "verified_passage_count": 4, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ERROR-CATALOG/EC-WIRE", "SYN-WIRE-RECALL/WR-ELIGIBILITY", "SYN-WIRE-RECALL/WR-ESCALATE", "SYN-WIRE-RECALL/WR-REQUEST", "SYN-WIRE-RECALL/WR-SCOPE", "SYN-WIRE-RECALL/WR-TRACK"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 1.0, "precision_at_5": 0.2, "mrr_at_5": 0.5, "ndcg_at_5": 0.6309297535714575, "evidence_group_coverage": 1.0, "multi_document_evidence_coverage": null, "required_document_coverage": 1.0, "complete_evidence": true}, "missing_sections": [], "missing_evidence_groups": [], "nonrelevant_sections": ["SYN-ERROR-CATALOG/EC-WIRE", "SYN-WIRE-RECALL/WR-ELIGIBILITY", "SYN-WIRE-RECALL/WR-ESCALATE", "SYN-WIRE-RECALL/WR-SCOPE"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Wire Recall SOP | SYN-WIRE-RECALL/WR-REQUEST | v1.0.0

Chunk `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08`; offsets 81:462.

> Required details: payment ID, original instruction reference, rail, original
> amount and currency, synthetic sender and beneficiary references, requester
> reference, requester-verification reviewer/outcome, reason for recall, last
> confirmed payment status, status timestamp/source, related case references, and
> the proposed case owner. Record these using `SYN-EXCEPTION/EX-EVIDENCE`.

Chunk `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08`; offsets 627:782.

> 3. Ask the Wire Operations supervisor to review completeness and duplicate risk.
> 4. Record a simulated request reference only when that review is complete.

[2] Wire Recall SOP | SYN-WIRE-RECALL/WR-ELIGIBILITY | v1.0.0

Chunk `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63`; offsets 86:322.

> Prerequisites: an identifiable synthetic wire, a documented request from a
> verified fictional requester, and current release evidence. Read status meanings
> in `SYN-STATUS/SS-STATES` and evidence requirements in `SYN-STATUS/SS-EVIDENCE`.

Chunk `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63`; offsets 707:854.

> If mandatory details or verification are missing, record `SYN-WR-101`
>    (recall prerequisites missing), stop request preparation, and obtain them.

### Q02: Does ACCEPTED mean a payment has settled?

Category: Simple factual; related states; class: answerable; status: answered; reason: answered.

Service latency: 5.996 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

ACCEPTED does not mean a payment has settled. In the synthetic lifecycle, ACCEPTED indicates that the instruction has been initially accepted, but release and settlement are not yet established. Settlement requires both a matched settlement confirmation and a matched reconciliation record, as stated in the SS-EVIDENCE section. The ACCEPTED state may precede RELEASED and SETTLED, but it does not imply settlement has occurred. [1] [2]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233", "document_id": "SYN-STATUS", "section_id": "SS-STATES", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0", "document_id": "SYN-STATUS", "section_id": "SS-STATES", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe", "document_id": "SYN-STATUS", "section_id": "SS-EVIDENCE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-LOOKUP", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-STATUS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-ELIGIBILITY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233"}]`

Citation checks: `{"citation_count": 2, "valid_citation_count": 2, "passage_count": 3, "verified_passage_count": 3, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ERROR-CATALOG/EC-LOOKUP", "SYN-ERROR-CATALOG/EC-STATUS", "SYN-STATUS/SS-EVIDENCE", "SYN-STATUS/SS-STATES", "SYN-WIRE-RECALL/WR-ELIGIBILITY"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 1.0, "precision_at_5": 0.2, "mrr_at_5": 1.0, "ndcg_at_5": 1.0, "evidence_group_coverage": 1.0, "multi_document_evidence_coverage": null, "required_document_coverage": 1.0, "complete_evidence": true}, "missing_sections": [], "missing_evidence_groups": [], "nonrelevant_sections": ["SYN-ERROR-CATALOG/EC-LOOKUP", "SYN-ERROR-CATALOG/EC-STATUS", "SYN-STATUS/SS-EVIDENCE"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Settlement and Payment Status Guide | SYN-STATUS/SS-STATES | v1.0.0

Chunk `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233`; offsets 288:425.

> ACCEPTED does not mean SETTLED.
> Validation success, approval readiness, and a recipient's acknowledgment are not
> settlement confirmation.

Chunk `SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0`; offsets 941:1042.

> | ACCEPTED | Initial intake accepted; release and settlement not established | RELEASED or REJECTED |

[2] Settlement and Payment Status Guide | SYN-STATUS/SS-EVIDENCE | v1.0.0

Chunk `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe`; offsets 722:862.

> For a settlement claim, obtain both settlement confirmation and matched
>    reconciliation record. Missing one leaves settlement unconfirmed.

### Q03: What does SYN-BEN-301 mean, and what should I do first?

Category: Exact error-code lookup; class: answerable; status: answered; reason: answered.

Service latency: 4.121 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

SYN-BEN-301 means a name mismatch, indicating a discrepancy between the submitted beneficiary name and the verified beneficiary record that remains unresolved. [1]

The first action is to compare the submitted name with the verified beneficiary record and document the discrepancy. [1] [2]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-BENEFICIARY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd", "document_id": "SYN-BENEFICIARY", "section_id": "BV-FORMAT", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-LOOKUP", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-CLASSIFY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74", "document_id": "SYN-BENEFICIARY", "section_id": "BV-CHECKS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4", "document_id": "SYN-BENEFICIARY", "section_id": "BV-NAME", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856"}]`

Citation checks: `{"citation_count": 2, "valid_citation_count": 2, "passage_count": 3, "verified_passage_count": 3, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ACH-RETURNS/AR-CLASSIFY", "SYN-BENEFICIARY/BV-CHECKS", "SYN-BENEFICIARY/BV-FORMAT", "SYN-BENEFICIARY/BV-NAME", "SYN-ERROR-CATALOG/EC-BENEFICIARY", "SYN-ERROR-CATALOG/EC-LOOKUP"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 0.5, "precision_at_5": 0.2, "mrr_at_5": 1.0, "ndcg_at_5": 0.6131471927654584, "evidence_group_coverage": 1.0, "multi_document_evidence_coverage": null, "required_document_coverage": null, "complete_evidence": true}, "missing_sections": ["SYN-BENEFICIARY/BV-NAME"], "missing_evidence_groups": [], "nonrelevant_sections": ["SYN-ACH-RETURNS/AR-CLASSIFY", "SYN-BENEFICIARY/BV-CHECKS", "SYN-BENEFICIARY/BV-FORMAT", "SYN-ERROR-CATALOG/EC-LOOKUP"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Payment Error-Code Catalog | SYN-ERROR-CATALOG/EC-BENEFICIARY | v1.0.0

Chunk `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856`; offsets 221:485.

> SYN-BEN-301 | Name mismatch | Beneficiary identity/detail discrepancy unresolved | Compare submitted name with verified beneficiary record | Do not bypass validation; verified correction and revalidation required | Beneficiary Maintenance | SYN-BENEFICIARY/BV-NAME

Chunk `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856`; offsets 304:359.

> Compare submitted name with verified beneficiary record

[2] Beneficiary Validation Runbook | SYN-BENEFICIARY/BV-NAME | v1.0.0

Chunk `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4`; offsets 285:359.

> 1. Compare the submitted name and verified record; record the discrepancy.

### Q04: What does SYN-ACH-201 mean? Can I immediately retry?

Category: Exact code; action restriction; class: answerable; status: answered; reason: answered.

Service latency: 5.011 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

SYN-ACH-201 means 'Account closed' and indicates that the original destination account cannot be reused for retry. [1] [2]

You cannot immediately retry a payment with SYN-ACH-201 because the code explicitly prohibits immediate retry and requires correction, reconciliation, duplicate checks, and supervisor review before any retry preparation. [1] [2] [3]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-CLASSIFY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-ACH", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-STATUS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-NEXT", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-LOOKUP", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-STATUS:1.0.0:SS-DELAY:0:structural-v1:dd54558a2d58ea466015a4b045e91f79b09ad43b66cc0bc3e368b1922ce50b24", "document_id": "SYN-STATUS", "section_id": "SS-DELAY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35"}]`

Citation checks: `{"citation_count": 3, "valid_citation_count": 3, "passage_count": 5, "verified_passage_count": 5, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ACH-RETURNS/AR-CLASSIFY", "SYN-ACH-RETURNS/AR-NEXT", "SYN-ERROR-CATALOG/EC-ACH", "SYN-ERROR-CATALOG/EC-LOOKUP", "SYN-ERROR-CATALOG/EC-STATUS", "SYN-STATUS/SS-DELAY"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 1.0, "precision_at_5": 0.4, "mrr_at_5": 0.5, "ndcg_at_5": 0.6509209298071326, "evidence_group_coverage": 1.0, "multi_document_evidence_coverage": null, "required_document_coverage": null, "complete_evidence": true}, "missing_sections": [], "missing_evidence_groups": [], "nonrelevant_sections": ["SYN-ACH-RETURNS/AR-CLASSIFY", "SYN-ERROR-CATALOG/EC-LOOKUP", "SYN-ERROR-CATALOG/EC-STATUS"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] ACH Returns Guide | SYN-ACH-RETURNS/AR-CLASSIFY | v1.0.0

Chunk `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f`; offsets 150:254.

> SYN-ACH-201 | Account closed | Stop retry preparation; obtain verified replacement details and review. |

Chunk `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f`; offsets 444:523.

> Neither code means a simple temporary timeout. Neither permits immediate retry.

[2] Payment Error-Code Catalog | SYN-ERROR-CATALOG/EC-ACH | v1.0.0

Chunk `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586`; offsets 193:464.

> SYN-ACH-201 | Account closed | Original destination cannot be reused for retry | Obtain verified replacement details and review | No immediate retry; correction, reconciliation, duplicate checks, and supervisor review required | ACH Operations | SYN-ACH-RETURNS/AR-NEXT |

Chunk `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586`; offsets 323:419.

> No immediate retry; correction, reconciliation, duplicate checks, and supervisor review required

[3] ACH Returns Guide | SYN-ACH-RETURNS/AR-NEXT | v1.0.0

Chunk `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb`; offsets 84:308.

> For `SYN-ACH-201`, do not retry to the same closed account. Obtain verified
>    replacement beneficiary details from the fictional beneficiary-maintenance
>    workflow; absence of replacement details keeps the case unresolved.

### Q05: We already sent the wire and want to get the money back. Where do we start?

Category: Semantic/paraphrased; class: answerable; status: answered; reason: answered.

Service latency: 3.502 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

To initiate a wire recall, first confirm the wire is released or settled and not canceled or returned. Use the payment ID, original instruction reference, rail, amount, currency, and requester details to prepare a recall request. Verify the requester's authority and ensure no duplicate request exists. If prerequisites are missing, record code SYN-WR-101 and stop preparation. If all prerequisites are met, create a recall case, record required details using `SYN-EXCEPTION/EX-EVIDENCE`, and escalate to the Wire Operations supervisor for review of completeness and duplicate risk before assigning a case owner and follow-up checkpoint. [1]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-SCOPE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-ESCALATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-WIRE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-REQUEST", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-ELIGIBILITY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-SCOPE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa"}]`

Citation checks: `{"citation_count": 1, "valid_citation_count": 1, "passage_count": 1, "verified_passage_count": 1, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ACH-RETURNS/AR-SCOPE", "SYN-ERROR-CATALOG/EC-WIRE", "SYN-WIRE-RECALL/WR-ELIGIBILITY", "SYN-WIRE-RECALL/WR-ESCALATE", "SYN-WIRE-RECALL/WR-REQUEST", "SYN-WIRE-RECALL/WR-SCOPE"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 1.0, "precision_at_5": 0.4, "mrr_at_5": 0.25, "ndcg_at_5": 0.5012658353418871, "evidence_group_coverage": 1.0, "multi_document_evidence_coverage": null, "required_document_coverage": 1.0, "complete_evidence": true}, "missing_sections": [], "missing_evidence_groups": [], "nonrelevant_sections": ["SYN-ERROR-CATALOG/EC-WIRE", "SYN-WIRE-RECALL/WR-ESCALATE", "SYN-WIRE-RECALL/WR-SCOPE"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Wire Recall SOP | SYN-WIRE-RECALL/WR-REQUEST | v1.0.0

Chunk `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08`; offsets 81:1002.

> Required details: payment ID, original instruction reference, rail, original
> amount and currency, synthetic sender and beneficiary references, requester
> reference, requester-verification reviewer/outcome, reason for recall, last
> confirmed payment status, status timestamp/source, related case references, and
> the proposed case owner. Record these using `SYN-EXCEPTION/EX-EVIDENCE`.
> 
> 1. Create or link one recall case and preserve the original instruction unchanged.
> 2. Record the required details and supporting evidence; identify missing items.
> 3. Ask the Wire Operations supervisor to review completeness and duplicate risk.
> 4. Record a simulated request reference only when that review is complete.
>    This is an educational case record, not transmission to a bank or network.
> 5. Assign an owner and record the next follow-up checkpoint agreed by that owner.
>    This SOP establishes no universal elapsed-time deadline.

### Q06: The payee label differs from the account holder. How do I resolve it?

Category: Semantic/paraphrased; class: answerable; status: answered; reason: answered.

Service latency: 3.556 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

A payee label differing from the verified account holder requires investigation even if the account reference is well formed. The first step is to compare the submitted name with the verified beneficiary record and document the discrepancy. [1]

The intended recipient must be verified through the recorded synthetic maintenance workflow by Beneficiary Maintenance. Do not assume a nickname or different company name is equivalent solely because it looks similar. [1]

If the submitted name is incorrect, obtain a verified correction using the `SYN-BENEFICIARY/BV-CORRECT` procedure. If the verified record is disputed, stop and escalate instead of changing it to make the check pass. [1]

Retain the unresolved status until verified correction and revalidation evidence exist. Do not bypass the name check, remove the code manually, or claim that resolving the mismatch establishes ownership or settlement beyond the available evidence. [1]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4", "document_id": "SYN-BENEFICIARY", "section_id": "BV-NAME", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-BENEFICIARY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74", "document_id": "SYN-BENEFICIARY", "section_id": "BV-CHECKS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-ESCALATE:0:structural-v1:cc1eff7c335c15d24ac477e5a4b4940be69adaa708cdb0b9d91ba5bb7d64cad4", "document_id": "SYN-BENEFICIARY", "section_id": "BV-ESCALATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-LOOKUP", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-CORRECT:0:structural-v1:f3748f030fd07f4ae32a0e11dbd12aba171efa2e3fe508601276dba0a4aa5445", "document_id": "SYN-BENEFICIARY", "section_id": "BV-CORRECT", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4"}]`

Citation checks: `{"citation_count": 1, "valid_citation_count": 1, "passage_count": 4, "verified_passage_count": 4, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-BENEFICIARY/BV-CHECKS", "SYN-BENEFICIARY/BV-CORRECT", "SYN-BENEFICIARY/BV-ESCALATE", "SYN-BENEFICIARY/BV-NAME", "SYN-ERROR-CATALOG/EC-BENEFICIARY", "SYN-ERROR-CATALOG/EC-LOOKUP"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 0.5, "precision_at_5": 0.2, "mrr_at_5": 1.0, "ndcg_at_5": 0.6131471927654584, "evidence_group_coverage": 0.5, "multi_document_evidence_coverage": null, "required_document_coverage": 1.0, "complete_evidence": false}, "missing_sections": ["SYN-BENEFICIARY/BV-CORRECT"], "missing_evidence_groups": ["evidence-2"], "nonrelevant_sections": ["SYN-BENEFICIARY/BV-CHECKS", "SYN-BENEFICIARY/BV-ESCALATE", "SYN-ERROR-CATALOG/EC-BENEFICIARY", "SYN-ERROR-CATALOG/EC-LOOKUP"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Beneficiary Validation Runbook | SYN-BENEFICIARY/BV-NAME | v1.0.0

Chunk `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4`; offsets 288:359.

> Compare the submitted name and verified record; record the discrepancy.

Chunk `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4`; offsets 363:580.

> Ask Beneficiary Maintenance to verify the intended recipient through the
>    recorded synthetic maintenance workflow. Do not assume a nickname or different
>    company name is equivalent solely because it looks similar.

Chunk `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4`; offsets 584:789.

> If the submitted detail is wrong, obtain verified correction under
>    `SYN-BENEFICIARY/BV-CORRECT`. If the comparison record is disputed, stop and
>    escalate instead of changing it to make the check pass.

Chunk `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4`; offsets 793:1028.

> Retain unresolved status until correction and revalidation evidence exist.
> 
> Do not bypass the name check, remove the code manually, or claim that resolving
> the mismatch establishes ownership or settlement beyond the available evidence.

### Q07: A status update is delayed and the analyst wants to resend. What checks and escalation apply?

Category: Multi-document; class: answerable; status: insufficient_evidence; reason: invalid_response.

Service latency: 10.679 seconds. Correct disposition: False (status only).

Synthetic educational material — not an actual bank policy.

A supported answer could not be validated from the retrieved evidence.

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-STATUS:1.0.0:SS-DELAY:0:structural-v1:dd54558a2d58ea466015a4b045e91f79b09ad43b66cc0bc3e368b1922ce50b24", "document_id": "SYN-STATUS", "section_id": "SS-DELAY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-STATUS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-ESCALATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-EXCEPTION:1.0.0:EX-ESCALATE:0:structural-v1:b6ca345d40c85ef09d4a1e31beb46b17368924d682f5878065e15a95426d71c5", "document_id": "SYN-EXCEPTION", "section_id": "EX-ESCALATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-STATUS:1.0.0:SS-ESCALATE:0:structural-v1:324c5b27397826d024568564b8ceba97c1dd167c3e3c7939400421a367282354", "document_id": "SYN-STATUS", "section_id": "SS-ESCALATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-EXCEPTION:1.0.0:EX-DUPLICATE:0:structural-v1:f7f86f3c9de84a16692fe867b42356b11f93da7e2c21b1977402e37b37975cc5", "document_id": "SYN-EXCEPTION", "section_id": "EX-DUPLICATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-STATUS:1.0.0:SS-DELAY:0:structural-v1:dd54558a2d58ea466015a4b045e91f79b09ad43b66cc0bc3e368b1922ce50b24"}]`

Citation checks: `{"citation_count": 0, "valid_citation_count": 0, "passage_count": 0, "verified_passage_count": 0, "all_claim_candidates_cited": null, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ERROR-CATALOG/EC-STATUS", "SYN-EXCEPTION/EX-DUPLICATE", "SYN-EXCEPTION/EX-ESCALATE", "SYN-STATUS/SS-DELAY", "SYN-STATUS/SS-ESCALATE", "SYN-WIRE-RECALL/WR-ESCALATE"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 0.6666666666666666, "precision_at_5": 0.4, "mrr_at_5": 1.0, "ndcg_at_5": 0.6713860725233041, "evidence_group_coverage": 0.6666666666666666, "multi_document_evidence_coverage": 0.6666666666666666, "required_document_coverage": 1.0, "complete_evidence": false}, "missing_sections": ["SYN-EXCEPTION/EX-DUPLICATE"], "missing_evidence_groups": ["evidence-2"], "nonrelevant_sections": ["SYN-ERROR-CATALOG/EC-STATUS", "SYN-STATUS/SS-ESCALATE", "SYN-WIRE-RECALL/WR-ESCALATE"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[{"stage": "grounding_validation", "category": "quote_not_found", "statement_index": 5, "evidence_index": 1, "source_id": "S2", "quote_characters": 87, "quote_sha256": "78715ef1795009e815d3f7a24177983f474955dfff8563c2713b7bfe7976b12a", "matching_source_ids": [], "missing_sections": [], "http_status": null, "field_name": null, "value_type": null, "item_index": null, "exception_type": null}]`

### Q08: An ACH return cites invalid account details. What correction and case evidence are needed?

Category: Multi-document; class: answerable; status: answered; reason: answered.

Service latency: 10.065 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

For an ACH return citing invalid account details (SYN-ACH-202), the required correction is to identify the invalid field and obtain verified correction of that field through the beneficiary validation workflow. [1]

The required case evidence includes the original instruction and case, the proposed corrected field, synthetic evidence reference, evidence source/timestamp, reason for correction, and the maintenance reviewer who verified it, as well as a second reviewer's confirmation that the change matches the verified recipient record. [2]

After correction, rerun synthetic validation checks on the proposed details and retain each result, timestamp, and reference, including any remaining failures, and link the original and corrected versions without rewriting historical evidence. [2]

The corrected details must be reviewed by an ACH Operations supervisor, who must assess revalidation results, return evidence, and duplicate suspicion, and record the review outcome before retry preparation is permitted. [3]

The case must also confirm reconciliation of the return, check for pending replacements, and resolve any duplicate suspicion under `SYN-EXCEPTION/EX-DUPLICATE`, which is not retrieved but is a required gate. [3]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-ACH", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-NEXT", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-SCOPE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-CLASSIFY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc", "document_id": "SYN-STATUS", "section_id": "SS-RETURNS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-CORRECT:0:structural-v1:f3748f030fd07f4ae32a0e11dbd12aba171efa2e3fe508601276dba0a4aa5445", "document_id": "SYN-BENEFICIARY", "section_id": "BV-CORRECT", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb"}, {"source_id": "S7", "chunk_id": "SYN-EXCEPTION:1.0.0:EX-EVIDENCE:0:structural-v1:c2158f927546da9c63cad16b0b4ec704ba1719a5ad7e7948db911664ae600ee5", "document_id": "SYN-EXCEPTION", "section_id": "EX-EVIDENCE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "requested_section", "linked_from_chunk_id": null}]`

Citation checks: `{"citation_count": 3, "valid_citation_count": 3, "passage_count": 5, "verified_passage_count": 5, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ACH-RETURNS/AR-CLASSIFY", "SYN-ACH-RETURNS/AR-NEXT", "SYN-ACH-RETURNS/AR-SCOPE", "SYN-BENEFICIARY/BV-CORRECT", "SYN-ERROR-CATALOG/EC-ACH", "SYN-EXCEPTION/EX-EVIDENCE", "SYN-STATUS/SS-RETURNS"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 0.3333333333333333, "precision_at_5": 0.2, "mrr_at_5": 0.5, "ndcg_at_5": 0.2960819109658652, "evidence_group_coverage": 0.3333333333333333, "multi_document_evidence_coverage": 0.3333333333333333, "required_document_coverage": 0.3333333333333333, "complete_evidence": false}, "missing_sections": ["SYN-BENEFICIARY/BV-CORRECT", "SYN-EXCEPTION/EX-EVIDENCE"], "missing_evidence_groups": ["evidence-2", "evidence-3"], "nonrelevant_sections": ["SYN-ACH-RETURNS/AR-CLASSIFY", "SYN-ACH-RETURNS/AR-SCOPE", "SYN-ERROR-CATALOG/EC-ACH", "SYN-STATUS/SS-RETURNS"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Payment Error-Code Catalog | SYN-ERROR-CATALOG/EC-ACH | v1.0.0

Chunk `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586`; offsets 467:754.

> SYN-ACH-202 | Account details invalid | Supplied destination details require correction | Identify invalid field and obtain verified correction | No immediate retry; revalidation, reconciliation, duplicate checks, and supervisor review required | ACH Operations | SYN-ACH-RETURNS/AR-NEXT

[2] Beneficiary Validation Runbook | SYN-BENEFICIARY/BV-CORRECT | v1.0.0

Chunk `SYN-BENEFICIARY:1.0.0:BV-CORRECT:0:structural-v1:f3748f030fd07f4ae32a0e11dbd12aba171efa2e3fe508601276dba0a4aa5445`; offsets 82:475.

> 1. Link the original instruction and case; retain original field values.
> 2. Record the proposed corrected field, synthetic evidence reference, evidence
>    source/timestamp, reason, and maintenance reviewer who verified the correction.
> 3. Have a second reviewer, distinct from the preparing analyst, confirm that
>    the change matches the verified recipient record. Record reviewer and outcome.

Chunk `SYN-BENEFICIARY:1.0.0:BV-CORRECT:0:structural-v1:f3748f030fd07f4ae32a0e11dbd12aba171efa2e3fe508601276dba0a4aa5445`; offsets 476:712.

> 4. Rerun the relevant synthetic validation checks on the proposed details and
>    retain each result, timestamp, and reference, including remaining failures.
> 5. Link the original and corrected versions; never rewrite historical evidence.

[3] ACH Returns Guide | SYN-ACH-RETURNS/AR-NEXT | v1.0.0

Chunk `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb`; offsets 630:787.

> 4. Have the ACH Operations supervisor review corrected details, revalidation
>    result, return evidence, and duplicate assessment. Record the review outcome.

Chunk `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb`; offsets 478:629.

> 3. Confirm the return is matched and reconciled, check for pending replacements,
>    and resolve duplicate suspicion under `SYN-EXCEPTION/EX-DUPLICATE`.

### Q09: How do I reverse this payment?

Category: Ambiguous; class: ambiguous; status: clarification; reason: missing_transaction_context.

Service latency: 0.000 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

Please provide the payment rail (for example, wire or ACH) and current confirmed payment status, including whether it has been released before I select a procedure.

Retrieved sources: `[]`

Citation checks: `{"citation_count": 0, "valid_citation_count": 0, "passage_count": 0, "verified_passage_count": 0, "all_claim_candidates_cited": null, "issues": []}`

Current gold evidence gaps: `null`

Prior Dense retrieval baseline gaps: `null`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[{"stage": "clarification", "category": "missing_rail_or_status", "statement_index": null, "evidence_index": null, "source_id": null, "quote_characters": null, "quote_sha256": null, "matching_source_ids": [], "missing_sections": [], "http_status": null, "field_name": null, "value_type": null, "item_index": null, "exception_type": null}]`

### Q10: It failed. Should I retry?

Category: Ambiguous; class: ambiguous; status: clarification; reason: missing_transaction_context.

Service latency: 0.000 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

Please provide the payment rail (for example, wire or ACH) and current confirmed payment status, including whether it has been released before I select a procedure.

Retrieved sources: `[]`

Citation checks: `{"citation_count": 0, "valid_citation_count": 0, "passage_count": 0, "verified_passage_count": 0, "all_claim_candidates_cited": null, "issues": []}`

Current gold evidence gaps: `null`

Prior Dense retrieval baseline gaps: `null`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[{"stage": "clarification", "category": "missing_rail_or_status", "statement_index": null, "evidence_index": null, "source_id": null, "quote_characters": null, "quote_sha256": null, "matching_source_ids": [], "missing_sections": [], "http_status": null, "field_name": null, "value_type": null, "item_index": null, "exception_type": null}]`

### Q11: How does a recall differ from cancellation before release?

Category: Closely related procedures; class: answerable; status: answered; reason: answered.

Service latency: 4.462 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

A recall is a request to recover a wire that has already been released from the operator's processing boundary, while cancellation is a request to stop an instruction before release. [1]

For a released or settled wire, assess recall prerequisites; for an instruction that has not been released, route a cancellation assessment to Wire Operations. [1]

A recall request requires specific details such as payment ID, original instruction reference, rail, amount, currency, synthetic sender and beneficiary references, requester reference, verification reviewer/outcome, reason for recall, last confirmed status, status timestamp/source, related case references, and proposed case owner. [2]

Recall eligibility requires identifiable synthetic wire, documented request from a verified requester, and current release evidence; missing prerequisites block request preparation. [3]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-SCOPE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-WIRE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-REQUEST", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc", "document_id": "SYN-STATUS", "section_id": "SS-RETURNS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-SCOPE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-ELIGIBILITY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321"}]`

Citation checks: `{"citation_count": 3, "valid_citation_count": 3, "passage_count": 5, "verified_passage_count": 5, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ACH-RETURNS/AR-SCOPE", "SYN-ERROR-CATALOG/EC-WIRE", "SYN-STATUS/SS-RETURNS", "SYN-WIRE-RECALL/WR-ELIGIBILITY", "SYN-WIRE-RECALL/WR-REQUEST", "SYN-WIRE-RECALL/WR-SCOPE"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 1.0, "precision_at_5": 0.2, "mrr_at_5": 1.0, "ndcg_at_5": 1.0, "evidence_group_coverage": 1.0, "multi_document_evidence_coverage": null, "required_document_coverage": 1.0, "complete_evidence": true}, "missing_sections": [], "missing_evidence_groups": [], "nonrelevant_sections": ["SYN-ACH-RETURNS/AR-SCOPE", "SYN-ERROR-CATALOG/EC-WIRE", "SYN-STATUS/SS-RETURNS", "SYN-WIRE-RECALL/WR-REQUEST"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Wire Recall SOP | SYN-WIRE-RECALL/WR-SCOPE | v1.0.0

Chunk `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa`; offsets 701:916.

> A recall is a request to recover a wire already released from the fictional
> operator's processing boundary. It is a request, not a reversal guarantee.
> Cancellation is a request to stop an instruction before release.

Chunk `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa`; offsets 1012:1211.

> For RECEIVED or ACCEPTED instructions, route a cancellation assessment to Wire
> Operations; this SOP does not define cancellation execution. For RELEASED or
> SETTLED wires, assess recall prerequisites.

[2] Wire Recall SOP | SYN-WIRE-RECALL/WR-REQUEST | v1.0.0

Chunk `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08`; offsets 81:414.

> Required details: payment ID, original instruction reference, rail, original
> amount and currency, synthetic sender and beneficiary references, requester
> reference, requester-verification reviewer/outcome, reason for recall, last
> confirmed payment status, status timestamp/source, related case references, and
> the proposed case owner.

[3] Wire Recall SOP | SYN-WIRE-RECALL/WR-ELIGIBILITY | v1.0.0

Chunk `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63`; offsets 86:220.

> Prerequisites: an identifiable synthetic wire, a documented request from a
> verified fictional requester, and current release evidence.

Chunk `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63`; offsets 707:854.

> If mandatory details or verification are missing, record `SYN-WR-101`
>    (recall prerequisites missing), stop request preparation, and obtain them.

### Q12: Is SYN-BEN-302 handled the same way as SYN-BEN-301?

Category: Closely related codes; class: answerable; status: answered; reason: answered.

Service latency: 7.582 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

SYN-BEN-302 is not handled the same way as SYN-BEN-301, as they represent distinct validation failures requiring separate resolution paths. [1]

SYN-BEN-301 (name mismatch) requires verifying the intended recipient through the recorded synthetic maintenance workflow and resolving discrepancies without assuming equivalence based on similarity. [2]

SYN-BEN-302 (account format invalid) requires identifying the specific format failure—such as missing prefix, wrong digit count, or nondecimal suffix—against the fictional convention `SYN-ACCT-` followed by four decimal digits, and obtaining the correct reference from verified maintenance evidence. [3]

Both codes require verified correction and revalidation, but the nature of the correction and the validation checks differ: format correction cannot resolve a name mismatch, and vice versa. [3] [2]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-BENEFICIARY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd", "document_id": "SYN-BENEFICIARY", "section_id": "BV-FORMAT", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74", "document_id": "SYN-BENEFICIARY", "section_id": "BV-CHECKS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4", "document_id": "SYN-BENEFICIARY", "section_id": "BV-NAME", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-ESCALATE:0:structural-v1:cc1eff7c335c15d24ac477e5a4b4940be69adaa708cdb0b9d91ba5bb7d64cad4", "document_id": "SYN-BENEFICIARY", "section_id": "BV-ESCALATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-CORRECT:0:structural-v1:f3748f030fd07f4ae32a0e11dbd12aba171efa2e3fe508601276dba0a4aa5445", "document_id": "SYN-BENEFICIARY", "section_id": "BV-CORRECT", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd"}]`

Citation checks: `{"citation_count": 3, "valid_citation_count": 3, "passage_count": 5, "verified_passage_count": 5, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-BENEFICIARY/BV-CHECKS", "SYN-BENEFICIARY/BV-CORRECT", "SYN-BENEFICIARY/BV-ESCALATE", "SYN-BENEFICIARY/BV-FORMAT", "SYN-BENEFICIARY/BV-NAME", "SYN-ERROR-CATALOG/EC-BENEFICIARY"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 1.0, "precision_at_5": 0.6, "mrr_at_5": 1.0, "ndcg_at_5": 0.9674679834891693, "evidence_group_coverage": 1.0, "multi_document_evidence_coverage": null, "required_document_coverage": null, "complete_evidence": true}, "missing_sections": [], "missing_evidence_groups": [], "nonrelevant_sections": ["SYN-BENEFICIARY/BV-CHECKS", "SYN-BENEFICIARY/BV-ESCALATE"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Payment Error-Code Catalog | SYN-ERROR-CATALOG/EC-BENEFICIARY | v1.0.0

Chunk `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856`; offsets 783:947.

> These checks differ: a well-formed account reference may still have a name
> mismatch. Passing either check alone establishes neither payment approval nor settlement.

[2] Beneficiary Validation Runbook | SYN-BENEFICIARY/BV-NAME | v1.0.0

Chunk `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4`; offsets 285:580.

> 1. Compare the submitted name and verified record; record the discrepancy.
> 2. Ask Beneficiary Maintenance to verify the intended recipient through the
>    recorded synthetic maintenance workflow. Do not assume a nickname or different
>    company name is equivalent solely because it looks similar.

Chunk `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4`; offsets 790:867.

> 4. Retain unresolved status until correction and revalidation evidence exist.

[3] Beneficiary Validation Runbook | SYN-BENEFICIARY/BV-FORMAT | v1.0.0

Chunk `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd`; offsets 409:690.

> 1. Compare the supplied reference with this exact synthetic convention.
> 2. Identify the missing prefix, wrong digit count, or nondecimal suffix; do not
>    fabricate digits, pad a number, or guess the destination.
> 3. Obtain the intended reference from verified maintenance evidence.

Chunk `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd`; offsets 691:855.

> 4. Apply `SYN-BENEFICIARY/BV-CORRECT` and revalidate both format and any outstanding
>    name mismatch. A format correction cannot resolve a name mismatch by itself.

### Q13: What does SYN-ACH-299 mean?

Category: Deliberately unanswerable; unknown code; class: unsupported; status: insufficient_evidence; reason: insufficient_evidence.

Service latency: 6.753 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

Insufficient evidence: the meaning of SYN-ACH-299 cannot be established from the available synthetic catalog.

4. For an undocumented identifier, state that its meaning is not established,
   preserve the received text, and route to the relevant operations owner using
   `SYN-EXCEPTION/EX-TRIAGE`. Do not guess from a neighboring code or external code set. [1]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-CLASSIFY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-ACH", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-LOOKUP", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-SCOPE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-STATUS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-NEXT", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586"}]`

Citation checks: `{"citation_count": 1, "valid_citation_count": 1, "passage_count": 1, "verified_passage_count": 1, "all_claim_candidates_cited": null, "issues": []}`

Current gold evidence gaps: `null`

Prior Dense retrieval baseline gaps: `null`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[{"stage": "evidence_sufficiency", "category": "undocumented_identifier", "statement_index": null, "evidence_index": null, "source_id": null, "quote_characters": null, "quote_sha256": null, "matching_source_ids": [], "missing_sections": [], "http_status": null, "field_name": null, "value_type": null, "item_index": null, "exception_type": null}]`

[1] Payment Error-Code Catalog | SYN-ERROR-CATALOG/EC-LOOKUP | v1.0.0

Chunk `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10`; offsets 1172:1418.

> 4. For an undocumented identifier, state that its meaning is not established,
>    preserve the received text, and route to the relevant operations owner using
>    `SYN-EXCEPTION/EX-TRIAGE`. Do not guess from a neighboring code or external code set.

### Q14: Has real customer account 123456 received its payment today?

Category: Deliberately unanswerable; live data; class: unsupported; status: insufficient_evidence; reason: insufficient_evidence.

Service latency: 6.877 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

The retrieved evidence is insufficient to answer this question completely and reliably.

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233", "document_id": "SYN-STATUS", "section_id": "SS-STATES", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-LOOKUP", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe", "document_id": "SYN-STATUS", "section_id": "SS-EVIDENCE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0", "document_id": "SYN-STATUS", "section_id": "SS-STATES", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74", "document_id": "SYN-BENEFICIARY", "section_id": "BV-CHECKS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-ELIGIBILITY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233"}]`

Citation checks: `{"citation_count": 0, "valid_citation_count": 0, "passage_count": 0, "verified_passage_count": 0, "all_claim_candidates_cited": null, "issues": []}`

Current gold evidence gaps: `null`

Prior Dense retrieval baseline gaps: `null`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[{"stage": "evidence_sufficiency", "category": "model_abstention", "statement_index": null, "evidence_index": null, "source_id": null, "quote_characters": null, "quote_sha256": null, "matching_source_ids": [], "missing_sections": [], "http_status": null, "field_name": null, "value_type": null, "item_index": null, "exception_type": null}]`

### Q15: What legally mandated recall deadline applies to every US bank?

Category: Deliberately unanswerable; external policy; class: unsupported; status: insufficient_evidence; reason: insufficient_evidence.

Service latency: 14.278 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

The retrieved evidence is insufficient to answer this question completely and reliably.

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-WIRE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-REQUEST", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-SCOPE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc", "document_id": "SYN-STATUS", "section_id": "SS-RETURNS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-ELIGIBILITY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-TRACK", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321"}]`

Citation checks: `{"citation_count": 0, "valid_citation_count": 0, "passage_count": 0, "verified_passage_count": 0, "all_claim_candidates_cited": null, "issues": []}`

Current gold evidence gaps: `null`

Prior Dense retrieval baseline gaps: `null`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[{"stage": "evidence_sufficiency", "category": "model_abstention", "statement_index": null, "evidence_index": null, "source_id": null, "quote_characters": null, "quote_sha256": null, "matching_source_ids": [], "missing_sections": [], "http_status": null, "field_name": null, "value_type": null, "item_index": null, "exception_type": null}]`

### Q16: Does an acknowledgment of my recall request guarantee recovery?

Category: Factual; related outcomes; class: answerable; status: answered; reason: answered.

Service latency: 6.935 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

An acknowledgment of a recall request does not guarantee recovery, as it only confirms receipt of the request and does not establish that funds have been recovered or that the payment has been reversed. [1] [2] [3]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-TRACK", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc", "document_id": "SYN-STATUS", "section_id": "SS-RETURNS", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-WIRE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-REQUEST", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa", "document_id": "SYN-WIRE-RECALL", "section_id": "WR-SCOPE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-CLASSIFY", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc"}]`

Citation checks: `{"citation_count": 3, "valid_citation_count": 3, "passage_count": 3, "verified_passage_count": 3, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ACH-RETURNS/AR-CLASSIFY", "SYN-ERROR-CATALOG/EC-WIRE", "SYN-STATUS/SS-RETURNS", "SYN-WIRE-RECALL/WR-REQUEST", "SYN-WIRE-RECALL/WR-SCOPE", "SYN-WIRE-RECALL/WR-TRACK"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 1.0, "precision_at_5": 0.4, "mrr_at_5": 1.0, "ndcg_at_5": 1.0, "evidence_group_coverage": 1.0, "multi_document_evidence_coverage": null, "required_document_coverage": null, "complete_evidence": true}, "missing_sections": [], "missing_evidence_groups": [], "nonrelevant_sections": ["SYN-ERROR-CATALOG/EC-WIRE", "SYN-WIRE-RECALL/WR-REQUEST", "SYN-WIRE-RECALL/WR-SCOPE"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Wire Recall SOP | SYN-WIRE-RECALL/WR-TRACK | v1.0.0

Chunk `SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b`; offsets 258:355.

> ACKNOWLEDGED | Response referencing the request | Receipt acknowledged; recovery not established.

[2] Settlement and Payment Status Guide | SYN-STATUS/SS-RETURNS | v1.0.0

Chunk `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc`; offsets 407:581.

> A wire recall acknowledgment confirms receipt of a recovery request only. It
> does not establish returned funds, invalidate earlier settlement evidence, or
> guarantee recovery.

[3] Payment Error-Code Catalog | SYN-ERROR-CATALOG/EC-WIRE | v1.0.0

Chunk `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321`; offsets 671:797.

> A pending response is neither a decline nor proof of recovery. Request receipt
> and recovered funds require different evidence.

### Q19: What did the recall procedure require in 2024?

Category: Unanswerable historical scope; class: unsupported; status: insufficient_evidence; reason: policy_period_unsupported.

Service latency: 5.535 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

No applicable document version supports the requested policy period; current policy cannot be substituted for historical evidence.

Retrieved sources: `[]`

Citation checks: `{"citation_count": 0, "valid_citation_count": 0, "passage_count": 0, "verified_passage_count": 0, "all_claim_candidates_cited": null, "issues": []}`

Current gold evidence gaps: `null`

Prior Dense retrieval baseline gaps: `null`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[{"stage": "temporal_applicability", "category": "no_applicable_version", "statement_index": null, "evidence_index": null, "source_id": null, "quote_characters": null, "quote_sha256": null, "matching_source_ids": [], "missing_sections": [], "http_status": null, "field_name": null, "value_type": null, "item_index": null, "exception_type": null}]`

### Q20: Which evidence is required to close a suspected duplicate case?

Category: Simple factual; class: answerable; status: answered; reason: answered.

Service latency: 4.409 seconds. Correct disposition: True (status only).

Synthetic educational material — not an actual bank policy.

To close a suspected duplicate case, the required evidence includes a documented comparison of original obligation/reference, rail, amount/currency, synthetic payee, instruction timestamps, release references, and confirmed lifecycle outcomes. [1]

The case must include a documented determination of whether the candidates are distinct obligations or possible repeats, based on the comparison. [1]

A supervisor review of the comparison and outcome must be obtained, with documentation of the reviewer, decision, and supporting references. [1]

The closure record must retain the candidate comparison, determination of distinctness or duplication, each known payment outcome, reconciliation findings, supervisor review, and the recorded decision about further retry preparation. [2]

The closure must be recorded with the reviewer, timestamp, owner, related cases, and communication of the supported outcome, and only if all material evidence and review are present. [2]

Retrieved sources: `[{"source_id": "S1", "chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-EXCEPTION:0:structural-v1:01b318fcb499256886be2be88b7cb4c41e47774ca31d259e875ef9c048cb0591", "document_id": "SYN-ERROR-CATALOG", "section_id": "EC-EXCEPTION", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S2", "chunk_id": "SYN-EXCEPTION:1.0.0:EX-DUPLICATE:0:structural-v1:f7f86f3c9de84a16692fe867b42356b11f93da7e2c21b1977402e37b37975cc5", "document_id": "SYN-EXCEPTION", "section_id": "EX-DUPLICATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S3", "chunk_id": "SYN-EXCEPTION:1.0.0:EX-CLOSE:0:structural-v1:9ff4c852bd956cf181b41bacdc7b4477ddc2b202caab00700bbe3e79921ad3f0", "document_id": "SYN-EXCEPTION", "section_id": "EX-CLOSE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S4", "chunk_id": "SYN-EXCEPTION:1.0.0:EX-EVIDENCE:0:structural-v1:c2158f927546da9c63cad16b0b4ec704ba1719a5ad7e7948db911664ae600ee5", "document_id": "SYN-EXCEPTION", "section_id": "EX-EVIDENCE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S5", "chunk_id": "SYN-ACH-RETURNS:1.0.0:AR-INVESTIGATE:0:structural-v1:e00c017c07104f97160dd2cdd2d564d8ba74c8df6a3dfd85b248c20ab027e557", "document_id": "SYN-ACH-RETURNS", "section_id": "AR-INVESTIGATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "ranked", "linked_from_chunk_id": null}, {"source_id": "S6", "chunk_id": "SYN-EXCEPTION:1.0.0:EX-ESCALATE:0:structural-v1:b6ca345d40c85ef09d4a1e31beb46b17368924d682f5878065e15a95426d71c5", "document_id": "SYN-EXCEPTION", "section_id": "EX-ESCALATE", "document_version": "1.0.0", "effective_date": "2026-10-28", "retrieval_origin": "explicit_reference", "linked_from_chunk_id": "SYN-ERROR-CATALOG:1.0.0:EC-EXCEPTION:0:structural-v1:01b318fcb499256886be2be88b7cb4c41e47774ca31d259e875ef9c048cb0591"}]`

Citation checks: `{"citation_count": 2, "valid_citation_count": 2, "passage_count": 5, "verified_passage_count": 5, "all_claim_candidates_cited": true, "issues": []}`

Current gold evidence gaps: `{"retrieved_sections": ["SYN-ACH-RETURNS/AR-INVESTIGATE", "SYN-ERROR-CATALOG/EC-EXCEPTION", "SYN-EXCEPTION/EX-CLOSE", "SYN-EXCEPTION/EX-DUPLICATE", "SYN-EXCEPTION/EX-ESCALATE", "SYN-EXCEPTION/EX-EVIDENCE"], "missing_relevant_sections": [], "missing_evidence_groups": [], "group_coverage": 1.0}`

Prior Dense retrieval baseline gaps: `{"metrics": {"recall_at_5": 1.0, "precision_at_5": 0.2, "mrr_at_5": 0.3333333333333333, "ndcg_at_5": 0.5, "evidence_group_coverage": 1.0, "multi_document_evidence_coverage": null, "required_document_coverage": 1.0, "complete_evidence": true}, "missing_sections": [], "missing_evidence_groups": [], "nonrelevant_sections": ["SYN-ACH-RETURNS/AR-INVESTIGATE", "SYN-ERROR-CATALOG/EC-EXCEPTION", "SYN-EXCEPTION/EX-DUPLICATE", "SYN-EXCEPTION/EX-EVIDENCE"]}`

Missing-evidence declarations exposed by the service: `[]`

Safe diagnostics: `[]`

[1] Payment Exception Handling SOP | SYN-EXCEPTION/EX-DUPLICATE | v1.0.0

Chunk `SYN-EXCEPTION:1.0.0:EX-DUPLICATE:0:structural-v1:f7f86f3c9de84a16692fe867b42356b11f93da7e2c21b1977402e37b37975cc5`; offsets 410:572.

> 2. Compare original obligation/reference, rail, amount/currency, synthetic payee,
>    instruction timestamps, release references, and confirmed lifecycle outcomes.

Chunk `SYN-EXCEPTION:1.0.0:EX-DUPLICATE:0:structural-v1:f7f86f3c9de84a16692fe867b42356b11f93da7e2c21b1977402e37b37975cc5`; offsets 573:733.

> 3. Ask the rail owner and Reconciliation to resolve missing or inconsistent
>    evidence. Record whether candidates are distinct obligations or possible repeats.

Chunk `SYN-EXCEPTION:1.0.0:EX-DUPLICATE:0:structural-v1:f7f86f3c9de84a16692fe867b42356b11f93da7e2c21b1977402e37b37975cc5`; offsets 734:874.

> 4. Obtain Payment Exceptions supervisor review of the comparison and outcome.
>    Document the reviewer, decision, and supporting references.

[2] Payment Exception Handling SOP | SYN-EXCEPTION/EX-CLOSE | v1.0.0

Chunk `SYN-EXCEPTION:1.0.0:EX-CLOSE:0:structural-v1:9ff4c852bd956cf181b41bacdc7b4477ddc2b202caab00700bbe3e79921ad3f0`; offsets 313:559.

> 3. For suspected duplicates, retain the candidate comparison, distinct-obligation
>    or duplicate determination, each known payment outcome, reconciliation findings,
>    supervisor review, and the recorded decision about further retry preparation.

Chunk `SYN-EXCEPTION:1.0.0:EX-CLOSE:0:structural-v1:9ff4c852bd956cf181b41bacdc7b4477ddc2b202caab00700bbe3e79921ad3f0`; offsets 787:1012.

> 5. Record closure reviewer, timestamp, owner, related cases, and communication
>    of the supported outcome. If material evidence or review is missing, keep the
>    case open or escalated rather than recording resolved closure.


## Recurring SYN-BEN-301 analysis and next actions

Q03 observed status: answered; reason: answered. Compare its current gold gaps, declared missing sections and retrieved catalog text above. Only human scope/completeness review can establish whether abstention was unnecessary.
Status-disposition mismatches: Q07. These are review priorities, not automatic faithfulness judgments.

Complete human claim and completeness sheets before drawing quality conclusions. Preserve this frozen development-set run before any separate prompt/retrieval experiment. Check unsupported instructions, incomplete procedures, unnecessary abstentions and bounded answers. Do not treat this reused development set as held-out validation.

## Limitations

No automatic semantic judge is used. Sentence candidates can contain multiple claims; citation inheritance needs review. A matching quote can be misinterpreted. Missing-evidence declarations include only missing sections exposed by AnswerResult diagnostics, not the raw model's complete required_sections list. Guard clarifications can skip retrieval, correctly resulting in no source hits. Model aliases/provider behavior can change despite frozen code; run hashes identify local inputs only. 18 requests at concurrency one do not establish P95 performance under load or the formal warm-query target. Fixture-dependent cases, held-out paraphrases and broader safety evaluation remain outstanding.

## Commands

From an authenticated PowerShell terminal at repository root:

```powershell
uv run python -m payment_ops.knowledge.evaluate_answers --live
```

The command prints a unique ignored run directory. Review its claims.csv and completeness.csv, then:

```powershell
uv run python -m payment_ops.knowledge.evaluate_answers --review "evaluation/week2/results/answers_development/RUN_DIRECTORY"
```

--review reads saved data only and makes no API calls. It refreshes the saved run report and this report. Without --live/--review, only a pending report is prepared. Credentials remain in the environment.


## Baseline V1 comparison

Same development questions; no independent validation. Human faithfulness remains unmeasured until review.

| Measure | Baseline V1 | Development run |
|---|---:|---:|
| correct dispositions / 18 | 12 | 17 |
| evaluated_questions | 18 | 18 |
| successful_generation_rate | 0.5 | 0.6111111111111112 |
| answerable_response_coverage | 0.6666666666666666 | 0.9166666666666666 |
| invalid_response_count | 0 | 1 |
| invalid_response_frequency | 0.0 | 0.05555555555555555 |
| incomplete_evidence_count | 2 | 0 |
| incomplete_evidence_frequency | 0.1111111111111111 | 0.0 |
| unavailable_count | 0 | 0 |
| citation_membership_validity | 1.0 | 1.0 |
| quote_verification_rate | 1.0 | 1.0 |
| answers_with_all_claim_candidates_cited | 1.0 | 1.0 |