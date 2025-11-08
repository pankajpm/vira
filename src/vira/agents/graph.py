"""LangGraph orchestration for Iteration 2 reflective agent workflow.

This module defines the state graph that orchestrates the multi-step
reflection and research workflow. The graph routes between initial analysis,
reflection, research, and regeneration based on confidence thresholds.
"""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, StateGraph

from ..config.settings import get_settings
from ..rag.pipeline import AlignmentAnalyzer
from .reflection import reflect_on_explanation
from .research import conduct_research
from .state import AgentState


def initial_analysis_node(state: AgentState) -> AgentState:
    """Execute initial alignment analysis using Iteration 1 RAG pipeline.

    Args:
        state: Current agent state with input data

    Returns:
        Updated state with initial_docs and initial_explanation
    """
    print("🔍 Running initial analysis...")
    
    # Use Iteration 1 analyzer
    analyzer = AlignmentAnalyzer()
    
    try:
        result, docs = analyzer.analyze(
            company_name=state["company_name"],
            plan_summary=state["plan_summary"],
            query=state["query"]
        )
        
        state["initial_docs"] = docs
        state["initial_explanation"] = result
        state["iteration_count"] = 0
        
        print(f"   ✓ Generated {len(result.aligns)} alignments, {len(result.gaps)} gaps")
        
    except Exception as e:
        print(f"   ⚠️  Error in initial analysis: {e}")
        state["initial_docs"] = []
        state["initial_explanation"] = None  # type: ignore
        state["iteration_count"] = 0
        state["error"] = str(e)
    
    return state


def reflection_node(state: AgentState) -> AgentState:
    """Perform reflection and confidence assessment on the explanation.

    Args:
        state: Current agent state with explanation to assess

    Returns:
        Updated state with reflection_result and overall_confidence
    """
    print("🤔 Running reflection...")
    
    from langchain_openai import ChatOpenAI
    
    # Get explanation to reflect on (prefer final if available, else initial)
    explanation = state.get("final_explanation") or state.get("initial_explanation")
    
    if not explanation:
        print("   ⚠️  No explanation to reflect on, skipping")
        state["overall_confidence"] = 0.7
        state["reflection_result"] = None
        return state
    
    # Create LLM for reflection (use temperature=0 for consistency)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    try:
        # Perform reflection
        reflection_result = reflect_on_explanation(
            explanation=explanation,
            retrieved_docs=state.get("initial_docs", []),
            llm=llm
        )
        
        state["reflection_result"] = reflection_result
        state["overall_confidence"] = reflection_result.overall_confidence
        
        print(f"   📊 Confidence: {reflection_result.overall_confidence:.2f}")
        print(f"   📋 Information gaps: {len(reflection_result.information_gaps)}")
        
    except Exception as e:
        print(f"   ⚠️  Reflection error: {e}")
        # Fallback: moderate confidence
        state["overall_confidence"] = 0.7
        state["reflection_result"] = None
    
    return state


def research_node(state: AgentState) -> AgentState:
    """Conduct research: always run baseline (3 queries), optionally add gap-driven research.

    Args:
        state: Current agent state with identified gaps

    Returns:
        Updated state with research_results and research_queries
    """
    print("🔬 Running research...")
    
    settings = get_settings()
    all_results: list = []
    
    # Step 1: Always run baseline research (3 queries)
    print("   📊 Running baseline research (3 core queries)...")
    try:
        baseline_results = conduct_research(
            gaps=[],  # No gaps needed for baseline
            company_name=state.get("company_name", ""),
            max_queries=3,
            baseline_mode=True,
            plan_summary=state.get("plan_summary", "")
        )
        all_results.extend(baseline_results)
        print(f"   ✓ Baseline research complete: {len(baseline_results)} result sets")
    except Exception as e:
        print(f"   ⚠️  Baseline research error: {e}")
    
    # Step 2: Optionally add gap-driven research if confidence is low and gaps exist
    reflection_result = state.get("reflection_result")
    confidence = state.get("overall_confidence", 1.0)
    
    if reflection_result and reflection_result.information_gaps and confidence < settings.reflection_confidence_threshold:
        print(f"   📋 Low confidence ({confidence:.2f}) - adding gap-driven research...")
        try:
            # Limit gap-driven queries to 2 (since we already did 3 baseline)
            gap_results = conduct_research(
                gaps=reflection_result.information_gaps,
                company_name=state.get("company_name", ""),
                max_queries=2,  # Limit to 2 to keep total around 5
                baseline_mode=False,
                plan_summary=state.get("plan_summary", "")
            )
            all_results.extend(gap_results)
            print(f"   ✓ Gap-driven research complete: {len(gap_results)} result sets")
        except Exception as e:
            print(f"   ⚠️  Gap-driven research error: {e}")
    else:
        if not reflection_result or not reflection_result.information_gaps:
            print("   ℹ️  No information gaps identified")
        else:
            print(f"   ℹ️  High confidence ({confidence:.2f}) - skipping gap-driven research")
    
    # Store all results
    state["research_results"] = all_results
    state["research_queries"] = [r.query for r in all_results]
    
    print(f"   📚 Total research complete: {len(all_results)} result sets")
    return state


