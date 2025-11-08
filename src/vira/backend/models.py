"""Pydantic models describing API contracts for the FastAPI backend."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Payload accepted by the /analyze endpoint."""

    company_name: str = Field(..., description="Name of the founder's company.")
    plan_text: str = Field(..., description="Full text of the business plan.")


class AlignmentPoint(BaseModel):
    title: str
    explanation: str
    sources: List[str]
    confidence: float | None = Field(default=None, description="Confidence score 0-1 (Iteration 2)")
    evidence_quality: str | None = Field(
        default=None, description="Evidence quality: strong/medium/weak/insufficient (Iteration 2)"
    )


class AnalyzeResponse(BaseModel):
    company_name: str
    aligns: List[AlignmentPoint]
    gaps: List[AlignmentPoint]
    summary: str
    retrieved_documents: int
    model_name: str
    
    # Iteration 2: Reflection Agent fields
    overall_confidence: float | None = Field(
        default=None, description="Overall confidence score 0-1 (Iteration 2)"
    )
    research_conducted: List[dict] | None = Field(
        default=None, description="Research queries and results (Iteration 2)"
    )
    data_gaps: List[str] | None = Field(
        default=None, description="Identified information gaps (Iteration 2)"
    )


