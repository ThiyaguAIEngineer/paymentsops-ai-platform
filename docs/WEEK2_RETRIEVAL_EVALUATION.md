# Week 2 retrieval evaluation

Status: **complete-real-embeddings**.

## Configuration

```json
{
  "model": "Qwen/Qwen3-Embedding-8B",
  "provider": "Nebius",
  "expected_dimensions": 4096,
  "actual_dimensions": 4096,
  "top_k": 5,
  "candidate_k_per_method": 5,
  "rrf_constant": 60,
  "rrf_weights": "equal",
  "bm25_k1": 1.5,
  "bm25_b": 0.75,
  "dense_similarity": "cosine",
  "document_count": 6,
  "section_count": 31,
  "chunk_count": 32,
  "chunker_version": "structural-v1",
  "dataset_version": "1.0.0",
  "gold_sha256": "6b229d92923a1737f34a7fe3704f40cba8a78bc9e0680e3724e308a89cf1132d",
  "corpus_sha256": {
    "SYN-ACH-RETURNS": "e8a647d4cc05b0065ac8e159ad4a82e7c50a39d961396966fdaa2f8e4b204a7c",
    "SYN-BENEFICIARY": "74649a098f59ad27f76124e85cc62bce97e61af041cdb17d548d0f18061cca6f",
    "SYN-ERROR-CATALOG": "0089f72ed4c5344b7b26284e793548650534eb79d91b3d2d1bea0eccc217944e",
    "SYN-EXCEPTION": "b1e934ac6a4f966b70e97676c67d13d2e9a0736271a6e647ba311de316fc5ef1",
    "SYN-STATUS": "7e6e4c838557a2409edfdd32e2635c84236dc155181e3c9dcdb1e8d883f57612",
    "SYN-WIRE-RECALL": "c8639fe6349e481e53abeb9324dd251237c98b3d279087997561860796751dc7"
  },
  "chunk_ids": [
    "SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03",
    "SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f",
    "SYN-ACH-RETURNS:1.0.0:AR-INVESTIGATE:0:structural-v1:e00c017c07104f97160dd2cdd2d564d8ba74c8df6a3dfd85b248c20ab027e557",
    "SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb",
    "SYN-ACH-RETURNS:1.0.0:AR-ESCALATE:0:structural-v1:47b7139218d3716b40b98327e6f1ffa3ede82d03d75a7f51a3cb1c82522badc4",
    "SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74",
    "SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4",
    "SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd",
    "SYN-BENEFICIARY:1.0.0:BV-CORRECT:0:structural-v1:f3748f030fd07f4ae32a0e11dbd12aba171efa2e3fe508601276dba0a4aa5445",
    "SYN-BENEFICIARY:1.0.0:BV-ESCALATE:0:structural-v1:cc1eff7c335c15d24ac477e5a4b4940be69adaa708cdb0b9d91ba5bb7d64cad4",
    "SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10",
    "SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321",
    "SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586",
    "SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856",
    "SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35",
    "SYN-ERROR-CATALOG:1.0.0:EC-EXCEPTION:0:structural-v1:01b318fcb499256886be2be88b7cb4c41e47774ca31d259e875ef9c048cb0591",
    "SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33",
    "SYN-EXCEPTION:1.0.0:EX-EVIDENCE:0:structural-v1:c2158f927546da9c63cad16b0b4ec704ba1719a5ad7e7948db911664ae600ee5",
    "SYN-EXCEPTION:1.0.0:EX-DUPLICATE:0:structural-v1:f7f86f3c9de84a16692fe867b42356b11f93da7e2c21b1977402e37b37975cc5",
    "SYN-EXCEPTION:1.0.0:EX-ESCALATE:0:structural-v1:b6ca345d40c85ef09d4a1e31beb46b17368924d682f5878065e15a95426d71c5",
    "SYN-EXCEPTION:1.0.0:EX-CLOSE:0:structural-v1:9ff4c852bd956cf181b41bacdc7b4477ddc2b202caab00700bbe3e79921ad3f0",
    "SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0",
    "SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233",
    "SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe",
    "SYN-STATUS:1.0.0:SS-DELAY:0:structural-v1:dd54558a2d58ea466015a4b045e91f79b09ad43b66cc0bc3e368b1922ce50b24",
    "SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc",
    "SYN-STATUS:1.0.0:SS-ESCALATE:0:structural-v1:324c5b27397826d024568564b8ceba97c1dd167c3e3c7939400421a367282354",
    "SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa",
    "SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63",
    "SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08",
    "SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b",
    "SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67"
  ],
  "python": "3.13.14",
  "packages": {
    "langchain-core": "1.7.1",
    "numpy": "2.5.4",
    "rank-bm25": "0.2.2",
    "httpx": "0.28.1"
  },
  "code_sha256": {
    "__init__.py": "428b64849b2962e1e57edee1ee4c2475d33034948ad746c8fd7a03f15afd363e",
    "chunking.py": "81ac75d6878608a3f7ffe88957a14687f577c6513e2344cad52a044e94b3f62b",
    "embeddings.py": "31a82b5302dad5ca440a38dd382c649992b5731dfced42389aba90f84d896794",
    "evaluate_retrieval.py": "bad17f4d98acf5c35cdeb4e221c7f16aab6bb2b78d545050044fe94a9bd16b0a",
    "evaluation.py": "b28ddbc15384f08ddf3ed28ccfd96cfa6006afd489660e3d2e8f976b8137e698",
    "index.py": "c522f1209da3a5163481bd3e49227ef7ebb8aae7c8745bd0f4bb1129e0ff9c43",
    "ingestion.py": "bc97afcca02fc2e02ec821ce9cf4745e8d17cf3e72c001d3a8d4fbab51034901",
    "inspect_retrieval.py": "3181ac6c0266ef682edb94145fb370ed2b85e09d15a87134f3e4baf47b91cda0",
    "models.py": "2f343caaa92e046c21a34d52ec25e312871ed6546a152ba953fdfdc580b84446",
    "retrieval.py": "24dfd564eea6c6e303be70d8b17c5f2047e82e75d3e07ca0350de18bf68989de"
  }
}
```

The project owner reports a successful Qwen smoke test (4096 dimensions) and three live inspections. That history is separate from measurements produced by this runner.

Gold labels are derived from corpus procedures, not prior rankings. Original question text and categories are preserved in `evaluation/week2/golden_questions.json`. Each record states its relevance justification and required groups. Supporting context is distinguished from directly relevant evidence.

## Question eligibility

