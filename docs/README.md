# VIRA Documentation

**Version:** 1.0  
**Last Updated:** November 25, 2025

Complete documentation for building and understanding the VIRA (Venture Intelligence Research Assistant) system from scratch.

---

## 📚 Documentation Structure

This documentation follows a **5-layer architecture** based on separation of concerns:

### Layer 1: Foundation (WHY & WHAT)
*Defines the problem, goals, and requirements*

- **[PRD-Complete.md](./01-FOUNDATION/PRD-Complete.md)** - Complete product requirements covering all 3 iterations
- **[Vision-And-Roadmap.md](./01-FOUNDATION/Vision-And-Roadmap.md)** - Strategic context and future plans

### Layer 2: Architecture (HOW - Design)
*System design decisions and component interactions*

- **[00-System-Architecture-Overview.md](./02-ARCHITECTURE/00-System-Architecture-Overview.md)** - High-level system map
- **[01-Data-Architecture.md](./02-ARCHITECTURE/01-Data-Architecture.md)** - Data flow & storage
- **[02-RAG-Architecture.md](./02-ARCHITECTURE/02-RAG-Architecture.md)** - Iteration 1: RAG Pipeline
- **[03-Agent-Architecture.md](./02-ARCHITECTURE/03-Agent-Architecture.md)** - Iteration 2: Reflective Agent
- **[04-Multi-Agent-Architecture.md](./02-ARCHITECTURE/04-Multi-Agent-Architecture.md)** - Iteration 3: Investment Committee
- **[05-Backend-Architecture.md](./02-ARCHITECTURE/05-Backend-Architecture.md)** - API & Services
- **[06-Frontend-Architecture.md](./02-ARCHITECTURE/06-Frontend-Architecture.md)** - UI Layer

### Layer 3: API & Contracts (HOW - Interfaces)
*Detailed interface specifications and contracts*

- **[01-REST-API-Specification.md](./03-API-CONTRACTS/01-REST-API-Specification.md)** - OpenAPI-style documentation
- **[02-Data-Schemas.md](./03-API-CONTRACTS/02-Data-Schemas.md)** - Data models & types
- **[03-Function-Contracts.md](./03-API-CONTRACTS/03-Function-Contracts.md)** - Internal module interfaces
- **[04-Integration-Points.md](./03-API-CONTRACTS/04-Integration-Points.md)** - External integrations

### Layer 4: Implementation (HOW - Build)
*Implementation details and workflows*

- **[01-Iteration1-Implementation.md](./04-IMPLEMENTATION/01-Iteration1-Implementation.md)** - RAG Pipeline
- **[02-Iteration2-Implementation.md](./04-IMPLEMENTATION/02-Iteration2-Implementation.md)** - Reflective Agent
- **[03-Iteration3-Implementation.md](./04-IMPLEMENTATION/03-Iteration3-Implementation.md)** - Multi-Agent (Spec)
- **[04-Agent-Workflows.md](./04-IMPLEMENTATION/04-Agent-Workflows.md)** - Detailed agent behaviors
- **[05-UI-Implementation.md](./04-IMPLEMENTATION/05-UI-Implementation.md)** - Frontend details
- **[06-Database-Implementation.md](./04-IMPLEMENTATION/06-Database-Implementation.md)** - Data persistence

### Layer 5: Operations (RUN & MAINTAIN)
*Running, monitoring, and maintaining the system*

- **[01-Getting-Started.md](./05-OPERATIONS/01-Getting-Started.md)** - Quick start guide
- **[02-Deployment-Guide.md](./05-OPERATIONS/02-Deployment-Guide.md)** - Production deployment
- **[03-Operations-Runbook.md](./05-OPERATIONS/03-Operations-Runbook.md)** - Day-to-day operations
- **[04-Evaluation-Framework.md](./05-OPERATIONS/04-Evaluation-Framework.md)** - Quality assurance
- **[05-Maintenance-Guide.md](./05-OPERATIONS/05-Maintenance-Guide.md)** - Long-term maintenance

### Reference
*Supporting documentation*

- **[Architecture-Decision-Records/](./06-REFERENCE/Architecture-Decision-Records/)** - ADRs for key decisions
- **[Glossary.md](./06-REFERENCE/Glossary.md)** - Terms & definitions
- **[FAQ.md](./06-REFERENCE/FAQ.md)** - Common questions
- **[Change-Log.md](./06-REFERENCE/Change-Log.md)** - Version history

---

## 🎯 Quick Navigation by Role

