"""
FastAPI backend — six endpoints mapping 1:1 to the six dashboard screens.

Dashboard screen   → Endpoint
─────────────────────────────────────────────────────────────────────
Document upload    → POST /upload          (ingest a new document)
AI Copilot         → POST /query           (open Q&A, cited answers)
Asset Explorer     → GET  /asset/{tag}     (graph-style linked context — vector stub)
Maintenance Intel  → POST /maintenance/rca (RCA-structured output)
Compliance Intel   → POST /compliance      (gap check + evidence pack)
Notifications      → GET  /notifications   (proactive alert digest)

System / corpus    → GET  /health | /corpus/stats | /corpus/categories
"""
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

from rag_engine.copilot import ask, rca_query, compliance_check, notify_scan
from ingestion.embedder import get_collection_stats

app = FastAPI(
    title="Industrial Knowledge Intelligence API",
    description=(
        "Six-screen RAG platform for petroleum refinery / petrochemical plant operations.\n\n"
        "One backend pipeline (ingest → index → retrieve → generate) "
        "powers all screens with mode-specific prompts."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CATEGORIES = ["pids", "oem_manuals", "regulatory", "incident_reports", "maintenance_data"]


# ── Request / Response models ─────────────────────────────────────────────────

class SourceRef(BaseModel):
    index: int
    filename: str
    category: str
    source_url: str
    document_type: str
    description: str
    relevance_score: float

class RAGResponse(BaseModel):
    answer: str
    confidence: str
    sources: list[SourceRef]
    chunks_retrieved: int

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5)
    category: Optional[str] = Field(None, description="Filter by category (optional)")
    top_k: int = Field(8, ge=1, le=20)

class RCARequest(BaseModel):
    equipment_tag: str = Field(..., description="e.g. P-101A, E-203, PSV-301")
    symptom: str      = Field(..., description="Observed failure or symptom description")
    top_k: int = Field(10, ge=1, le=20)

class ComplianceRequest(BaseModel):
    topic: str                         = Field(..., description="e.g. 'pressure relief valve testing', 'fire water system'")
    equipment_or_area: Optional[str]   = Field(None, description="e.g. 'CDU unit', 'P-101A'")
    top_k: int = Field(10, ge=1, le=20)

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str
    openai_key_set: bool
    chroma_dir: str
    api_version: str

class StatsResponse(BaseModel):
    total_chunks: int
    chunks_by_category: dict[str, int]


# ── Helper ────────────────────────────────────────────────────────────────────

def _require_key():
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured. Add it to .env.")
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(status_code=503, detail="GOOGLE_API_KEY not configured. Add it to .env.")

def _to_rag_response(result: dict) -> RAGResponse:
    return RAGResponse(
        answer=result["answer"],
        confidence=result["confidence"],
        sources=[SourceRef(**s) for s in result["sources"]],
        chunks_retrieved=len(result["chunks"]),
    )


# ── System endpoints ──────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    return HealthResponse(
        status="ok",
        openai_key_set=bool(os.getenv("GROQ_API_KEY") and os.getenv("GOOGLE_API_KEY")),
        chroma_dir=CHROMA_DIR,
        api_version=app.version,
    )

@app.get("/corpus/categories", tags=["System"])
def list_categories():
    return {"categories": CATEGORIES}

@app.get("/corpus/stats", response_model=StatsResponse, tags=["System"])
def corpus_stats():
    try:
        return StatsResponse(**get_collection_stats(CHROMA_DIR))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Screen 1: Document Upload ─────────────────────────────────────────────────

def _ingest_uploaded_file(tmp_path: str, original_name: str):
    """Background task: parse → chunk → embed a single uploaded PDF."""
    from ingestion.pdf_parser import extract_text_from_pdf, ParsedDocument
    from ingestion.chunker import chunk_documents
    from ingestion.embedder import embed_chunks

    text, page_count, is_scanned = extract_text_from_pdf(tmp_path)
    doc = ParsedDocument(
        filename=original_name,
        category="uploaded",
        folder_path=f"uploads/{original_name}",
        source_url="user-upload",
        description=f"User-uploaded document: {original_name}",
        document_type="UPLOADED",
        text=text,
        page_count=page_count,
        file_size_kb=int(Path(tmp_path).stat().st_size / 1024),
        is_scanned=is_scanned,
        metadata={
            "filename": original_name, "category": "uploaded",
            "source_url": "user-upload", "document_type": "UPLOADED",
            "description": f"User-uploaded: {original_name}",
            "page_count": page_count, "file_size_kb": 0,
            "is_scanned": is_scanned,
        },
    )
    chunks = chunk_documents([doc], verbose=False)
    embed_chunks(chunks, persist_dir=CHROMA_DIR, verbose=False)
    Path(tmp_path).unlink(missing_ok=True)

