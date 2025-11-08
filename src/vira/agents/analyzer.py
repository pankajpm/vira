"""High-level analyzer interface for Iteration 2 reflective agent system.

This module provides a simple interface that wraps the LangGraph workflow,
making it easy to use from the API layer while maintaining backward
compatibility with Iteration 1.
"""

from __future__ import annotations

from typing import Any

from ..config.settings import get_settings
from ..rag.pipeline import AlignmentAnalyzer as Iteration1Analyzer, AlignmentResponse
from .graph import create_reflection_graph
from .state import AgentState


class ReflectiveAnalyzer:
    """High-level interface for Iteration 2 analysis with reflection and research.

    This analyzer wraps the complete LangGraph workflow, providing a simple
    analyze() method that matches the Iteration 1 API while adding reflection
    and research capabilities.
    """

    def __init__(self) -> None:
        """Initialize the reflective analyzer."""
        self.settings = get_settings()
        self.iteration1_analyzer = Iteration1Analyzer()
        self.graph = create_reflection_graph()

    def analyze(
        self,
        company_name: str,
        plan_summary: str,
        query: str,
    ) -> tuple[AlignmentResponse, dict[str, Any]]:
        """Analyze alignment with reflection and optional research.

        This is the main entry point that:
        1. Runs Iteration 1 analysis (initial explanation)
        2. Reflects on the explanation (confidence assessment)
        3. Conducts research if confidence is low
        4. Regenerates explanation with research findings (if applicable)
        5. Returns final explanation with metadata

        Args:
            company_name: Name of the company being analyzed
            plan_summary: Business plan summary text
            query: Search query for retrieval

        Returns:
            Tuple of:
            - AlignmentResponse with final analysis (includes confidence, research metadata)
            - Metadata dict with execution details (iterations, research queries, etc.)
        """
        print("\n" + "=" * 60)
        print(f"ITERATION 2 ANALYSIS: {company_name}")
        print("=" * 60)

        # Step 1: Run Iteration 1 analysis
        print("\n📝 Step 1: Initial analysis (Iteration 1 pipeline)...")
        initial_result, initial_docs = self.iteration1_analyzer.analyze(
            company_name=company_name,
            plan_summary=plan_summary,
            query=query
        )

        # Create initial state
        initial_state: AgentState = {
            "company_name": company_name,
            "plan_summary": plan_summary,
            "query": query,
            "initial_docs": initial_docs,
            "initial_explanation": initial_result,
            "reflection_result": None,
            "overall_confidence": 0.0,
            "research_queries": [],
            "research_results": [],
            "final_explanation": None,
            "iteration_count": 0,
            "error": None,
        }

        # Step 2-4: Run reflection graph (reflection -> research -> regenerate)
        print("\n🔄 Step 2-4: Running reflection workflow...")
        try:
            final_state = self.graph.invoke(initial_state)
        except Exception as e:
            print(f"\n⚠️  Error in reflection workflow: {e}")
            # Fallback: return initial result
            final_state = initial_state
            final_state["final_explanation"] = initial_result
            final_state["overall_confidence"] = 0.7

        # Extract final explanation
        final_explanation = final_state.get("final_explanation") or initial_result

        # Add confidence and research metadata to the explanation
        if final_state.get("overall_confidence"):
            final_explanation.overall_confidence = final_state["overall_confidence"]

        # Populate research_conducted with full details including sources
        if final_state.get("research_results"):
            final_explanation.research_conducted = [
                {
                    "query": r.query,
                    "snippets": r.snippets,
                    "sources": r.sources,
                    "gap_addressed": r.gap_addressed,
                    "num_results": len(r.sources)
                }
                for r in final_state["research_results"]
            ]

        if final_state.get("reflection_result") and final_state["reflection_result"].information_gaps:
            final_explanation.data_gaps = [
                gap.description for gap in final_state["reflection_result"].information_gaps
            ]

        # Build metadata
        metadata = {
            "iterations": final_state.get("iteration_count", 0),
            "overall_confidence": final_state.get("overall_confidence", 0.7),
            "research_queries": final_state.get("research_queries", []),
            "num_research_results": len(final_state.get("research_results", [])),
            "information_gaps_identified": len(
                final_state.get("reflection_result", {}).information_gaps
                if final_state.get("reflection_result")
                else []
            ),
        }

        print("\n✅ Analysis complete!")
        print(f"   Confidence: {metadata['overall_confidence']:.2f}")
        print(f"   Research queries: {len(metadata['research_queries'])}")
        print(f"   Iterations: {metadata['iterations']}")
        print("=" * 60 + "\n")

        return final_explanation, metadata


__all__ = ["ReflectiveAnalyzer"]

