<div align="center">

# Industrial Knowledge Intelligence
### Unified Asset & Operations Brain + Knowledge Capture System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-RAG_Pipeline-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B35?style=for-the-badge&logo=databricks&logoColor=white)](https://trychroma.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![FastEmbed](https://img.shields.io/badge/FastEmbed-Local_Embeddings-8A2BE2?style=for-the-badge&logo=huggingface&logoColor=white)](https://qdrant.github.io/fastembed/)

---

![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen?style=flat-square)
![Hackathon](https://img.shields.io/badge/ET_Hackathon-2026-orange?style=flat-square)
![Theme](https://img.shields.io/badge/Theme-Industrial_Intelligence-blue?style=flat-square)
![Corpus](https://img.shields.io/badge/Corpus-102_Documents-green?style=flat-square)
![Embeddings](https://img.shields.io/badge/Embeddings-FastEmbed_Local-8A2BE2?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=flat-square)

</div>

---

## Problem Statement

When experienced engineers retire, **80% of their critical knowledge** walks out the door — equipment quirks, safety workarounds, vendor relationships, and troubleshooting intuition that takes decades to develop. Simultaneously, new hires face a 7.9M character corpus of regulatory documents with no way to quickly find relevant, actionable guidance.

**The solution**: An AI-powered knowledge copilot that both **preserves expert knowledge** through video capture and **accelerates learning** through intelligent document retrieval.

---

## The Problem (By the Numbers)

| Statistic | Source |
|---|---|
| 35% of working hours spent searching for information | McKinsey Global Survey 2024 |
| 7–12 disconnected document systems per large plant | NASSCOM-EY Study |
| 18–22% of unplanned downtime linked to knowledge fragmentation | BIS Research |
| 25% of experienced industrial engineers retiring this decade | Industry estimate |
| **80% of expert knowledge exists only in their heads** | MIT Research |

---

## Dual Solution Approach

### 1. **Knowledge Preservation** (Expert → System)
Video capture system records experienced engineers demonstrating equipment procedures, troubleshooting walkthroughs, and safety practices. Whisper converts speech to text, LLM structures the knowledge, and the system builds a growing repository of expert insights before they retire.

### 2. **Knowledge Acceleration** (System → Users)  
RAG-powered copilot provides instant, cited answers from the complete document corpus — regulatory standards, maintenance procedures, incident reports, OEM manuals — making decades of documentation instantly searchable.

---

## Complete Solution: 7 Integrated Modules

### **Document Intelligence** (Screens 1-6)
Six dashboard screens powered by the same RAG pipeline with mode-specific prompts:

1. **Document Upload** — drag & drop PDFs, auto-processing pipeline  
2. **AI Copilot** — open Q&A with dynamic sample questions based on indexed content
3. **Asset Explorer** — equipment tag search with P&ID integration  
4. **Maintenance Intel** — structured RCA reports from work order history
5. **Compliance Intel** — regulatory gap analysis and evidence packs  
6. **Notifications** — proactive risk alerts from knowledge base patterns

### **Knowledge Capture System** (Screen 7)
**Digital Apprenticeship Platform** to preserve expert knowledge before retirement:

- **Browser-based Speech Recognition** (Web Speech API) — zero setup, works offline
- **Real-time Transcription** — live speech-to-text as experts demonstrate procedures  
- **LLM Structuring** — converts informal explanations into searchable procedures
- **Equipment Context** — tags knowledge to specific assets and systems
- **Photo Integration** — visual documentation of equipment states and procedures
- **ChromaDB Integration** — expert knowledge becomes instantly searchable alongside documents

---

## Architecture: RAG Pipeline + Knowledge Capture

**Document Processing Pipeline:**
```
PDF Upload → Parse (PyMuPDF) → Chunk (800 chars) → Embed (FastEmbed) → ChromaDB
```

**Knowledge Capture Pipeline:**
```
Expert Speech → Web Speech API → Transcript → Groq LLM → Structured Knowledge → ChromaDB
```

**Query Pipeline:**
```
User Question → retrieve() → format_context() → LLM (Groq) → Cited Answer
```

**Unified Search:** Both document chunks and expert knowledge appear together in search results.

---

## The Seven Screens

**Document Upload** (`POST /upload`)
User drags in a PDF. It's stored, queued, and the ingestion pipeline runs async — parse → chunk → embed → indexed. The screen shows progress then flips the doc to "indexed". Non-blocking.

**AI Copilot** (`POST /query`)
Open Q&A across the full corpus. Question hits the retriever, top-k chunks are pulled, GPT-4o generates a cited answer. Every answer links back to the originating document with a relevance score and confidence level (HIGH / MEDIUM / LOW).

**Asset Explorer** (`GET /asset/{tag}`)
Click any equipment tag on a P&ID (e.g. `P-101A`, `E-203`, `PSV-301`) — pulls everything the knowledge base knows about that tag: specs from OEM manuals, work order history, inspection findings, operating procedures, any related incident reports. Currently vector search; Neo4j graph traversal will replace it for true linked-node queries.

**Maintenance Intel** (`POST /maintenance/rca`)
Provide an equipment tag and a symptom. The RCA prompt joins structured work order records with unstructured inspection notes and incident history, then surfaces: probable root causes ranked by evidence, contributing factors, recommended actions, and similar historical failures. Same retrieval pipeline as the copilot — different system prompt, structured output.

**Compliance Intel** (`POST /compliance`)
Provide a topic (e.g. "pressure relief valve testing") and optional equipment/area. The compliance prompt maps live state against OISD, PESO, Factories Act, and DGMS requirements, identifies gaps, and generates an evidence pack listing every document that serves as audit evidence.

**Notifications** (`GET /notifications`)
Proactive, not reactive. A background job calls this on a schedule — no user action needed. Scans the knowledge base for active risk patterns, compliance gaps, and lessons from historical incidents, then pushes a digest to the alert feed. This is the lessons-learned engine surfacing before similar conditions recur.

**Knowledge Capture** (`POST /capture/process`)
The 7th screen: Expert speech-to-structured-knowledge pipeline. Engineers record equipment walkthroughs, troubleshooting procedures, and safety practices. Web Speech API captures audio in real-time, Groq LLM structures informal explanations into documented procedures, and ChromaDB makes expert knowledge instantly searchable alongside regulatory documents.

---

## Document Corpus

102 documents (100 PDFs + 2 CSVs) assembled across 5 categories, all tracked via Git LFS:

| Category | Files | Key Sources |
|---|---|---|
| P&IDs & Process Diagrams | 19 | AIChE, OSHA, Honeywell + 12 synthetic ISA-5.1 plant P&IDs (CDU, HDS, utilities) |
| OEM Equipment Manuals | 14 | Emerson/Fisher, Atlas Copco, Alfa Laval, Pentair, SKF, Siemens + 2 synthetic pump IOMs |
| Regulatory & Standards | 30 | OISD.gov.in (STD-117/144/152), PESO.gov.in, DGMS.gov.in, Factories Act 1948, EPA 1986 |
| Incident & Safety Reports | 21 | CSB.gov (14 reports), OSHA PSM, ILO Major Hazards, DGMS safety alerts |
| Maintenance & Inspection Data | 18 | SKF bearing guides, NASA CMAPSS, synthetic inspection records, 2160-row sensor CSV |

Full provenance in [`corpus_manifest.csv`](./corpus_manifest.csv).

---

## Tech Stack

| Layer | Technology | Status |
|---|---|---|
| Document Parsing | PyMuPDF 1.28 | ✅ Done |
| Chunking | LangChain RecursiveCharacterTextSplitter (800 chars / 150 overlap) | ✅ Done |
| Embeddings | FastEmbed `BAAI/bge-small-en-v1.5` (384 dims, runs locally) | ✅ Done |
| Vector Store | ChromaDB 1.1 — local persistence, incremental upsert | ✅ Done |
| LLM / RAG | Groq `llama-3.3-70b-versatile` via LangChain — 7 prompt modes | ✅ Done |
| Backend API | FastAPI 0.111 + Uvicorn — 7 screen endpoints | ✅ Done |
| Async Ingestion | FastAPI BackgroundTasks — upload → parse → embed | ✅ Done |
| Frontend | React 18 + Tailwind 3 + Vite — 7-screen responsive dashboard | ✅ Done |
| Speech Recognition | Web Speech API — browser-native, real-time transcription | ✅ Done |
| Knowledge Capture | Audio → Transcript → LLM → Structured Knowledge | ✅ Done |
| Expert Knowledge Storage | ChromaDB integration with "expert_knowledge" category | ✅ Done |
| Mobile Responsive | Google-style source cards, touch-friendly interface | ✅ Done |
| Dynamic Sample Questions | Auto-generated based on indexed content categories | ✅ Done |

---

## Repository Structure

```
.
├── corpus/                         # 102-document corpus via Git LFS
│   ├── pids/                       # P&IDs and process diagrams (19)
│   ├── oem_manuals/                # Equipment O&M manuals (14)
│   ├── regulatory/                 # OISD, PESO, DGMS, Factories Act, EPA (30)
│   ├── incident_reports/           # CSB, OSHA, ILO incident investigations (21)
│   └── maintenance_data/           # Inspection records, sensor data, SKF guides (18)
├── ingestion/
│   ├── pdf_parser.py               # PyMuPDF extraction + manifest integration
│   ├── chunker.py                  # Industrial-aware text chunking (800 chars, 150 overlap)
│   ├── embedder.py                 # OpenAI embeddings → ChromaDB (incremental)
│   └── run_ingestion.py            # CLI entry point: parse → chunk → embed
├── rag_engine/
│   ├── retriever.py                # Semantic search with optional category filter
│   └── copilot.py                  # Four prompt modes: ask/rca/compliance/notify
├── api/
│   └── main.py                     # Six screen endpoints + system endpoints
├── frontend/                       # React 18 + Tailwind 3 + Vite dashboard
│   ├── src/
│   │   ├── App.jsx                 # Root: sidebar routing, layout shell
│   │   ├── api.js                  # Axios client wrapping all 8 API calls
│   │   ├── index.css               # Tailwind base + custom prose-industrial styles
│   │   ├── components/
│   │   │   ├── Sidebar.jsx         # Left nav with active highlight + notification badge
│   │   │   ├── Header.jsx          # Top bar with live KPI strip (chunks, docs, categories)
│   │   │   ├── AnswerPanel.jsx     # Markdown answer + collapsible sources
│   │   │   ├── ConfidenceBadge.jsx # HIGH/MEDIUM/LOW coloured indicator
│   │   │   ├── SourceCard.jsx      # Per-source card with category colour + URL
│   │   │   ├── Spinner.jsx         # Animated loading indicator
│   │   │   └── ErrorBanner.jsx     # Dismissible error display
│   │   ├── screens/
│   │       ├── UploadScreen.jsx    # Drag-drop, per-file progress, pipeline steps
│   │       ├── CopilotScreen.jsx   # Chat interface, dynamic sample questions, category filter
│   │       ├── AssetScreen.jsx     # Tag search, quick chips, grouped source list
│   │       ├── MaintenanceScreen.jsx # RCA form, structured section renderer
│   │       ├── ComplianceScreen.jsx  # Gap check, evidence pack renderer
│   │       ├── NotifyScreen.jsx    # Auto-load alert digest, severity badges
│   │       └── KnowledgeCaptureScreen.jsx # Speech-to-text, expert knowledge recording
│   ├── index.html
│   ├── vite.config.js              # Dev proxy: /api → localhost:8000
│   ├── tailwind.config.js          # Industrial dark palette
│   └── package.json
├── generate_pids.py                # Synthetic P&ID generator (ISA-5.1 symbols)
├── generate_pump_manuals.py        # Synthetic pump IOM generator
├── generate_inspection_docs.py     # Synthetic inspection records & sensor CSV generator
├── corpus_manifest.csv             # Full provenance: source URL, category, file size
├── requirements.txt                # Pinned Python dependencies
├── .env.example                    # Environment variable template
└── docs/                           # Architecture diagrams (coming soon)
```

---

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/economic-times-hackathon/industrial-knowledge-copilot.git
cd industrial-knowledge-copilot
git lfs pull                        # download the corpus PDFs (155 MB)
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set:
# GROQ_API_KEY=gsk_...        # Get free API key from https://console.groq.com
# EMBEDDING_BACKEND=fastembed  # Use local embeddings (recommended)
```

### 3. Run the ingestion pipeline (Fast Mode)

Indexes 2 high-quality documents for quick testing (~30 seconds):

```bash
python -m ingestion.run_ingestion
# Processes 2 documents → ~69 chunks → ready for queries
```

For more documents:
```bash
python -m ingestion.run_ingestion --max-total 16    # 16 documents (~5 minutes)
python -m ingestion.run_ingestion --full           # All 102 documents (~30 minutes)
```

Verify the index:
```bash
python -m ingestion.run_ingestion --stats-only
```

### 4. Start the backend API

```bash
python -m api.main
# API:      http://localhost:8000
# Swagger:  http://localhost:8000/docs
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
# UI: http://localhost:3000
```

### 6. Test Knowledge Capture

1. Navigate to the **Knowledge Capture** screen (7th tab)
2. Select equipment context (e.g., "Pump P-101A")
3. Click **Start Recording** and speak a procedure
4. Click **Stop Recording** and **Process Knowledge**
5. Your expert knowledge is now searchable in the AI Copilot!

The frontend proxies all `/api/*` calls to `http://localhost:8000` via Vite's dev proxy — no CORS setup needed.

---

## API Reference

All seven dashboard screens map to dedicated endpoints. One backend pipeline, seven specialized modes.

| Screen | Method | Endpoint | Description |
|---|---|---|---|
| Document Upload | `POST` | `/upload` | Ingest a PDF async — parse, chunk, embed |
| AI Copilot | `POST` | `/query` | Open Q&A with cited answers + confidence |
| Asset Explorer | `GET` | `/asset/{tag}` | Everything linked to an equipment tag |
| Maintenance Intel | `POST` | `/maintenance/rca` | RCA report — root causes + recommendations |
| Compliance Intel | `POST` | `/compliance` | Gap check + evidence pack against OISD/PESO |
| Notifications | `GET` | `/notifications` | Proactive alert digest (background scan) |
| **Knowledge Capture** | `POST` | `/capture/process` | **Convert expert speech to structured knowledge** |
| — | `GET` | `/health` | API health + key status |
| — | `GET` | `/corpus/stats` | Chunks indexed, breakdown by category |

**Interactive docs:** `http://localhost:8000/docs`

**Example — Knowledge Capture:**
```json
POST /capture/process
{
  "transcript": "To check pump bearing, first isolate pump with LOTO. Remove coupling guard. Listen for unusual noise. Feel bearing housing - should be warm but not hot. Check for vibration. Replace bearing if temperature over 180F.",
  "equipment_context": "P-101A",
  "session_type": "maintenance_procedure"
}
```

**Example — AI Copilot:**
```json
POST /query
{
  "question": "What caused the BP Texas City refinery explosion?",
  "category": "incident_reports",
  "top_k": 8
}
```

**Example — Maintenance RCA:**
```json
POST /maintenance/rca
{
  "equipment_tag": "P-101A",
  "symptom": "High bearing temperature alarm at 88°C, vibration trending up"
}
```

**Example — Compliance check:**
```json
POST /compliance
{
  "topic": "pressure relief valve testing and certification",
  "equipment_or_area": "CDU overhead system"
}
```

---

## Key Features

### ✅ **Zero-Cost Operation**
- **Local Embeddings**: FastEmbed runs offline, no API costs
- **Free LLM**: Groq provides free tier for LLaMA 3.3 70B
- **Browser Speech Recognition**: Web Speech API, zero setup

### ✅ **Mobile-First Design**  
- **Responsive Layout**: Works on phones, tablets, desktops
- **Google-Style Source Cards**: Clean, touch-friendly result display
- **Offline Capable**: Core functionality works without internet

### ✅ **Production Ready**
- **Real-time Speech Processing**: Live transcription with Web Speech API
- **Dynamic Sample Questions**: Auto-generated based on indexed content
- **Expert Knowledge Integration**: Captured knowledge appears in all searches
- **Background Document Processing**: Non-blocking PDF ingestion
- **Confidence Scoring**: HIGH/MEDIUM/LOW reliability indicators

### ✅ **Knowledge Preservation**
- **Digital Apprenticeship**: Prevent knowledge loss when experts retire
- **Equipment-Specific Tagging**: Link procedures to exact assets
- **Tacit Knowledge Capture**: Preserve "feel" and experience-based insights
- **Searchable Expert Procedures**: Instantly find captured knowledge

---

## Architecture

The Knowledge Capture design document is available at [`KNOWLEDGE_CAPTURE_MODULE.md`](./KNOWLEDGE_CAPTURE_MODULE.md) with complete implementation details, technical requirements, and deployment strategies.

---

## Demo

> Demo video and live link coming soon.

---

<div align="center">

Built for the **Economic Times Hackathon 2026**
Theme: Industrial Intelligence / Document Management / Knowledge Engineering / Quality

</div>
