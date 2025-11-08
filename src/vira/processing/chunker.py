"""Utilities to convert raw scraped documents into embedding-friendly chunks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass(slots=True)
class ChunkParams:
    """Parameters controlling the chunking strategy."""

    chunk_size: int = 900
    chunk_overlap: int = 150
    separators: Sequence[str] = (
        "\n\n",
        "\n",
        ".",
        "?",
        "!",
        " ",
    )


def build_splitter(params: ChunkParams | None = None) -> RecursiveCharacterTextSplitter:
    """Return a LangChain splitter configured with sensible defaults."""

    params = params or ChunkParams()
    return RecursiveCharacterTextSplitter(
        chunk_size=params.chunk_size,
        chunk_overlap=params.chunk_overlap,
        separators=list(params.separators),
        length_function=len,
        is_separator_regex=False,
    )


def chunk_document(content: str, metadata: dict[str, str], splitter: RecursiveCharacterTextSplitter | None = None) -> list[dict[str, str]]:
    """Chunk a single document body into records suitable for embeddings."""

    splitter = splitter or build_splitter()
    chunks = splitter.split_text(content)
    results: list[dict[str, str]] = []
    for index, chunk in enumerate(chunks):
        record = {"content": chunk, "chunk_index": str(index)}
        record.update(metadata)
        results.append(record)
    return results


def chunk_documents(records: Iterable[dict[str, str]], splitter: RecursiveCharacterTextSplitter | None = None) -> list[dict[str, str]]:
    """Chunk multiple records and flatten the result list."""

    splitter = splitter or build_splitter()
    all_chunks: list[dict[str, str]] = []
    for record in records:
        metadata = {k: v for k, v in record.items() if k != "content"}
        all_chunks.extend(chunk_document(record.get("content", ""), metadata, splitter))
    return all_chunks


__all__ = ["ChunkParams", "build_splitter", "chunk_document", "chunk_documents"]

