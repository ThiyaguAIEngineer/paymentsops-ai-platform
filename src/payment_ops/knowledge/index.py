"""Local LangChain cosine index and content-addressed JSON embedding cache."""

from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore

from payment_ops.knowledge.embeddings import EmbeddingError, validate_vectors
from payment_ops.knowledge.models import KnowledgeChunk


class CachedEmbeddings(Embeddings):
    """Cache document vectors by provider/model/preprocessing identity and input.

Callers must change identity when model revision or embedding settings change.
Query vectors are validated but not persisted. Corrupt cache entries fail
explicitly instead of silently changing retrieval. Atomic writes avoid partial JSON.
"""

    def __init__(self, delegate: Embeddings, *, identity: str, directory: Path | str):
        if not identity.strip():
            raise ValueError("Embedding cache identity is required")
        self.delegate, self.identity = delegate, identity
        self.directory = Path(directory)
        self.dimensions = None

    def _path(self, text: str) -> Path:
        key = sha256(json.dumps([self.identity, text], ensure_ascii=False).encode()).hexdigest()
        return self.directory / f"{key}.json"

    def _check(self, vectors, count):
        result = validate_vectors(vectors, count, self.dimensions)
        if result:
            self.dimensions = len(result[0])
        return result

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if any(not isinstance(t, str) or not t.strip() for t in texts):
            raise EmbeddingError("Embedding inputs must be nonempty text")
        found = {}
        missing = []
        for text in dict.fromkeys(texts):
            path = self._path(text)
            if path.exists():
                try:
                    found[text] = self._check([json.loads(path.read_text(encoding="utf-8"))], 1)[0]
                except (OSError, ValueError, TypeError):
                    raise EmbeddingError("Invalid local embedding cache entry") from None
            else:
                missing.append(text)
        if missing:
            vectors = self._check(self.delegate.embed_documents(missing), len(missing))
            self.directory.mkdir(parents=True, exist_ok=True)
            for text, vector in zip(missing, vectors, strict=True):
                path = self._path(text)
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.directory,
                                                     suffix=".tmp", delete=False) as handle:
                        temporary = Path(handle.name)
                        json.dump(vector, handle, allow_nan=False)
                    os.replace(temporary, path)
                finally:
                    if temporary is not None:
                        temporary.unlink(missing_ok=True)
                found[text] = vector
        return [list(found[text]) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        if not isinstance(text, str) or not text.strip():
            raise EmbeddingError("Query must be nonempty text")
        return self._check([self.delegate.embed_query(text)], 1)[0]


class LocalVectorIndex:
    """In-process cosine similarity over immutable source chunks; no index dump."""

    def __init__(self, chunks: tuple[KnowledgeChunk, ...], embeddings: Embeddings):
        if not chunks:
            raise ValueError("Cannot index an empty corpus")
        self.chunks = {chunk.chunk_id: chunk for chunk in chunks}
        if len(self.chunks) != len(chunks):
            raise ValueError("Duplicate chunk IDs")
        # Always validate arbitrary injected embedding providers too.
        self.embeddings = embeddings
        vectors = validate_vectors(embeddings.embed_documents([c.content for c in chunks]), len(chunks))
        self.dimensions = len(vectors[0])
        # Supported store API receives precomputed vectors via a tiny embedding
        # adapter, so building the store never calls the provider a second time.
        class Precomputed(Embeddings):
            def embed_documents(self, texts):
                return vectors

            def embed_query(self, text):
                raise NotImplementedError("Use the index query method")

        self.store = InMemoryVectorStore(Precomputed())
        documents = []
        for chunk in chunks:
            metadata = asdict(chunk)
            metadata.pop("content")
            metadata["effective_date"] = chunk.effective_date.isoformat()
            documents.append(Document(id=chunk.chunk_id, page_content=chunk.content, metadata=metadata))
        self.store.add_documents(documents, ids=list(self.chunks))

    def search(self, query: str, k: int = 5):
        if not query.strip():
            return []
        if isinstance(k, bool) or not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive integer")
        vector = validate_vectors([self.embeddings.embed_query(query)], 1, self.dimensions)[0]
        # Rank all 32 candidates so cutoff ties are deterministic by stable ID.
        hits = self.store.similarity_search_with_score_by_vector(vector, k=len(self.chunks))
        ranked = [(self.chunks[doc.id], float(score)) for doc, score in hits]
        return sorted(ranked, key=lambda item: (-item[1], item[0].chunk_id))[:k]