def regenerate_node(state: AgentState) -> AgentState:
    """Regenerate explanation with research findings.

    Args:
        state: Current agent state with research results

    Returns:
        Updated state with final_explanation and incremented iteration_count
    """
    print("♻️  Regenerating explanation with research...")
    
    # For prototype: just increment iteration and copy initial to final
    # In production, would re-run AlignmentAnalyzer with enhanced context
    
    # Build enhanced context from research
    research_context = _build_research_context(state.get("research_results", []))
    
    if research_context:
        print(f"   📚 Added {len(state.get('research_results', []))} research result sets")
        # TODO Phase 4.1: Re-run analysis with research context
        # For now, just attach research metadata to initial explanation
        explanation = state.get("initial_explanation")
        if explanation:
            # Add research metadata with full details including sources
            if not explanation.research_conducted:
                explanation.research_conducted = []
            
            for result in state.get("research_results", []):
                explanation.research_conducted.append({
                    "query": result.query,
                    "snippets": result.snippets,
                    "sources": result.sources,
                    "gap_addressed": result.gap_addressed or "",
                    "num_results": len(result.sources)
                })
            
            state["final_explanation"] = explanation
    else:
        # No research, just use initial
        state["final_explanation"] = state.get("initial_explanation")
    
    state["iteration_count"] = state.get("iteration_count", 0) + 1
    
    return state


def _build_research_context(research_results: list) -> str:
    """Build context string from research results.
    
    Args:
        research_results: List of ResearchResult objects
        
    Returns:
        Formatted research context string
    """
    if not research_results:
        return ""
    
    context_parts = []
    for result in research_results:
        if hasattr(result, 'query') and hasattr(result, 'snippets'):
            context_parts.append(f"Query: {result.query}")
            for snippet in result.snippets[:3]:  # Limit to top 3 per query
                context_parts.append(f"  - {snippet}")
            context_parts.append("")
    
    return "\n".join(context_parts)


def should_research(state: AgentState) -> Literal["research", "end"]:
    """Determine if research is needed. Always runs baseline research (3 queries).

    Args:
        state: Current agent state

    Returns:
        "research" to always run baseline research, "end" only if max iterations reached
    """
    settings = get_settings()
    
    iteration = state.get("iteration_count", 0)
    confidence = state.get("overall_confidence", 1.0)
    
    # Always run baseline research unless we've exceeded max iterations
    if iteration < settings.max_reflection_iterations:
        print(f"   🔍 Running research (baseline always, gap-driven if confidence < {settings.reflection_confidence_threshold:.2f})")
        return "research"
    
    print(f"   🛑 Max iterations ({settings.max_reflection_iterations}) reached - ending")
    return "end"


def should_reflect_again(state: AgentState) -> Literal["reflection", "end"]:
    """Determine if another reflection pass is needed after regeneration.

    Args:
        state: Current agent state

    Returns:
        "reflection" if another pass is needed, "end" otherwise
    """
    settings = get_settings()
    iteration = state.get("iteration_count", 0)
    
    # Don't reflect again if we've reached max iterations
    if iteration >= settings.max_reflection_iterations:
        print(f"   🛑 Max iterations ({settings.max_reflection_iterations}) reached")
        return "end"
    
    # For prototype: just do one research pass, don't loop
    return "end"


def create_reflection_graph() -> Any:
    """Create and compile the LangGraph workflow for Iteration 2.

    Returns:
        Compiled state graph ready for execution
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("initial_analysis", initial_analysis_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("research", research_node)
    workflow.add_node("regenerate", regenerate_node)
    
    # Define flow
    workflow.set_entry_point("initial_analysis")
    
    # initial_analysis -> reflection
    workflow.add_edge("initial_analysis", "reflection")
    
    # reflection -> research OR end (based on confidence)
    workflow.add_conditional_edges(
        "reflection",
        should_research,
        {
            "research": "research",
            "end": END,
        }
    )
    
    # research -> regenerate
    workflow.add_edge("research", "regenerate")
    
    # regenerate -> reflection OR end (based on iteration count)
    workflow.add_conditional_edges(
        "regenerate",
        should_reflect_again,
        {
            "reflection": "reflection",
            "end": END,
        }
    )
    
    return workflow.compile()


__all__ = [
    "create_reflection_graph",
    "initial_analysis_node",
    "reflection_node",
    "research_node",
    "regenerate_node",
]

