"""
run_ingestion.py — main entry point for the full ingestion pipeline.

Usage:
    python -m ingestion.run_ingestion
    python -m ingestion.run_ingestion --corpus ./corpus --stats-only
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from ingestion.pdf_parser import parse_corpus
from ingestion.chunker import chunk_documents
from ingestion.embedder import embed_chunks, get_collection_stats


def main():
    parser = argparse.ArgumentParser(description="Industrial Knowledge Ingestion Pipeline")
    parser.add_argument("--corpus",      default="./corpus",             help="Path to corpus root directory")
    parser.add_argument("--manifest",    default="./corpus_manifest.csv",help="Path to corpus_manifest.csv")
    parser.add_argument("--chroma-dir",  default="./chroma_db",          help="ChromaDB persist directory")
    parser.add_argument("--chunk-size",  type=int, default=800,          help="Chunk size in characters")
    parser.add_argument("--chunk-overlap",type=int,default=150,          help="Chunk overlap in characters")
    parser.add_argument("--batch-size",  type=int, default=100,          help="Embedding batch size")
    parser.add_argument("--stats-only",  action="store_true",            help="Print collection stats and exit")
    parser.add_argument("--quiet",       action="store_true",            help="Suppress verbose output")
    args = parser.parse_args()

    verbose = not args.quiet

    # Stats-only mode
    if args.stats_only:
        stats = get_collection_stats(args.chroma_dir)
        print(f"ChromaDB collection stats:")
        print(f"  Total chunks indexed: {stats['total_chunks']}")
        print(f"  Chunks by category:")
        for cat, count in sorted(stats["chunks_by_category"].items()):
            print(f"    {cat:30s}: {count:5d} chunks")
        return

    # Validate required API keys
    if not os.getenv("GOOGLE_API_KEY"):
        print("[ERROR] GOOGLE_API_KEY not set. Get a free key at https://aistudio.google.com/apikey")
        sys.exit(1)
    if not os.getenv("GROQ_API_KEY"):
        print("[ERROR] GROQ_API_KEY not set. Get a free key at https://console.groq.com")
        sys.exit(1)

    print("=" * 60)
    print("  Industrial Knowledge Intelligence — Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Parse
    print("\n[1/3] Parsing PDFs from corpus...")
    docs = parse_corpus(
        corpus_root=args.corpus,
        manifest_path=args.manifest,
        verbose=verbose,
    )
    total_chars = sum(len(d.text) for d in docs)
    scanned = sum(1 for d in docs if d.is_scanned)
    print(f"\n  Parsed: {len(docs)} documents")
    print(f"  Total text: {total_chars:,} characters")
    print(f"  Scanned/empty PDFs (skipped): {scanned}")

    # Step 2: Chunk
    print("\n[2/3] Chunking documents...")
    chunks = chunk_documents(
        docs,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        verbose=verbose,
    )
    print(f"\n  Total chunks: {len(chunks)}")

    # Step 3: Embed + Index
    print("\n[3/3] Embedding and indexing into ChromaDB...")
    store = embed_chunks(
        chunks,
        persist_dir=args.chroma_dir,
        batch_size=args.batch_size,
        verbose=verbose,
    )

    # Final stats
    print("\n" + "=" * 60)
    print("  Ingestion complete!")
    print("=" * 60)
    stats = get_collection_stats(args.chroma_dir)
    print(f"\n  Total chunks indexed: {stats['total_chunks']}")
    print(f"  Chunks by category:")
    for cat, count in sorted(stats["chunks_by_category"].items()):
        print(f"    {cat:30s}: {count:5d} chunks")
    print(f"\n  Vector store location: {args.chroma_dir}")
    print("  Ready for RAG queries.\n")


if __name__ == "__main__":
    main()
