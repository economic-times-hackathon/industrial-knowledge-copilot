<div align="center">

# Industrial Knowledge Intelligence
### Unified Asset & Operations Brain

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-RAG_Pipeline-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Neo4j](https://img.shields.io/badge/Neo4j-Knowledge_Graph-4581C3?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B35?style=for-the-badge&logo=databricks&logoColor=white)](https://trychroma.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT_4o-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)

---

![Status](https://img.shields.io/badge/Status-In_Development-yellow?style=flat-square)
![Hackathon](https://img.shields.io/badge/ET_Hackathon-2026-orange?style=flat-square)
![Theme](https://img.shields.io/badge/Theme-Industrial_Intelligence-blue?style=flat-square)
![Corpus](https://img.shields.io/badge/Corpus-72_Documents-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=flat-square)

</div>

---

## What This Is

Industrial plants — refineries, petrochemical facilities, steel plants — operate across 7 to 12 disconnected document systems. P&IDs live in one place, maintenance work orders in another, inspection records in a third, and regulatory submissions scattered across email archives. Maintenance teams make decisions without complete equipment history. Experienced engineers retire taking decades of undocumented knowledge with them.

**This platform is the fix.**

It ingests heterogeneous industrial documents — engineering drawings, OEM manuals, maintenance records, safety procedures, inspection reports, regulatory standards — extracts entities and relationships, builds a unified knowledge graph, and makes the collective intelligence of an entire plant queryable at the point of need, on any device, by any function.

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
Processes PDFs, P&IDs, scanned forms, spreadsheets, and engineering drawings. Extracts equipment tags, process parameters, regulatory references, personnel, and dates — building a unified knowledge graph that updates as new records arrive.

**Expert Knowledge Copilot**
RAG-powered conversational AI that answers operational, maintenance, and engineering queries across the full document corpus. Returns source citations, confidence scores, and direct links to originating documents. Works on mobile for field technicians.

**Maintenance Intelligence & RCA Agent**
Fuses work order history, equipment failure records, OEM manuals, and inspection findings to generate predictive maintenance recommendations and root cause analysis support.

**Quality & Regulatory Compliance Intelligence**
Maps OISD, PESO, Factories Act, and environmental standards against current procedures and inspection records. Identifies compliance gaps and auto-generates evidence packages for audits.

**Lessons Learned Engine**
Analyses incident reports, near-miss records, and audit findings across organisational history to identify systemic failure patterns and proactively surface warnings before similar conditions recur.

---

## Document Corpus

72 real public documents assembled as the knowledge base, spanning 5 categories:

| Category | Files | Key Sources |
|---|---|---|
| P&IDs & Process Diagrams | 7 | AIChE, LibreTexts, Honeywell, OSHA |
| OEM Equipment Manuals | 8 | Emerson/Fisher, Atlas Copco, Alfa Laval, SKF, Siemens |
| Regulatory & Standards | 30 | OISD.gov.in, PESO.gov.in, DGMS.gov.in, India Code |
| Incident & Safety Reports | 19 | CSB.gov, OSHA, ILO, DGMS |
| Maintenance & Inspection Data | 9 | SKF, NASA CMAPSS, OSHA, DGMS |

Full provenance in [`corpus_manifest.csv`](./corpus_manifest.csv).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Document Ingestion | PyMuPDF, Tesseract OCR, Unstructured.io |
| Embeddings | OpenAI text-embedding-3-large |
| Vector Store | ChromaDB |
| Knowledge Graph | Neo4j + custom industrial ontology |
| LLM / RAG | GPT-4o via LangChain |
| Backend API | FastAPI |
| Frontend | React + Tailwind CSS |
| Deployment | Docker Compose |

---

## Repository Structure

```
.
├── corpus/                    # Downloaded document corpus (72 PDFs)
│   ├── pids/                  # P&IDs and process diagrams
│   ├── oem_manuals/           # Equipment operation & maintenance manuals
│   ├── regulatory/            # OISD, PESO, DGMS, Factories Act, EPA
│   ├── incident_reports/      # CSB, OSHA, ILO incident investigations
│   └── maintenance_data/      # SKF, NASA CMAPSS, inspection references
├── corpus_manifest.csv        # Full provenance: source URL, category, size
├── ingestion/                 # Document parsing & entity extraction pipeline
├── knowledge_graph/           # Neo4j schema and graph construction
├── rag_engine/                # RAG pipeline and query handling
├── api/                       # FastAPI backend
├── frontend/                  # React UI
└── docs/                      # Architecture diagrams and design docs
```

---

## Getting Started

> Setup instructions will be added as components are built.

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