| Classification | Count |
| --- | --- |
| ambiguous | 2 |
| answerable | 12 |
| fixture-dependent | 2 |
| unsupported | 4 |

Q09/Q10 require clarification and have no definitive answer labels. Q13/Q14/Q15/Q19 are unsupported (unknown code, live data, legal rule, historical version). Q17/Q18 require archived/conflicting fixtures and are not retrieved or scored in this baseline.

## Metric definitions

Only answerable questions enter macro averages. Relevance is binary at the
document/section level, not document-only or chunk level. Top five chunk slots
are retained in their original ranking: repeated sections earn gain only once
and still consume a slot. Fewer than five hits leaves the other slots empty.

- Recall@5: distinct relevant sections retrieved / all gold relevant sections.
- Precision@5: distinct relevant sections retrieved / 5.
- MRR@5: reciprocal rank of the first relevant section, or zero when none appear.
- NDCG@5: binary unique-section gain discounted by log2(rank + 1), divided by
  ideal gain for min(5, number of relevant sections).
- Evidence-group coverage: fraction of required groups satisfied; all groups
  are required (AND), any listed alternative satisfies a group (OR).
- Multi-document evidence coverage: evidence-group coverage macro-averaged only
  over questions requiring evidence from at least two unavoidable documents.
  Report its question count separately. Document presence alone is insufficient.
- Required-document coverage: fraction of unavoidable documents represented by
  a relevant hit. Complete evidence rate: fraction with every evidence group met.

Alternative sources remain separately relevant for Recall/NDCG: retrieving only
one alternative can satisfy a group without obtaining perfect section recall.
An empty relevance set is undefined (null), never a scored zero or perfect score.
Unsupported, ambiguous, and fixture-dependent cases are excluded from all these
averages. Context sections are never scored as direct answer evidence.

## Method comparison

| Method | Evaluated | Recall@5 | Precision@5 | MRR@5 | NDCG@5 | Multi-doc evidence coverage | Complete evidence rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Dense | 12 | 0.8333 | 0.3000 | 0.7569 | 0.7037 | 0.5000 | 0.7500 |
| BM25 | 12 | 0.6250 | 0.2333 | 0.6042 | 0.5479 | 0.5000 | 0.5833 |
| Hybrid | 12 | 0.6806 | 0.2333 | 0.7667 | 0.6352 | 0.3333 | 0.6667 |

## Per-question results and evidence gaps

### Q01: What details are required to open a wire recall request?

Classification: answerable. WR-REQUEST enumerates recall-specific fields, requester verification, case preparation, and owner review.

Relevant sections: `SYN-WIRE-RECALL/WR-REQUEST`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.791970 |
| 2 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.763550 |
| 3 | Wire Recall SOP | WR-ELIGIBILITY | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` | 0.757775 |
| 4 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.730420 |
| 5 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 0.684755 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.5, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6309297535714575, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-WIRE, SYN-WIRE-RECALL/WR-ELIGIBILITY, SYN-WIRE-RECALL/WR-ESCALATE, SYN-WIRE-RECALL/WR-SCOPE

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 7.651473 |
| 2 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 6.244794 |
| 3 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 5.630510 |
| 4 | Wire Recall SOP | WR-ELIGIBILITY | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` | 5.206175 |
| 5 | Wire Recall SOP | WR-TRACK | `SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b` | 5.091146 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.5, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6309297535714575, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-WIRE, SYN-STATUS/SS-RETURNS, SYN-WIRE-RECALL/WR-ELIGIBILITY, SYN-WIRE-RECALL/WR-TRACK

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.032266 |
| 2 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.032258 |
| 3 | Wire Recall SOP | WR-ELIGIBILITY | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` | 0.031498 |
| 4 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 0.016393 |
| 5 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.015625 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.5, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6309297535714575, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-WIRE, SYN-STATUS/SS-RETURNS, SYN-WIRE-RECALL/WR-ELIGIBILITY, SYN-WIRE-RECALL/WR-SCOPE

### Q02: Does ACCEPTED mean a payment has settled?

Classification: answerable. SS-STATES explicitly distinguishes ACCEPTED from SETTLED and defines matched confirmation/reconciliation evidence.

Relevant sections: `SYN-STATUS/SS-STATES`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 0.664889 |
| 2 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0` | 0.632102 |
| 3 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 0.609711 |
| 4 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.534696 |
| 5 | Payment Error-Code Catalog | EC-STATUS | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` | 0.534192 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-LOOKUP, SYN-ERROR-CATALOG/EC-STATUS, SYN-STATUS/SS-EVIDENCE

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 8.825026 |
| 2 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 8.337119 |
| 3 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0` | 5.125497 |
| 4 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 4.413825 |
| 5 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 3.867474 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-SCOPE, SYN-STATUS/SS-EVIDENCE, SYN-WIRE-RECALL/WR-SCOPE

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 0.032787 |
| 2 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 0.032002 |
| 3 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0` | 0.032002 |
| 4 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.015625 |
| 5 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.015625 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-LOOKUP, SYN-STATUS/SS-EVIDENCE, SYN-WIRE-RECALL/WR-SCOPE

### Q03: What does SYN-BEN-301 mean, and what should I do first?

Classification: answerable. Both the canonical catalog entry and name-mismatch procedure establish SYN-BEN-301 and the initial comparison action; either supports the requested first step.

Relevant sections: `SYN-BENEFICIARY/BV-NAME`, `SYN-ERROR-CATALOG/EC-BENEFICIARY`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 0.450369 |
| 2 | Beneficiary Validation Runbook | BV-FORMAT | `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd` | 0.440322 |
| 3 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.424006 |
| 4 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 0.423362 |
| 5 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 0.415028 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6131471927654584, "precision_at_5": 0.2, "recall_at_5": 0.5, "required_document_coverage": null}`

Missing sections: SYN-BENEFICIARY/BV-NAME

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-CLASSIFY, SYN-BENEFICIARY/BV-CHECKS, SYN-BENEFICIARY/BV-FORMAT, SYN-ERROR-CATALOG/EC-LOOKUP

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 7.531963 |
| 2 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 5.279606 |
| 3 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 4.973795 |
| 4 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 4.295109 |
| 5 | Settlement and Payment Status Guide | SS-DELAY | `SYN-STATUS:1.0.0:SS-DELAY:0:structural-v1:dd54558a2d58ea466015a4b045e91f79b09ad43b66cc0bc3e368b1922ce50b24` | 4.081752 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.25, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.2640681225725909, "precision_at_5": 0.2, "recall_at_5": 0.5, "required_document_coverage": null}`

Missing sections: SYN-BENEFICIARY/BV-NAME

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-LOOKUP, SYN-STATUS/SS-DELAY, SYN-STATUS/SS-EVIDENCE, SYN-STATUS/SS-STATES

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 0.032018 |
| 2 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.032002 |
| 3 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 0.016393 |
| 4 | Beneficiary Validation Runbook | BV-FORMAT | `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd` | 0.016129 |
| 5 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 0.015873 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6131471927654584, "precision_at_5": 0.2, "recall_at_5": 0.5, "required_document_coverage": null}`

