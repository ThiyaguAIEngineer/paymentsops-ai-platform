"""LangChain-compatible Nebius embeddings; no provider calls during import."""

import math
import os

import httpx
from langchain_core.embeddings import Embeddings


class EmbeddingError(ValueError):
    """Configuration, provider, or vector validation failed (no raw provider data)."""


def validate_vectors(vectors, count: int, dimensions: int | None = None) -> list[list[float]]:
    if not isinstance(vectors, (list, tuple)) or len(vectors) != count:
        raise EmbeddingError("Embedding response count does not match input count")
    result = []
    for vector in vectors:
        if not isinstance(vector, (list, tuple)) or not vector:
            raise EmbeddingError("Embedding vector is empty or malformed")
        if dimensions is None:
            dimensions = len(vector)
        if len(vector) != dimensions:
            raise EmbeddingError("Embedding dimension mismatch")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in vector):
            raise EmbeddingError("Embedding vector must contain finite numbers")
        norm = math.hypot(*vector)
        if not math.isfinite(norm) or norm == 0:
            raise EmbeddingError("Embedding vector must have a finite nonzero norm")
        result.append([float(v) for v in vector])
    return result


class NebiusEmbeddings(Embeddings):
    """Small REST adapter using Nebius's OpenAI-compatible embeddings contract.

Model choice is mandatory: account availability must be checked, not assumed.
The model-list check is followed by an embedding request that verifies modality.
Set NEBIUS_API_KEY and NEBIUS_EMBEDDING_MODEL; optionally NEBIUS_BASE_URL.
No key, provider response body, or raw exception is logged or re-raised.
"""

    def __init__(self, *, model: str | None = None, base_url: str | None = None,
                 batch_size: int = 32, client: httpx.Client | None = None):
        key = os.getenv("NEBIUS_API_KEY", "").strip()
        if not key:
            raise EmbeddingError("NEBIUS_API_KEY is required")
        self.model = (model or os.getenv("NEBIUS_EMBEDDING_MODEL", "")).strip()
        if not self.model:
            raise EmbeddingError("NEBIUS_EMBEDDING_MODEL is required; verify account model availability")
        self.base_url = (base_url or os.getenv("NEBIUS_BASE_URL") or
                         "https://api.tokenfactory.nebius.com/v1").rstrip("/")
        if not self.base_url.startswith("https://"):
            raise EmbeddingError("Nebius base URL must use HTTPS")
        if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size < 1:
            raise EmbeddingError("batch_size must be a positive integer")
        self.batch_size = batch_size
        self._headers = {"Authorization": f"Bearer {key}"}
        self._client = client or httpx.Client(timeout=30, follow_redirects=False)
        self._owns_client = client is None
        self._verified = False
        self.dimensions = None

    @property
    def cache_identity(self) -> str:
        # Include preprocessing version; no secret forms part of cache identity.
        return f"nebius:{self.base_url}:{self.model}:raw-input-v1"

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _request(self, method: str, path: str, **kwargs):
        try:
            response = self._client.request(method, self.base_url + path, headers=self._headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError):
            raise EmbeddingError("Nebius request failed; check access, model, and endpoint") from None

    def verify_model(self) -> None:
        try:
            data = self._request("GET", "/models")["data"]
            available = any(item["id"] == self.model for item in data)
        except (KeyError, TypeError):
            raise EmbeddingError("Nebius model-list response is malformed") from None
        if not available:
            raise EmbeddingError("Configured embedding model is not available to this account")
        self._verified = True

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise EmbeddingError("Embedding inputs must be nonempty text")
        if not self._verified:
            self.verify_model()
        vectors = []
        for offset in range(0, len(texts), self.batch_size):
            batch = texts[offset:offset + self.batch_size]
            payload = self._request("POST", "/embeddings", json={
                "model": self.model, "input": batch, "encoding_format": "float",
            })
            try:
                rows = payload["data"]
                if sorted(row["index"] for row in rows) != list(range(len(batch))):
                    raise EmbeddingError("Nebius embedding response indices are invalid")
                ordered = [row["embedding"] for row in sorted(rows, key=lambda row: row["index"])]
            except (KeyError, TypeError):
                raise EmbeddingError("Nebius embedding response is malformed") from None
            checked = validate_vectors(ordered, len(batch), self.dimensions)
            self.dimensions = len(checked[0])
            vectors.extend(checked)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
