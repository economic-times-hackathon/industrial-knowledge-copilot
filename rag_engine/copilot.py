"""
RAG engine — four prompt modes mapping to the six dashboard screens:

  ask()          → AI Copilot (open Q&A with citations)
  rca_query()    → Maintenance Intel (RCA-style structured output)
  compliance()   → Compliance Intel (gap check + evidence pack)
  notify_scan()  → Notifications (proactive pattern scan, no user question)

All four share the same backend pipeline:
  retrieve() → format_context() → LLM with mode-specific system prompt
"""
import os
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from rag_engine.retriever import retrieve, format_context

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
TOP_K     = int(os.getenv("TOP_K_RETRIEVAL", "8"))

# ── System prompts — one per screen ──────────────────────────────────────────

_COPILOT_PROMPT = """You are an Expert Industrial Knowledge Copilot for a petroleum refinery / petrochemical plant.
You have access to a curated knowledge base: P&IDs, OEM manuals, Indian regulatory standards (OISD, PESO, DGMS,
Factories Act), incident investigation reports (CSB, OSHA, ILO), and maintenance inspection records.

Answer the user's question using ONLY the provided context chunks.
If the context does not contain enough information, say so clearly.

Response format:
1. Direct answer (2-5 sentences)
2. Supporting details with inline citations [1], [2], etc.
3. Sources: [1] filename — description
4. Confidence: HIGH / MEDIUM / LOW

Rules:
- Never fabricate facts, specs, or regulatory requirements
- Always cite the originating document
- Flag discrepancies when sources conflict
- For safety-critical items (PSVs, LOTO, hazardous materials) always reference the relevant standard
"""

_RCA_PROMPT = """You are a Maintenance Intelligence and Root Cause Analysis (RCA) agent for an industrial plant.
You have access to work order history, equipment failure records, OEM manuals, inspection findings,
and incident reports.

Given the equipment tag, failure symptom, or maintenance question, produce a structured RCA report:

## Failure Summary
(1-2 sentences: what failed, when, observed symptoms)

## Probable Root Causes
(ranked list with supporting evidence from the context — cite [1], [2], etc.)

## Contributing Factors
(process conditions, maintenance gaps, human factors found in context)

## Recommended Actions
(immediate actions | short-term PM changes | long-term engineering fixes)

## Similar Historical Incidents
(any matching failure patterns from incident reports or work order history in context)

## Sources
[1] filename — description

Confidence: HIGH / MEDIUM / LOW

Rules:
- Base every finding on the retrieved context — never guess at root causes
- If insufficient data, state what additional information is needed
"""

_COMPLIANCE_PROMPT = """You are a Regulatory Compliance Intelligence agent for an Indian industrial plant.
You have access to OISD standards, PESO regulations, Factories Act 1948, Environment Protection Act 1986,
DGMS circulars, and plant inspection/procedure records.

Given the compliance topic or equipment/area in question, produce a structured compliance check:

## Applicable Regulations
(list the specific standards, clauses, and sections that apply — cite [1], [2], etc.)

## Current State Assessment
(what the retrieved context shows about current plant state or procedures)

## Compliance Gaps Identified
(specific gaps between regulatory requirement and current state)

## Evidence Pack
(list of documents from context that serve as compliance evidence, ready for audit)

## Recommended Corrective Actions
(prioritised by risk: CRITICAL / HIGH / MEDIUM / LOW)

## Sources
[1] filename — description

Confidence: HIGH / MEDIUM / LOW
"""

_NOTIFY_PROMPT = """You are a proactive Failure Pattern and Compliance Alert agent for an industrial plant.
Scan the provided context for patterns that warrant proactive alerts to operational teams.

Produce a structured alert digest:

## Active Risk Alerts
(equipment or process conditions matching known failure precursors — cite source [n])

## Compliance Flags
(regulatory requirements approaching due date or showing gaps)

## Lessons from Similar Incidents
(historical incidents relevant to current conditions)

## Recommended Immediate Actions
(what the on-shift team should check or escalate now)

## Sources
[1] filename — description

Keep output concise — this feeds a notification feed, not a report.
"""


# ── Shared internal runner ────────────────────────────────────────────────────

