"""
PDF Parser — extracts text from all corpus PDFs using PyMuPDF.
Handles scanned PDFs gracefully (returns empty text, flags for OCR).
"""
import fitz  # PyMuPDF
import csv
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedDocument:
    filename: str
    category: str
    folder_path: str
    source_url: str
    description: str
    document_type: str          # AUTHORITATIVE | EDUCATIONAL/SAMPLE
    text: str
    page_count: int
    file_size_kb: int
    is_scanned: bool = False    # True if OCR needed
    metadata: dict = field(default_factory=dict)


def load_manifest(manifest_path: str) -> list[dict]:
    """Load corpus_manifest.csv into a list of dicts."""
    records = []
    with open(manifest_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            records.append(row)
    return records


def extract_text_from_pdf(pdf_path: str) -> tuple[str, int, bool]:
    """
    Extract full text from a PDF using PyMuPDF.
    Returns (text, page_count, is_scanned).
    is_scanned=True when < 50 chars per page on average — likely image-only PDF.
    """
    try:
        doc = fitz.open(pdf_path)
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text"))
        doc.close()

        full_text = "\n\n".join(pages_text)
        page_count = len(pages_text)
        avg_chars = len(full_text) / max(page_count, 1)
        is_scanned = avg_chars < 50

        return full_text.strip(), page_count, is_scanned

    except Exception as e:
        print(f"  [WARN] Failed to parse {pdf_path}: {e}")
        return "", 0, True


def parse_corpus(
    corpus_root: str,
    manifest_path: str,
    verbose: bool = True,
) -> list[ParsedDocument]:
    """
    Parse all PDFs in the corpus using the manifest for metadata.
    Returns a list of ParsedDocument objects.
    """
    manifest = load_manifest(manifest_path)
    manifest_index = {row["filename"]: row for row in manifest}

    documents: list[ParsedDocument] = []
    corpus_root = Path(corpus_root)

    all_pdfs = list(corpus_root.rglob("*.pdf"))
    if verbose:
        print(f"Found {len(all_pdfs)} PDFs in corpus")

    for pdf_path in sorted(all_pdfs):
        filename = pdf_path.name
        meta = manifest_index.get(filename, {})

        # Determine category from folder name if not in manifest
        category = meta.get("category") or pdf_path.parent.name

        if verbose:
            print(f"  Parsing [{category}] {filename} ...", end=" ")

        text, page_count, is_scanned = extract_text_from_pdf(str(pdf_path))
        size_kb = int(pdf_path.stat().st_size / 1024)

        doc = ParsedDocument(
            filename=filename,
            category=category,
            folder_path=meta.get("folder_path", str(pdf_path.relative_to(corpus_root.parent))),
            source_url=meta.get("source_url", ""),
            description=meta.get("description", ""),
            document_type=meta.get("document_type", "UNKNOWN"),
            text=text,
            page_count=page_count,
            file_size_kb=size_kb,
            is_scanned=is_scanned,
            metadata={
                "filename": filename,
                "category": category,
                "source_url": meta.get("source_url", ""),
                "document_type": meta.get("document_type", "UNKNOWN"),
                "description": meta.get("description", ""),
                "page_count": page_count,
                "file_size_kb": size_kb,
                "is_scanned": is_scanned,
            },
        )
        documents.append(doc)

        if verbose:
            status = "SCANNED/EMPTY" if is_scanned else f"{page_count}p, {len(text):,} chars"
            print(status)

    scanned = sum(1 for d in documents if d.is_scanned)
    if verbose:
        print(f"\nParsed {len(documents)} documents — {scanned} flagged as scanned/empty")

    return documents


if __name__ == "__main__":
    root = Path(__file__).parent.parent
    docs = parse_corpus(
        corpus_root=str(root / "corpus"),
        manifest_path=str(root / "corpus_manifest.csv"),
    )
    print(f"\nTotal documents parsed: {len(docs)}")
    print(f"Total text extracted: {sum(len(d.text) for d in docs):,} characters")
