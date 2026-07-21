<div align="center">

# Industrial Knowledge Intelligence
### Unified Asset & Operations Brain

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-RAG_Pipeline-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B35?style=for-the-badge&logo=databricks&logoColor=white)](https://trychroma.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![Gemini](https://img.shields.io/badge/Gemini-Embeddings-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)

---

![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![Hackathon](https://img.shields.io/badge/ET_Hackathon-2026-orange?style=flat-square)
![Theme](https://img.shields.io/badge/Theme-Industrial_Intelligence-blue?style=flat-square)
![Corpus](https://img.shields.io/badge/Corpus-102_Documents-green?style=flat-square)
![Chunks](https://img.shields.io/badge/Embedding-Gemini_text--embedding--004-4285F4?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=flat-square)

</div>

---

## What This Is

Industrial plants — refineries, petrochemical facilities, steel plants — operate across 7 to 12 disconnected document systems. P&IDs live in one place, maintenance work orders in another, inspection records in a third, and regulatory submissions scattered across email archives. Maintenance teams make decisions without complete equipment history. Experienced engineers retire taking decades of undocumented knowledge with them.

**This platform is the fix.**

It ingests heterogeneous industrial documents — engineering drawings, OEM manuals, maintenance records, safety procedures, inspection reports, regulatory standards — and makes their collective intelligence queryable at the point of need, on any device, by any function.

---

## The Problem (By the Numbers)

| Statistic | Source |
|---|---|
| 35% of working hours spent searching for information | McKinsey Global Survey 2024 |
| 7–12 disconnected document systems per large plant | NASSCOM-EY Study |
| 18–22% of unplanned downtime linked to knowledge fragmentation | BIS Research |
| 25% of experienced industrial engineers retiring this decade | Industry estimate |

---

## How It Works

Five of the six dashboard screens are the same backend pipeline wearing different prompts and output formats. That's what keeps this buildable in a hackathon window rather than six separate products.

```
User action → POST /endpoint
                 ↓
           retrieve() — semantic search over 13,779 chunks
                 ↓
           format_context() — ranked chunks + metadata
                 ↓
           LLM (GPT-4o) + mode-specific system prompt
                 ↓
           Structured response with citations
```

## The Six Screens

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
| Document Parsing | PyMuPDF 1.28 | Done |
| Chunking | LangChain RecursiveCharacterTextSplitter (800 chars / 150 overlap) | Done |
| Embeddings | Google Gemini `text-embedding-004` (768 dims, free tier) | Done |
| Vector Store | ChromaDB 1.1 — local persistence, incremental upsert | Done |
| LLM / RAG | Groq `llama-3.3-70b-versatile` via LangChain — 4 prompt modes | Done |
| Backend API | FastAPI 0.111 + Uvicorn — 6 screen endpoints | Done |
| Async Ingestion | FastAPI BackgroundTasks — upload → parse → embed | Done |
| Frontend | React 18 + Tailwind 3 + Vite — 6-screen dashboard | Done |
| Knowledge Graph | Neo4j — Asset Explorer graph traversal | Planned |
| Deployment | Docker Compose | Planned |

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
│   │   └── screens/
│   │       ├── UploadScreen.jsx    # Drag-drop, per-file progress, pipeline steps
│   │       ├── CopilotScreen.jsx   # Chat interface, starters, category filter
│   │       ├── AssetScreen.jsx     # Tag search, quick chips, grouped source list
│   │       ├── MaintenanceScreen.jsx # RCA form, structured section renderer
│   │       ├── ComplianceScreen.jsx  # Gap check, evidence pack renderer
│   │       └── NotifyScreen.jsx    # Auto-load alert digest, severity badges
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
# Open .env and set OPENAI_API_KEY=sk-...
```

### 3. Run the ingestion pipeline

Parses all 102 documents, chunks into 13,779 segments, indexes into ChromaDB (~5 min, costs ~$0.20 in embeddings):

```bash
python -m ingestion.run_ingestion
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

The frontend proxies all `/api/*` calls to `http://localhost:8000` via Vite's dev proxy — no CORS setup needed.

---

## API Reference

All six dashboard screens map to one endpoint each. One backend pipeline, six prompt modes.

| Screen | Method | Endpoint | Description |
|---|---|---|---|
| Document Upload | `POST` | `/upload` | Ingest a PDF async — parse, chunk, embed |
| AI Copilot | `POST` | `/query` | Open Q&A with cited answers + confidence |
| Asset Explorer | `GET` | `/asset/{tag}` | Everything linked to an equipment tag |
| Maintenance Intel | `POST` | `/maintenance/rca` | RCA report — root causes + recommendations |
| Compliance Intel | `POST` | `/compliance` | Gap check + evidence pack against OISD/PESO |
| Notifications | `GET` | `/notifications` | Proactive alert digest (background scan) |
| — | `GET` | `/health` | API health + key status |
| — | `GET` | `/corpus/stats` | Chunks indexed, breakdown by category |

**Interactive docs:** `http://localhost:8000/docs`

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

## Architecture

> Architecture diagram coming soon.

---

## Demo

> Demo video and live link coming soon.

---

<div align="center">

Built for the **Economic Times Hackathon 2026**
Theme: Industrial Intelligence / Document Management / Knowledge Engineering / Quality

</div>
