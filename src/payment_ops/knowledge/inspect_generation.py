"""Live-only generation inspection; never substitutes offline fake answers."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from payment_ops.knowledge.chunking import chunk_documents
from payment_ops.knowledge.embeddings import EmbeddingError, NebiusEmbeddings
from payment_ops.knowledge.generation import GenerationError, create_generation_provider
from payment_ops.knowledge.index import CachedEmbeddings, LocalVectorIndex
from payment_ops.knowledge.ingestion import IngestionError, load_documents
from payment_ops.knowledge.retrieval import BM25Retriever, DenseRetriever, HybridRetriever
from payment_ops.knowledge.service import KnowledgeService


QUESTIONS = (
    ("Factual", "Does ACCEPTED mean a payment has settled?"),
    ("Exact code", "What does SYN-BEN-301 mean, and what should I do first?"),
    ("Paraphrase", "We already sent the wire and want to get the money back. Where do we start?"),
    ("Multi-document", "A status update is delayed and the analyst wants to resend. What checks and escalation apply?"),
    ("Unsupported", "What legally mandated recall deadline applies to every US bank?"),
    ("Ambiguous", "How do I reverse this payment?"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Exact account-visible generation model ID; otherwise NEBIUS_GENERATION_MODEL")
    parser.add_argument("--provider", help="Initial adapter: nebius; otherwise KNOWLEDGE_GENERATION_PROVIDER")
    parser.add_argument("--method", choices=("dense", "bm25", "hybrid"), default="dense")
    parser.add_argument("--embedding-model", default="Qwen/Qwen3-Embedding-8B")
    parser.add_argument("--documents", type=Path, default=Path("data/knowledge/documents"))
    parser.add_argument("--cache", type=Path, default=Path(".cache/payment_ops/embeddings"))
    parser.add_argument("--diagnostics", action="store_true", help="Show allowlisted validation diagnostics and retrieved-source manifest; no raw model output")
    parser.add_argument("--diagnostics-json", type=Path, help="Save secret-free six-scenario statuses, diagnostics, and source manifest (no raw model output)")
    args = parser.parse_args()
    generation = embedding = None
    try:
        generation = create_generation_provider(provider=args.provider, model=args.model)
        generation.verify_model()
        print(f"Generation model listed for this account: {generation.model}; chat compatibility pending first response.")
        chunks = chunk_documents(load_documents(args.documents))
        sparse = BM25Retriever(chunks)
        retrievers = {"bm25": sparse}
        if args.method != "bm25":
            embedding = NebiusEmbeddings(model=args.embedding_model)
            cached = CachedEmbeddings(embedding, identity=embedding.cache_identity, directory=args.cache)
            index = LocalVectorIndex(chunks, cached)
            dense = DenseRetriever(index)
            retrievers.update(dense=dense, hybrid=HybridRetriever(dense, sparse))
            print(f"Embedding model: {embedding.model}; dimensions: {index.dimensions}; chunks: {len(chunks)}.")
        service = KnowledgeService(retrievers, generation, default_method=args.method, section_catalog=chunks)
        failed = False
        diagnostic_rows = []
        by_id = {chunk.chunk_id: chunk for chunk in chunks}
        for category, question in QUESTIONS:
            answer = service.ask(question)
            print(f"\n{category}: {question}\nMethod: {answer.retrieval_method}; status: {answer.status}; reason: {answer.reason_code}")
            print(answer.answer)
            for diagnostic in answer.diagnostics:
                print(f"Diagnostic: {diagnostic.stage}/{diagnostic.category}")
                if args.diagnostics:
                    print(json.dumps(asdict(diagnostic), sort_keys=True))
            manifest = []
            for i, chunk_id in enumerate(dict.fromkeys(answer.retrieved_chunk_ids), 1):
                chunk = by_id[chunk_id]
                manifest.append({"source_id": f"S{i}", "chunk_id": chunk_id,
                                 "document_id": chunk.document_id, "section_id": chunk.section_id,
                                 "document_version": chunk.document_version})
            if args.diagnostics:
                print("Retrieved-source manifest: " + json.dumps(manifest, sort_keys=True))
            diagnostic_rows.append({"scenario": category, "status": answer.status,
                                    "reason_code": answer.reason_code, "prompt_version": answer.prompt_version,
                                    "retrieval_method": answer.retrieval_method,
                                    "diagnostics": [asdict(d) for d in answer.diagnostics], "sources": manifest})
            for c in answer.citations:
                print(f"[{c.number}] {c.document_title} | {c.document_id}/{c.section_id} | v{c.document_version}")
                for passage in c.passages:
                    print(f"    Chunk: {passage.chunk_id}; offsets: {passage.start}:{passage.end}\n    Evidence: {passage.quote}")
            if answer.status == "unavailable" or answer.reason_code == "invalid_response":
                failed = True
        print(f"\nReal chat-completion transport verified: {generation.chat_verified}.")
        print("Citation membership/quote checks are not a faithfulness evaluation; review all live answers.")
        if args.diagnostics_json:
            args.diagnostics_json.parent.mkdir(parents=True, exist_ok=True)
            args.diagnostics_json.write_text(json.dumps({"model": generation.model, "scenarios": diagnostic_rows}, indent=2) + "\n", encoding="utf-8")
            print(f"Safe diagnostics saved: {args.diagnostics_json}")
        return int(failed)
    except GenerationError as exc:
        print(f"Diagnostic: {exc.diagnostic.stage}/{exc.diagnostic.category}")
        print("Live generation inspection could not start. No offline fake answers were substituted.")
        return 1
    except (EmbeddingError, IngestionError, OSError):
        print("Live generation inspection could not start. Check environment credentials, exact model IDs, endpoint, corpus, and cache.")
        print("No offline fake answers were substituted. Live generation remains unverified for this run.")
        return 1
    finally:
        if generation is not None:
            generation.close()
        if embedding is not None:
            embedding.close()


if __name__ == "__main__":
    raise SystemExit(main())
