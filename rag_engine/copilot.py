"""
Expert Knowledge Copilot — the main RAG chain.
Takes a user question, retrieves relevant chunks, and generates a
grounded answer with source citations and confidence indication.
"""
import os
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from rag_engine.retriever import retrieve, format_context, RetrievedChunk

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
TOP_K     = int(os.getenv("TOP_K_RETRIEVAL", "8"))

SYSTEM_PROMPT = """You are an Expert Industrial Knowledge Copilot for a petroleum refinery / petrochemical plant.
You have access to a curated knowledge base containing:
- P&IDs and process diagrams
- OEM equipment manuals (pumps, compressors, valves, heat exchangers)
- Indian regulatory standards (OISD, PESO, DGMS, Factories Act, EPA)
- Incident investigation reports (CSB, OSHA, ILO)
- Maintenance inspection records and sensor data

Answer the user's question using ONLY the provided context chunks.
If the context does not contain enough information to answer confidently, say so clearly.

Response format:
1. Direct answer first (2-5 sentences)
2. Supporting details with inline citations: [1], [2], etc. referencing the source numbers
3. Source list at the end: "Sources: [1] filename — description"
4. Confidence: HIGH / MEDIUM / LOW based on how directly the context answers the question

Rules:
- Never fabricate facts, specifications, or regulatory requirements
- Always cite which document the information comes from
- If multiple sources say different things, flag the discrepancy
- For safety-critical information (PSVs, LOTO, hazardous materials), always include the relevant standard reference
"""


def ask(
    question: str,
    category_filter: Optional[str] = None,
    top_k: int = TOP_K,
    persist_dir: str = "./chroma_db",
    verbose: bool = False,
) -> dict:
    """
    Main RAG query function.

    Args:
        question:        User's question in natural language
        category_filter: Optionally restrict retrieval to one category
        top_k:           Number of context chunks to retrieve
        persist_dir:     ChromaDB location

    Returns:
        dict with keys: answer, sources, chunks, confidence
    """
    # Step 1: Retrieve relevant chunks
    chunks = retrieve(
        query=question,
        top_k=top_k,
        category_filter=category_filter,
        persist_dir=persist_dir,
    )

    if not chunks:
        return {
            "answer": "No relevant documents found in the knowledge base for this query.",
            "sources": [],
            "chunks": [],
            "confidence": "LOW",
        }

    if verbose:
        print(f"  Retrieved {len(chunks)} chunks")
        for c in chunks:
            print(f"    [{c.score:.3f}] {c.filename} ({c.category})")

    # Step 2: Build context
    context = format_context(chunks)

    # Step 3: Query LLM
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    user_message = f"""CONTEXT:
{context}

QUESTION: {question}

Answer based on the context above. Include source citations [1], [2], etc."""

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    answer_text = response.content

    # Build source list
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

    # Extract confidence from the answer (LLM includes it per system prompt)
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


if __name__ == "__main__":
    import json

    questions = [
        "What are the OISD requirements for emergency siren codes at oil and gas installations?",
        "What causes mechanical seal failure in centrifugal pumps and how is it diagnosed?",
        "What were the root causes of the BP Texas City refinery explosion?",
        "What is the recommended bearing oil change interval for process pumps?",
        "What are the PESO regulations for pressure vessel inspection in India?",
    ]

    for q in questions:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        print("="*70)
        result = ask(q, verbose=True)
        print(result["answer"])
        print(f"\nSources used: {[s['filename'] for s in result['sources'][:3]]}")
        print(f"Confidence: {result['confidence']}")
