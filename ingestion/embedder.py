"""
Embedder — generates embeddings and stores in ChromaDB.

Uses FastEmbed (ONNX-based, no torch, no API key, no rate limits).
Model: BAAI/bge-small-en-v1.5 — 384-dim, ~130 MB, downloads once on first run.

To switch to Gemini (higher quality, API rate-limited):
    Set EMBEDDING_BACKEND=gemini in .env
"""
import os
import time
import re
from tqdm import tqdm

from dotenv import load_dotenv
load_dotenv()

# pyrefly: ignore [missing-import]
from langchain_chroma import Chroma
from langchain_core.documents import Document as LCDocument

from ingestion.chunker import DocumentChunk

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME    = "industrial_knowledge"
EMBEDDING_BACKEND  = os.getenv("EMBEDDING_BACKEND", "fastembed").lower()
FASTEMBED_MODEL    = os.getenv("FASTEMBED_MODEL", "BAAI/bge-small-en-v1.5")
GEMINI_MODEL       = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")


def _get_embeddings():
    if EMBEDDING_BACKEND == "gemini":
        # pyrefly: ignore [missing-import]
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY not set.")
        print(f"  Embedding backend: Gemini ({GEMINI_MODEL})")
        return GoogleGenerativeAIEmbeddings(
            google_api_key=api_key,
            model=GEMINI_MODEL,
            task_type="retrieval_document",
        )
    else:
        from langchain_community.embeddings import FastEmbedEmbeddings
        print(f"  Embedding backend: FastEmbed ({FASTEMBED_MODEL})")
        return FastEmbedEmbeddings(model_name=FASTEMBED_MODEL)


def get_vector_store(persist_dir: str = CHROMA_PERSIST_DIR) -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_get_embeddings(),
        persist_directory=persist_dir,
    )


def chunk_to_lc_document(chunk: DocumentChunk) -> LCDocument:
    return LCDocument(page_content=chunk.text, metadata=chunk.metadata)


def _add_batch_with_retry(store, docs, ids):
    """Retry on Gemini 429 rate-limit errors."""
    for attempt in range(1, 6):
        try:
            store.add_documents(documents=docs, ids=ids)
            return
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                match = re.search(r"retry in (\d+)", str(e))
                wait = int(match.group(1)) + 2 if match else 60
                print(f"\n  [Rate limit] Waiting {wait}s (attempt {attempt}/5)...")
                time.sleep(wait)
            else:
                raise


def embed_chunks(
    chunks: list[DocumentChunk],
    persist_dir: str = CHROMA_PERSIST_DIR,
    batch_size: int = 256,
    verbose: bool = True,
) -> Chroma:
    """Embed all chunks and upsert into ChromaDB. Idempotent."""
    store = get_vector_store(persist_dir)

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
        print(f"  Chunks to index: {len(new_chunks)} "
              f"(skipping {len(chunks) - len(new_chunks)} already indexed)")

    if not new_chunks:
        print("  Nothing new to index.")
        return store

    lc_docs = [chunk_to_lc_document(c) for c in new_chunks]
    ids     = [c.chunk_id for c in new_chunks]

    for i in tqdm(range(0, len(lc_docs), batch_size),
                  desc="Embedding batches", disable=not verbose):
        _add_batch_with_retry(
            store,
            lc_docs[i : i + batch_size],
            ids[i : i + batch_size],
        )

    if verbose:
        total = len(existing_ids) + len(new_chunks)
        print(f"\n  ChromaDB '{COLLECTION_NAME}': {total} total chunks indexed")

    return store


def get_collection_stats(persist_dir: str = CHROMA_PERSIST_DIR) -> dict:
    store = get_vector_store(persist_dir)
    result = store.get(include=[])
    ids = result.get("ids", [])

    categories: dict[str, int] = {}
    for meta in (result.get("metadatas") or []):
        cat = (meta or {}).get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    return {"total_chunks": len(ids), "chunks_by_category": categories}
