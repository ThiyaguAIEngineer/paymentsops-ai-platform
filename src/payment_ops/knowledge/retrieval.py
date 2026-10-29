"""Independent dense/BM25 retrievers and deterministic reciprocal rank fusion."""

from collections import Counter
from dataclasses import dataclass
import re

from rank_bm25 import BM25Okapi

from payment_ops.knowledge.index import LocalVectorIndex
from payment_ops.knowledge.models import KnowledgeChunk


@dataclass(frozen=True)
class RetrievalHit:
    chunk: KnowledgeChunk
    score: float  # Method-specific ranking score, never answer confidence.
    rank: int
    origin: str = "ranked"
    linked_from_chunk_id: str | None = None


def include_requested_section(hits: tuple[RetrievalHit, ...], catalog: tuple[KnowledgeChunk, ...],
                              reference: str) -> tuple[RetrievalHit, ...]:
    """Bounded exact metadata lookup for an explicitly requested knowledge scope.

    Unlike link following, this has no parent source. Keep that provenance honest.
    Include only a complete single-chunk, single-version section; never truncate it.
    """
    if any(f"{h.chunk.document_id}/{h.chunk.section_id}" == reference for h in hits):
        return hits
    candidates = [c for c in catalog if f"{c.document_id}/{c.section_id}" == reference]
    if len(candidates) != 1:
        return hits
    return (*hits, RetrievalHit(candidates[0], 0.0, len(hits) + 1, "requested_section"))


def follow_explicit_reference(hits: tuple[RetrievalHit, ...], catalog: tuple[KnowledgeChunk, ...],
                              *, max_chunks: int = 2) -> tuple[RetrievalHit, ...]:
    """One hop, ONE additional referenced section, at most two additional chunks.

Seed rank takes precedence; within a seed prefer its own document's procedures.
Only literal document/section references from original seed text may resolve.
No recursion, semantic search, gold labels, or additional provider calls. Linked
scores are 0 placeholders, explicitly not cosine/BM25 scores; origin is retained.
"""
    if not hits or not catalog:
        return hits
    present = {(h.chunk.document_id, h.chunk.section_id) for h in hits}
    available = {}
    for chunk in catalog:
        available.setdefault((chunk.document_id, chunk.section_id), []).append(chunk)
    for seed in hits:
        references = list(dict.fromkeys(re.findall(r"\b(SYN-[A-Z]+(?:-[A-Z]+)*)/([A-Z]{2}-[A-Z]+)\b", seed.chunk.content)))
        references.sort(key=lambda ref: ref[0] != seed.chunk.document_id)
        for ref in references:
            if ref in present or ref not in available:
                continue
            candidates = sorted(available[ref], key=lambda c: (c.chunk_index, c.chunk_id))
            # Never combine versions, or silently include only part of a section.
            if len({c.document_version for c in candidates}) != 1 or len(candidates) > max_chunks:
                continue
            additions = tuple(RetrievalHit(c, 0.0, len(hits) + i, "explicit_reference", seed.chunk.chunk_id)
                              for i, c in enumerate(candidates, 1))
            return (*hits, *additions)
    return hits


def tokenize(text: str) -> list[str]:
    """Keep hyphenated codes (SYN-BEN-301, POPS-WIRE-104) as whole tokens."""
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


def _validate_k(k: int) -> None:
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")


class DenseRetriever:
    def __init__(self, index: LocalVectorIndex):
        self.index = index

    def retrieve(self, query: str, k: int = 5) -> tuple[RetrievalHit, ...]:
        _validate_k(k)
        return tuple(RetrievalHit(c, score, rank) for rank, (c, score)
                     in enumerate(self.index.search(query, k), 1))


class BM25Retriever:
    def __init__(self, chunks: tuple[KnowledgeChunk, ...]):
        if not chunks or len({c.chunk_id for c in chunks}) != len(chunks):
            raise ValueError("BM25 requires nonempty chunks with unique IDs")
        self.chunks = chunks
        self.tokens = [tokenize(c.content) for c in chunks]
        if any(not tokens for tokens in self.tokens):
            raise ValueError("BM25 chunk contains no searchable tokens")
        self.index = BM25Okapi(self.tokens, k1=1.5, b=0.75)

    def retrieve(self, query: str, k: int = 5) -> tuple[RetrievalHit, ...]:
        _validate_k(k)
        tokens = tokenize(query)
        if not tokens:
            return ()
        scores = self.index.get_scores(tokens)
        # Do not return unrelated zero-overlap chunks just to fill top-k.
        terms = set(tokens)
        candidates = [(c, float(score)) for c, score, words in
                      zip(self.chunks, scores, self.tokens, strict=True) if terms.intersection(words)]
        candidates.sort(key=lambda item: (-item[1], item[0].chunk_id))
        return tuple(RetrievalHit(c, score, rank) for rank, (c, score)
                     in enumerate(candidates[:k], 1))


def reciprocal_rank_fusion(*rankings: tuple[RetrievalHit, ...], k: int = 5,
                           rank_constant: int = 60) -> tuple[RetrievalHit, ...]:
    """Equal weights; sum 1/(60 + one-based rank), top 5 per input by default.

Deduplicate within each method before assigning rank; sort ties by chunk ID.
Scores have no calibrated confidence interpretation.
"""
    _validate_k(k)
    if isinstance(rank_constant, bool) or not isinstance(rank_constant, int) or rank_constant < 1:
        raise ValueError("rank_constant must be a positive integer")
    scores = Counter()
    chunks = {}
    for ranking in rankings:
        seen = set()
        for hit in ranking:
            identity = hit.chunk.chunk_id
            if identity in chunks and chunks[identity] != hit.chunk:
                raise ValueError("Conflicting content for the same chunk ID")
            if identity in seen:
                continue
            seen.add(identity)
            chunks[identity] = hit.chunk
            scores[identity] += 1 / (rank_constant + len(seen))
    ordered = sorted(scores, key=lambda identity: (-scores[identity], identity))[:k]
    return tuple(RetrievalHit(chunks[identity], scores[identity], rank)
                 for rank, identity in enumerate(ordered, 1))


class HybridRetriever:
    def __init__(self, dense: DenseRetriever, sparse: BM25Retriever):
        self.dense, self.sparse = dense, sparse

    def retrieve(self, query: str, k: int = 5, *, candidate_k: int = 5) -> tuple[RetrievalHit, ...]:
        _validate_k(k)
        _validate_k(candidate_k)
        if not query.strip():
            return ()
        return reciprocal_rank_fusion(self.dense.retrieve(query, candidate_k),
                                      self.sparse.retrieve(query, candidate_k), k=k)