### For Product Managers / Leadership
**Start here to understand the product:**
1. [PRD-Complete.md](./01-FOUNDATION/PRD-Complete.md) - What we're building and why
2. [Vision-And-Roadmap.md](./01-FOUNDATION/Vision-And-Roadmap.md) - Strategic direction
3. [System Architecture Overview](./02-ARCHITECTURE/00-System-Architecture-Overview.md) - High-level design

### For New Engineers
**Start here to onboard:**
1. [Getting-Started.md](./05-OPERATIONS/01-Getting-Started.md) - Setup and first run
2. [System Architecture Overview](./02-ARCHITECTURE/00-System-Architecture-Overview.md) - Component map
3. [REST API Specification](./03-API-CONTRACTS/01-REST-API-Specification.md) - API contracts

### For Implementation Engineers
**Deep-dive into building:**
1. [Data Architecture](./02-ARCHITECTURE/01-Data-Architecture.md) - Data pipeline
2. [Iteration1 Implementation](./04-IMPLEMENTATION/01-Iteration1-Implementation.md) - RAG details
3. [Iteration2 Implementation](./04-IMPLEMENTATION/02-Iteration2-Implementation.md) - Agent details
4. [Function Contracts](./03-API-CONTRACTS/03-Function-Contracts.md) - Internal APIs

### For DevOps / SRE
**Focus on operations:**
1. [Deployment Guide](./05-OPERATIONS/02-Deployment-Guide.md) - Production setup
2. [Operations Runbook](./05-OPERATIONS/03-Operations-Runbook.md) - Day-to-day ops
3. [Maintenance Guide](./05-OPERATIONS/05-Maintenance-Guide.md) - Long-term care

---

## 📖 Reading Paths

### Path 1: Complete Understanding (Full Read)
For someone who needs to understand and justify the entire project:

```
01-FOUNDATION/
  ├── PRD-Complete.md (60 min)
  └── Vision-And-Roadmap.md (30 min)

02-ARCHITECTURE/
  ├── 00-System-Architecture-Overview.md (45 min)
  ├── 01-Data-Architecture.md (40 min)
  ├── 02-RAG-Architecture.md (30 min)
  ├── 03-Agent-Architecture.md (40 min)
  ├── 04-Multi-Agent-Architecture.md (35 min)
  ├── 05-Backend-Architecture.md (25 min)
  └── 06-Frontend-Architecture.md (25 min)

03-API-CONTRACTS/
  ├── 01-REST-API-Specification.md (30 min)
  ├── 02-Data-Schemas.md (20 min)
  ├── 03-Function-Contracts.md (25 min)
  └── 04-Integration-Points.md (15 min)

04-IMPLEMENTATION/
  ├── 01-Iteration1-Implementation.md (35 min)
  ├── 02-Iteration2-Implementation.md (40 min)
  ├── 03-Iteration3-Implementation.md (30 min)
  ├── 04-Agent-Workflows.md (30 min)
  ├── 05-UI-Implementation.md (25 min)
  └── 06-Database-Implementation.md (20 min)

05-OPERATIONS/
  ├── 01-Getting-Started.md (20 min)
  ├── 02-Deployment-Guide.md (30 min)
  ├── 03-Operations-Runbook.md (25 min)
  ├── 04-Evaluation-Framework.md (30 min)
  └── 05-Maintenance-Guide.md (20 min)

Total: ~10-12 hours for complete understanding
```

### Path 2: Quick Start (Minimum Viable Knowledge)
For someone who just needs to get started:

```
1. PRD-Complete.md (Skim: 15 min)
2. System-Architecture-Overview.md (Skim: 15 min)
3. Getting-Started.md (Read: 20 min)
4. REST-API-Specification.md (Reference: 10 min)

Total: ~1 hour to get running
```

### Path 3: Implementation Focus
For engineers building features:

```
1. PRD-Complete.md (Feature requirements)
2. System-Architecture-Overview.md (Component map)
3. Relevant Architecture doc (RAG, Agent, or Multi-Agent)
4. Relevant Implementation doc
5. Function-Contracts.md (Internal APIs)
6. Data-Schemas.md (Data models)

Total: ~3-4 hours per iteration
```

---

## 🏗️ Implementation Status

| Component | Iteration 1 | Iteration 2 | Iteration 3 |
|-----------|-------------|-------------|-------------|
| **RAG Pipeline** | ✅ Complete | N/A | N/A |
| **Reflection Agent** | N/A | ✅ Complete | N/A |
| **Research Agent** | N/A | ✅ Complete | N/A |
| **Multi-Agent Committee** | N/A | N/A | 📋 Spec Only |
| **Chainlit UI** | ✅ Complete | ✅ Complete | 📋 Planned |
| **React UI** | ✅ Complete | ✅ Complete | 📋 Planned |
| **Backend API** | ✅ Complete | ✅ Complete | 📋 Planned |
| **Data Pipeline** | ✅ Complete | ✅ Complete | ✅ Complete |