@app.post("/upload", response_model=UploadResponse, tags=["Document Upload"])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF document to ingest"),
):
    """
    Upload a PDF. It is stored temporarily, then ingested asynchronously —
    parsed, chunked, and embedded into the vector index. Mirrors the
    'Document upload — auto-process' screen behaviour.
    """
    _require_key()
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB).")

    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    background_tasks.add_task(_ingest_uploaded_file, tmp_path, file.filename)

    return UploadResponse(
        filename=file.filename,
        status="queued",
        message="Document queued for ingestion. It will appear in search results within ~30 seconds.",
    )


# ── Screen 2: AI Copilot ──────────────────────────────────────────────────────

@app.post("/query", response_model=RAGResponse, tags=["AI Copilot"])
def query_copilot(req: QueryRequest):
    """
    Open Q&A across the full knowledge base with cited answers and confidence scoring.
    Mirrors the 'AI Copilot — Ask + cited answers' screen.
    """
    _require_key()
    if req.category and req.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Valid: {CATEGORIES}")
    try:
        return _to_rag_response(ask(req.question, req.category, req.top_k, CHROMA_DIR))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Screen 3: Asset Explorer (vector stub — graph layer coming) ───────────────

@app.get("/asset/{tag}", response_model=RAGResponse, tags=["Asset Explorer"])
def asset_context(
    tag: str,
    top_k: int = 12,
):
    """
    Pull everything the knowledge base knows about an equipment tag.
    Click any tag on a P&ID → manuals, work orders, incidents, standards all surface.
    Currently a rich vector search; Neo4j graph traversal will replace this.
    Mirrors the 'Asset Explorer — Interactive P&ID map' screen.
    """
    _require_key()
    question = (
        f"Show everything related to equipment tag {tag}: "
        f"specifications, maintenance history, inspection findings, "
        f"operating procedures, and any related incident reports."
    )
    try:
        return _to_rag_response(ask(question, top_k=top_k, persist_dir=CHROMA_DIR))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Screen 4: Maintenance Intel ───────────────────────────────────────────────

@app.post("/maintenance/rca", response_model=RAGResponse, tags=["Maintenance Intel"])
def maintenance_rca(req: RCARequest):
    """
    Root Cause Analysis — joins work order history, OEM manuals, and incident reports
    into a structured RCA report with ranked probable causes and recommended actions.
    Mirrors the 'Maintenance Intel — Predictive + RCA' screen.
    """
    _require_key()
    try:
        return _to_rag_response(rca_query(req.equipment_tag, req.symptom, req.top_k, CHROMA_DIR))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Screen 5: Compliance Intel ────────────────────────────────────────────────

@app.post("/compliance", response_model=RAGResponse, tags=["Compliance Intel"])
def compliance_intel(req: ComplianceRequest):
    """
    Maps regulatory requirements (OISD, PESO, Factories Act) against current
    procedures/inspection state, identifies gaps, and generates an evidence pack
    ready for auditors.
    Mirrors the 'Compliance Intel — Gap checks + audits' screen.
    """
    _require_key()
    try:
        return _to_rag_response(
            compliance_check(req.topic, req.equipment_or_area, req.top_k, CHROMA_DIR)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Screen 6: Notifications ───────────────────────────────────────────────────

@app.get("/notifications", response_model=RAGResponse, tags=["Notifications"])
def get_notifications(top_k: int = 10):
    """
    Proactive alert digest — scans the knowledge base for active risk patterns,
    compliance flags, and lessons from historical incidents. Push, not pull.
    Mirrors the 'Notifications — Proactive alert feed' screen.
    In production this is called by a scheduler (e.g. every 6 hours), not the user.
    """
    _require_key()
    try:
        return _to_rag_response(notify_scan(top_k=top_k, persist_dir=CHROMA_DIR))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