Missing sections: SYN-BENEFICIARY/BV-NAME

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-BENEFICIARY/BV-FORMAT, SYN-ERROR-CATALOG/EC-LOOKUP, SYN-STATUS/SS-EVIDENCE, SYN-STATUS/SS-STATES

### Q04: What does SYN-ACH-201 mean? Can I immediately retry?

Classification: answerable. EC-ACH defines account closed and no immediate retry; AR-NEXT identifies the same code and details correction/review gates. These are alternative sufficient sources for this narrow question.

Relevant sections: `SYN-ACH-RETURNS/AR-NEXT`, `SYN-ERROR-CATALOG/EC-ACH`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 0.627329 |
| 2 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 0.609962 |
| 3 | Payment Error-Code Catalog | EC-STATUS | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` | 0.565185 |
| 4 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 0.529188 |
| 5 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.528334 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.5, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6509209298071326, "precision_at_5": 0.4, "recall_at_5": 1.0, "required_document_coverage": null}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-CLASSIFY, SYN-ERROR-CATALOG/EC-LOOKUP, SYN-ERROR-CATALOG/EC-STATUS

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 3.283870 |
| 2 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 3.160907 |
| 3 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 3.007176 |
| 4 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 2.931528 |
| 5 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 2.813976 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.5, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.38685280723454163, "precision_at_5": 0.2, "recall_at_5": 0.5, "required_document_coverage": null}`

Missing sections: SYN-ACH-RETURNS/AR-NEXT

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-CLASSIFY, SYN-STATUS/SS-EVIDENCE, SYN-STATUS/SS-RETURNS, SYN-STATUS/SS-STATES

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 0.032258 |
| 2 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 0.031778 |
| 3 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 0.016393 |
| 4 | Payment Error-Code Catalog | EC-STATUS | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` | 0.015873 |
| 5 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 0.015873 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6131471927654584, "precision_at_5": 0.2, "recall_at_5": 0.5, "required_document_coverage": null}`

Missing sections: SYN-ACH-RETURNS/AR-NEXT

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-CLASSIFY, SYN-ERROR-CATALOG/EC-STATUS, SYN-STATUS/SS-RETURNS, SYN-STATUS/SS-STATES

### Q05: We already sent the wire and want to get the money back. Where do we start?

Classification: answerable. Eligibility establishes status/prerequisites and uncertain recovery; request preparation supplies starting case steps and required details.

Relevant sections: `SYN-WIRE-RECALL/WR-ELIGIBILITY`, `SYN-WIRE-RECALL/WR-REQUEST`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.638151 |
| 2 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 0.598041 |
| 3 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.596689 |
| 4 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.593014 |
| 5 | Wire Recall SOP | WR-ELIGIBILITY | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` | 0.576990 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.25, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.5012658353418871, "precision_at_5": 0.4, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-WIRE, SYN-WIRE-RECALL/WR-ESCALATE, SYN-WIRE-RECALL/WR-SCOPE

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 11.594004 |
| 2 | ACH Returns Guide | AR-ESCALATE | `SYN-ACH-RETURNS:1.0.0:AR-ESCALATE:0:structural-v1:47b7139218d3716b40b98327e6f1ffa3ede82d03d75a7f51a3cb1c82522badc4` | 8.154018 |
| 3 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 7.612749 |
| 4 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 6.551489 |
| 5 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0` | 6.255245 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.0, "mrr_at_5": 0.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.0, "precision_at_5": 0.0, "recall_at_5": 0.0, "required_document_coverage": 0.0}`

Missing sections: SYN-WIRE-RECALL/WR-ELIGIBILITY, SYN-WIRE-RECALL/WR-REQUEST

Missing required groups: evidence-1, evidence-2

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-ESCALATE, SYN-ACH-RETURNS/AR-SCOPE, SYN-STATUS/SS-STATES, SYN-WIRE-RECALL/WR-ESCALATE, SYN-WIRE-RECALL/WR-SCOPE

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.032787 |
| 2 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 0.031754 |
| 3 | ACH Returns Guide | AR-ESCALATE | `SYN-ACH-RETURNS:1.0.0:AR-ESCALATE:0:structural-v1:47b7139218d3716b40b98327e6f1ffa3ede82d03d75a7f51a3cb1c82522badc4` | 0.016129 |
| 4 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 0.015873 |
| 5 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.015873 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.0, "mrr_at_5": 0.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.0, "precision_at_5": 0.0, "recall_at_5": 0.0, "required_document_coverage": 0.0}`

Missing sections: SYN-WIRE-RECALL/WR-ELIGIBILITY, SYN-WIRE-RECALL/WR-REQUEST

Missing required groups: evidence-1, evidence-2

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-ESCALATE, SYN-ACH-RETURNS/AR-SCOPE, SYN-ERROR-CATALOG/EC-WIRE, SYN-WIRE-RECALL/WR-ESCALATE, SYN-WIRE-RECALL/WR-SCOPE

### Q06: The payee label differs from the account holder. How do I resolve it?

Classification: answerable. Name mismatch triage and verified correction/revalidation are distinct required parts of the resolution workflow.

