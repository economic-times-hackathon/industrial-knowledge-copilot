"""
RAG engine — four prompt modes for the six dashboard screens.

LLM   : Groq (GROQ_API_KEY)   — free tier, llama-3.3-70b-versatile
Embed : Gemini (GOOGLE_API_KEY) — free tier, text-embedding-004

No OpenAI dependency.
"""
import os
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from rag_engine.retriever import retrieve, format_context

LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
TOP_K     = int(os.getenv("TOP_K_RETRIEVAL", "8"))


def _get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY not set. Get a free key at https://console.groq.com "
            "and add GROQ_API_KEY=gsk_... to your .env file."
        )
    return ChatGroq(api_key=api_key, model=LLM_MODEL, temperature=0)


# ── System prompts ────────────────────────────────────────────────────────────

_COPILOT_PROMPT = """You are an Expert Industrial Knowledge Copilot for a petroleum refinery / petrochemical plant.
You have access to a curated knowledge base: P&IDs, OEM manuals, Indian regulatory standards (OISD, PESO, DGMS,
Factories Act), incident investigation reports (CSB, OSHA, ILO), and maintenance inspection records.

For technical questions: Use the provided context chunks to give detailed, cited answers.
For general questions (greetings, general conversation): Respond helpfully as an industrial expert.
If no relevant context is found, provide general industrial knowledge while noting the limitation.

Response format for technical questions:
1. Direct answer (2-5 sentences)
2. Supporting details with inline citations [1], [2], etc.
3. Sources: [1] filename — description
4. Confidence: HIGH / MEDIUM / LOW

Response format for general questions:
Provide helpful, brief response as an industrial knowledge expert.

Rules:
- Never fabricate facts, specs, or regulatory requirements
- Always cite documents when using specific information
- For greetings/general chat, be friendly but concise
- Flag discrepancies when sources conflict
- For safety-critical items (PSVs, LOTO, hazardous materials) always reference the relevant standard
"""

_RCA_PROMPT = """You are a Maintenance Intelligence and Root Cause Analysis (RCA) agent for an industrial plant.
You have access to work order history, equipment failure records, OEM manuals, inspection findings,
and incident reports.

Given the equipment tag and failure symptom, produce a structured RCA report:

## Failure Summary
(1-2 sentences: what failed, when, observed symptoms)

## Probable Root Causes
(ranked list with supporting evidence — cite [1], [2], etc.)

## Contributing Factors
(process conditions, maintenance gaps, human factors found in context)

## Recommended Actions
(immediate actions | short-term PM changes | long-term engineering fixes)

## Similar Historical Incidents
(matching failure patterns from incident reports or work order history in context)

## Sources
[1] filename — description

Confidence: HIGH / MEDIUM / LOW

Rules:
- Base every finding on the retrieved context — never guess
- If insufficient data, state what additional information is needed
"""

_COMPLIANCE_PROMPT = """You are a Regulatory Compliance Intelligence agent for an Indian industrial plant.
You have access to OISD standards, PESO regulations, Factories Act 1948, Environment Protection Act 1986,
DGMS circulars, and plant inspection/procedure records.

Given the compliance topic, produce a structured compliance check:

## Applicable Regulations
(specific standards, clauses, sections — cite [1], [2], etc.)

## Current State Assessment
(what the retrieved context shows about current plant state or procedures)

## Compliance Gaps Identified
(specific gaps between regulatory requirement and current state)

## Evidence Pack
(documents from context that serve as compliance evidence for auditors)

## Recommended Corrective Actions
(prioritised by risk: CRITICAL / HIGH / MEDIUM / LOW)

## Sources
[1] filename — description

Confidence: HIGH / MEDIUM / LOW
"""

