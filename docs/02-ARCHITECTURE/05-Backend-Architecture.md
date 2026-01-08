# VIRA: Backend Architecture

**Version:** 1.0  
**Last Updated:** November 25, 2025  
**Status:** ✅ Implemented and Operational

---

## Overview

VIRA's backend is built with **FastAPI** and provides REST API endpoints for business plan analysis, session management, and real-time updates via WebSocket.

### Key Components
- FastAPI application (async Python web framework)
- Analyzer selection logic (Iteration 1 vs 2 routing)
- Session management (SQLite database)
- File upload handling (PDF/DOCX/TXT)
- WebSocket support for real-time updates

---

## FastAPI Application Structure

### Main Application

**File:** `src/vira/backend/api.py`

```python
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from vira.backend.models import AnalyzeRequest, AnalyzeResponse
from vira.backend.ui_routes import router as ui_router
from vira.config.settings import get_settings
from vira.rag.pipeline import AlignmentAnalyzer
from vira.common.langsmith import configure_langsmith

# Initialize LangSmith observability
configure_langsmith()
settings = get_settings()

# Initialize analyzers
analyzer_v1 = AlignmentAnalyzer()  # Iteration 1: RAG
analyzer_v2 = None

if settings.enable_reflection:
    from vira.agents.analyzer import ReflectiveAnalyzer
    analyzer_v2 = ReflectiveAnalyzer()  # Iteration 2: Reflective Agent

# Active analyzer (Iteration 2 if available, else Iteration 1)
analyzer = analyzer_v2 or analyzer_v1

# Create FastAPI app
app = FastAPI(
    title="VIRA Iteration 1 API",
    version="0.1.0",
    description="Venture Intelligence Research Assistant"
)

# CORS middleware (allow all origins for prototype)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include UI-specific routes
app.include_router(ui_router)
```

### Health Check

```python
@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
```

---

## Core Endpoints

### POST /analyze

**Purpose:** Analyze business plan (text input)

```python
@app.post("/analyze", response_model=AnalyzeResponse, tags=["analysis"])
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze plan text provided inline.
    
    Uses Iteration 2 (reflection + research) if ENABLE_REFLECTION=true,
    otherwise uses Iteration 1 (basic RAG).
    
    Args:
        request: AnalyzeRequest with company_name and plan_text
        
    Returns:
        AnalyzeResponse with alignment analysis
    """
    if not request.plan_text.strip():
        raise HTTPException(status_code=400, detail="plan_text must not be empty")
    
    # Summarize business plan
    summary = _build_summary(request.plan_text)
    query = _derive_query(request.plan_text)
    
    # Route to appropriate analyzer
    if analyzer_v2:
        # Iteration 2: Reflective agent
        logger.info("using_iteration2_analyzer", extra={"company": request.company_name})
        result, metadata = analyzer_v2.analyze(
            company_name=request.company_name,
            plan_summary=summary,
            query=query
        )
        return _build_response_v2(result, metadata)
    else:
        # Iteration 1: Basic RAG
        result, docs = analyzer_v1.analyze(
            company_name=request.company_name,
            plan_summary=summary,
            query=query
        )
        return _build_response(result, len(docs), analyzer_v1.model_name)
```

**Request Schema:**
```python
class AnalyzeRequest(BaseModel):
    """Request body for /analyze endpoint."""
    company_name: str = Field(..., description="Name of the company")
    plan_text: str = Field(..., description="Full text of the business plan")
```

**Response Schema:**
```python
class AnalyzeResponse(BaseModel):
    """Response from /analyze endpoint."""
    company_name: str
    aligns: List[AlignmentPoint]     # How plan aligns
    gaps: List[AlignmentPoint]       # How plan doesn't align
    summary: str                     # Overall summary
    sources: List[str]               # Source URLs
    num_docs_retrieved: int          # Number of docs used
    model_used: str                  # LLM model name
    
    # Iteration 2 specific fields (optional)
    confidence: Optional[float] = None
    research_queries: Optional[List[str]] = None
    data_gaps: Optional[List[str]] = None
```

### POST /analyze/upload

**Purpose:** Analyze business plan (file upload)

