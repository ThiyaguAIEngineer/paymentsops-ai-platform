# Retrieval infrastructure inspection

## Configuration and verification status

- Python 3.13.14; dependencies installed with uv: langchain-core 1.7.1, httpx 0.28.1, rank-bm25 0.2.2, numpy 2.5.4 (already present, now direct).
- Provider adapter: Nebius Token Factory OpenAI-compatible embeddings API, implementing LangChain Embeddings.
- No model locked: NEBIUS_EMBEDDING_MODEL must identify a model available to the account. The adapter checks GET /models, then validates an embedding response. A listed model alone does not prove embedding capability.
- NEBIUS_API_KEY and NEBIUS_EMBEDDING_MODEL were absent during this inspection. No real embedding API call succeeded or was attempted; real semantic retrieval remains unverified.
- Dense and hybrid implementations were tested only with handcrafted offline test vectors. Those rankings are not retrieval-quality evidence and are not reported below.
- Local index: LangChain InMemoryVectorStore, cosine similarity. No index is persisted.
- Document vector cache: atomic JSON entries keyed by provider endpoint/model/preprocessing identity and exact chunk content; change identity when model revision/settings change. Query vectors are not cached.
- Generated cache path: .cache/payment_ops/embeddings/ (ignored by Git); data/knowledge/indexes/ is also ignored.
- BM25Okapi: k1=1.5, b=0.75; lowercase word tokens retaining complete hyphenated identifiers, including POPS-WIRE-104. The actual corpus uses SYN-* codes; POPS-WIRE-104 is not invented as corpus content.
- Hybrid: top 5 per method, equal-weight RRF with constant 60, score = sum(1 / (60 + one-based rank)); stable-ID deduplication and deterministic tie ordering. No reranker or confidence threshold.

## Run inspection

Offline lexical inspection (no API calls):

```powershell
uv run python -m payment_ops.knowledge.inspect_retrieval
```

For real retrieval, configure NEBIUS_API_KEY and NEBIUS_EMBEDDING_MODEL in the environment, verify the model in the account, then run:

```powershell
uv run python -m payment_ops.knowledge.inspect_retrieval --live
```

Optional NEBIUS_BASE_URL must be HTTPS; the default is https://api.tokenfactory.nebius.com/v1. Do not put keys in command arguments, documentation, or Git. The utility has no fake-embedding fallback.

## Actual BM25 results

Corpus: 32 chunks. Top five requested; return fewer if fewer chunks contain query terms. Scores are ranking scores, not confidence.

### SYN-BEN-301

**Dense:** unavailable (credentials/model not configured).

**Hybrid:** unavailable (no real dense candidates).

| Rank | Document title | Section | BM25 score | Chunk ID |
| --- | --- | --- | --- | --- |
| 1 | Payment Error-Code Catalog | EC-BENEFICIARY | 2.512067 | `SYN-ERROR-CATALOG:1.0.0:EC-BENEFICIARY:0:structural-v1:001bc9033ae40c917ffecfdb2ef85e5a692bf5ab176c5b620888521433820856` |
| 2 | Beneficiary Validation Runbook | BV-NAME | 2.165712 | `SYN-BENEFICIARY:1.0.0:BV-NAME:0:structural-v1:2871931628944323a627e96687424f7be714e7f5930dc6347d6dc08ac979a6a4` |
| 3 | Payment Error-Code Catalog | EC-LOOKUP | 1.631003 | `SYN-ERROR-CATALOG:1.0.0:EC-LOOKUP:0:structural-v1:99ebee6473299e5e00ef98de66d53c72d5289a1036a0dbfbb21ee7547eea1a10` |

### We already sent the wire and want to get the money back. Where do we start?

**Dense:** unavailable (credentials/model not configured).

**Hybrid:** unavailable (no real dense candidates).