Relevant sections: `SYN-BENEFICIARY/BV-CORRECT`, `SYN-BENEFICIARY/BV-NAME`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Beneficiary Validation Runbook | BV-NAME | `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4` | 0.702824 |
| 2 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 0.591828 |
| 3 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 0.563972 |
| 4 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.542081 |
| 5 | Beneficiary Validation Runbook | BV-ESCALATE | `SYN-BENEFICIARY:1.0.0:BV-ESCALATE:0:structural-v1:cc1eff7c335c15d24ac477e5a4b4940be69adaa708cdb0b9d91ba5bb7d64cad4` | 0.541885 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.5, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6131471927654584, "precision_at_5": 0.2, "recall_at_5": 0.5, "required_document_coverage": 1.0}`

Missing sections: SYN-BENEFICIARY/BV-CORRECT

Missing required groups: evidence-2

Nonrelevant sections occupying top-five slots: SYN-BENEFICIARY/BV-CHECKS, SYN-BENEFICIARY/BV-ESCALATE, SYN-ERROR-CATALOG/EC-BENEFICIARY, SYN-ERROR-CATALOG/EC-LOOKUP

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Beneficiary Validation Runbook | BV-NAME | `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4` | 12.147230 |
| 2 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 7.484234 |
| 3 | Beneficiary Validation Runbook | BV-FORMAT | `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd` | 6.948100 |
| 4 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 5.987820 |
| 5 | ACH Returns Guide | AR-INVESTIGATE | `SYN-ACH-RETURNS:1.0.0:AR-INVESTIGATE:0:structural-v1:e00c017c07104f97160dd2cdd2d564d8ba74c8df6a3dfd85b248c20ab027e557` | 5.497010 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.5, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6131471927654584, "precision_at_5": 0.2, "recall_at_5": 0.5, "required_document_coverage": 1.0}`

Missing sections: SYN-BENEFICIARY/BV-CORRECT

Missing required groups: evidence-2

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-INVESTIGATE, SYN-ACH-RETURNS/AR-NEXT, SYN-BENEFICIARY/BV-CHECKS, SYN-BENEFICIARY/BV-FORMAT

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Beneficiary Validation Runbook | BV-NAME | `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4` | 0.032787 |
| 2 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 0.032002 |
| 3 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 0.016129 |
| 4 | Beneficiary Validation Runbook | BV-FORMAT | `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd` | 0.015873 |
| 5 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 0.015625 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.5, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.6131471927654584, "precision_at_5": 0.2, "recall_at_5": 0.5, "required_document_coverage": 1.0}`

Missing sections: SYN-BENEFICIARY/BV-CORRECT

Missing required groups: evidence-2

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-NEXT, SYN-BENEFICIARY/BV-CHECKS, SYN-BENEFICIARY/BV-FORMAT, SYN-ERROR-CATALOG/EC-BENEFICIARY

### Q07: A status update is delayed and the analyst wants to resend. What checks and escalation apply?

Classification: answerable. Status investigation, duplicate comparison/review, and escalation ownership/handoff each supply distinct operational evidence. A cross-reference alone does not substitute for the target procedure.

Relevant sections: `SYN-EXCEPTION/EX-DUPLICATE`, `SYN-EXCEPTION/EX-ESCALATE`, `SYN-STATUS/SS-DELAY`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-DELAY | `SYN-STATUS:1.0.0:SS-DELAY:0:structural-v1:dd54558a2d58ea466015a4b045e91f79b09ad43b66cc0bc3e368b1922ce50b24` | 0.773694 |
| 2 | Payment Error-Code Catalog | EC-STATUS | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` | 0.754776 |
| 3 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 0.616924 |
| 4 | Payment Exception Handling SOP | EX-ESCALATE | `SYN-EXCEPTION:1.0.0:EX-ESCALATE:0:structural-v1:b6ca345d40c85ef09d4a1e31beb46b17368924d682f5878065e15a95426d71c5` | 0.591017 |
| 5 | Settlement and Payment Status Guide | SS-ESCALATE | `SYN-STATUS:1.0.0:SS-ESCALATE:0:structural-v1:324c5b27397826d024568564b8ceba97c1dd167c3e3c7939400421a367282354` | 0.576759 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.6666666666666666, "mrr_at_5": 1.0, "multi_document_evidence_coverage": 0.6666666666666666, "ndcg_at_5": 0.6713860725233041, "precision_at_5": 0.4, "recall_at_5": 0.6666666666666666, "required_document_coverage": 1.0}`

Missing sections: SYN-EXCEPTION/EX-DUPLICATE

Missing required groups: evidence-2

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-STATUS, SYN-STATUS/SS-ESCALATE, SYN-WIRE-RECALL/WR-ESCALATE

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-DELAY | `SYN-STATUS:1.0.0:SS-DELAY:0:structural-v1:dd54558a2d58ea466015a4b045e91f79b09ad43b66cc0bc3e368b1922ce50b24` | 14.909871 |
| 2 | Wire Recall SOP | WR-ELIGIBILITY | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` | 10.833708 |
| 3 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 10.814151 |
| 4 | Payment Error-Code Catalog | EC-STATUS | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` | 10.270894 |
| 5 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 9.641472 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.3333333333333333, "mrr_at_5": 1.0, "multi_document_evidence_coverage": 0.3333333333333333, "ndcg_at_5": 0.46927872602275644, "precision_at_5": 0.2, "recall_at_5": 0.3333333333333333, "required_document_coverage": 0.5}`

Missing sections: SYN-EXCEPTION/EX-DUPLICATE, SYN-EXCEPTION/EX-ESCALATE

Missing required groups: evidence-2, evidence-3

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-STATUS, SYN-EXCEPTION/EX-TRIAGE, SYN-WIRE-RECALL/WR-ELIGIBILITY, SYN-WIRE-RECALL/WR-ESCALATE

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-DELAY | `SYN-STATUS:1.0.0:SS-DELAY:0:structural-v1:dd54558a2d58ea466015a4b045e91f79b09ad43b66cc0bc3e368b1922ce50b24` | 0.032787 |
| 2 | Payment Error-Code Catalog | EC-STATUS | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` | 0.031754 |
| 3 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 0.031258 |
| 4 | Wire Recall SOP | WR-ELIGIBILITY | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` | 0.016129 |
| 5 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 0.015873 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.3333333333333333, "mrr_at_5": 1.0, "multi_document_evidence_coverage": 0.3333333333333333, "ndcg_at_5": 0.46927872602275644, "precision_at_5": 0.2, "recall_at_5": 0.3333333333333333, "required_document_coverage": 0.5}`

Missing sections: SYN-EXCEPTION/EX-DUPLICATE, SYN-EXCEPTION/EX-ESCALATE

Missing required groups: evidence-2, evidence-3

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-STATUS, SYN-EXCEPTION/EX-TRIAGE, SYN-WIRE-RECALL/WR-ELIGIBILITY, SYN-WIRE-RECALL/WR-ESCALATE

### Q08: An ACH return cites invalid account details. What correction and case evidence are needed?

Classification: answerable. Return-specific retry gates, verified correction/revalidation, and full common case fields are separately required.

Relevant sections: `SYN-ACH-RETURNS/AR-NEXT`, `SYN-BENEFICIARY/BV-CORRECT`, `SYN-EXCEPTION/EX-EVIDENCE`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 0.788872 |
| 2 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 0.703643 |
| 3 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 0.697812 |
| 4 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 0.692336 |
| 5 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 0.660055 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.3333333333333333, "mrr_at_5": 0.5, "multi_document_evidence_coverage": 0.3333333333333333, "ndcg_at_5": 0.2960819109658652, "precision_at_5": 0.2, "recall_at_5": 0.3333333333333333, "required_document_coverage": 0.3333333333333333}`

