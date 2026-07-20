"""
Text Chunker — splits parsed document text into overlapping chunks
suitable for embedding. Uses LangChain's RecursiveCharacterTextSplitter
with industrial-domain-aware separators.
"""
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from dataclasses import dataclass
from typing import Optional
import re

from ingestion.pdf_parser import ParsedDocument


@dataclass
class DocumentChunk:
    chunk_id: str           # "{filename}::chunk_{n}"
    filename: str
    category: str
    source_url: str
    document_type: str
    description: str
    text: str
    chunk_index: int
    total_chunks: int
    metadata: dict


# Separators tuned for industrial documents:
# section headings, numbered clauses, ISA tag patterns, table rows
INDUSTRIAL_SEPARATORS = [
    "\n\n\n",           # major section breaks
    "\n\n",             # paragraph breaks
    "\nSection ",
    "\nCHAPTER ",
    "\n4.","\n3.","\n2.","\n1.",  # numbered clauses
    "\nTable ",
    "\nFigure ",
    "\n•", "\n-",       # bullet lists
    "\n",
    ". ",
    " ",
]


def build_splitter(chunk_size: int = 800, chunk_overlap: int = 150) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=INDUSTRIAL_SEPARATORS,
        length_function=len,
        is_separator_regex=False,
    )


def clean_text(text: str) -> str:
    """Light cleaning: collapse excessive whitespace, remove control chars."""
    # Remove non-printable except newlines/tabs
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]", " ", text)
    # Collapse runs of blank lines to max 2
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    # Collapse runs of spaces
    text = re.sub(r"[ \t]{3,}", "  ", text)
    return text.strip()


def chunk_documents(
    documents: list[ParsedDocument],
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    skip_scanned: bool = True,
    min_chunk_chars: int = 100,
    verbose: bool = True,
) -> list[DocumentChunk]:
    """
    Split all documents into chunks. Skips scanned/empty PDFs by default.
    Returns flat list of DocumentChunk objects.
    """
    splitter = build_splitter(chunk_size, chunk_overlap)
    all_chunks: list[DocumentChunk] = []

    for doc in documents:
        if skip_scanned and doc.is_scanned:
            if verbose:
                print(f"  [SKIP] {doc.filename} — scanned/empty")
            continue

        if len(doc.text) < min_chunk_chars:
            if verbose:
                print(f"  [SKIP] {doc.filename} — too short ({len(doc.text)} chars)")
            continue

        cleaned = clean_text(doc.text)
        raw_chunks = splitter.split_text(cleaned)

        # Filter out trivially short chunks
        raw_chunks = [c for c in raw_chunks if len(c.strip()) >= min_chunk_chars]

        total = len(raw_chunks)
        for i, chunk_text in enumerate(raw_chunks):
            chunk_id = f"{doc.filename}::chunk_{i:04d}"
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                filename=doc.filename,
                category=doc.category,
                source_url=doc.source_url,
                document_type=doc.document_type,
                description=doc.description,
                text=chunk_text,
                chunk_index=i,
                total_chunks=total,
                metadata={
                    "chunk_id": chunk_id,
                    "filename": doc.filename,
                    "category": doc.category,
                    "source_url": doc.source_url,
                    "document_type": doc.document_type,
                    "description": doc.description,
                    "page_count": doc.page_count,
                    "chunk_index": i,
                    "total_chunks": total,
                },
            )
            all_chunks.append(chunk)

        if verbose:
            print(f"  Chunked {doc.filename}: {total} chunks")

    if verbose:
        print(f"\nTotal chunks produced: {len(all_chunks)}")

    return all_chunks


if __name__ == "__main__":
    from pathlib import Path
    from ingestion.pdf_parser import parse_corpus

    root = Path(__file__).parent.parent
    docs = parse_corpus(
        corpus_root=str(root / "corpus"),
        manifest_path=str(root / "corpus_manifest.csv"),
        verbose=False,
    )
    chunks = chunk_documents(docs, verbose=True)
    print(f"\nSample chunk from '{chunks[0].filename}':")
    print(chunks[0].text[:400])
