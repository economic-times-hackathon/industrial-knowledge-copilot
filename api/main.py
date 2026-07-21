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
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

from dotenv import load_dotenv
load_dotenv()

from rag_engine.copilot import ask, rca_query, compliance_check, notify_scan
try:
    from rag_engine.graph import get_neighbors
except ImportError:
    # Neo4j not installed - use stub implementation
    def get_neighbors(tag): return []

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

os.makedirs("corpus", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/corpus", StaticFiles(directory="corpus"), name="corpus")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CATEGORIES = ["pids", "oem_manuals", "regulatory", "incident_reports", "maintenance_data", "uploaded", "expert_knowledge"]


# ── Request / Response models ─────────────────────────────────────────────────

class SourceRef(BaseModel):
    index: int
    filename: str
    category: str
    source_url: str
    document_type: str
    description: str
    relevance_score: float
    excerpt: str

class RAGResponse(BaseModel):
    answer: str
    confidence: str
    sources: list[SourceRef]
    chunks_retrieved: int

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
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
    groq_key_set: bool
    google_key_set: bool
    chroma_dir: str
    api_version: str

class StatsResponse(BaseModel):
    total_chunks: int
    chunks_by_category: dict[str, int]


# ── Helper ────────────────────────────────────────────────────────────────────

def _require_key():
    """Raise 503 if the Groq API key (used for LLM inference) is not set."""
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY not configured. Add it to .env. "
                   "Get a free key at https://console.groq.com"
        )

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
        groq_key_set=bool(os.getenv("GROQ_API_KEY")),
        google_key_set=bool(os.getenv("GOOGLE_API_KEY")),
        chroma_dir=CHROMA_DIR,
        api_version=app.version,
    )

@app.get("/corpus/categories", tags=["System"])
def list_categories():
    return {"categories": CATEGORIES}

@app.get("/corpus/stats", response_model=StatsResponse, tags=["System"])
def corpus_stats():
    # Simple stats response - enhanced later
    return StatsResponse(
        total_chunks=69,  # Based on our 2-document ingestion
        chunks_by_category={
            "incident_reports": 62,
            "maintenance_data": 7
        }
    )


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

@app.post("/upload", response_model=UploadResponse, tags=["Document Upload"])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF document to ingest"),
):
    """
    Upload a PDF. It is stored temporarily, then ingested asynchronously —
    parsed, chunked, and embedded into the vector index. Mirrors the
    'Document upload — auto-process' screen behaviour.
    Upload uses only the embedding pipeline (FastEmbed) — no LLM key needed.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB).")

    content = await file.read()
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    background_tasks.add_task(_ingest_uploaded_file, file_path, file.filename)

    return UploadResponse(
        filename=file.filename,
        status="queued",
        message="Document queued for ingestion. It will appear in search results within ~30 seconds.",
    )

@app.get("/documents", tags=["System"])
def list_documents():
    """List all ingested documents (from corpus and uploads)."""
    res = []
    
    # 1. Base Corpus
    if os.path.exists("corpus"):
        for root, _, files in os.walk("corpus"):
            for f in files:
                if f.endswith(".pdf"):
                    path = os.path.join(root, f)
                    stat = os.stat(path)
                    res.append({
                        "name": f,
                        "size": stat.st_size,
                        "source": "corpus",
                        "category": os.path.basename(root)
                    })
    
    # 2. Uploads
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        for upload_file in uploads_dir.iterdir():
            if upload_file.suffix.lower() == ".pdf":
                stat = upload_file.stat()
                res.append({
                    "name": upload_file.name,
                    "size": stat.st_size,
                    "source": "upload",
                    "category": "uploaded"
                })
    return {"files": res}


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


# ── Screen 3: Asset Explorer (Neo4j Graph Traversal) ────────────────────────

@app.get("/asset/{tag}", response_model=RAGResponse, tags=["Asset Explorer"])
def asset_context(
    tag: str,
    top_k: int = 12,
):
    """
    Pull everything the knowledge base knows about an equipment tag.
    Traverses the Neo4j equipment graph to include context about connected components.
    Mirrors the 'Asset Explorer — Interactive P&ID map' screen.
    """
    _require_key()
    tag = tag.upper()
    neighbors = get_neighbors(tag)
    neighbors_str = f" Pay special attention to its connected equipment: {', '.join(neighbors)}." if neighbors else ""

    question = (
        f"Show everything related to equipment tag {tag}.{neighbors_str} "
        f"Include specifications, maintenance history, inspection findings, "
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


# ── Screen 7: Knowledge Capture ──────────────────────────────────────────────

class CaptureRequest(BaseModel):
    transcript: str = Field(..., description="Speech transcript from expert")
    equipment_context: str = Field(..., description="Equipment tag or context")
    session_type: str = Field("procedure_walkthrough", description="Type of knowledge session")
    photos: Optional[list[str]] = Field(None, description="Base64 encoded photos (optional)")

@app.post("/capture/process", tags=["Knowledge Capture"])
def process_knowledge_capture(req: CaptureRequest):
    """
    Process captured expert knowledge (speech + photos) into structured, searchable format.
    Converts informal expert explanations into documented procedures and adds to knowledge base.
    """
    _require_key()
    
    try:
        # Create LLM instance
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")
        
        llm = ChatGroq(api_key=api_key, model="llama-3.3-70b-versatile", temperature=0)
        
        system_prompt = """You are an Industrial Knowledge Extraction AI. Convert expert explanations into structured, searchable procedures.

Extract and format:
1. **Equipment**: Equipment tag/context
2. **Procedure Type**: What kind of knowledge this represents
3. **Safety Requirements**: Critical safety steps (LOTO, PPE, hazards)
4. **Step-by-step Instructions**: Numbered procedure steps
5. **Expert Tips**: Tacit knowledge, warnings, "feel" indicators
6. **Troubleshooting**: Diagnostic steps if mentioned

Format as clear, searchable text that preserves the expert's knowledge."""

        user_message = f"""Equipment Context: {req.equipment_context}
Session Type: {req.session_type}
Expert Transcript: {req.transcript}

Convert this expert knowledge into structured documentation."""

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])
        
        structured_knowledge = response.content
        
        # Store in ChromaDB as expert knowledge
        from ingestion.embedder import get_vector_store
        from langchain_core.documents import Document
        import uuid
        
        doc = Document(
            page_content=structured_knowledge,
            metadata={
                "filename": f"Expert_Knowledge_{req.equipment_context}_{uuid.uuid4().hex[:8]}.txt",
                "category": "expert_knowledge",
                "source_url": "expert-capture",
                "document_type": "EXPERT_KNOWLEDGE",
                "description": f"Expert knowledge: {req.equipment_context} - {req.session_type}",
                "equipment_context": req.equipment_context,
                "session_type": req.session_type,
                "chunk_id": f"expert_{uuid.uuid4().hex[:8]}"
            }
        )
        
        # Add to vector store
        store = get_vector_store(persist_dir=CHROMA_DIR)
        store.add_documents([doc])
        
        return {
            "status": "success",
            "structured_knowledge": structured_knowledge,
            "message": "Expert knowledge captured and indexed successfully",
            "equipment_context": req.equipment_context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
