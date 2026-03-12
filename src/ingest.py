"""
Document ingestion and chunking for RAG chatbot.

Reads PDFs (via PyPDF2) and markdown/text files from a folder,
splits them into ~300-token chunks with ~50-token overlap,
and preserves source metadata on each chunk.
"""

import os
import sys
import re
from pathlib import Path

from PyPDF2 import PdfReader


# ---------------------------------------------------------------------------
# Tokenization helpers (word-based approximation: 1 token ≈ 0.75 words)
# ---------------------------------------------------------------------------

WORDS_PER_TOKEN = 0.75  # conservative estimate

def _estimate_tokens(text: str) -> int:
    """Estimate token count from text (word-based approximation)."""
    return int(len(text.split()) / WORDS_PER_TOKEN)


def _chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """
    Split text into chunks of roughly `chunk_size` tokens with `overlap` tokens
    of overlap between consecutive chunks. Works on word boundaries.
    """
    words = text.split()
    chunk_words = int(chunk_size * WORDS_PER_TOKEN)
    overlap_words = int(overlap * WORDS_PER_TOKEN)

    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_words
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap_words

    return chunks


# ---------------------------------------------------------------------------
# PDF ingestion
# ---------------------------------------------------------------------------

def _ingest_pdf(filepath: str) -> list[dict]:
    """Read a PDF and return chunks with page-level metadata."""
    reader = PdfReader(filepath)
    filename = os.path.basename(filepath)
    chunks = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue

        page_chunks = _chunk_text(text)
        for i, chunk_text in enumerate(page_chunks):
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": filename,
                    "page": page_num,
                    "chunk_index": i,
                },
            })

    return chunks


# ---------------------------------------------------------------------------
# Markdown / text ingestion
# ---------------------------------------------------------------------------

def _extract_sections(text: str, filename: str) -> list[tuple[str, str]]:
    """
    Split markdown into (section_heading, body) pairs.
    Falls back to a single section for plain text files.
    """
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(text))

    if not matches:
        return [("(full document)", text)]

    sections = []
    for idx, match in enumerate(matches):
        heading = match.group(2).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            sections.append((heading, body))

    # Capture any text before the first heading
    preamble = text[: matches[0].start()].strip()
    if preamble:
        sections.insert(0, ("(preamble)", preamble))

    return sections


def _ingest_text(filepath: str) -> list[dict]:
    """Read a markdown or text file and return chunks with section metadata."""
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    if not text.strip():
        return []

    sections = _extract_sections(text, filename)
    chunks = []

    for section_name, section_body in sections:
        section_chunks = _chunk_text(section_body)
        for i, chunk_text in enumerate(section_chunks):
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": filename,
                    "section": section_name,
                    "chunk_index": i,
                },
            })

    return chunks


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_chunks(folder_path: str = "./docs") -> list[dict]:
    """
    Ingest all PDFs, markdown, and text files from `folder_path`.

    Returns a list of chunk dicts:
        {"text": "...", "metadata": {"source": ..., "page"|"section": ..., "chunk_index": ...}}
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    all_chunks = []
    files_processed = 0

    for filepath in sorted(folder.rglob("*")):
        if not filepath.is_file():
            continue

        ext = filepath.suffix.lower()

        if ext == ".pdf":
            chunks = _ingest_pdf(str(filepath))
        elif ext in (".md", ".txt", ".markdown"):
            chunks = _ingest_text(str(filepath))
        else:
            continue

        if chunks:
            files_processed += 1
            all_chunks.extend(chunks)

    return all_chunks


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "./docs"

    print(f"Ingesting documents from: {os.path.abspath(folder)}")
    print("-" * 50)

    chunks = get_chunks(folder)

    sources = {}
    for chunk in chunks:
        src = chunk["metadata"]["source"]
        sources[src] = sources.get(src, 0) + 1

    print(f"Documents processed: {len(sources)}")
    print(f"Total chunks created: {len(chunks)}")
    print()

    for src, count in sources.items():
        print(f"  {src}: {count} chunks")

    if chunks:
        print()
        sample = chunks[0]
        preview = sample["text"][:200] + "..." if len(sample["text"]) > 200 else sample["text"]
        print(f"Sample chunk (from {sample['metadata']['source']}):")
        print(f"  {preview}")


if __name__ == "__main__":
    main()
