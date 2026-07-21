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


def _pick_subset(docs: list[ParsedDocument], max_per_category: int = None, max_total: int = None) -> list[ParsedDocument]:
    """
    Pick documents either by:
    - max_per_category: up to N docs from each category
    - max_total: exactly N docs total (distributed across categories)
    Prefers non-scanned, shorter docs (faster indexing); deterministic sort for reproducibility.
    """
    by_cat: dict[str, list[ParsedDocument]] = defaultdict(list)
    for d in docs:
        if not d.is_scanned and d.page_count <= 50:  # Prefer smaller docs for faster processing
            by_cat[d.category].append(d)

    # Sort each category by: 1) reasonable length, 2) rich text content
    for cat in by_cat:
        by_cat[cat] = sorted(by_cat[cat], key=lambda d: (d.page_count < 20, len(d.text)), reverse=True)

    subset = []
    
    if max_total:
        # Distribute max_total documents across all categories
        categories = sorted(by_cat.keys())
        docs_per_cat = max_total // len(categories)
        remaining = max_total % len(categories)
        
        for i, cat in enumerate(categories):
            # Give extra docs to first few categories if there's remainder
            take = docs_per_cat + (1 if i < remaining else 0)
            picked = by_cat[cat][:take]
            subset.extend(picked)
            print(f"    {cat:30s}: {len(picked)} docs selected")
            
            if len(subset) >= max_total:
                break
                
    elif max_per_category:
        # Original logic - N docs per category
        for cat, cat_docs in sorted(by_cat.items()):
            picked = cat_docs[:max_per_category]
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
    parser.add_argument("--max-per-category", type=int, default=0,
                        help="Max docs per category (use with --per-category mode)")
    parser.add_argument("--max-total",        type=int, default=2,
                        help="Max total documents to index (default: 2 for fast testing)")
    parser.add_argument("--per-category",     action="store_true",
                        help="Use max-per-category mode instead of max-total")
    parser.add_argument("--full",             action="store_true",             help="Index the full corpus (overrides other limits)")
    parser.add_argument("--stats-only",       action="store_true",             help="Print collection stats and exit")
    parser.add_argument("--quiet",            action="store_true",             help="Suppress verbose output")
    args = parser.parse_args()

    if args.full:
        args.max_total = 0
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
    if args.max_total > 0:
        print(f"\n  Fast mode: selecting {args.max_total} best docs total...")
        docs = _pick_subset(docs, max_total=args.max_total)
        print(f"  → {len(docs)} docs selected for indexing")
    elif args.per_category and args.max_per_category > 0:
        print(f"\n  Per-category mode: selecting {args.max_per_category} docs per category...")
        docs = _pick_subset(docs, max_per_category=args.max_per_category)
        print(f"  → {len(docs)} docs selected for indexing")
    elif not args.full:
        # Default fallback - use max_total
        print(f"\n  Default mode: selecting {2} best docs total...")
        docs = _pick_subset(docs, max_total=2)
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
