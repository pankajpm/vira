"""FastAPI application exposing the Iteration 1 alignment service."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ..business_plan.parser import SUPPORTED_EXTENSIONS, extract_text, summarise_sections
from ..common.langsmith import configure_langsmith
from ..config.settings import get_settings
from ..rag.pipeline import AlignmentAnalyzer, AlignmentResponse
from .models import AlignmentPoint, AnalyzeRequest, AnalyzeResponse
from .ui_routes import router as ui_router

logger = logging.getLogger(__name__)

configure_langsmith()
settings = get_settings()

# Initialize analyzers
analyzer_v1 = AlignmentAnalyzer()
logger.info("iteration1_analyzer_initialised", extra={"vector_dir": str(settings.vector_db_dir)})

# Initialize Iteration 2 analyzer if enabled
analyzer_v2 = None
if settings.enable_reflection:
    try:
        from ..agents.analyzer import ReflectiveAnalyzer
        analyzer_v2 = ReflectiveAnalyzer()
        logger.info("iteration2_analyzer_initialised", extra={"reflection_enabled": True})
    except Exception as e:
        logger.warning(f"Could not initialize Iteration 2 analyzer: {e}")

# Backward compatibility
analyzer = analyzer_v1

app = FastAPI(title="VIRA Iteration 1 API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include UI routes
app.include_router(ui_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Simple health check endpoint."""

    return {"status": "ok"}


def _build_summary(plan_text: str) -> str:
    sections = summarise_sections(plan_text)
    summary_lines = []
    for key, value in sections.items():
        if not value:
            continue
        summary_lines.append(f"{key.title()}:\n{value[:800]}")
    return "\n\n".join(summary_lines) or plan_text[:2000]


def _derive_query(plan_text: str) -> str:
    return plan_text[:1500]


def _build_response(result: AlignmentResponse, retrieved: int, model_name: str) -> AnalyzeResponse:
    return AnalyzeResponse(
        company_name=result.company_name,
        aligns=[AlignmentPoint(title=entry.title, explanation=entry.explanation, sources=entry.sources) for entry in result.aligns],
        gaps=[AlignmentPoint(title=entry.title, explanation=entry.explanation, sources=entry.sources) for entry in result.gaps],
        summary=result.summary,
        retrieved_documents=retrieved,
        model_name=model_name,
    )


def _build_response_v2(result: AlignmentResponse, metadata: dict) -> AnalyzeResponse:
    """Build response for Iteration 2 with additional metadata."""
    return AnalyzeResponse(
        company_name=result.company_name,
        aligns=[
            AlignmentPoint(
                title=entry.title, 
                explanation=entry.explanation, 
                sources=entry.sources,
                confidence=entry.confidence,
                evidence_quality=entry.evidence_quality
            ) 
            for entry in result.aligns
        ],
        gaps=[
            AlignmentPoint(
                title=entry.title, 
                explanation=entry.explanation, 
                sources=entry.sources,
                confidence=entry.confidence,
                evidence_quality=entry.evidence_quality
            ) 
            for entry in result.gaps
        ],
        summary=result.summary,
        retrieved_documents=metadata.get("num_research_results", 0),
        model_name="gpt-4o-mini",
        overall_confidence=result.overall_confidence,
        research_conducted=result.research_conducted,
        data_gaps=result.data_gaps,
    )


@app.post("/analyze", response_model=AnalyzeResponse, tags=["analysis"])
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze plan text provided inline.
    
    Uses Iteration 2 (reflection + research) if ENABLE_REFLECTION=true,
    otherwise uses Iteration 1 (basic RAG).
    """

    if not request.plan_text.strip():
        raise HTTPException(status_code=400, detail="plan_text must not be empty")

    summary = _build_summary(request.plan_text)
    query = _derive_query(request.plan_text)
    
    # Use Iteration 2 if enabled and initialized
    if analyzer_v2:
        logger.info("using_iteration2_analyzer", extra={"company": request.company_name})
        result, metadata = analyzer_v2.analyze(
            company_name=request.company_name, 
            plan_summary=summary, 
            query=query
        )
        return _build_response_v2(result, metadata)
    else:
        # Fallback to Iteration 1
        result, docs = analyzer_v1.analyze(
            company_name=request.company_name, 
            plan_summary=summary, 
            query=query
        )
        logger.info("analysis_completed", extra={"company": request.company_name, "docs": len(docs)})
        return _build_response(result, len(docs), analyzer_v1.model_name)


@app.post("/analyze/upload", response_model=AnalyzeResponse, tags=["analysis"])
async def analyze_upload(company_name: str, file: UploadFile = File(...)) -> AnalyzeResponse:
    """Handle file uploads (PDF/DOCX/TXT)."""

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type {suffix}")

    data = await file.read()
    temp_path = Path("/tmp") / f"vira_{file.filename}"
    temp_path.write_bytes(data)

    try:
        plan_text = extract_text(temp_path)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass

    summary = _build_summary(plan_text)
    query = _derive_query(plan_text)
    result, docs = analyzer.analyze(company_name=company_name, plan_summary=summary, query=query)
    logger.info("analysis_completed_upload", extra={"company": company_name, "docs": len(docs)})
    return _build_response(result, len(docs), analyzer.model_name)