```python
@app.post("/analyze/upload", response_model=AnalyzeResponse, tags=["analysis"])
async def analyze_upload(
    company_name: str, 
    file: UploadFile = File(...)
) -> AnalyzeResponse:
    """
    Handle file uploads (PDF/DOCX/TXT).
    
    Args:
        company_name: Name of company
        file: Uploaded file (PDF, DOCX, or TXT)
        
    Returns:
        AnalyzeResponse with alignment analysis
    """
    from pathlib import Path
    from vira.business_plan.parser import extract_text, SUPPORTED_EXTENSIONS
    
    # Validate file type
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type {suffix}. Supported: {SUPPORTED_EXTENSIONS}"
        )
    
    # Save file temporarily
    data = await file.read()
    temp_path = Path("/tmp") / f"vira_{file.filename}"
    temp_path.write_bytes(data)
    
    try:
        # Extract text from file
        plan_text = extract_text(temp_path)
        
        # Analyze (same logic as /analyze)
        summary = _build_summary(plan_text)
        query = _derive_query(plan_text)
        result, docs = analyzer.analyze(
            company_name=company_name,
            plan_summary=summary,
            query=query
        )
        
        return _build_response(result, len(docs), analyzer.model_name)
        
    finally:
        # Clean up temp file
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
```

---

## UI-Specific Routes

**File:** `src/vira/backend/ui_routes.py`

### Session Management

```python
from fastapi import APIRouter, WebSocket
from vira.ui.database.session_manager import SessionManager

router = APIRouter(prefix="/api", tags=["ui"])
db = SessionManager("./data/vira_sessions.db")

@router.post("/sessions")
async def create_session(req: CreateSessionRequest):
    """Create new chat session."""
    session = db.create_session(
        company_name=req.company_name,
        user_id=req.user_id
    )
    return session.to_dict()

@router.get("/sessions")
async def list_sessions(limit: int = 50, status: str = "active"):
    """List recent sessions."""
    sessions = db.list_sessions(limit=limit, status=status)
    return [s.to_dict() for s in sessions]

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session by ID."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()
```

### Business Plan Management

```python
@router.post("/sessions/{session_id}/plan")
async def save_plan(session_id: str, req: SavePlanRequest):
    """Save business plan for session."""
    plan = db.save_business_plan(
        session_id=session_id,
        content=req.content,
        version=req.version or 1
    )
    return plan.to_dict()

@router.get("/sessions/{session_id}/plan")
async def get_latest_plan(session_id: str):
    """Get latest business plan version."""
    plan = db.get_latest_plan(session_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found")
    return plan.to_dict()

@router.get("/sessions/{session_id}/plan/versions")
async def get_plan_versions(session_id: str):
    """Get all plan versions."""
    versions = db.get_all_plan_versions(session_id)
    return [v.to_dict() for v in versions]
```

### Analysis Execution

```python
@router.post("/sessions/{session_id}/analyze")
async def analyze_plan(session_id: str):
    """
    Analyze business plan for session.
    
    Returns:
        Formatted analysis message (HTML for UI display)
    """
    import time
    start_time = time.time()
    
    # Retrieve session and plan
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    plan = db.get_latest_plan(session_id)
    if not plan:
        raise HTTPException(status_code=400, detail="No business plan found")
    
    # Run analysis
    query = plan.content[:1500]
    
    if analyzer_v2:
        # Iteration 2: Reflective agent
        result, metadata = analyzer_v2.analyze(
            company_name=session.company_name,
            plan_summary=plan.content[:1500],
            query=query
        )
        
        # Save analysis
        db.save_analysis(
            session_id=session_id,
            plan_version=plan.version,
            result=result.model_dump_json(),
            metadata=metadata
        )
        
        # Format for UI
        return {
            "content": _format_analysis_message(result, session.company_name),
            "metadata": metadata,
            "duration": time.time() - start_time
        }
    else:
        # Iteration 1: Basic RAG
        result, docs = analyzer_v1.analyze(
            company_name=session.company_name,
            plan_summary=plan.content[:1500],
            query=query
        )
        
        db.save_analysis(
            session_id=session_id,
            plan_version=plan.version,
            result=result.model_dump_json(),
            metadata={"num_docs": len(docs)}
        )
        
        return {
            "content": _format_analysis_message(result, session.company_name),
            "duration": time.time() - start_time
        }
```

### WebSocket Support