def _run(
    system_prompt: str,
    user_message: str,
    chunks,
) -> dict:
    """Shared LLM call used by all four modes."""
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ])
    answer_text = response.content

    sources = []
    for i, c in enumerate(chunks, 1):
        sources.append({
            "index": i,
            "filename": c.filename,
            "category": c.category,
            "source_url": c.source_url,
            "document_type": c.document_type,
            "description": c.description,
            "relevance_score": c.score,
        })

    confidence = "MEDIUM"
    for level in ["HIGH", "MEDIUM", "LOW"]:
        if f"Confidence: {level}" in answer_text or f"confidence: {level}" in answer_text.lower():
            confidence = level
            break

    return {
        "answer": answer_text,
        "sources": sources,
        "chunks": [{"chunk_id": c.chunk_id, "text": c.text, "score": c.score} for c in chunks],
        "confidence": confidence,
    }


# ── Public API — four modes ───────────────────────────────────────────────────

def ask(
    question: str,
    category_filter: Optional[str] = None,
    top_k: int = TOP_K,
    persist_dir: str = "./chroma_db",
    verbose: bool = False,
) -> dict:
    """
    AI Copilot — open Q&A with cited answers.
    Maps to: Dashboard > AI Copilot screen.
    """
    chunks = retrieve(question, top_k=top_k, category_filter=category_filter, persist_dir=persist_dir)
    if not chunks:
        return {"answer": "No relevant documents found.", "sources": [], "chunks": [], "confidence": "LOW"}

    if verbose:
        for c in chunks:
            print(f"  [{c.score:.3f}] {c.filename}")

    user_msg = f"CONTEXT:\n{format_context(chunks)}\n\nQUESTION: {question}\n\nAnswer with inline citations [1], [2], etc."
    return _run(_COPILOT_PROMPT, user_msg, chunks)


def rca_query(
    equipment_tag: str,
    symptom: str,
    top_k: int = TOP_K,
    persist_dir: str = "./chroma_db",
) -> dict:
    """
    Maintenance Intel — RCA-structured output joining work orders + manuals + incident history.
    Maps to: Dashboard > Maintenance Intel screen.
    """
    query = f"failure root cause {equipment_tag} {symptom} maintenance work order inspection"
    chunks = retrieve(query, top_k=top_k, persist_dir=persist_dir)
    if not chunks:
        return {"answer": "Insufficient maintenance data for this equipment.", "sources": [], "chunks": [], "confidence": "LOW"}

    user_msg = (
        f"CONTEXT:\n{format_context(chunks)}\n\n"
        f"EQUIPMENT TAG: {equipment_tag}\n"
        f"REPORTED SYMPTOM / FAILURE: {symptom}\n\n"
        f"Produce a structured RCA report as instructed."
    )
    return _run(_RCA_PROMPT, user_msg, chunks)


def compliance_check(
    topic: str,
    equipment_or_area: Optional[str] = None,
    top_k: int = TOP_K,
    persist_dir: str = "./chroma_db",
) -> dict:
    """
    Compliance Intel — gap check against Indian regulations + evidence pack generation.
    Maps to: Dashboard > Compliance Intel screen.
    """
    query = f"compliance regulation {topic} {equipment_or_area or ''} OISD PESO Factories Act inspection"
    chunks = retrieve(query, top_k=top_k, persist_dir=persist_dir)
    if not chunks:
        return {"answer": "No relevant regulatory context found.", "sources": [], "chunks": [], "confidence": "LOW"}

    user_msg = (
        f"CONTEXT:\n{format_context(chunks)}\n\n"
        f"COMPLIANCE TOPIC: {topic}\n"
        + (f"EQUIPMENT / AREA: {equipment_or_area}\n" if equipment_or_area else "")
        + "\nProduce a structured compliance check as instructed."
    )
    return _run(_COMPLIANCE_PROMPT, user_msg, chunks)


def notify_scan(
    context_hint: str = "safety incident failure compliance gap",
    top_k: int = 10,
    persist_dir: str = "./chroma_db",
) -> dict:
    """
    Notifications — proactive background scan, push-not-pull alert digest.
    Maps to: Dashboard > Notifications screen.
    Called by a background scheduler, not by user request.
    """
    chunks = retrieve(context_hint, top_k=top_k, persist_dir=persist_dir)
    if not chunks:
        return {"answer": "No alerts identified.", "sources": [], "chunks": [], "confidence": "LOW"}

    user_msg = (
        f"CONTEXT:\n{format_context(chunks)}\n\n"
        "Scan the above for active risks, compliance flags, and lessons from incidents. "
        "Produce a concise alert digest."
    )
    return _run(_NOTIFY_PROMPT, user_msg, chunks)