Missing sections: SYN-BENEFICIARY/BV-CORRECT, SYN-EXCEPTION/EX-EVIDENCE

Missing required groups: evidence-2, evidence-3

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-CLASSIFY, SYN-ACH-RETURNS/AR-SCOPE, SYN-ERROR-CATALOG/EC-ACH, SYN-STATUS/SS-RETURNS

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 9.365522 |
| 2 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 8.208915 |
| 3 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 8.095964 |
| 4 | Beneficiary Validation Runbook | BV-FORMAT | `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd` | 6.508066 |
| 5 | Payment Exception Handling SOP | EX-EVIDENCE | `SYN-EXCEPTION:1.0.0:EX-EVIDENCE:0:structural-v1:c2158f927546da9c63cad16b0b4ec704ba1719a5ad7e7948db911664ae600ee5` | 5.771523 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.6666666666666666, "mrr_at_5": 0.5, "multi_document_evidence_coverage": 0.6666666666666666, "ndcg_at_5": 0.4776237035032179, "precision_at_5": 0.4, "recall_at_5": 0.6666666666666666, "required_document_coverage": 0.6666666666666666}`

Missing sections: SYN-BENEFICIARY/BV-CORRECT

Missing required groups: evidence-2

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-CLASSIFY, SYN-BENEFICIARY/BV-FORMAT, SYN-ERROR-CATALOG/EC-ACH

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 0.032787 |
| 2 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 0.032258 |
| 3 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 0.031498 |
| 4 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 0.015873 |
| 5 | Beneficiary Validation Runbook | BV-FORMAT | `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd` | 0.015625 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.3333333333333333, "mrr_at_5": 0.5, "multi_document_evidence_coverage": 0.3333333333333333, "ndcg_at_5": 0.2960819109658652, "precision_at_5": 0.2, "recall_at_5": 0.3333333333333333, "required_document_coverage": 0.3333333333333333}`

Missing sections: SYN-BENEFICIARY/BV-CORRECT, SYN-EXCEPTION/EX-EVIDENCE

Missing required groups: evidence-2, evidence-3

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-CLASSIFY, SYN-ACH-RETURNS/AR-SCOPE, SYN-BENEFICIARY/BV-FORMAT, SYN-ERROR-CATALOG/EC-ACH

### Q09: How do I reverse this payment?

Classification: ambiguous. Rail and release status are absent; WR-SCOPE, AR-SCOPE, and SS-STATES provide disambiguation context, not a definitive procedure for this unspecified payment.

Relevant sections: None (unscored).

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.528430 |
| 2 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.490094 |
| 3 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 0.461296 |
| 4 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.454556 |
| 5 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 0.443316 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 4.343451 |
| 2 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 3.989799 |
| 3 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 2.332594 |
| 4 | Beneficiary Validation Runbook | BV-ESCALATE | `SYN-BENEFICIARY:1.0.0:BV-ESCALATE:0:structural-v1:cc1eff7c335c15d24ac477e5a4b4940be69adaa708cdb0b9d91ba5bb7d64cad4` | 2.075161 |
| 5 | Settlement and Payment Status Guide | SS-ESCALATE | `SYN-STATUS:1.0.0:SS-ESCALATE:0:structural-v1:324c5b27397826d024568564b8ceba97c1dd167c3e3c7939400421a367282354` | 2.005383 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.032787 |
| 2 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 0.031514 |
| 3 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.031498 |
| 4 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.016129 |
| 5 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 0.015873 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

### Q10: It failed. Should I retry?

Classification: ambiguous. EX-TRIAGE and EC-LOOKUP require exact error, rail, and status before action; unspecified failure cannot justify retry.

Relevant sections: None (unscored).

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 0.481333 |
| 2 | Payment Error-Code Catalog | EC-STATUS | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` | 0.474809 |
| 3 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 0.471519 |
| 4 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.468923 |
| 5 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 0.461549 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 2.656928 |
| 2 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 2.149207 |
| 3 | ACH Returns Guide | AR-ESCALATE | `SYN-ACH-RETURNS:1.0.0:AR-ESCALATE:0:structural-v1:47b7139218d3716b40b98327e6f1ffa3ede82d03d75a7f51a3cb1c82522badc4` | 2.094923 |
| 4 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 1.605275 |
| 5 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 1.178043 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 0.032018 |
| 2 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 0.031778 |
| 3 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 0.016129 |
| 4 | Payment Error-Code Catalog | EC-STATUS | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` | 0.016129 |
| 5 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 0.015873 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

### Q11: How does a recall differ from cancellation before release?

Classification: answerable. WR-SCOPE directly defines both recall and pre-release cancellation, including their status boundary; SS-STATES is supporting context rather than necessary additional evidence.

