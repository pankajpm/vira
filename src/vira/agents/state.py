"""State definitions for LangGraph agent orchestration.

This module defines the state structure used by the reflection and research
agents in Iteration 2. The state tracks the flow through initial analysis,
reflection, research, and regeneration steps.
"""

from __future__ import annotations

from typing import Any, TypedDict

from langchain_core.documents import Document
from pydantic import BaseModel, Field

from ..rag.pipeline import AlignmentResponse


class ReflectionResult(BaseModel):
    """Results from the reflection agent's meta-assessment."""

    overall_confidence: float = Field(..., description="Overall confidence score (0-1)")
    per_claim_confidence: dict[str, float] = Field(
        default_factory=dict, description="Confidence score for each claim"
    )
    information_gaps: list[InformationGap] = Field(
        default_factory=list, description="Identified gaps in information"
    )
    reasoning: str = Field(..., description="Explanation of confidence assessment")


class InformationGap(BaseModel):
    """Represents a gap in information identified during reflection."""

    category: str = Field(
        ...,
        description="Category: team_info, market_data, competitive_landscape, vc_preferences",
    )
    description: str = Field(..., description="What information is missing")
    priority: int = Field(..., description="Priority level (1=critical, 2=supporting, 3=nice-to-have)")
    claim_id: str | None = Field(default=None, description="Associated claim requiring this info")


class ResearchResult(BaseModel):
    """Results from a research query."""

    query: str = Field(..., description="Search query executed")
    snippets: list[str] = Field(default_factory=list, description="Relevant snippets found")
    sources: list[str] = Field(default_factory=list, description="Source URLs")
    gap_addressed: str | None = Field(
        default=None, description="Information gap this research addresses"
    )


class AgentState(TypedDict, total=False):
    """State passed between nodes in the LangGraph workflow.
    
    This state tracks the complete flow from initial analysis through
    reflection, research, and regeneration.
    """

    # Input
    company_name: str
    plan_summary: str
    query: str

    # Iteration 1 results
    initial_docs: list[Document]
    initial_explanation: AlignmentResponse

    # Reflection results
    reflection_result: ReflectionResult | None
    overall_confidence: float

    # Research results
    research_queries: list[str]
    research_results: list[ResearchResult]

    # Final output
    final_explanation: AlignmentResponse | None
    iteration_count: int

    # Metadata
    error: str | None


__all__ = [
    "AgentState",
    "ReflectionResult",
    "InformationGap",
    "ResearchResult",
]

