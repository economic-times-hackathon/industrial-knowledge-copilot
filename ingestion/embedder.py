"""
Embedder — generates OpenAI embeddings for chunks and stores them in ChromaDB.
Supports incremental indexing (skips already-indexed chunks).
"""
import os
import hashlib
from pathlib import Path
from tqdm import tqdm

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document as LCDocument

from ingestion.chunker import DocumentChunk

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
COLLECTION_NAME    = "industrial_knowledge"


def get_vector_store(persist_dir: str = CHROMA_PERSIST_DIR) -> Chroma:
    """Load or create the ChromaDB vector store."""
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )
    return store


def chunk_to_lc_document(chunk: DocumentChunk) -> LCDocument:
    """Convert our DocumentChunk to a LangChain Document."""
    return LCDocument(
        page_content=chunk.text,
        metadata=chunk.metadata,
    )


def embed_chunks(
    chunks: list[DocumentChunk],
    persist_dir: str = CHROMA_PERSIST_DIR,
    batch_size: int = 100,
    verbose: bool = True,
) -> Chroma:
    """
    Embed all chunks and upsert into ChromaDB.
    Uses chunk_id as the document ID for idempotent upserts.
    """
    store = get_vector_store(persist_dir)

    # Check existing IDs to skip already-indexed chunks
    existing_ids: set[str] = set()
    try:
        existing = store.get(include=[])
        existing_ids = set(existing.get("ids", []))
        if verbose and existing_ids:
            print(f"  Existing index: {len(existing_ids)} chunks already indexed")
    except Exception:
        pass

    new_chunks = [c for c in chunks if c.chunk_id not in existing_ids]
    if verbose:
        print(f"  Chunks to index: {len(new_chunks)} (skipping {len(chunks) - len(new_chunks)} duplicates)")

    if not new_chunks:
        print("  Nothing new to index.")
        return store

    # Batch upsert
    lc_docs = [chunk_to_lc_document(c) for c in new_chunks]
    ids      = [c.chunk_id for c in new_chunks]

    for i in tqdm(range(0, len(lc_docs), batch_size), desc="Embedding batches", disable=not verbose):
        batch_docs = lc_docs[i : i + batch_size]
        batch_ids  = ids[i : i + batch_size]
        store.add_documents(documents=batch_docs, ids=batch_ids)

    if verbose:
        total = len(existing_ids) + len(new_chunks)
        print(f"\n  ChromaDB collection '{COLLECTION_NAME}': {total} total chunks indexed")

    return store


def get_collection_stats(persist_dir: str = CHROMA_PERSIST_DIR) -> dict:
    """Return stats about the current ChromaDB collection."""
    store = get_vector_store(persist_dir)
    result = store.get(include=[])
    ids = result.get("ids", [])

    categories: dict[str, int] = {}
    for meta in (result.get("metadatas") or []):
        cat = (meta or {}).get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_chunks": len(ids),
        "chunks_by_category": categories,
    }


if __name__ == "__main__":
    from pathlib import Path
    from ingestion.pdf_parser import parse_corpus
    from ingestion.chunker import chunk_documents

    root = Path(__file__).parent.parent
    print("Step 1: Parsing PDFs...")
    docs = parse_corpus(
        corpus_root=str(root / "corpus"),
        manifest_path=str(root / "corpus_manifest.csv"),
        verbose=True,
    )

    print("\nStep 2: Chunking...")
    chunks = chunk_documents(docs, verbose=True)

    print("\nStep 3: Embedding & indexing...")
    store = embed_chunks(chunks, verbose=True)

    print("\nStep 4: Collection stats:")
    stats = get_collection_stats()
    print(f"  Total chunks: {stats['total_chunks']}")
    for cat, count in sorted(stats["chunks_by_category"].items()):
        print(f"    {cat}: {count} chunks")
