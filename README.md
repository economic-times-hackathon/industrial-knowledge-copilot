<div align="center">

# Industrial Knowledge Intelligence
### Unified Asset & Operations Brain

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-RAG_Pipeline-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B35?style=for-the-badge&logo=databricks&logoColor=white)](https://trychroma.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT_4o-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)

---

![Status](https://img.shields.io/badge/Status-In_Development-yellow?style=flat-square)
![Hackathon](https://img.shields.io/badge/ET_Hackathon-2026-orange?style=flat-square)
![Theme](https://img.shields.io/badge/Theme-Industrial_Intelligence-blue?style=flat-square)
![Corpus](https://img.shields.io/badge/Corpus-102_Documents-green?style=flat-square)
![Chunks](https://img.shields.io/badge/Indexed-13%2C779_Chunks-blue?style=flat-square)
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

## Core Capabilities

**Universal Document Ingestion**
Parses PDFs across all industrial document types using PyMuPDF. Chunks intelligently with industrial-domain-aware separators, embeds with OpenAI, and indexes into ChromaDB — producing 13,779 searchable chunks from 100 documents across 7.9 million characters of text.

**Expert Knowledge Copilot**
RAG-powered conversational AI that answers operational, maintenance, and engineering queries across the full document corpus. Returns grounded answers with source citations, confidence scores, and direct links to originating documents.

**Maintenance Intelligence & RCA Agent**
Fuses work order history, equipment failure records, OEM manuals, and inspection findings to generate predictive maintenance recommendations and root cause analysis support.

**Quality & Regulatory Compliance Intelligence**
Maps OISD, PESO, Factories Act, and environmental standards against current procedures and inspection records. Identifies compliance gaps and flags quality deviations before they escalate.

**Lessons Learned Engine**
Analyses incident reports, near-miss records, and audit findings to identify systemic failure patterns and proactively surface warnings before similar conditions recur.

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
| Chunking | LangChain RecursiveCharacterTextSplitter | Done |
| Embeddings | OpenAI `text-embedding-3-small` | Done |
| Vector Store | ChromaDB 1.1 (local persistence) | Done |
| LLM / RAG | GPT-4o via LangChain | Done |
| Backend API | FastAPI 0.111 + Uvicorn | Done |
| Frontend | React + Tailwind CSS | In progress |
| Knowledge Graph | Neo4j + industrial ontology | Planned |
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
│   ├── retriever.py                # Semantic search with category filtering
│   └── copilot.py                  # RAG chain: retrieve → GPT-4o → cited answer
├── api/
│   └── main.py                     # FastAPI: POST /query, GET /corpus/stats, GET /health
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
git lfs pull                        # download the corpus PDFs
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# edit .env — add your OPENAI_API_KEY
```

### 3. Run the ingestion pipeline

Parses all 102 documents, chunks them into 13,779 segments, and indexes embeddings into ChromaDB:

```bash
python -m ingestion.run_ingestion
```

Check the index afterwards:

```bash
python -m ingestion.run_ingestion --stats-only
```

### 4. Start the API

```bash
python -m api.main
# API runs at http://localhost:8000
# Docs at  http://localhost:8000/docs
```

### 5. Query the copilot

```bash
# POST /query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are OISD requirements for emergency siren codes?"}'
```

Or use the interactive docs at `http://localhost:8000/docs`.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check — confirms API and key status |
| `GET` | `/corpus/stats` | Total chunks indexed, breakdown by category |
| `GET` | `/corpus/categories` | List available document categories |
| `POST` | `/query` | Ask the knowledge copilot |

**Query request body:**
```json
{
  "question": "What caused the BP Texas City refinery explosion?",
  "category": "incident_reports",
  "top_k": 8
}
```

**Response includes:** grounded answer, confidence level (HIGH/MEDIUM/LOW), and numbered source citations with filename, category, and source URL.

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