Relevant sections: `SYN-WIRE-RECALL/WR-SCOPE`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.756488 |
| 2 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.635934 |
| 3 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.622432 |
| 4 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 0.608189 |
| 5 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 0.586734 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-SCOPE, SYN-ERROR-CATALOG/EC-WIRE, SYN-STATUS/SS-RETURNS, SYN-WIRE-RECALL/WR-REQUEST

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 8.437605 |
| 2 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 6.137328 |
| 3 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 4.479411 |
| 4 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 4.115520 |
| 5 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 4.043553 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-BENEFICIARY, SYN-EXCEPTION/EX-TRIAGE, SYN-STATUS/SS-RETURNS, SYN-STATUS/SS-STATES

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.032787 |
| 2 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 0.031250 |
| 3 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.016129 |
| 4 | Payment Exception Handling SOP | EX-TRIAGE | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` | 0.016129 |
| 5 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 0.015873 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-BENEFICIARY, SYN-ERROR-CATALOG/EC-WIRE, SYN-EXCEPTION/EX-TRIAGE, SYN-STATUS/SS-RETURNS

### Q12: Is SYN-BEN-302 handled the same way as SYN-BEN-301?

Classification: answerable. EC-BENEFICIARY compares both meanings and initial actions in one table. Alternatively BV-NAME and BV-FORMAT together supply the two handling branches. The catalog alone can satisfy both groups; additional sections are not inherently required.

Relevant sections: `SYN-BENEFICIARY/BV-FORMAT`, `SYN-BENEFICIARY/BV-NAME`, `SYN-ERROR-CATALOG/EC-BENEFICIARY`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 0.460942 |
| 2 | Beneficiary Validation Runbook | BV-FORMAT | `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd` | 0.440285 |
| 3 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 0.436600 |
| 4 | Beneficiary Validation Runbook | BV-NAME | `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4` | 0.433308 |
| 5 | Beneficiary Validation Runbook | BV-ESCALATE | `SYN-BENEFICIARY:1.0.0:BV-ESCALATE:0:structural-v1:cc1eff7c335c15d24ac477e5a4b4940be69adaa708cdb0b9d91ba5bb7d64cad4` | 0.426471 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.9674679834891693, "precision_at_5": 0.6, "recall_at_5": 1.0, "required_document_coverage": null}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-BENEFICIARY/BV-CHECKS, SYN-BENEFICIARY/BV-ESCALATE

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-TRACK | `SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b` | 6.406468 |
| 2 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 6.115832 |
| 3 | Beneficiary Validation Runbook | BV-NAME | `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4` | 5.863585 |
| 4 | Beneficiary Validation Runbook | BV-FORMAT | `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd` | 4.458639 |
| 5 | ACH Returns Guide | AR-NEXT | `SYN-ACH-RETURNS:1.0.0:AR-NEXT:0:structural-v1:ba63e364641691c2d9aa92d2ceb0d2d0c4df065bacbb73c669327fe9bce645cb` | 4.103879 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.5, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.7328286204777911, "precision_at_5": 0.6, "recall_at_5": 1.0, "required_document_coverage": null}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-NEXT, SYN-WIRE-RECALL/WR-TRACK

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-BENEFICIARY | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` | 0.032522 |
| 2 | Beneficiary Validation Runbook | BV-FORMAT | `SYN-BENEFICIARY:1.0.0:BV-FORMAT:0:structural-v1:6fc5850e12345ded3e0a0521d65a043873872e2926d2e6228e379574af6148fd` | 0.031754 |
| 3 | Beneficiary Validation Runbook | BV-NAME | `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4` | 0.031498 |
| 4 | Wire Recall SOP | WR-TRACK | `SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b` | 0.016393 |
| 5 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 0.015873 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.6, "recall_at_5": 1.0, "required_document_coverage": null}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-BENEFICIARY/BV-CHECKS, SYN-WIRE-RECALL/WR-TRACK

### Q13: What does SYN-ACH-299 mean?

Classification: unsupported. SYN-ACH-299 is absent from the eight-code catalog. EC-LOOKUP supports unknown-code handling only, not an invented meaning.

Relevant sections: None (unscored).

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 0.530655 |
| 2 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 0.520755 |
| 3 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.501339 |
| 4 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 0.486322 |
| 5 | Payment Error-Code Catalog | EC-STATUS | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` | 0.457152 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 3.283870 |
| 2 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 2.931528 |
| 3 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 1.912366 |
| 4 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 1.756659 |
| 5 | ACH Returns Guide | AR-INVESTIGATE | `SYN-ACH-RETURNS:1.0.0:AR-INVESTIGATE:0:structural-v1:e00c017c07104f97160dd2cdd2d564d8ba74c8df6a3dfd85b248c20ab027e557` | 0.509111 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.031746 |
| 2 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 0.016393 |
| 3 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 0.016393 |
| 4 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 0.016129 |
| 5 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 0.016129 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

### Q14: Has real customer account 123456 received its payment today?

Classification: unsupported. No document contains live customer/account data or transaction access.

Relevant sections: None (unscored).

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 0.480395 |
| 2 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.469965 |
| 3 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 0.454939 |
| 4 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0` | 0.454479 |
| 5 | Beneficiary Validation Runbook | BV-CHECKS | `SYN-BENEFICIARY:1.0.0:BV-CHECKS:0:structural-v1:5e518191c37c70698ec9b4658efd2f47aea8565b5128e9c92d8e4774b128ae74` | 0.446148 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 4.985300 |
| 2 | Beneficiary Validation Runbook | BV-ESCALATE | `SYN-BENEFICIARY:1.0.0:BV-ESCALATE:0:structural-v1:cc1eff7c335c15d24ac477e5a4b4940be69adaa708cdb0b9d91ba5bb7d64cad4` | 3.877866 |
| 3 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 3.802085 |
| 4 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 3.785660 |
| 5 | ACH Returns Guide | AR-CLASSIFY | `SYN-ACH-RETURNS:1.0.0:AR-CLASSIFY:0:structural-v1:14e3b750caaed102ed776b62bc43bf6fb47db672fbe6914b57ca409a3c1c132f` | 3.754166 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-LOOKUP | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` | 0.032522 |
| 2 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 0.031498 |
| 3 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 0.016393 |
| 4 | Beneficiary Validation Runbook | BV-ESCALATE | `SYN-BENEFICIARY:1.0.0:BV-ESCALATE:0:structural-v1:cc1eff7c335c15d24ac477e5a4b4940be69adaa708cdb0b9d91ba5bb7d64cad4` | 0.016129 |
| 5 | Payment Error-Code Catalog | EC-ACH | `SYN-ERROR-CATALOG:1.0.0:EC-ACH:0:structural-v1:78a0c1ef86a21b31562cf91f5cc606602adba2072269d36ccc5f14e33ba63586` | 0.015873 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

### Q15: What legally mandated recall deadline applies to every US bank?

Classification: unsupported. All corpus procedures are fictional and explicitly establish no universal legal recall deadline.

Relevant sections: None (unscored).

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.599157 |
| 2 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.576276 |
| 3 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.558483 |
| 4 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 0.534886 |
| 5 | Wire Recall SOP | WR-ELIGIBILITY | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` | 0.526761 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 4.357174 |
| 2 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 4.000164 |
| 3 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 3.803933 |
| 4 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 3.467428 |
| 5 | ACH Returns Guide | AR-SCOPE | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` | 3.378248 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.032522 |
| 2 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.031746 |
| 3 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.016393 |
| 4 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 0.016129 |
| 5 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 0.015625 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

### Q16: Does an acknowledgment of my recall request guarantee recovery?

Classification: answerable. Both sections explicitly state acknowledgment is receipt only, not guaranteed recovery, and distinguish recovery evidence. They are alternative sufficient sources.

Relevant sections: `SYN-STATUS/SS-RETURNS`, `SYN-WIRE-RECALL/WR-TRACK`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-TRACK | `SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b` | 0.650098 |
| 2 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 0.648399 |
| 3 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.640738 |
| 4 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.628501 |
| 5 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.599663 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.4, "recall_at_5": 1.0, "required_document_coverage": null}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-WIRE, SYN-WIRE-RECALL/WR-REQUEST, SYN-WIRE-RECALL/WR-SCOPE

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 9.896099 |
| 2 | Wire Recall SOP | WR-TRACK | `SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b` | 6.856800 |
| 3 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 4.941551 |
| 4 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 3.947227 |
| 5 | Wire Recall SOP | WR-ELIGIBILITY | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` | 3.578764 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.4, "recall_at_5": 1.0, "required_document_coverage": null}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-STATUS/SS-STATES, SYN-WIRE-RECALL/WR-ELIGIBILITY, SYN-WIRE-RECALL/WR-SCOPE

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 0.032522 |
| 2 | Wire Recall SOP | WR-TRACK | `SYN-WIRE-RECALL:1.0.0:WR-TRACK:0:structural-v1:dff5348a209ba4863c7ba2db36cbd2ccf7a6f009e0291bc8c2eb15813faf2e5b` | 0.032522 |
| 3 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.031258 |
| 4 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.015873 |
| 5 | Settlement and Payment Status Guide | SS-STATES | `SYN-STATUS:1.0.0:SS-STATES:1:structural-v1:9220d99484aeb54e8fa908a1529e6daf042ff0962d4c90210e78719dca9b1233` | 0.015625 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 1.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 1.0, "precision_at_5": 0.4, "recall_at_5": 1.0, "required_document_coverage": null}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-WIRE, SYN-STATUS/SS-STATES, SYN-WIRE-RECALL/WR-SCOPE