_NOTIFY_PROMPT = """You are a proactive Failure Pattern and Compliance Alert agent for an industrial plant.
Scan the provided context for patterns that warrant proactive alerts to operational teams.

## Active Risk Alerts
(equipment or process conditions matching known failure precursors — cite [n])

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


# ── Shared runner ─────────────────────────────────────────────────────────────

def _run(system_prompt: str, user_message: str, chunks) -> dict:
    llm = _get_llm()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ])
    answer_text = response.content

    sources = [
        {
            "index": i,
            "filename": c.filename,
            "category": c.category,
            "source_url": c.source_url,
            "document_type": c.document_type,
            "description": c.description,
            "relevance_score": c.score,
            "excerpt": c.text[:100],
        }
        for i, c in enumerate(chunks, 1)
    ]

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


# ── Public API ────────────────────────────────────────────────────────────────

def ask(question, category_filter=None, top_k=TOP_K, persist_dir="./chroma_db", verbose=False):
    """AI Copilot — open Q&A with cited answers."""
    
    # Check for simple greetings/general questions
    simple_questions = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
    if question.lower().strip() in simple_questions:
        return {
            "answer": f"Hello! I'm your Industrial Knowledge Copilot. I can help you with questions about safety procedures, equipment maintenance, regulatory compliance, and process operations. What would you like to know?",
            "sources": [], 
            "chunks": [], 
            "confidence": "HIGH"
        }
    
    chunks = retrieve(question, top_k=top_k, category_filter=category_filter, persist_dir=persist_dir)
    
    if not chunks:
        # For general industrial questions without specific context
        general_response = _run(_COPILOT_PROMPT, 
                              f"No specific documents found for this question: '{question}'. "
                              f"Provide helpful general industrial knowledge if appropriate, "
                              f"or suggest what kind of documents might contain this information.",
                              [])
        return {
            "answer": general_response["answer"], 
            "sources": [], 
            "chunks": [], 
            "confidence": "LOW"
        }
    
    if verbose:
        for c in chunks: print(f"  [{c.score:.3f}] {c.filename}")
        
    return _run(_COPILOT_PROMPT,
                f"CONTEXT:\n{format_context(chunks)}\n\nQUESTION: {question}\n\nAnswer with citations [1],[2],etc.",
                chunks)


def rca_query(equipment_tag, symptom, top_k=TOP_K, persist_dir="./chroma_db"):
    """Maintenance Intel — structured RCA report."""
    query = f"failure root cause {equipment_tag} {symptom} maintenance work order inspection"
    chunks = retrieve(query, top_k=top_k, persist_dir=persist_dir)
    if not chunks:
        return {"answer": "Insufficient maintenance data.", "sources": [], "chunks": [], "confidence": "LOW"}
    return _run(_RCA_PROMPT,
                f"CONTEXT:\n{format_context(chunks)}\n\n"
                f"EQUIPMENT TAG: {equipment_tag}\nSYMPTOM: {symptom}\n\nProduce RCA report.",
                chunks)


def compliance_check(topic, equipment_or_area=None, top_k=TOP_K, persist_dir="./chroma_db"):
    """Compliance Intel — gap check + evidence pack."""
    query = f"compliance {topic} {equipment_or_area or ''} OISD PESO Factories Act DGMS inspection"
    chunks = retrieve(query, top_k=top_k, persist_dir=persist_dir)
    if not chunks:
        return {"answer": "No relevant regulatory context found.", "sources": [], "chunks": [], "confidence": "LOW"}
    return _run(_COMPLIANCE_PROMPT,
                f"CONTEXT:\n{format_context(chunks)}\n\n"
                f"TOPIC: {topic}\n"
                + (f"AREA: {equipment_or_area}\n" if equipment_or_area else "")
                + "\nProduce compliance check.",
                chunks)


def notify_scan(context_hint="safety incident failure compliance gap", top_k=10, persist_dir="./chroma_db"):
    """Notifications — proactive background alert digest."""
    chunks = retrieve(context_hint, top_k=top_k, persist_dir=persist_dir)
    if not chunks:
        return {"answer": "No alerts identified.", "sources": [], "chunks": [], "confidence": "LOW"}
    return _run(_NOTIFY_PROMPT,
                f"CONTEXT:\n{format_context(chunks)}\n\nProduce alert digest.",
                chunks)
