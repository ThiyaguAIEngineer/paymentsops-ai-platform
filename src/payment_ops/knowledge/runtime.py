"""Application composition only; retrieval and answer contracts stay unchanged."""

from pathlib import Path
from weakref import finalize

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.embeddings import NebiusEmbeddings
from payment_ops.knowledge.generation import create_generation_provider
from payment_ops.knowledge.index import CachedEmbeddings, LocalVectorIndex
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import DenseRetriever
from payment_ops.knowledge.service import KnowledgeService


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCUMENTS = PROJECT_ROOT / "data/knowledge/documents"
EMBEDDING_CACHE = PROJECT_ROOT / ".cache/payment_ops/embeddings"


def _close_clients(generation, embedding) -> None:
    try:
        generation.close()
    finally:
        if embedding is not None:
            embedding.close()


def create_knowledge_service() -> KnowledgeService:
    """Reuse the verified Dense composition; adapters read environment configuration.

    Nothing initializes on import. No payment records, gold labels or UI state
    cross this boundary. Cached document vectors are reused by the existing cache.
    """
    generation = create_generation_provider()
    embedding = None
    try:
        embedding = NebiusEmbeddings()
        chunks = chunk_documents(load_documents(DOCUMENTS))
        generation.verify_model()
        cached = CachedEmbeddings(embedding, identity=embedding.cache_identity, directory=EMBEDDING_CACHE)
        index = LocalVectorIndex(chunks, cached)
        service = KnowledgeService({"dense": DenseRetriever(index)}, generation, section_catalog=chunks)
    except Exception:
        _close_clients(generation, embedding)
        raise
    # Session cache eviction/disconnect releases the service; HTTP clients follow
    # its lifetime without changing the KnowledgeService public interface.
    finalize(service, _close_clients, generation, embedding)
    return service
