# ADR-001: Use Chroma for Vector Database

**Date:** 2025-11-01  
**Status:** Accepted  
**Context:** Need vector database for semantic search

---

## Decision
Use Chroma DB for MVP vector storage.

## Rationale
- **Simplicity:** Pure Python, no Docker required
- **Cost:** Free (self-hosted)
- **Speed:** <100ms queries, sufficient for prototype
- **Portability:** Easy migration path to Pinecone/Weaviate

## Consequences
✅ Faster prototyping  
✅ Lower costs  
⚠️ Single-instance only (no horizontal scaling)  
⚠️ Manual backups required

## Alternatives Considered
- **Pinecone:** Better scaling, but $70/month cost
- **Weaviate:** More features, but requires Docker setup

---

**Future:** Migrate to Pinecone for production scaling
