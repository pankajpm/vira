"""End-to-end routines for transforming raw crawl data into the vector store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from langchain_core.documents import Document

from .chunker import chunk_documents
from ..vectorstore.manager import ingest_documents


def load_raw_jsonl(path: Path) -> List[dict[str, str]]:
    """Load JSONL records emitted by the crawler."""

    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def build_documents(records: Iterable[dict[str, str]]) -> List[Document]:
    """Transform chunked records into LangChain documents."""

    docs: List[Document] = []
    for record in records:
        metadata = {k: v for k, v in record.items() if k != "content"}
        for key, value in list(metadata.items()):
            if isinstance(value, dict):
                metadata.pop(key)
                for nested_key, nested_value in value.items():
                    metadata[f"{key}_{nested_key}"] = nested_value
        docs.append(Document(page_content=record.get("content", ""), metadata=metadata))
    return docs


def ingest_from_path(raw_path: Path) -> int:
    """Convenience function: load → chunk → embed from a raw JSONL path."""

    raw_records = load_raw_jsonl(raw_path)
    chunked = chunk_documents(raw_records)
    documents = build_documents(chunked)
    return ingest_documents(documents)


__all__ = ["load_raw_jsonl", "build_documents", "ingest_from_path"]