```python
@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time updates during analysis.
    
    Streams progress updates:
    - Retrieval started
    - Documents retrieved
    - LLM generation started
    - Analysis complete
    """
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "analyze":
                # Stream analysis steps
                await websocket.send_text("Retrieving documents...")
                # ... retrieval logic
                
                await websocket.send_text("Generating analysis...")
                # ... LLM generation
                
                await websocket.send_text("Complete!")
                await websocket.send_json(result.model_dump())
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
```

---

## Response Formatting

### Two-Column Layout (HTML)

```python
def _format_analysis_message(result: AlignmentResponse, company_name: str) -> str:
    """
    Format analysis as two-column HTML layout.
    
    Layout:
    ┌─────────────────┬─────────────────┐
    │ HOW THIS ALIGNS │ HOW THIS DOESN'T│
    │                 │     ALIGN       │
    │ • Match 1       │ • Gap 1         │
    │ • Match 2       │ • Gap 2         │
    │ • Match 3       │ • Gap 3         │
    └─────────────────┴─────────────────┘
              SUMMARY (full width)
    """
    html = f"""
<div style="margin-bottom: 20px;">
    <h2 style="color: #2c3e50;">Alignment Analysis: {company_name} vs a16z</h2>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
    <div style="border: 1px solid #27ae60; border-radius: 8px; padding: 15px;">
        <h3 style="color: #27ae60; margin-top: 0;">✓ HOW THIS PLAN ALIGNS</h3>
        <ul>
"""
    
    # Add matches
    for align in result.aligns:
        html += f"""
            <li style="margin-bottom: 10px;">
                <strong>{align.description}</strong><br/>
                <span style="color: #555;">{align.evidence}</span><br/>
                <a href="{align.source}" target="_blank" style="font-size: 0.9em;">{align.source}</a>
            </li>
"""
    
    html += """
        </ul>
    </div>
    
    <div style="border: 1px solid #e74c3c; border-radius: 8px; padding: 15px;">
        <h3 style="color: #e74c3c; margin-top: 0;">✗ HOW THIS PLAN DOESN'T ALIGN</h3>
        <ul>
"""
    
    # Add gaps
    for gap in result.gaps:
        html += f"""
            <li style="margin-bottom: 10px;">
                <strong>{gap.description}</strong><br/>
                <span style="color: #555;">{gap.evidence}</span><br/>
                <a href="{gap.source}" target="_blank" style="font-size: 0.9em;">{gap.source}</a>
            </li>
"""
    
    html += f"""
        </ul>
    </div>
</div>

<div style="border: 1px solid #3498db; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
    <h3 style="color: #3498db; margin-top: 0;">📊 SUMMARY</h3>
    <p>{result.summary}</p>
</div>

<div style="background-color: #f8f9fa; border-radius: 8px; padding: 10px; font-size: 0.9em;">
    <strong>Sources:</strong> {len(result.sources)} documents analyzed
</div>
"""
    
    return html
```

---

## Configuration

### Settings Management

**File:** `src/vira/config/settings.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str
    serper_api_key: str | None = None
    langsmith_api_key: str | None = None
    
    # Feature Flags
    enable_reflection: bool = False  # Enable Iteration 2
    developer_mode: bool = False     # Show debug panels
    
    # Paths
    vector_db_dir: Path = Path("./data/processed/chroma")
    session_db_path: Path = Path("./data/vira_sessions.db")
    
    # LangSmith (optional observability)
    langsmith_project: str = "vira-alignment"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
```

---

## Error Handling

### Global Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )
```

---

## Performance Optimizations

### Response Caching (Future)

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_analyze(company_name: str, plan_hash: str) -> AnalyzeResponse:
    """Cache analysis results to avoid redundant LLM calls."""
    # Implementation
    pass
```

### Async Processing

```python
import asyncio

async def analyze_async(request: AnalyzeRequest) -> AnalyzeResponse:
    """Async version of analyze for concurrent requests."""
    # Run analysis in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, analyze_sync, request)
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | November 25, 2025 | VIRA Team | Initial backend architecture documentation |

---

## Related Documents

- **System Architecture:** [`00-System-Architecture-Overview.md`](./00-System-Architecture-Overview.md)
- **API Specification:** [`../03-API-CONTRACTS/01-REST-API-Specification.md`](../03-API-CONTRACTS/01-REST-API-Specification.md)
- **Database Implementation:** [`../04-IMPLEMENTATION/06-Database-Implementation.md`](../04-IMPLEMENTATION/06-Database-Implementation.md)

---

**End of Document**