### Q17: An archived v0.9 draft says delayed status permits immediate retry; what applies now?

Classification: fixture-dependent. Current SS-DELAY and EX-DUPLICATE prohibit retry under uncertainty, but archived v0.9 evidence and mixed-version fixtures do not exist. Defer the version-handling test.

Relevant sections: None (unscored).

Deferred until isolated evaluation fixtures exist.

### Q18: Two equally current approved excerpts disagree on whether SYN-EXC-501 permits retry. Which should I follow?

Classification: fixture-dependent. No two authoritative current excerpts in the corpus contradict each other on duplicate retry. Controlled contradictory fixtures are required; ordinary current guidance cannot test conflict detection.

Relevant sections: None (unscored).

Deferred until isolated evaluation fixtures exist.

### Q19: What did the recall procedure require in 2024?

Classification: unsupported. Only initial version 1.0.0 effective 2026-10-28 is supplied; no historical 2024 procedure exists.

Relevant sections: None (unscored).

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.547228 |
| 2 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.543749 |
| 3 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.524871 |
| 4 | Settlement and Payment Status Guide | SS-RETURNS | `SYN-STATUS:1.0.0:SS-RETURNS:0:structural-v1:c6c8b80d3b3249dfb2dfabac1a59d94eb6dc329750d2fe7624c109d8c87502dc` | 0.482136 |
| 5 | Wire Recall SOP | WR-ELIGIBILITY | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` | 0.480178 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 7.472539 |
| 2 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 4.948902 |
| 3 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 4.091460 |
| 4 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 3.580506 |
| 5 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 3.303948 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-WIRE | `SYN-ERROR-CATALOG:1.0.0:EC-WIRE:0:structural-v1:772026a893d6bfd8498df73042c7cb287149cd7a2b80a774daeb8ad2830b2321` | 0.032258 |
| 2 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 0.031778 |
| 3 | Wire Recall SOP | WR-SCOPE | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` | 0.031498 |
| 4 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 0.016393 |
| 5 | Settlement and Payment Status Guide | SS-EVIDENCE | `SYN-STATUS:1.0.0:SS-EVIDENCE:0:structural-v1:8f6ec0c8d7879cdacf186dcdeb38c1713b0103d2a31c07693ec04f7b07121afe` | 0.015873 |

Observation only: returned passages are not evidence that this question is answerable. Retrieval ranking cannot measure abstention or clarification accuracy.

### Q20: Which evidence is required to close a suspected duplicate case?

Classification: answerable. EX-CLOSE directly enumerates duplicate-specific closure evidence and supervisor review; EX-DUPLICATE adds investigation context but is not necessary to list closure requirements.

Relevant sections: `SYN-EXCEPTION/EX-CLOSE`

**Dense**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-EXCEPTION | `SYN-ERROR-CATALOG:1.0.0:EC-EXCEPTION:0:structural-v1:01b318fcb499256886be2be88b7cb4c41e47774ca31d259e875ef9c048cb0591` | 0.635367 |
| 2 | Payment Exception Handling SOP | EX-DUPLICATE | `SYN-EXCEPTION:1.0.0:EX-DUPLICATE:0:structural-v1:f7f86f3c9de84a16692fe867b42356b11f93da7e2c21b1977402e37b37975cc5` | 0.620708 |
| 3 | Payment Exception Handling SOP | EX-CLOSE | `SYN-EXCEPTION:1.0.0:EX-CLOSE:0:structural-v1:9ff4c852bd956cf181b41bacdc7b4477ddc2b202caab00700bbe3e79921ad3f0` | 0.597460 |
| 4 | Payment Exception Handling SOP | EX-EVIDENCE | `SYN-EXCEPTION:1.0.0:EX-EVIDENCE:0:structural-v1:c2158f927546da9c63cad16b0b4ec704ba1719a5ad7e7948db911664ae600ee5` | 0.572530 |
| 5 | ACH Returns Guide | AR-INVESTIGATE | `SYN-ACH-RETURNS:1.0.0:AR-INVESTIGATE:0:structural-v1:e00c017c07104f97160dd2cdd2d564d8ba74c8df6a3dfd85b248c20ab027e557` | 0.559043 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.3333333333333333, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.5, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-INVESTIGATE, SYN-ERROR-CATALOG/EC-EXCEPTION, SYN-EXCEPTION/EX-DUPLICATE, SYN-EXCEPTION/EX-EVIDENCE

