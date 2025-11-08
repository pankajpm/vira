"""Hybrid retrieval utilities combining semantic and keyword search."""

from __future__ import annotations

from typing import Dict, List

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma


class HybridRetriever:
    """Simple hybrid retriever weighting semantic and keyword results."""

    def __init__(self, vectorstore: Chroma, k: int = 6, bm25_k: int = 8, weight: float = 0.7) -> None:
        if not 0.0 <= weight <= 1.0:
            raise ValueError("weight must be between 0 and 1")

        self.vectorstore = vectorstore
        self.k = k
        self.bm25_k = bm25_k
        self.weight = weight
        store_snapshot = vectorstore.get(include=["metadatas", "documents"])
        documents = [
            Document(page_content=doc, metadata=metadata or {})
            for doc, metadata in zip(store_snapshot.get("documents", []), store_snapshot.get("metadatas", []))
            if doc
        ]
        self.keyword_retriever = BM25Retriever.from_documents(documents) if documents else None
        self.semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    def get_relevant_documents(self, query: str) -> List[Document]:
        semantic_docs = self.semantic_retriever.invoke(query)
        if self.keyword_retriever is not None:
            keyword_docs = self.keyword_retriever.invoke(query)[: self.bm25_k]
        else:
            keyword_docs = []

        scored: Dict[str, float] = {}
        for idx, doc in enumerate(semantic_docs):
            scored[doc.page_content] = scored.get(doc.page_content, 0.0) + self.weight * self._score(idx, len(semantic_docs))

        for idx, doc in enumerate(keyword_docs):
            scored[doc.page_content] = scored.get(doc.page_content, 0.0) + (1 - self.weight) * self._score(
                idx, len(keyword_docs)
            )

        combined_docs = {doc.page_content: doc for doc in semantic_docs + keyword_docs}
        ranked_contents = sorted(scored.items(), key=lambda item: item[1], reverse=True)
        top_n = max(self.k, self.bm25_k)
        return [combined_docs[content] for content, _ in ranked_contents[:top_n]]

    @staticmethod
    def _score(position: int, total: int) -> float:
        return 1 - (position / max(total, 1))


__all__ = ["HybridRetriever"]

