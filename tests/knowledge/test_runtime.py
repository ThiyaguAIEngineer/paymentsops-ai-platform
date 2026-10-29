"""Offline application composition/lifetime tests; no provider calls."""

import gc
from types import SimpleNamespace

import pytest

from payment_ops.knowledge import runtime
from payment_ops.knowledge.generation import GenerationError
from payment_ops.knowledge.service import KnowledgeService


def resources(monkeypatch):
    events = []
    generation = SimpleNamespace(verify_model=lambda: events.append("verify"), close=lambda: events.append("generation_closed"))
    embedding = SimpleNamespace(cache_identity="offline-test", close=lambda: events.append("embedding_closed"))
    monkeypatch.setattr(runtime, "create_generation_provider", lambda: generation)
    monkeypatch.setattr(runtime, "NebiusEmbeddings", lambda: embedding)
    return generation, embedding, events


def test_factory_reuses_existing_composition_and_document_cache(monkeypatch):
    generation, embedding, events = resources(monkeypatch)
    captured = {}

    def cached(delegate, *, identity, directory):
        captured.update(delegate=delegate, identity=identity, directory=directory)
        return "cached-embeddings-double"

    def index(chunks, embeddings):
        captured.update(chunks=chunks, embeddings=embeddings)
        return SimpleNamespace()

    monkeypatch.setattr(runtime, "CachedEmbeddings", cached)
    monkeypatch.setattr(runtime, "LocalVectorIndex", index)
    service = runtime.create_knowledge_service()
    assert isinstance(service, KnowledgeService) and service.provider is generation
    assert service.default_method == "dense" and set(service.retrievers) == {"dense"}
    assert service.section_catalog == captured["chunks"] and len(service.section_catalog) == 32
    assert captured["delegate"] is embedding and captured["identity"] == "offline-test"
    assert captured["directory"] == runtime.EMBEDDING_CACHE
    assert runtime.DOCUMENTS.is_absolute() and runtime.EMBEDDING_CACHE.is_absolute()
    assert captured["embeddings"] == "cached-embeddings-double"
    assert events == ["verify"]  # No generation/question during construction.
    del service
    gc.collect()
    assert events == ["verify", "generation_closed", "embedding_closed"]


@pytest.mark.parametrize("failure_stage", ["embedding", "index"])
def test_initialization_failure_closes_partial_resources(monkeypatch, failure_stage):
    _, _, events = resources(monkeypatch)
    def fail(*args, **kwargs):
        raise RuntimeError("simulated initialization failure")
    if failure_stage == "embedding":
        monkeypatch.setattr(runtime, "NebiusEmbeddings", fail)
    else:
        monkeypatch.setattr(runtime, "LocalVectorIndex", fail)
    with pytest.raises(RuntimeError):
        runtime.create_knowledge_service()
    assert "generation_closed" in events
    assert ("embedding_closed" in events) == (failure_stage == "index")


def test_missing_key_stops_before_ingestion_or_network(monkeypatch):
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    def forbidden(*args):
        pytest.fail("Missing credentials must stop before corpus/index work")
    monkeypatch.setattr(runtime, "load_documents", forbidden)
    with pytest.raises(GenerationError) as error:
        runtime.create_knowledge_service()
    assert error.value.diagnostic.category == "missing_credentials"
