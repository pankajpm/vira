"""Helpers for creating and querying the Chroma vector store."""

from __future__ import annotations

from typing import Iterable

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from ..config.settings import get_settings


def _chunk_documents(documents: list[Document], batch_size: int) -> list[list[Document]]:
    return [documents[i : i + batch_size] for i in range(0, len(documents), batch_size)]


def build_embeddings() -> OpenAIEmbeddings:
    """Return an OpenAI embeddings client configured from settings."""

    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY must be configured to create embeddings.")
    return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)


def load_vectorstore() -> Chroma:
    """Instantiate (or create) a disk-backed Chroma store."""

    settings = get_settings()
    embeddings = build_embeddings()
    return Chroma(
        collection_name="a16z_content",
        embedding_function=embeddings,
        persist_directory=str(settings.vector_db_dir),
    )


def ingest_documents(documents: Iterable[Document], batch_size: int = 2000) -> int:
    """Ingest a batch of LangChain Documents into the vector store."""

    docs_list = list(documents)
    if not docs_list:
        return 0

    vectorstore = load_vectorstore()
    total = 0
    for batch in _chunk_documents(docs_list, batch_size):
        vectorstore.add_documents(batch)
        total += len(batch)
    vectorstore.persist()
    return total


__all__ = ["build_embeddings", "load_vectorstore", "ingest_documents"]

