"""Business plan parsing utilities supporting PDF, DOCX, and plain text."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Iterable

import docx
import fitz  # type: ignore

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class UnsupportedFormatError(ValueError):
    """Raised when a business plan is provided in an unsupported format."""


def _read_pdf(data: bytes) -> str:
    with fitz.open(stream=data, filetype="pdf") as doc:
        return "\n".join(page.get_text("text") for page in doc)


def _read_docx(data: bytes) -> str:
    with io.BytesIO(data) as buffer:
        document = docx.Document(buffer)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _read_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def extract_text(file_path: Path) -> str:
    """Extract textual content from a business plan file."""

    extension = file_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError(f"Unsupported file type: {extension}")

    data = file_path.read_bytes()
    if extension == ".pdf":
        return _read_pdf(data)
    if extension == ".docx":
        return _read_docx(data)
    return _read_txt(data)


def summarise_sections(text: str) -> dict[str, str]:
    """Heuristic section splitter to aid prompt construction."""

    sections = {
        "problem": [],
        "solution": [],
        "market": [],
        "team": [],
        "traction": [],
    }

    current_key = "problem"
    for line in text.splitlines():
        lower = line.lower()
        if "problem" in lower:
            current_key = "problem"
        elif "solution" in lower or "product" in lower:
            current_key = "solution"
        elif "market" in lower or "competition" in lower:
            current_key = "market"
        elif "team" in lower or "founder" in lower:
            current_key = "team"
        elif "traction" in lower or "metrics" in lower:
            current_key = "traction"
        sections[current_key].append(line.strip())

    return {key: "\n".join(value).strip() for key, value in sections.items()}


__all__ = ["extract_text", "summarise_sections", "UnsupportedFormatError", "SUPPORTED_EXTENSIONS"]

