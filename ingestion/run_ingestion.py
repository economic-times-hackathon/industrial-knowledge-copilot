"""
run_ingestion.py — main entry point for the full ingestion pipeline.

Usage:
    # Prototype (default): 2 best docs per category → ~10 docs, ~400 chunks
    python -m ingestion.run_ingestion

    # Richer demo: more docs per category
    python -m ingestion.run_ingestion --max-per-category 4

    # Full corpus (102 docs, ~13k chunks — needs plenty of RAM)
    python -m ingestion.run_ingestion --full

    # Check what's indexed
    python -m ingestion.run_ingestion --stats-only
"""
import argparse
import os
import sys
import random
from pathlib import Path
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()

from ingestion.pdf_parser import parse_corpus, ParsedDocument
from ingestion.chunker import chunk_documents
from ingestion.embedder import embed_chunks, get_collection_stats

EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "fastembed").lower()


def _pick_subset(docs: list[ParsedDocument], max_per_category: int) -> list[ParsedDocument]:
    """
    Pick up to `max_per_category` docs from each category.
    Prefers non-scanned (text-extractable) docs; deterministic sort for reproducibility.
    """
    by_cat: dict[str, list[ParsedDocument]] = defaultdict(list)
    for d in docs:
        if not d.is_scanned:
            by_cat[d.category].append(d)

    subset = []
    for cat, cat_docs in sorted(by_cat.items()):
        # Sort by text length descending (richest docs first), then take top N
        picked = sorted(cat_docs, key=lambda d: len(d.text), reverse=True)[:max_per_category]
        subset.extend(picked)
        print(f"    {cat:30s}: {len(picked)} docs selected")

    return subset


def main():
    parser = argparse.ArgumentParser(description="Industrial Knowledge Ingestion Pipeline")
    parser.add_argument("--corpus",           default="./corpus",              help="Path to corpus root directory")
    parser.add_argument("--manifest",         default="./corpus_manifest.csv", help="Path to corpus_manifest.csv")
    parser.add_argument("--chroma-dir",       default="./chroma_db",           help="ChromaDB persist directory")
    parser.add_argument("--chunk-size",       type=int, default=800,           help="Chunk size in characters")
    parser.add_argument("--chunk-overlap",    type=int, default=150,           help="Chunk overlap in characters")
    parser.add_argument("--batch-size",       type=int, default=32,            help="Embedding batch size (keep low to avoid OOM)")
    parser.add_argument("--max-per-category", type=int, default=2,
                        help="Max docs per category (default: 2 for prototype). "
                             "Use --full to index everything.")
    parser.add_argument("--full",             action="store_true",             help="Index the full corpus (overrides --max-per-category)")
    parser.add_argument("--stats-only",       action="store_true",             help="Print collection stats and exit")
    parser.add_argument("--quiet",            action="store_true",             help="Suppress verbose output")
    args = parser.parse_args()

    if args.full:
        args.max_per_category = 0

    verbose = not args.quiet

    # ── Stats-only mode ──────────────────────────────────────────────────────
    if args.stats_only:
        stats = get_collection_stats(args.chroma_dir)
        print(f"ChromaDB collection stats:")
        print(f"  Total chunks indexed: {stats['total_chunks']}")
        print(f"  Chunks by category:")
        for cat, count in sorted(stats["chunks_by_category"].items()):
            print(f"    {cat:30s}: {count:5d} chunks")
        return

    # ── Validate API key only when Gemini backend is selected ───────────────
    if EMBEDDING_BACKEND == "gemini" and not os.getenv("GOOGLE_API_KEY"):
        print("[ERROR] GOOGLE_API_KEY not set. Copy .env.example to .env and add your key.")
        print("        Get a free key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    print("=" * 60)
    print("  Industrial Knowledge Intelligence — Ingestion Pipeline")
    print("=" * 60)

    # ── Step 1: Parse ────────────────────────────────────────────────────────
    print("\n[1/3] Parsing PDFs from corpus...")
    docs = parse_corpus(
        corpus_root=args.corpus,
        manifest_path=args.manifest,
        verbose=verbose,
    )
    scanned = sum(1 for d in docs if d.is_scanned)
    print(f"\n  Parsed:  {len(docs)} documents  ({scanned} scanned/empty, skipped)")

    # ── Subset selection ─────────────────────────────────────────────────────
    if args.max_per_category > 0:
        print(f"\n  Prototype mode: selecting {args.max_per_category} best docs per category...")
        docs = _pick_subset(docs, args.max_per_category)
        print(f"  → {len(docs)} docs selected for indexing")
    else:
        docs = [d for d in docs if not d.is_scanned]
        print(f"  → Full corpus: {len(docs)} text-extractable docs will be indexed")

    print(f"  Total text: {sum(len(d.text) for d in docs):,} characters")

    # ── Step 2: Chunk ────────────────────────────────────────────────────────
    print("\n[2/3] Chunking documents...")
    chunks = chunk_documents(
        docs,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        verbose=verbose,
    )
    print(f"\n  Total chunks: {len(chunks)}")

    # ── Step 3: Embed + Index ────────────────────────────────────────────────
    print("\n[3/3] Embedding and indexing into ChromaDB...")
    embed_chunks(
        chunks,
        persist_dir=args.chroma_dir,
        batch_size=args.batch_size,
        verbose=verbose,
    )

    # ── Done ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  Ingestion complete!")
    print("=" * 60)
    stats = get_collection_stats(args.chroma_dir)
    print(f"\n  Total chunks indexed: {stats['total_chunks']}")
    print(f"  Chunks by category:")
    for cat, count in sorted(stats["chunks_by_category"].items()):
        print(f"    {cat:30s}: {count:5d} chunks")
    print(f"\n  Vector store: {args.chroma_dir}")
    print("  Ready for RAG queries.\n")


if __name__ == "__main__":
    main()
