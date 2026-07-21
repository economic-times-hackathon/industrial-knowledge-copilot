"""
Retriever — semantic search over ChromaDB.

Uses the same embedding backend as the ingestion pipeline (FastEmbed by default).
MUST match the embedding model used at index time — mismatched models cause
dimension errors or silent garbage results.
"""
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME    = "industrial_knowledge"
TOP_K              = int(os.getenv("TOP_K_RETRIEVAL", "8"))
EMBEDDING_BACKEND  = os.getenv("EMBEDDING_BACKEND", "fastembed").lower()
FASTEMBED_MODEL    = os.getenv("FASTEMBED_MODEL", "BAAI/bge-small-en-v1.5")
GEMINI_MODEL       = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")


@dataclass
class RetrievedChunk:
    chunk_id:      str
    filename:      str
    category:      str
    source_url:    str
    document_type: str
    description:   str
    text:          str
    score:         float


def _get_query_embeddings():
    """
    Return the same embedding model used at ingestion time.
    FastEmbed uses task_type='query' automatically for retrieval.
    """
    if EMBEDDING_BACKEND == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY not set.")
        return GoogleGenerativeAIEmbeddings(
            google_api_key=api_key,
            model=GEMINI_MODEL,
            task_type="retrieval_query",
        )
    else:
        from langchain_community.embeddings import FastEmbedEmbeddings
        return FastEmbedEmbeddings(model_name=FASTEMBED_MODEL)


def load_retriever(persist_dir: str = CHROMA_PERSIST_DIR) -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_get_query_embeddings(),
        persist_directory=persist_dir,
    )


def retrieve(
    query: str,
    top_k: int = TOP_K,
    category_filter: Optional[str] = None,
    persist_dir: str = CHROMA_PERSIST_DIR,
) -> list[RetrievedChunk]:
    store = load_retriever(persist_dir)
    where = {"category": category_filter} if category_filter else None

    results = store.similarity_search_with_relevance_scores(
        query=query, k=top_k, filter=where,
    )

    chunks = []
    for doc, score in results:
        m = doc.metadata
        chunks.append(RetrievedChunk(
            chunk_id      = m.get("chunk_id", ""),
            filename      = m.get("filename", ""),
            category      = m.get("category", ""),
            source_url    = m.get("source_url", ""),
            document_type = m.get("document_type", ""),
            description   = m.get("description", ""),
            text          = doc.page_content,
            score         = round(score, 4),
        ))
    return chunks


def format_context(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(
            f"[{i}] SOURCE: {c.filename} | Category: {c.category} | "
            f"Type: {c.document_type}\n"
            f"Description: {c.description}\n"
            f"---\n{c.text}\n"
        )
    return "\n\n".join(parts)
