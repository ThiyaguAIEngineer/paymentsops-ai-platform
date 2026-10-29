"""Run with uv run python -m payment_ops.knowledge.inspect_retrieval.

Default is offline BM25 only. --live explicitly enables Nebius verification,
real document/query embeddings, and ignored local caching. No fake fallback.
"""

import argparse
from pathlib import Path

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.embeddings import EmbeddingError, NebiusEmbeddings
from payment_ops.knowledge.index import CachedEmbeddings, LocalVectorIndex
from payment_ops.knowledge.ingestion import load_documents
from payment_ops.knowledge.retrieval import BM25Retriever, DenseRetriever, HybridRetriever


QUESTIONS = (
    "SYN-BEN-301",
    "We already sent the wire and want to get the money back. Where do we start?",
    "A status update is delayed and the analyst wants to resend. What checks and escalation apply?",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--documents", type=Path, default=Path("data/knowledge/documents"))
    parser.add_argument("--cache", type=Path, default=Path(".cache/payment_ops/embeddings"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    chunks = chunk_documents(load_documents(args.documents))
    sparse = BM25Retriever(chunks)
    methods = {"BM25": sparse}
    provider = None
    try:
        if args.live:
            try:
                provider = NebiusEmbeddings()
                provider.verify_model()
                cached = CachedEmbeddings(provider, identity=provider.cache_identity, directory=args.cache)
                dense = DenseRetriever(LocalVectorIndex(chunks, cached))
                methods = {"Dense": dense, "BM25": sparse, "Hybrid": HybridRetriever(dense, sparse)}
            except EmbeddingError as exc:
                print(f"Dense/Hybrid unavailable: {exc}. Real semantic retrieval NOT verified.")
        else:
            print("Offline BM25 only. Dense/Hybrid unavailable: real embeddings not requested.")
        print(f"Corpus: {len(chunks)} chunks. RRF: equal weights, constant 60, top 5 per method.")
        for question in QUESTIONS:
            print(f"\nQuestion: {question}")
            for name, retriever in methods.items():
                print(f"{name} top 5:")
                try:
                    hits = retriever.retrieve(question, k=5)
                except EmbeddingError as exc:
                    print(f"Unavailable: {exc}")
                    continue
                for hit in hits:
                    c = hit.chunk
                    print(f"{hit.rank}. {c.document_title} | {c.section_heading} | score={hit.score:.6f}")
                    print(f"   {c.chunk_id}")
    finally:
        if provider is not None:
            provider.close()


if __name__ == "__main__":
    main()
