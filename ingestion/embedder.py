"""
Embedder — generates Google Gemini embeddings and stores in ChromaDB.
Uses GoogleGenerativeAIEmbeddings (text-embedding-004, 768 dims, free tier).
No OpenAI dependency.
"""
import os
from pathlib import Path
from tqdm import tqdm

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document as LCDocument

from ingestion.chunker import DocumentChunk

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
COLLECTION_NAME    = "industrial_knowledge"


def _get_embeddings():
    """Return Gemini embedding model — requires GOOGLE_API_KEY in .env."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY not set. Get a free key at https://aistudio.google.com/apikey "
            "and add GOOGLE_API_KEY=... to your .env file."
        )
    return GoogleGenerativeAIEmbeddings(
        google_api_key=api_key,
        model=EMBEDDING_MODEL,
        task_type="retrieval_document",
    )


def get_vector_store(persist_dir: str = CHROMA_PERSIST_DIR) -> Chroma:
    """Load or create the ChromaDB vector store with Gemini embeddings."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_get_embeddings(),
        persist_directory=persist_dir,
    )


def chunk_to_lc_document(chunk: DocumentChunk) -> LCDocument:
    return LCDocument(page_content=chunk.text, metadata=chunk.metadata)


def embed_chunks(
    chunks: list[DocumentChunk],
    persist_dir: str = CHROMA_PERSIST_DIR,
    batch_size: int = 100,
    verbose: bool = True,
) -> Chroma:
    """
    Embed all chunks with Gemini text-embedding-004 and upsert into ChromaDB.
    Idempotent — skips chunks already indexed by chunk_id.
    """
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
                  desc="Embedding batches (Gemini)", disable=not verbose):
        store.add_documents(
            documents=lc_docs[i : i + batch_size],
            ids=ids[i : i + batch_size],
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
