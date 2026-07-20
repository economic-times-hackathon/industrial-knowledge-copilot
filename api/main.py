"""
FastAPI backend for the Industrial Knowledge Intelligence platform.

Endpoints:
    GET  /health              — health check
    POST /query               — ask the knowledge copilot
    GET  /corpus/stats        — corpus and index statistics
    GET  /corpus/categories   — list available document categories
"""
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

from rag_engine.copilot import ask
from ingestion.embedder import get_collection_stats

app = FastAPI(
    title="Industrial Knowledge Intelligence API",
    description="RAG-powered copilot for industrial plant operations, maintenance, and compliance.",
    version="0.1.0",
)

# Allow all origins for hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CATEGORIES = ["pids", "oem_manuals", "regulatory", "incident_reports", "maintenance_data"]


# ── Request / Response models ─────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5, description="Natural language question")
    category: Optional[str] = Field(None, description="Filter by category (optional)")
    top_k: int = Field(8, ge=1, le=20, description="Number of context chunks to retrieve")

class SourceRef(BaseModel):
    index: int
    filename: str
    category: str
    source_url: str
    document_type: str
    description: str
    relevance_score: float

class QueryResponse(BaseModel):
    answer: str
    confidence: str
    sources: list[SourceRef]
    chunks_retrieved: int

class HealthResponse(BaseModel):
    status: str
    openai_key_set: bool
    chroma_dir: str

class StatsResponse(BaseModel):
    total_chunks: int
    chunks_by_category: dict[str, int]


# ── Routes ────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    return HealthResponse(
        status="ok",
        openai_key_set=bool(os.getenv("OPENAI_API_KEY")),
        chroma_dir=CHROMA_DIR,
    )


@app.get("/corpus/categories", tags=["Corpus"])
def list_categories():
    return {"categories": CATEGORIES}


@app.get("/corpus/stats", response_model=StatsResponse, tags=["Corpus"])
def corpus_stats():
    try:
        stats = get_collection_stats(CHROMA_DIR)
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch stats: {e}")


@app.post("/query", response_model=QueryResponse, tags=["Copilot"])
def query_copilot(req: QueryRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")

    if req.category and req.category not in CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{req.category}'. Valid: {CATEGORIES}"
        )

    try:
        result = ask(
            question=req.question,
            category_filter=req.category,
            top_k=req.top_k,
            persist_dir=CHROMA_DIR,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

    return QueryResponse(
        answer=result["answer"],
        confidence=result["confidence"],
        sources=[SourceRef(**s) for s in result["sources"]],
        chunks_retrieved=len(result["chunks"]),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