**Legend:**
- ✅ Complete: Implemented and operational
- 🔬 Testing: Implemented, validation in progress
- 📋 Spec Only: Specification complete, implementation pending
- ⚠️ Partial: Partially implemented

---

## 🔧 Technology Stack Summary

### Core Technologies
- **Language:** Python 3.10+
- **AI Framework:** LangChain, LangGraph
- **Vector DB:** ChromaDB
- **Backend:** FastAPI, Uvicorn
- **Frontend:** Chainlit (primary), React (alternative)
- **Database:** SQLite (prototype), PostgreSQL (future)
- **LLM:** OpenAI GPT-4o-mini
- **Embeddings:** OpenAI text-embedding-3-small

### External Services
- **OpenAI API:** LLM + Embeddings
- **Serper API:** Web Search (Iteration 2+)
- **LangSmith:** Observability (optional)

---

## 📊 Key Metrics & Performance

| Metric | Iteration 1 | Iteration 2 | Iteration 3 (Target) |
|--------|-------------|-------------|---------------------|
| **Latency** | <5s | 15-30s | 20-40s |
| **Cost per Query** | <$0.05 | <$0.15 | <$0.80 |
| **Accuracy** | 70%+ | 85%+ | 90%+ |
| **Use Case** | Screening | Diligence | Final Evaluation |

---

## 🤝 Contributing to Documentation

### Documentation Standards

1. **Inline Code Examples:** All architecture and implementation docs must include working code snippets
2. **Cross-References:** Link to related documents using relative paths
3. **Versioning:** Update version number and date when making changes
4. **Markdown Format:** Use standard GitHub-flavored Markdown
5. **Diagrams:** Use ASCII art or Mermaid for diagrams (keep portable)

### Document Template Structure

```markdown
# Document Title

**Version:** X.Y  
**Last Updated:** YYYY-MM-DD  
**Status:** Living Document / Stable / Deprecated

---

## Table of Contents
[Auto-generated or manual list]

---

## 1. Section Title
[Content with subsections]

---

## Document History
| Version | Date | Author | Changes |
|---------|------|--------|---------|

---

## Related Documents
- [Link to related doc](./path/to/doc.md)

---

**End of Document**
```

---

## 📝 Documentation Maintenance

### Review Schedule
- **Weekly:** Update implementation status
- **Monthly:** Review and update metrics
- **Quarterly:** Comprehensive review and restructure as needed
- **On Release:** Update all affected documents

### Ownership
- **Foundation Layer:** Product Team
- **Architecture Layer:** Engineering Leads
- **API Contracts:** Backend Team
- **Implementation:** Feature Teams
- **Operations:** DevOps/SRE

---

## 🆘 Getting Help

### Common Issues

**"Where do I start?"**
→ See [Quick Navigation by Role](#quick-navigation-by-role) above

**"How do I run VIRA locally?"**
→ [Getting-Started.md](./05-OPERATIONS/01-Getting-Started.md)

**"How does the RAG pipeline work?"**
→ [RAG-Architecture.md](./02-ARCHITECTURE/02-RAG-Architecture.md)

**"What are the API endpoints?"**
→ [REST-API-Specification.md](./03-API-CONTRACTS/01-REST-API-Specification.md)

**"How do I evaluate system performance?"**
→ [Evaluation-Framework.md](./05-OPERATIONS/04-Evaluation-Framework.md)

### Contact

- **Technical Questions:** Engineering team
- **Product Questions:** Product team
- **Operations Questions:** DevOps team

---

## 📚 External Resources

### LangChain / LangGraph
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Tutorial](https://python.langchain.com/docs/langgraph)

### Vector Databases
- [Chroma Docs](https://docs.trychroma.com/)
- [Pinecone Docs](https://docs.pinecone.io/)
- [Weaviate Docs](https://weaviate.io/developers/weaviate)

### Frontend Frameworks
- [Chainlit Docs](https://docs.chainlit.io/)
- [React Docs](https://react.dev/)

### APIs
- [OpenAI API](https://platform.openai.com/docs/)
- [Serper API](https://serper.dev/docs)

---

**Version:** 1.0  
**Last Updated:** November 25, 2025  
**Maintained by:** VIRA Documentation Team

