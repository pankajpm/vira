# Change Log

All notable changes to VIRA will be documented in this file.

---

## [1.0.0] - 2025-11-25

### Added
- Complete 5-layer documentation structure
- PRD covering all 3 iterations
- Architecture documentation (System, Data, RAG, Agents, Backend, Frontend)
- API contracts and data schemas
- Implementation guides for all iterations
- Operations runbook and evaluation framework
- Reference materials (Glossary, FAQ, Change Log)

---

## [0.2.0] - 2025-11-05

### Added (Iteration 2)
- Reflective agent with LangGraph
- Confidence scoring per claim
- Information gap identification
- Autonomous web research (Serper API)
- Iterative refinement workflow

### Changed
- Backend API now routes to Iteration 1 or 2 based on `ENABLE_REFLECTION` flag

---

## [0.1.0] - 2025-11-03

### Added (Iteration 1)
- RAG pipeline with hybrid retrieval
- Chroma vector database
- Business plan parsing (PDF/DOCX/TXT)
- Structured alignment analysis
- Chainlit UI with session management
- FastAPI backend
- SQLite database for sessions

---

## Future Releases

### [0.3.0] - Planned (Iteration 3)
- Multi-agent investment committee
- Consensus synthesis
- Strategic positioning recommendations
- Benchmark comparisons
- Interactive Q&A with agents

---

**Versioning:** Semantic versioning (MAJOR.MINOR.PATCH)
