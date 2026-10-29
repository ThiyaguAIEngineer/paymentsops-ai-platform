"""Offline infrastructure tests. Fake vectors are NOT semantic-quality evidence."""

from dataclasses import replace
from pathlib import Path

import httpx
from langchain_core.embeddings import Embeddings
import pytest

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.embeddings import EmbeddingError, NebiusEmbeddings, validate_vectors
from payment_ops.knowledge.index import CachedEmbeddings, LocalVectorIndex
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import (
    BM25Retriever, DenseRetriever, HybridRetriever, RetrievalHit, reciprocal_rank_fusion, tokenize,
)


class FakeEmbeddings(Embeddings):
    """Handcrafted ranking fixture, only for unit tests."""

    def __init__(self):
        self.document_calls = []
        self.query_calls = []

    def embed_documents(self, texts):
        self.document_calls.append(list(texts))
        return [[1.0, 0.0] if "alpha" in text else [0.0, 1.0] for text in texts]

    def embed_query(self, text):
        self.query_calls.append(text)
        return [1.0, 0.0]


@pytest.fixture
def chunks():
    directory = Path(__file__).resolve().parents[2] / "data/knowledge/documents"
    original = chunk_documents(load_documents(directory))[0]
    return (
        replace(original, chunk_id="a", content="alpha SYN-BEN-301 name mismatch"),
        replace(original, chunk_id="b", content="beta settlement status delayed"),
        replace(original, chunk_id="c", content="gamma wire recall response pending"),
    )


def test_embedding_interface_dense_ranking_and_metadata(chunks):
    fake = FakeEmbeddings()
    index = LocalVectorIndex(chunks, fake)
    dense = DenseRetriever(index)
    result = dense.retrieve("alpha")
    assert [h.chunk.chunk_id for h in result] == ["a", "b", "c"]
    assert result[0].score == pytest.approx(1.0)
    assert result[0].chunk is chunks[0]
    assert index.store.get_by_ids(["a"])[0].metadata["section_id"] == chunks[0].section_id
    assert len(fake.document_calls) == 1
    dense.retrieve("again")
    assert len(fake.document_calls) == 1


@pytest.mark.parametrize("vectors,count,dim", [
    ([], 1, None), ([[]], 1, None), ([[0, 0]], 1, None),
    ([[1, 2], [1]], 2, None), ([[1, 2]], 1, 3),
    ([[float("nan")]], 1, None), ([[float("inf")]], 1, None),
    ([[True]], 1, None), ([["1"]], 1, None),
])
def test_invalid_vectors(vectors, count, dim):
    with pytest.raises(EmbeddingError):
        validate_vectors(vectors, count, dim)


def test_document_query_dimension_mismatch(chunks):
    fake = FakeEmbeddings()
    index = LocalVectorIndex(chunks, fake)
    fake.embed_query = lambda text: [1, 2, 3]
    with pytest.raises(EmbeddingError, match="dimension"):
        DenseRetriever(index).retrieve("query")


def test_cache_reuse_and_invalidation(tmp_path):
    fake = FakeEmbeddings()
    cache = CachedEmbeddings(fake, identity="provider:model1:settings1", directory=tmp_path)
    assert cache.embed_documents(["alpha", "alpha", "beta"]) == [[1, 0], [1, 0], [0, 1]]
    assert fake.document_calls == [["alpha", "beta"]]
    # New wrapper simulates another run reading the persisted cache.
    again = CachedEmbeddings(fake, identity="provider:model1:settings1", directory=tmp_path)
    again.embed_documents(["alpha", "beta"])
    assert len(fake.document_calls) == 1
    again.embed_documents(["alpha changed"])
    assert len(fake.document_calls) == 2
    CachedEmbeddings(fake, identity="provider:model2:settings1", directory=tmp_path).embed_documents(["alpha"])
    assert len(fake.document_calls) == 3
    assert cache.embed_query("question") == [1, 0]


def test_cache_dimension_and_corruption(tmp_path):
    fake = FakeEmbeddings()
    cache = CachedEmbeddings(fake, identity="fixture", directory=tmp_path)
    cache.embed_documents(["alpha"])
    fake.embed_query = lambda text: [1, 2, 3]
    with pytest.raises(EmbeddingError, match="dimension"):
        cache.embed_query("q")
    next(tmp_path.glob("*.json")).write_text("invalid JSON", encoding="utf-8")
    with pytest.raises(EmbeddingError, match="cache"):
        cache.embed_documents(["alpha"])


def test_bm25_exact_codes_and_tokenization(chunks):
    assert tokenize("POPS-WIRE-104 / `SYN-BEN-301`?") == ["pops-wire-104", "syn-ben-301"]
    sparse = BM25Retriever(chunks)
    assert sparse.retrieve("SYN-BEN-301")[0].chunk is chunks[0]
    assert sparse.retrieve("SYN-BEN-399") == ()
    assert sparse.retrieve("unknownnothing") == ()