| Rank | Document title | Section | BM25 score | Chunk ID |
| --- | --- | --- | --- | --- |
| 1 | Wire Recall SOP | WR-SCOPE | 11.594004 | `SYN-WIRE-RECALL:1.0.0:WR-SCOPE:0:structural-v1:096338a0d016c0684836672fea9d9908360bd4c503728229c3550b705de5b7fa` |
| 2 | ACH Returns Guide | AR-ESCALATE | 8.154018 | `SYN-ACH-RETURNS:1.0.0:AR-ESCALATE:0:structural-v1:47b7139218d3716b40b98327e6f1ffa3ede82d03d75a7f51a3cb1c82522badc4` |
| 3 | ACH Returns Guide | AR-SCOPE | 7.612749 | `SYN-ACH-RETURNS:1.0.0:AR-SCOPE:0:structural-v1:2903d6642e82bf6cde2c9b520fb61edf2f79486c0a6a037f7bea19b946d00e03` |
| 4 | Wire Recall SOP | WR-ESCALATE | 6.551489 | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` |
| 5 | Settlement and Payment Status Guide | SS-STATES | 6.255245 | `SYN-STATUS:1.0.0:SS-STATES:0:structural-v1:0b844a27987147b7b89fc7968b29786955dd179b290c2d404f012b8f508c17d0` |

### A status update is delayed and the analyst wants to resend. What checks and escalation apply?

**Dense:** unavailable (credentials/model not configured).

**Hybrid:** unavailable (no real dense candidates).

| Rank | Document title | Section | BM25 score | Chunk ID |
| --- | --- | --- | --- | --- |
| 1 | Settlement and Payment Status Guide | SS-DELAY | 14.909871 | `SYN-STATUS:1.0.0:SS-DELAY:0:structural-v1:dd54558a2d58ea466015a4b045e91f79b09ad43b66cc0bc3e368b1922ce50b24` |
| 2 | Wire Recall SOP | WR-ELIGIBILITY | 10.833708 | `SYN-WIRE-RECALL:1.0.0:WR-ELIGIBILITY:0:structural-v1:0d881ecaed994165a6e8da15df6f34ad169842a10913ebd09fbdd1067bd4ef63` |
| 3 | Payment Exception Handling SOP | EX-TRIAGE | 10.814151 | `SYN-EXCEPTION:1.0.0:EX-TRIAGE:0:structural-v1:03af006985776c06c349b91d78543456c1e0f3ceb419305769a908a4988c7a33` |
| 4 | Payment Error-Code Catalog | EC-STATUS | 10.270894 | `SYN-ERROR-CATALOG:1.0.0:EC-STATUS:0:structural-v1:e2e739f24caf5f3dc5315736ac8735d1558d21f052645011944daa4dfaf21c35` |
| 5 | Wire Recall SOP | WR-ESCALATE | 9.641472 | `SYN-WIRE-RECALL:1.0.0:WR-ESCALATE:0:structural-v1:132f4b7750610b0edc05322a3529e98a793189c205ed2dc6fb3ddc63d61c7f67` |

## Interpretation and remaining blocker

The exact-code query returns the catalog definition and beneficiary procedure. The wire paraphrase returns recall scope first but also unrelated ACH results; this is a lexical baseline, not a validated semantic result. The delayed-status query returns SS-DELAY first but does not include both EX-DUPLICATE and EX-ESCALATE within top five, so multi-document evidence coverage needs evaluation. No retrieval-quality or answer-faithfulness target is claimed.

Next verification requires real provider access, a supported account-visible embedding model, one successful batch/query call, and rerunning all three inspection methods. No generation or Streamlit integration is implemented.

## Reference contracts

- [Nebius API documentation](https://api.tokenfactory.nebius.com/docs)
- [LangChain Embeddings interface](https://reference.langchain.com/python/langchain-core/embeddings/Embeddings)
- [LangChain InMemoryVectorStore](https://reference.langchain.com/python/langchain-core/vectorstores/in_memory/InMemoryVectorStore)

Compatibility evidence for this implementation is the installed Python 3.13 environment and passing automated suite; provider model availability is still unverified.
