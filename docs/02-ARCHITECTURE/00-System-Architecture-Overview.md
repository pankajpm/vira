# VIRA: System Architecture Overview

**Version:** 1.0  
**Last Updated:** November 25, 2025  
**Status:** Living Document

---

## Table of Contents

1. [System Topology](#1-system-topology)
2. [Component Inventory](#2-component-inventory)
3. [Technology Stack](#3-technology-stack)
4. [Deployment Architecture](#4-deployment-architecture)
5. [Architecture Decision Records](#5-architecture-decision-records)
6. [Data Flow](#6-data-flow)
7. [Integration Points](#7-integration-points)

---

## 1. System Topology

### 1.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          VIRA SYSTEM ARCHITECTURE                         │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  User Interface │
├─────────────────┤
│ • Chainlit UI   │  ← Primary (Chat-based, Session Management)
│ • React UI      │  ← Alternative (Component-based, Modern)
│ • Streamlit     │  ← Legacy (Simple, Prototype)
└────────┬────────┘
         │ HTTP / WebSocket
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND API LAYER                            │
├─────────────────────────────────────────────────────────────────────┤
│  FastAPI Application (uvicorn)                                      │
│  ├── /analyze (POST)           - Iteration 1/2 analysis            │
│  ├── /analyze/upload (POST)    - File upload support               │
│  ├── /api/sessions (CRUD)      - Session management                │
│  └── /ws/sessions/{id}         - WebSocket real-time updates       │
└────────┬─────────────────────────────────┬──────────────────────────┘
         │                                  │
         ▼                                  ▼
┌─────────────────────┐          ┌────────────────────────┐
│  ANALYZER LAYER     │          │  DATA PERSISTENCE      │
├─────────────────────┤          ├────────────────────────┤
│ Iteration 1:        │          │ SQLite Database        │
│ - AlignmentAnalyzer │          │ ├── sessions           │
│   (RAG Pipeline)    │          │ ├── messages           │
│                     │          │ ├── business_plans     │
│ Iteration 2:        │          │ └── analyses           │
│ - ReflectiveAnalyzer│          │                        │
│   (LangGraph Agent) │          │ Files (./data/)        │
│                     │          │ ├── raw/ (JSONL)       │
│ Iteration 3:        │          │ └── processed/         │
│ - CommitteeAnalyzer │          │     └── chroma/        │
│   (Multi-Agent)     │          │         (Vector DB)    │
└────────┬────────────┘          └────────────────────────┘
         │
         ├─────────────────────────┬─────────────────────────┐
         ▼                         ▼                         ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ RETRIEVAL LAYER  │    │  AGENT LAYER     │    │ BUSINESS PLAN    │
├──────────────────┤    ├──────────────────┤    │ PROCESSING       │
│ HybridRetriever  │    │ Reflection Agent │    ├──────────────────┤
│ ├── Semantic     │    │ Research Agent   │    │ • PDF Parser     │
│ │   (Chroma)     │    │ Synthesis Agent  │    │ • DOCX Parser    │
│ └── Keyword      │    │ Strategy Agent   │    │ • Text Splitter  │
│     (BM25)       │    │ Dialogue Agent   │    │ • Summarizer     │
└────────┬─────────┘    └────────┬─────────┘    └──────────────────┘
         │                       │
         ▼                       ▼
┌───────────────────────────────────────────────────────────────────┐
│                     VECTOR STORE LAYER                             │
├───────────────────────────────────────────────────────────────────┤
│  Chroma Vector Database (./data/processed/chroma/)                │
│  ├── Collection: a16z_content (~10,000 chunks)                    │
│  ├── Embeddings: OpenAI text-embedding-3-small (1536 dims)       │
│  └── Metadata: url, title, chunk_index, scraped_at               │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                     INGESTION PIPELINE                             │
├───────────────────────────────────────────────────────────────────┤
│  Step 1: Web Scraping (Scrapy Spider)                            │
│  ├── Crawl a16z.com (~400 pages)                                 │
│  ├── Extract: title, content, metadata                           │
│  └── Output: ./data/raw/a16z_raw.jsonl                          │
│                                                                   │
│  Step 2: Processing (Text Chunking)                              │
│  ├── Load JSONL records                                          │
│  ├── Chunk text (900 chars, 150 overlap)                        │
│  └── Enrich metadata                                             │
│                                                                   │
│  Step 3: Embedding & Indexing                                    │
│  ├── Generate embeddings (OpenAI API)                           │
│  ├── Store in Chroma                                             │
│  └── Build HNSW index                                            │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                              │
├───────────────────────────────────────────────────────────────────┤
│  • OpenAI API (GPT-4o-mini, text-embedding-3-small)              │
│  • Serper API (Google Search - Iteration 2+)                     │
│  • LangSmith (Observability - Optional)                          │
│  • Future: Crunchbase, LinkedIn, GitHub APIs (Iteration 3)       │
└───────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Interactions

**Request Flow (Iteration 1):**
```
User → Chainlit UI → FastAPI (/analyze) → AlignmentAnalyzer
                                          ↓
                                     HybridRetriever
                                          ↓
                                     Chroma (top-6 docs)
                                          ↓
                                     LLM (GPT-4o-mini)
                                          ↓
                                     Structured Response
                                          ↓
User ← Chainlit UI ← FastAPI ← AlignmentResponse (JSON)
```

**Request Flow (Iteration 2):**
```
User → Chainlit UI → FastAPI (/analyze) → ReflectiveAnalyzer
                                          ↓
                                     LangGraph Workflow
                                          ↓
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                              ▼
            Initial Analysis                              Reflection Node
            (RAG Pipeline)                                      ↓
                   │                                   Assess Confidence
                   │                                   Identify Gaps
                   │                                          ↓
                   │                                   Should Research?
                   │                                      ↓ Yes
                   │                                Research Node
                   │                                (Serper API)
                   │                                      ↓
                   └────────────────→ Regeneration Node
                                           ↓
User ← Chainlit UI ← FastAPI ← Enhanced AlignmentResponse + Metadata
```

---

## 2. Component Inventory

### 2.1 Core Modules

| Module | Path | Responsibility | Lines of Code | Status |
|--------|------|----------------|---------------|--------|
| **Ingestion** | `src/vira/ingestion/` | Web scraping, content extraction | ~300 | ✅ Complete |
| **Processing** | `src/vira/processing/` | Text chunking, pipeline orchestration | ~400 | ✅ Complete |
| **Vectorstore** | `src/vira/vectorstore/` | Chroma DB management, embedding | ~200 | ✅ Complete |
| **Retrieval** | `src/vira/retrieval/` | Hybrid retrieval (semantic + BM25) | ~250 | ✅ Complete |
| **RAG Pipeline** | `src/vira/rag/` | Iteration 1 alignment analysis | ~350 | ✅ Complete |
| **Agents** | `src/vira/agents/` | Iteration 2-3 agentic workflows | ~800 | ✅ Iter 2 Complete |
| **Backend API** | `src/vira/backend/` | FastAPI routes, models | ~600 | ✅ Complete |
| **UI (Chainlit)** | `src/vira/ui/` | Chat interface, session management | ~1800 | ✅ Complete |
| **Business Plan** | `src/vira/business_plan/` | PDF/DOCX parsing, summarization | ~150 | ✅ Complete |
| **Config** | `src/vira/config/` | Settings, environment management | ~100 | ✅ Complete |

**Total Codebase:** ~5,000 lines of Python (excluding tests, docs)

### 2.2 Detailed Component Breakdown

#### Ingestion Layer (`src/vira/ingestion/`)

**Files:**
- `spider.py`: Scrapy spider for a16z.com crawling
- `runner.py`: CLI entry point for crawl execution
- `crawl_config.py`: Configuration loader (YAML parsing)

**Key Functions:**
```python
class A16ZSpider(scrapy.Spider):
    """Crawl a16z.com and extract content."""
    name = 'a16z'
    allowed_domains = ['a16z.com']
    
    def parse(self, response):
        """Extract title, content, metadata from page."""
        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'content': self.extract_body(response),
            'scraped_at': datetime.utcnow().isoformat()
        }
```

**Dependencies:** scrapy, beautifulsoup4, PyYAML

---

#### Processing Layer (`src/vira/processing/`)

**Files:**
- `pipeline.py`: Main processing orchestration
- `chunker.py`: Text splitting utilities
- `cli.py`: Command-line interface

**Key Functions:**
```python
def load_raw_jsonl(path: Path) -> list[dict]:
    """Load JSONL records from disk."""
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def chunk_documents(
    records: list[dict], 
    chunk_size: int = 900, 
    overlap: int = 150
) -> list[dict]:
    """Split documents into retrievable chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", "?", "!", " "]
    )
    # ... chunking logic
```

**Dependencies:** langchain, tiktoken

---

#### Vector Store Layer (`src/vira/vectorstore/`)

**Files:**
- `manager.py`: Chroma DB wrapper and utilities

**Key Functions:**
```python
class VectorStoreManager:
    """Manage Chroma vector database."""
    
    def __init__(self, persist_directory: Path):
        self.client = chromadb.PersistentClient(
            path=str(persist_directory)
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        self.vectorstore = Chroma(
            client=self.client,
            collection_name="a16z_content",
            embedding_function=self.embeddings
        )
    
    def ingest_documents(self, documents: list[Document]):
        """Batch embed and store documents."""
        batch_size = 2000
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            self.vectorstore.add_documents(batch)
```

**Dependencies:** chromadb, langchain-openai

---

#### Retrieval Layer (`src/vira/retrieval/`)

**Files:**
- `hybrid.py`: Hybrid retriever (semantic + keyword)

**Key Functions:**
```python
class HybridRetriever:
    """Combine semantic and keyword search."""
    
    def __init__(
        self, 
        vectorstore: Chroma, 
        bm25_weight: float = 0.3,
        top_k: int = 6
    ):
        self.vectorstore = vectorstore
        self.bm25_weight = bm25_weight
        self.semantic_weight = 1.0 - bm25_weight
        self.top_k = top_k
        
        # Build BM25 index from all documents
        all_docs = vectorstore.get(include=["documents", "metadatas"])
        self.bm25 = BM25Okapi([doc.split() for doc in all_docs["documents"]])
    
    def retrieve(self, query: str, **kwargs) -> list[Document]:
        """Hybrid retrieval with score fusion."""
        # Semantic search (70%)
        semantic_docs = self.vectorstore.similarity_search_with_score(
            query, k=self.top_k * 2
        )
        
        # Keyword search (30%)
        bm25_scores = self.bm25.get_scores(query.split())
        
        # Fuse scores and re-rank
        final_docs = self._fuse_scores(semantic_docs, bm25_scores)
        return final_docs[:self.top_k]
```

**Dependencies:** rank-bm25

---

#### RAG Pipeline (`src/vira/rag/`)

**Files:**
- `pipeline.py`: Iteration 1 alignment analyzer

**Key Classes:**
```python
class AlignmentAnalyzer:
    """Iteration 1: RAG-based alignment analysis."""
    
    def __init__(self):
        self.vectorstore = VectorStoreManager(settings.vector_db_dir)
        self.retriever = HybridRetriever(self.vectorstore.vectorstore)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0  # Deterministic for consistency
        )
        self.prompt_template = load_alignment_prompt()
    
    def analyze(
        self, 
        company_name: str, 
        plan_summary: str, 
        query: str
    ) -> tuple[AlignmentResponse, list[Document]]:
        """
        Run RAG analysis pipeline.
        
        Returns:
            (AlignmentResponse, retrieved_documents)
        """
        # Step 1: Retrieve relevant docs
        docs = self.retriever.retrieve(query)
        
        # Step 2: Format context
        context = self._format_context(docs)
        
        # Step 3: Generate analysis
        prompt = self.prompt_template.format(
            company_name=company_name,
            plan_summary=plan_summary,
            context=context
        )
        
        response = self.llm.invoke(prompt)
        
        # Step 4: Parse structured output
        alignment_response = self._parse_response(response.content)
        
        return alignment_response, docs
```

**Output Schema:**
```python
class AlignmentResponse(BaseModel):
    """Structured alignment analysis output."""
    aligns: list[AlignmentPoint]     # Matches (3-4 items)
    gaps: list[AlignmentPoint]       # Gaps (3-4 items)
    summary: str                     # Neutral summary
    sources: list[str]               # Source URLs
```

---

#### Agent Layer (`src/vira/agents/`)

**Files:**
- `state.py`: LangGraph state definitions
- `graph.py`: Workflow orchestration
- `analyzer.py`: ReflectiveAnalyzer (Iteration 2 entry point)
- `reflection.py`: Confidence assessment, gap identification
- `research.py`: Web search tool, query generation

**LangGraph Workflow:**
```python
from langgraph.graph import StateGraph, END
from vira.agents.state import AgentState

def create_reflection_graph() -> StateGraph:
    """Build Iteration 2 LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("initial_analysis", initial_analysis_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("research", research_node)
    workflow.add_node("regeneration", regeneration_node)
    
    # Set entry point
    workflow.set_entry_point("initial_analysis")
    
    # Add edges
    workflow.add_edge("initial_analysis", "reflection")
    
    # Conditional edge: research only if needed
    workflow.add_conditional_edges(
        "reflection",
        should_research,  # Decision function
        {
            True: "research",
            False: END
        }
    )
    
    workflow.add_edge("research", "regeneration")
    workflow.add_edge("regeneration", "reflection")  # Loop back
    
    return workflow.compile()

def should_research(state: AgentState) -> bool:
    """Decide if research is needed."""
    return (
        state.overall_confidence < 0.7 and 
        state.iteration_count < 2 and
        len(state.reflection_result.information_gaps) > 0
    )
```

**Reflection Logic:**
```python
def reflect_on_explanation(
    explanation: AlignmentResponse,
    retrieved_docs: list[Document],
    llm: ChatOpenAI
) -> ReflectionResult:
    """
    Assess confidence and identify gaps.
    
    Returns:
        ReflectionResult with:
        - overall_confidence: float (0.0-1.0)
        - confidence_by_claim: dict
        - information_gaps: list[InformationGap]
        - reasoning: str
    """
    # Assess confidence per claim
    confidence_scores = {}
    for claim in explanation.aligns + explanation.gaps:
        score = assess_claim_confidence(claim, retrieved_docs, llm)
        confidence_scores[claim.description] = score
    
    # Aggregate overall confidence
    overall_confidence = sum(confidence_scores.values()) / len(confidence_scores)
    
    # Identify information gaps
    gaps = identify_information_gaps(explanation, retrieved_docs)
    
    return ReflectionResult(
        overall_confidence=overall_confidence,
        confidence_by_claim=confidence_scores,
        information_gaps=gaps,
        reasoning="..."
    )
```

**Research Tool:**
```python
from google_search_results import GoogleSearch

class WebSearchTool:
    """Web search via Serper API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def search(self, query: str, num_results: int = 5) -> list[dict]:
        """
        Execute Google search.
        
        Returns:
            List of {title, snippet, link}
        """
        params = {
            "api_key": self.api_key,
            "q": query,
            "num": num_results
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        return results.get("organic_results", [])[:num_results]
```

---

#### Backend API (`src/vira/backend/`)

**Files:**
- `api.py`: FastAPI app, core routes
- `ui_routes.py`: UI-specific endpoints (sessions, WebSocket)
- `models.py`: Pydantic schemas

**Key Endpoints:**
```python
from fastapi import FastAPI, UploadFile, File
from vira.backend.models import AnalyzeRequest, AnalyzeResponse

app = FastAPI(title="VIRA API", version="0.1.0")

# Analyzer selection (Iteration 1 vs 2)
analyzer_v1 = AlignmentAnalyzer()
analyzer_v2 = ReflectiveAnalyzer() if settings.enable_reflection else None
active_analyzer = analyzer_v2 or analyzer_v1

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze business plan alignment.
    
    Uses Iteration 2 if ENABLE_REFLECTION=true, else Iteration 1.
    """
    summary = summarise_sections(request.plan_text)
    query = derive_query(request.plan_text)
    
    if analyzer_v2:
        # Iteration 2: Reflective agent
        result, metadata = analyzer_v2.analyze(
            company_name=request.company_name,
            plan_summary=summary,
            query=query
        )
        return build_response_v2(result, metadata)
    else:
        # Iteration 1: Basic RAG
        result, docs = analyzer_v1.analyze(
            company_name=request.company_name,
            plan_summary=summary,
            query=query
        )
        return build_response(result, len(docs))

@app.post("/analyze/upload", response_model=AnalyzeResponse)
async def analyze_upload(
    company_name: str, 
    file: UploadFile = File(...)
) -> AnalyzeResponse:
    """Handle file uploads (PDF/DOCX/TXT)."""
    plan_text = extract_text_from_file(file)
    # ... same analysis logic as /analyze
```

**Session Management (UI Routes):**
```python
from vira.ui.database.session_manager import SessionManager

db = SessionManager("./data/vira_sessions.db")

@router.post("/api/sessions")
async def create_session(req: CreateSessionRequest):
    """Create new chat session."""
    session = db.create_session(
        company_name=req.company_name,
        user_id=req.user_id
    )
    return session.to_dict()

@router.get("/api/sessions")
async def list_sessions(limit: int = 50, status: str = "active"):
    """List recent sessions."""
    sessions = db.list_sessions(limit=limit, status=status)
    return [s.to_dict() for s in sessions]

@router.post("/api/sessions/{session_id}/analyze")
async def analyze_plan(session_id: str):
    """Analyze business plan for session."""
    session = db.get_session(session_id)
    plan = db.get_latest_plan(session_id)
    
    # Run analysis with active analyzer
    result, metadata = active_analyzer.analyze(
        company_name=session.company_name,
        plan_summary=plan.content[:1500],
        query=plan.content[:1500]
    )
    
    # Store analysis in DB
    db.save_analysis(session_id, result, metadata)
    
    return format_analysis_message(result, session.company_name)
```

---

#### UI Layer (`src/vira/ui/`)

**Structure:**
```
ui/
├── chainlit_app.py               # Main Chainlit app (497 lines)
├── app.py                        # Streamlit app (legacy)
├── components/
│   ├── chat_history.py           # Session list, loading
│   ├── business_plan_editor.py   # Plan viewer, versioning
│   └── debug_panel.py            # Performance metrics
├── database/
│   ├── models.py                 # SQLAlchemy models
│   └── session_manager.py        # DB operations
├── state/
│   └── context_manager.py        # Chat context management
└── utils/
    ├── token_counter.py          # Token estimation, cost calc
    └── langsmith_integration.py  # Observability setup
```

**Chainlit App Structure:**
```python
import chainlit as cl
from vira.ui.database.session_manager import SessionManager
from vira.ui.state.context_manager import ContextManager

db = SessionManager("./data/vira_sessions.db")

@cl.on_chat_start
async def start():
    """Initialize new session."""
    # Create database session
    session = db.create_session()
    
    # Initialize context manager
    context = ContextManager(session.id)
    cl.user_session.set("context", context)
    
    # Send welcome message
    await cl.Message(
        content="Welcome to VIRA! Paste your business plan to begin.",
        author="VIRA"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages."""
    context = cl.user_session.get("context")
    
    # Check if first message (business plan)
    if not context.has_plan():
        # Save plan to database
        plan = db.save_business_plan(
            session_id=context.session_id,
            content=message.content,
            version=1
        )
        context.set_plan(plan)
        
        await cl.Message(
            content="Business plan received. Type 'analyze' to begin analysis.",
            author="VIRA"
        ).send()
    
    # Handle commands
    elif message.content.lower() in ['analyze', 'yes', 'ok']:
        await run_analysis(context)
    
    elif message.content.startswith('/'):
        await handle_command(message.content, context)
    
    else:
        # General conversation
        await handle_chat(message.content, context)

async def run_analysis(context: ContextManager):
    """Run alignment analysis."""
    # Show progress steps
    async with cl.Step(name="Analyzing alignment...", type="run") as step:
        # Retrieve plan
        plan = db.get_latest_plan(context.session_id)
        session = db.get_session(context.session_id)
        
        # Run analysis
        result, metadata = active_analyzer.analyze(
            company_name=session.company_name,
            plan_summary=plan.content[:1500],
            query=plan.content[:1500]
        )
        
        # Format and send response
        formatted = format_two_column_analysis(result)
        await cl.Message(
            content=formatted,
            author="VIRA"
        ).send()
        
        # Show debug panel if enabled
        if settings.developer_mode:
            debug_info = build_debug_panel(metadata)
            await cl.Message(
                content=debug_info,
                author="Debug"
            ).send()
```

**Database Schema (SQLAlchemy):**
```python
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Session(Base):
    """Chat session."""
    __tablename__ = 'sessions'
    
    id = Column(String, primary_key=True)
    company_name = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    status = Column(String, default='active')  # active, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    """Chat message."""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class BusinessPlan(Base):
    """Versioned business plan."""
    __tablename__ = 'business_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(String, default='user')  # user, system
    created_at = Column(DateTime, default=datetime.utcnow)

class Analysis(Base):
    """Analysis run metadata."""
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False)
    plan_version = Column(Integer, nullable=False)
    result = Column(Text, nullable=False)  # JSON serialized
    metadata = Column(Text, nullable=True)  # Performance metrics, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 3. Technology Stack

### 3.1 Core Dependencies

**Python Ecosystem (Python 3.10+):**
```python
# From pyproject.toml
[project.dependencies]
fastapi = ">=0.115.0"
uvicorn = ">=0.30.6"
langchain = ">=0.2.14"
langchain-community = ">=0.2.11"
langchain-openai = ">=0.1.21"
langgraph = ">=0.2.0"              # Iteration 2+ (Agent orchestration)
chromadb = ">=0.5.3"
rank-bm25 = ">=0.2.2"
scrapy = ">=2.11.1"
beautifulsoup4 = ">=4.12.3"
python-dotenv = ">=1.0.1"
pydantic = ">=2.8.2"
pydantic-settings = ">=2.3.4"
PyMuPDF = ">=1.24.9"               # PDF parsing
python-docx = ">=1.1.2"            # DOCX parsing
tiktoken = ">=0.7.0"               # Token counting
chainlit = ">=1.0.0"               # Primary UI
streamlit = ">=1.36.0"             # Alternative UI
sqlalchemy = ">=2.0.0"             # ORM for session DB
aiosqlite = ">=0.19.0"             # Async SQLite
google-search-results = ">=2.4.2"  # Serper API client
```

### 3.2 External Services

| Service | Purpose | Cost | Required For |
|---------|---------|------|--------------|
| **OpenAI API** | GPT-4o-mini (LLM), text-embedding-3-small | $0.15/$0.60 per 1M tokens | All iterations |
| **Serper API** | Google Search results | $2.50 per 1K searches | Iteration 2+ |
| **LangSmith** | LLM call tracing, observability | Free tier available | Optional (all iterations) |
| **Crunchbase** | Company/funding data | TBD | Iteration 3 (future) |
| **LinkedIn API** | Founder backgrounds | TBD | Iteration 3 (future) |

### 3.3 Development Tools

```toml
[project.optional-dependencies.dev]
pytest = ">=8.3.2"
pytest-asyncio = ">=0.23.8"
mypy = ">=1.11.1"
ruff = ">=0.6.4"
black = ">=24.8.0"
ipykernel = ">=6.29.5"
```

**Linting & Formatting:**
- **ruff**: Fast Python linter (replaces flake8, isort, pyupgrade)
- **black**: Opinionated code formatter
- **mypy**: Static type checking

**Testing:**
- **pytest**: Test framework
- **pytest-asyncio**: Async test support

---

## 4. Deployment Architecture

### 4.1 Local Development Setup

**Directory Structure:**
```
vira/
├── src/vira/                   # Python package
├── data/
│   ├── raw/a16z_raw.jsonl     # Raw scraped data (~150 MB)
│   ├── processed/chroma/       # Vector DB (~100 MB)
│   └── vira_sessions.db        # SQLite DB (~10 MB)
├── config/
│   └── crawl_settings.yaml
├── .env                        # Environment variables
├── pyproject.toml              # Dependencies
└── README.md
```

**Environment Variables (`.env`):**
```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (Iteration 2+)
SERPER_API_KEY=...
ENABLE_REFLECTION=true

# Optional (Observability)
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=vira-alignment

# Optional (Development)
LOG_LEVEL=INFO
DEVELOPER_MODE=false
```

**Services:**
```bash
# Terminal 1: Backend API
uvicorn vira.backend.api:app --reload --port 8001

# Terminal 2: Chainlit UI
chainlit run src/vira/ui/chainlit_app.py --port 8000

# Alternative: All-in-one script
./start_react_stack.sh  # Backend + React UI
./start_chainlit_ui.sh  # Backend + Chainlit UI
```

### 4.2 Production Deployment (Future)

**Recommended Architecture:**
```
┌──────────────────────────────────────────────────────────────┐
│                      Load Balancer (nginx)                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│  Frontend (CDN)  │            │  Backend API     │
│  - Vercel/Netlify│            │  - 2-4 instances │
│  - React build   │            │  - Docker        │
└──────────────────┘            │  - Kubernetes    │
                                └────────┬─────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
                 ┌────────────────┐            ┌────────────────┐
                 │ Vector DB      │            │ SQL Database   │
                 │ - Pinecone     │            │ - PostgreSQL   │
                 │ - Weaviate     │            │ - RDS/Supabase │
                 │ - Qdrant       │            └────────────────┘
                 └────────────────┘
```

**Scalability Considerations:**
- **Horizontal scaling:** Multiple API instances behind load balancer
- **Vector DB:** Migrate to Pinecone/Weaviate for distributed queries
- **SQL DB:** PostgreSQL with read replicas
- **Caching:** Redis for session state, frequent queries
- **Background jobs:** Celery for crawl tasks, async processing

---

## 5. Architecture Decision Records

### ADR-001: Why Chroma Over Weaviate/Pinecone?

**Status:** Accepted  
**Context:** Need vector database for semantic search  
**Decision:** Use Chroma for MVP  

**Rationale:**
- **Simplicity:** Pure Python, no Docker required
- **Cost:** Free (self-hosted), $0 operational cost
- **Speed:** Fast enough for prototype (<100ms queries)
- **Portability:** Easy to migrate to Pinecone/Weaviate later

**Consequences:**
- ✅ Faster prototyping (no infrastructure setup)
- ✅ Lower costs during validation
- ⚠️ Limited to single-instance (no horizontal scaling)
- ⚠️ Manual backups required

**Future:** Migrate to Pinecone ($70/month) or Weaviate (self-hosted on AWS) for production

---

### ADR-002: Why JSONL for Raw Storage?

**Status:** Accepted  
**Context:** Need format for raw scraped data  
**Decision:** Use JSONL (JSON Lines) format  

**Rationale:**
- **Streamability:** Process line-by-line without loading entire file
- **Appendability:** Incremental crawls without rewriting file
- **Human-readable:** Easy to inspect and debug
- **Language-agnostic:** Parseable in any language
- **Error-tolerant:** Corrupted line doesn't break entire file

**Consequences:**
- ✅ High reusability (can export to CSV, SQL, Parquet, etc.)
- ✅ Lossless (all metadata preserved)
- ✅ Git-friendly (line-based diffs)
- ⚠️ Larger file size than binary formats

**Alternatives Considered:**
- SQLite: Less portable, harder to version control
- Parquet: Not human-readable, requires libraries
- CSV: Doesn't handle nested metadata well

---

### ADR-003: Why LangGraph for Agent Orchestration?

**Status:** Accepted  
**Context:** Need framework for Iteration 2 agentic workflow  
**Decision:** Use LangGraph for state management and control flow  

**Rationale:**
- **Native LangChain integration:** Built by same team
- **State machine model:** Clear graph-based workflow
- **Conditional edges:** Easy decision logic (should_research?)
- **Visualization:** Can render workflow graphs
- **Debugging:** Step-through execution, state inspection

**Consequences:**
- ✅ Clear separation of nodes (analysis, reflection, research)
- ✅ Easy to add new nodes (e.g., validation, scoring)
- ✅ Supports iteration limits and loops
- ⚠️ Learning curve (new paradigm vs simple functions)

**Alternatives Considered:**
- Manual loop: Less structured, harder to debug
- CrewAI: More opinionated, less control
- AutoGen: Heavier framework, more complex

---

### ADR-004: Why Chainlit as Primary UI?

**Status:** Accepted  
**Context:** Need chat-based UI for founder interactions  
**Decision:** Use Chainlit as primary UI, keep React as alternative  

**Rationale:**
- **Chat-first design:** Natural for conversational analysis
- **Built-in features:** Session management, message history, file uploads
- **LangChain integration:** Native support for steps, agents, tools
- **Developer experience:** Fast iteration, hot reload
- **Modern UI:** Clean, polished out-of-the-box

**Consequences:**
- ✅ Faster prototyping (less UI boilerplate)
- ✅ Better fit for multi-turn conversations
- ✅ Easy to show agent progress (nested steps)
- ⚠️ Less customization than React
- ⚠️ Tied to Chainlit's UI paradigm

**React UI Status:** Maintained as alternative for component-based use cases

---

## 6. Data Flow

### 6.1 Ingestion Data Flow

```
Step 1: Web Crawling
────────────────────
a16z.com (web pages)
    ↓ Scrapy Spider
HTML responses
    ↓ BeautifulSoup parsing
Title + Content + Metadata
    ↓ JSON serialization
./data/raw/a16z_raw.jsonl (JSONL file)

Step 2: Processing
───────────────────
JSONL file (400 records)
    ↓ load_raw_jsonl()
List[dict] in memory
    ↓ RecursiveCharacterTextSplitter
Chunked dicts (~10,000 chunks)
    ↓ build_documents()
List[LangChain Document]

Step 3: Embedding
─────────────────
Documents
    ↓ OpenAI API (batch)
Embeddings (1536-dim vectors)
    ↓ Chroma.add_documents()
Vector DB (indexed with HNSW)
```

### 6.2 Query Data Flow (Iteration 1)

```
User Input: Business Plan
    ↓ BusinessPlanParser
Parsed sections + Summary
    ↓ derive_query()
Query string (first 1500 chars)
    ↓ HybridRetriever.retrieve()
Top-6 relevant documents
    ↓ format_context()
Context string (concatenated)
    ↓ LLM.invoke(prompt)
Raw LLM response (text)
    ↓ parse_response()
AlignmentResponse (structured)
    ↓ JSON serialization
API Response → UI
```

### 6.3 Query Data Flow (Iteration 2)

```
User Input: Business Plan
    ↓ BusinessPlanParser
Parsed sections + Summary
    ↓ LangGraph Workflow
Initial State (AgentState)
    ↓ initial_analysis_node()
Iteration 1 RAG analysis
    ↓ reflection_node()
Confidence scores + Information gaps
    ↓ should_research() [decision]
If confidence < 0.7 AND gaps exist:
    ↓ research_node()
    Web search results (Serper API)
    ↓ regeneration_node()
    Updated analysis with research context
    ↓ Loop back to reflection_node()
Else:
    ↓ END
Final State (AgentState)
    ↓ Extract result
Enhanced AlignmentResponse + Metadata
    ↓ JSON serialization
API Response → UI
```

---

## 7. Integration Points

### 7.1 Internal Integrations

| From | To | Protocol | Data Format |
|------|----|-----------|-----------
| Chainlit UI | Backend API | HTTP REST | JSON (POST /analyze) |
| Backend API | AlignmentAnalyzer | Function call | Python objects |
| AlignmentAnalyzer | HybridRetriever | Function call | Documents |
| HybridRetriever | Chroma | Chroma API | Query + Results |
| Backend API | SessionManager | Function call | SQLAlchemy ORM |
| SessionManager | SQLite DB | SQLAlchemy | SQL queries |

### 7.2 External Integrations

| Service | Purpose | Protocol | Authentication |
|---------|---------|----------|----------------|
| **OpenAI API** | LLM + Embeddings | HTTPS REST | API Key (Bearer token) |
| **Serper API** | Web Search | HTTPS REST | API Key (Query param) |
| **LangSmith** | Observability | HTTPS REST | API Key (Header) |

**OpenAI API Usage:**
```python
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)

# Embedding
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["Text to embed"]
)

# LLM
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are..."},
        {"role": "user", "content": "Analyze..."}
    ]
)
```

**Serper API Usage:**
```python
from google_search_results import GoogleSearch

params = {
    "api_key": settings.serper_api_key,
    "q": "TechStartup Inc founder background",
    "num": 5
}

search = GoogleSearch(params)
results = search.get_dict()
organic_results = results.get("organic_results", [])
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | November 25, 2025 | VIRA Team | Initial system architecture overview |

---

## Related Documents

- **PRD:** [`../01-FOUNDATION/PRD-Complete.md`](../01-FOUNDATION/PRD-Complete.md)
- **Data Architecture:** [`01-Data-Architecture.md`](./01-Data-Architecture.md)
- **RAG Architecture:** [`02-RAG-Architecture.md`](./02-RAG-Architecture.md)
- **Agent Architecture:** [`03-Agent-Architecture.md`](./03-Agent-Architecture.md)
- **API Specification:** [`../03-API-CONTRACTS/01-REST-API-Specification.md`](../03-API-CONTRACTS/01-REST-API-Specification.md)

---

**End of Document**

