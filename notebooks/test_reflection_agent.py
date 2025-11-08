#!/usr/bin/env python3
"""Test reflection agent functionality.

This test verifies Phase 2 implementation: reflection agent can assess
confidence, identify gaps, and trigger research appropriately.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_openai import ChatOpenAI
from vira.agents.reflection import (
    assess_claim_confidence,
    identify_information_gaps,
    reflect_on_explanation,
)
from vira.rag.pipeline import AlignmentResponse, AlignmentSection


def test_confidence_scoring() -> None:
    """Test that confidence scoring works."""
    
    print("=" * 60)
    print("Test 1: Confidence Scoring")
    print("=" * 60)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    # Test with strong evidence
    print("\n📊 Testing strong evidence claim...")
    claim_strong = "Market Focus: Healthcare SaaS aligns with VC investment thesis"
    evidence_strong = """
    Source: a16z.com/healthcare-thesis
    "We invest heavily in healthcare technology, particularly SaaS solutions targeting providers and payers."
    
    Source: a16z.com/portfolio/health-tech
    "Our healthcare portfolio includes multiple SaaS companies serving hospitals and clinics."
    """
    
    score, reasoning = assess_claim_confidence(claim_strong, evidence_strong, llm)
    print(f"   Score: {score:.2f}")
    print(f"   Reasoning: {reasoning[:200]}...")
    assert score >= 0.7, f"Expected high confidence for strong evidence, got {score}"
    
    # Test with weak evidence
    print("\n📊 Testing weak evidence claim...")
    claim_weak = "Geographic Preference: Company location matches VC preference"
    evidence_weak = """
    Source: a16z.com/about
    "Andreessen Horowitz is headquartered in Menlo Park, California."
    
    (No clear statement about geographic investment preferences)
    """
    
    score_weak, reasoning_weak = assess_claim_confidence(claim_weak, evidence_weak, llm)
    print(f"   Score: {score_weak:.2f}")
    print(f"   Reasoning: {reasoning_weak[:200]}...")
    assert score_weak <= 0.6, f"Expected low confidence for weak evidence, got {score_weak}"
    
    print("\n✅ Confidence scoring working!")


def test_gap_identification() -> None:
    """Test information gap identification."""
    
    print("\n\n" + "=" * 60)
    print("Test 2: Gap Identification")
    print("=" * 60)
    
    # Create mock explanation with varying confidence
    explanation = AlignmentResponse(
        company_name="Test Startup",
        aligns=[
            AlignmentSection(
                title="Market Alignment",
                explanation="Good market fit",
                sources=["http://example.com"]
            ),
            AlignmentSection(
                title="Team Experience",
                explanation="Strong team background",
                sources=["http://example.com"]
            ),
        ],
        gaps=[
            AlignmentSection(
                title="Geographic Mismatch",
                explanation="Company not in preferred region",
                sources=["http://example.com"]
            ),
        ],
        summary="Mixed alignment"
    )
    
    # Mock confidence scores (align_0: high, align_1: low, gap_0: low)
    confidence_scores = {
        "align_0": 0.85,  # High confidence
        "align_1": 0.45,  # Low confidence - should trigger gap
        "gap_0": 0.50,    # Low confidence - should trigger gap
    }
    
    print("\n🔍 Identifying gaps...")
    gaps = identify_information_gaps(explanation, confidence_scores)
    
    print(f"   Found {len(gaps)} information gaps")
    for gap in gaps:
        print(f"   - [{gap.category}] {gap.description} (Priority: {gap.priority})")
    
    assert len(gaps) == 2, f"Expected 2 gaps, found {len(gaps)}"
    assert gaps[0].priority <= gaps[1].priority, "Gaps should be sorted by priority"
    
    print("\n✅ Gap identification working!")


def test_full_reflection() -> None:
    """Test full reflection workflow."""
    
    print("\n\n" + "=" * 60)
    print("Test 3: Full Reflection Workflow")
    print("=" * 60)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    # Create a simple explanation
    explanation = AlignmentResponse(
        company_name="AI Healthcare Startup",
        aligns=[
            AlignmentSection(
                title="Sector Focus",
                explanation="AI healthcare SaaS matches VC thesis on healthcare innovation",
                sources=["http://a16z.com/healthcare"]
            ),
        ],
        gaps=[
            AlignmentSection(
                title="Team Background",
                explanation="No clear indication if team has healthcare domain expertise",
                sources=["http://a16z.com/portfolio"]
            ),
        ],
        summary="Strong sector fit, unclear on team qualifications"
    )
    
    # Mock retrieved docs
    class MockDoc:
        def __init__(self, content: str, url: str):
            self.page_content = content
            self.metadata = {"url": url}
    
    docs = [
        MockDoc("We invest in healthcare technology startups...", "http://a16z.com/healthcare"),
        MockDoc("Portfolio companies typically have experienced founding teams...", "http://a16z.com/portfolio"),
    ]
    
    print("\n🤔 Running full reflection...")
    result = reflect_on_explanation(explanation, docs, llm)
    
    print(f"   Overall confidence: {result.overall_confidence:.2f}")
    print(f"   Claims assessed: {len(result.per_claim_confidence)}")
    print(f"   Information gaps: {len(result.information_gaps)}")
    print(f"\n   Reasoning preview:\n{result.reasoning[:300]}...")
    
    assert 0.0 <= result.overall_confidence <= 1.0, "Confidence should be 0-1"
    assert len(result.per_claim_confidence) == 2, "Should assess both claims"
    
    print("\n✅ Full reflection working!")


def test_reflection_triggers_research() -> None:
    """Test that low confidence triggers research decision."""
    
    print("\n\n" + "=" * 60)
    print("Test 4: Research Trigger Logic")
    print("=" * 60)
    
    from vira.agents.graph import should_research
    
    # Low confidence should trigger research
    state_low = {"overall_confidence": 0.5, "iteration_count": 0}
    decision = should_research(state_low)  # type: ignore
    print(f"   Low confidence (0.5): {decision}")
    assert decision == "research", "Should trigger research"
    
    # High confidence should not trigger research
    state_high = {"overall_confidence": 0.85, "iteration_count": 0}
    decision2 = should_research(state_high)  # type: ignore
    print(f"   High confidence (0.85): {decision2}")
    assert decision2 == "end", "Should not trigger research"
    
    # Max iterations should not trigger research even with low confidence
    state_max_iter = {"overall_confidence": 0.5, "iteration_count": 2}
    decision3 = should_research(state_max_iter)  # type: ignore
    print(f"   Low confidence but max iterations: {decision3}")
    assert decision3 == "end", "Should not trigger research at max iterations"
    
    print("\n✅ Research trigger logic working!")


if __name__ == "__main__":
    print("\n🧪 TESTING REFLECTION AGENT (Phase 2)\n")
    
    try:
        test_confidence_scoring()
        test_gap_identification()
        test_full_reflection()
        test_reflection_triggers_research()
        
        print("\n\n" + "🎉" * 30)
        print("Phase 2: Reflection Agent - ALL TESTS PASSED!")
        print("🎉" * 30)
        print("\nNext: Phase 3 - Research Agent Implementation")
        
    except AssertionError as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