**BM25**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Exception Handling SOP | EX-ESCALATE | `SYN-EXCEPTION:1.0.0:EX-ESCALATE:0:structural-v1:b6ca345d40c85ef09d4a1e31beb46b17368924d682f5878065e15a95426d71c5` | 5.925594 |
| 2 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 5.918359 |
| 3 | Wire Recall SOP | WR-REQUEST | `SYN-WIRE-RECALL:1.0.0:WR-REQUEST:0:structural-v1:1983dc861e4f3d417b455eaffb1ae6317436cb75944beffdc2289b62e4abfb08` | 5.872960 |
| 4 | ACH Returns Guide | AR-ESCALATE | `SYN-ACH-RETURNS:1.0.0:AR-ESCALATE:0:structural-v1:47b7139218d3716b40b98327e6f1ffa3ede82d03d75a7f51a3cb1c82522badc4` | 5.614664 |
| 5 | Payment Exception Handling SOP | EX-DUPLICATE | `SYN-EXCEPTION:1.0.0:EX-DUPLICATE:0:structural-v1:f7f86f3c9de84a16692fe867b42356b11f93da7e2c21b1977402e37b37975cc5` | 5.613387 |

Metrics: `{"complete_evidence": false, "evidence_group_coverage": 0.0, "mrr_at_5": 0.0, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.0, "precision_at_5": 0.0, "recall_at_5": 0.0, "required_document_coverage": 0.0}`

Missing sections: SYN-EXCEPTION/EX-CLOSE

Missing required groups: evidence-1

Nonrelevant sections occupying top-five slots: SYN-ACH-RETURNS/AR-ESCALATE, SYN-EXCEPTION/EX-DUPLICATE, SYN-EXCEPTION/EX-ESCALATE, SYN-WIRE-RECALL/WR-ESCALATE, SYN-WIRE-RECALL/WR-REQUEST

**Hybrid**

| Rank | Document | Section | Chunk ID | Score |
| --- | --- | --- | --- | --- |
| 1 | Payment Exception Handling SOP | EX-DUPLICATE | `SYN-EXCEPTION:1.0.0:EX-DUPLICATE:0:structural-v1:f7f86f3c9de84a16692fe867b42356b11f93da7e2c21b1977402e37b37975cc5` | 0.031514 |
| 2 | Payment Error-Code Catalog | EC-EXCEPTION | `SYN-ERROR-CATALOG:1.0.0:EC-EXCEPTION:0:structural-v1:01b318fcb499256886be2be88b7cb4c41e47774ca31d259e875ef9c048cb0591` | 0.016393 |
| 3 | Payment Exception Handling SOP | EX-ESCALATE | `SYN-EXCEPTION:1.0.0:EX-ESCALATE:0:structural-v1:b6ca345d40c85ef09d4a1e31beb46b17368924d682f5878065e15a95426d71c5` | 0.016393 |
| 4 | Wire Recall SOP | WR-ESCALATE | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` | 0.016129 |
| 5 | Payment Exception Handling SOP | EX-CLOSE | `SYN-EXCEPTION:1.0.0:EX-CLOSE:0:structural-v1:9ff4c852bd956cf181b41bacdc7b4477ddc2b202caab00700bbe3e79921ad3f0` | 0.015873 |

Metrics: `{"complete_evidence": true, "evidence_group_coverage": 1.0, "mrr_at_5": 0.2, "multi_document_evidence_coverage": null, "ndcg_at_5": 0.38685280723454163, "precision_at_5": 0.2, "recall_at_5": 1.0, "required_document_coverage": 1.0}`

Missing sections: None

Missing required groups: None

Nonrelevant sections occupying top-five slots: SYN-ERROR-CATALOG/EC-EXCEPTION, SYN-EXCEPTION/EX-DUPLICATE, SYN-EXCEPTION/EX-ESCALATE, SYN-WIRE-RECALL/WR-ESCALATE

## Multi-document coverage

- Dense: 2 multi-document questions; group coverage 0.5000. Per-question missing groups are listed above.
- BM25: 2 multi-document questions; group coverage 0.5000. Per-question missing groups are listed above.
- Hybrid: 2 multi-document questions; group coverage 0.3333. Per-question missing groups are listed above.

## Unsupported and ambiguous observations

Q13 asks for an undocumented code, Q14 needs live account access, Q15 asks for a universal legal rule, and Q19 needs a missing historical version. None has direct answer evidence. Q09/Q10 require clarification. Their per-question rankings above are observations only; thematic overlap is not answerability. Actual rankings are available above; no abstention accuracy is inferred.

## Does hybrid improve retrieval?

- recall_at_5: Hybrid minus Dense = -0.1528; Hybrid minus BM25 = +0.0556.
- precision_at_5: Hybrid minus Dense = -0.0667; Hybrid minus BM25 = +0.0000.
- mrr_at_5: Hybrid minus Dense = +0.0097; Hybrid minus BM25 = +0.1625.
- ndcg_at_5: Hybrid minus Dense = -0.0685; Hybrid minus BM25 = +0.0873.
- multi_document_evidence_coverage: Hybrid minus Dense = -0.1667; Hybrid minus BM25 = -0.1667.

Positive deltas are metric-specific improvements, not proof of overall superiority or answer quality. Review regressions and missing evidence in each question before changing parameters.

## Recommended follow-up and limitations

Review measured missing groups and nonrelevant top-five slots before a separate tuning experiment. If group coverage is incomplete, test candidate depth or section-context expansion only after preserving this baseline. Do not assume fusion benefits every question. No retriever parameters were changed here.

This is a small development set, not a held-out benchmark. Binary section labels credit any chunk from a relevant section, which can overstate evidence completeness when that section spans chunks. Required-group coverage mitigates alternative-source interpretation but is still section-level, not claim-level. Model alias stability is provider-controlled; hashes and package versions enable comparison but do not guarantee identical future embeddings. No answer faithfulness, abstention accuracy, legal correctness, or latency target is evaluated. Unsupported questions may retrieve thematically similar text without becoming supported.

## Reproduce

From the repository root, with NEBIUS_API_KEY available in the terminal:

```powershell
uv run python -m payment_ops.knowledge.evaluate_retrieval --live
```

The model is explicitly Qwen/Qwen3-Embedding-8B; the runner requires 4096 dimensions. It reuses .cache/payment_ops/embeddings, embeds each query once, and reuses those dense/sparse candidates for existing RRF fusion. It writes secret-free machine-readable configuration, hashes, scores, ranks, and evidence gaps to evaluation/week2/results/latest.json and refreshes this report. No source passages, credentials, headers, or raw provider errors are serialized. No --live flag creates only a pending report and performs no provider calls.