def test_real_corpus_exact_lookup():
    directory = Path(__file__).resolve().parents[2] / "data/knowledge/documents"
    chunks = chunk_documents(load_documents(directory))
    results = BM25Retriever(chunks).retrieve("SYN-BEN-301")
    assert results
    assert all("SYN-BEN-301" in h.chunk.content for h in results)
    assert any(h.chunk.section_id == "EC-BENEFICIARY" for h in results)


def test_rrf_math_dedup_ties_and_metadata(chunks):
    a, b, c = chunks
    left = (RetrievalHit(a, .9, 1), RetrievalHit(b, .8, 2), RetrievalHit(a, .7, 3))
    right = (RetrievalHit(b, 5, 1), RetrievalHit(c, 4, 2))
    result = reciprocal_rank_fusion(left, right)
    assert [h.chunk.chunk_id for h in result] == ["b", "a", "c"]
    assert result[0].score == pytest.approx(1/62 + 1/61)
    assert result[1].score == pytest.approx(1/61)
    assert result[0].chunk is b
    assert len({h.chunk.chunk_id for h in result}) == len(result)
    tie = reciprocal_rank_fusion((RetrievalHit(b, 1, 1),), (RetrievalHit(a, 1, 1),))
    assert [h.chunk.chunk_id for h in tie] == ["a", "b"]
    assert reciprocal_rank_fusion(left, right) == result


def test_hybrid_and_empty_queries(chunks):
    fake = FakeEmbeddings()
    dense = DenseRetriever(LocalVectorIndex(chunks, fake))
    sparse = BM25Retriever(chunks)
    hybrid = HybridRetriever(dense, sparse)
    assert hybrid.retrieve("SYN-BEN-301")[0].chunk is chunks[0]
    for method in (dense, sparse, hybrid):
        assert method.retrieve("   ") == ()
    assert fake.query_calls == ["SYN-BEN-301"]


@pytest.mark.parametrize("k", [0, -1, True, 1.5])
def test_bad_k(chunks, k):
    with pytest.raises(ValueError, match="positive integer"):
        BM25Retriever(chunks).retrieve("test", k=k)
    with pytest.raises(ValueError):
        reciprocal_rank_fusion(k=k)


def test_duplicate_empty_and_conflicting_chunks(chunks):
    for build in (BM25Retriever, lambda c: LocalVectorIndex(c, FakeEmbeddings())):
        with pytest.raises(ValueError):
            build(())
        with pytest.raises(ValueError):
            build((chunks[0], chunks[0]))
    with pytest.raises(ValueError, match="Conflicting"):
        reciprocal_rank_fusion((RetrievalHit(chunks[0], 1, 1),),
                               (RetrievalHit(replace(chunks[0], content="different"), 1, 1),))


def test_missing_credentials_and_model(monkeypatch):
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    with pytest.raises(EmbeddingError, match="NEBIUS_API_KEY"):
        NebiusEmbeddings()
    monkeypatch.setenv("NEBIUS_API_KEY", "test-only-not-real")
    monkeypatch.delenv("NEBIUS_EMBEDDING_MODEL", raising=False)
    with pytest.raises(EmbeddingError, match="NEBIUS_EMBEDDING_MODEL"):
        NebiusEmbeddings()


def test_nebius_batch_query_order_and_model_verification(monkeypatch):
    monkeypatch.setenv("NEBIUS_API_KEY", "test-only-not-real")
    calls = []
    def handler(request):
        calls.append(request)
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "fixture-model"}]})
        import json
        texts = json.loads(request.content)["input"]
        return httpx.Response(200, json={"data": [
            {"index": i, "embedding": [float(i + 1), 1.0]} for i in reversed(range(len(texts)))
        ]})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = NebiusEmbeddings(model="fixture-model", client=client, batch_size=2)
        assert provider.embed_documents(["a", "b", "c"]) == [[1, 1], [2, 1], [1, 1]]
        assert provider.embed_query("question") == [1, 1]
        assert len([r for r in calls if r.url.path.endswith("/models")]) == 1
        assert "test-only-not-real" not in provider.cache_identity
        assert provider.dimensions == 2


@pytest.mark.parametrize("mode", ["unavailable", "http", "malformed", "empty", "indices", "network"])
def test_nebius_explicit_sanitized_provider_errors(monkeypatch, mode):
    monkeypatch.setenv("NEBIUS_API_KEY", "test-secret-must-not-leak")
    def handler(request):
        if mode == "network":
            raise httpx.ConnectError("test-secret-must-not-leak", request=request)
        if mode == "http":
            return httpx.Response(401, text="test-secret-must-not-leak")
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "other" if mode == "unavailable" else "fixture"}]})
        payload = {"wrong": []} if mode == "malformed" else {"data": []}
        if mode == "indices":
            payload = {"data": [{"index": 9, "embedding": [1, 2]}]}
        return httpx.Response(200, json=payload)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = NebiusEmbeddings(model="fixture", client=client)
        with pytest.raises(EmbeddingError) as error:
            provider.embed_query("test")
        assert "test-secret-must-not-leak" not in str(error.value)
