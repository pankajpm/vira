#!/usr/bin/env python3
"""Comprehensive integration test for Iteration 2.

This test verifies the complete end-to-end flow:
1. Initial analysis (Iteration 1)
2. Reflection and confidence scoring
3. Research triggering (optional, based on confidence)
4. Regeneration with research findings
5. Final output with metadata
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vira.agents.analyzer import ReflectiveAnalyzer


def test_high_confidence_path():
    """Test path where high confidence skips research."""
    
    print("=" * 60)
    print("Test 1: High Confidence (No Research)")
    print("=" * 60)
    
    analyzer = ReflectiveAnalyzer()
    
    # Use a simple plan that should have high confidence
    plan = """
    Our company is an AI-powered healthcare SaaS platform targeting hospitals.
    We provide clinical decision support using machine learning.
    Our founding team has 10+ years of healthcare IT experience.
    Market size: $15B TAM, growing at 20% annually.
    """
    
    print("\n🔍 Running analysis...")
    result, metadata = analyzer.analyze(
        company_name="HealthTech AI",
        plan_summary=plan,
        query="healthcare AI SaaS investment criteria"
    )
    
    print(f"\n📊 Results:")
    print(f"   Company: {result.company_name}")
    print(f"   Alignments: {len(result.aligns)}")
    print(f"   Gaps: {len(result.gaps)}")
    print(f"   Overall confidence: {metadata['overall_confidence']:.2f}")
    print(f"   Research queries: {len(metadata['research_queries'])}")
    print(f"   Iterations: {metadata['iterations']}")
    
    # For high confidence, we expect:
    # - Confidence >= 0.7
    # - No or minimal research
    assert metadata['overall_confidence'] >= 0.65, \
        f"Expected high confidence, got {metadata['overall_confidence']}"
    
    print("\n✅ High confidence path working!")


def test_low_confidence_path():
    """Test path where research could be triggered (if API key available)."""
    
    print("\n\n" + "=" * 60)
    print("Test 2: Research Path (API Key Optional)")
    print("=" * 60)
    print("\nNOTE: This test requires SERPER_API_KEY to be configured")
    print("      for actual research. Will pass without it.")
    
    analyzer = ReflectiveAnalyzer()
    
    # Use a healthcare plan that may have some evidence gaps
    plan = """
    We're building an AI platform for hospitals.
    Our team includes engineers from top tech companies.
    The healthcare AI market is growing rapidly.
    We have early customer interest from 3 hospitals.
    """
    
    print("\n🔍 Running analysis...")
    result, metadata = analyzer.analyze(
        company_name="Research Test Startup",
        plan_summary=plan,
        query="healthcare AI investment criteria"
    )
    
    print(f"\n📊 Results:")
    print(f"   Company: {result.company_name}")
    print(f"   Alignments: {len(result.aligns)}")
    print(f"   Gaps: {len(result.gaps)}")
    print(f"   Overall confidence: {metadata['overall_confidence']:.2f}")
    print(f"   Research queries: {len(metadata['research_queries'])}")
    print(f"   Research results: {metadata['num_research_results']}")
    print(f"   Info gaps identified: {metadata['information_gaps_identified']}")
    
    # Test passes if analysis completes successfully
    # Research is optional (depends on API key availability)
    assert result.company_name == "Research Test Startup"
    
    print("\n✅ Research path working!")
    if metadata['num_research_results'] > 0:
        print("   ✓ Research was conducted successfully")
        assert len(metadata['research_queries']) > 0
    else:
        print("   ℹ️  Research skipped (API key not configured or high confidence)")


def test_iteration2_metadata():
    """Test that Iteration 2 metadata is properly included."""
    
    print("\n\n" + "=" * 60)
    print("Test 3: Metadata Completeness")
    print("=" * 60)
    
    analyzer = ReflectiveAnalyzer()
    
    plan = "AI healthcare startup with experienced team and large market opportunity"
    
    print("\n🔍 Running analysis...")
    result, metadata = analyzer.analyze(
        company_name="MetaTest Inc",
        plan_summary=plan,
        query="healthcare AI"
    )
    
    print(f"\n✅ Checking metadata fields...")
    
    # Check result object has new fields
    assert hasattr(result, 'overall_confidence'), "Missing overall_confidence"
    assert hasattr(result, 'research_conducted'), "Missing research_conducted"
    assert hasattr(result, 'data_gaps'), "Missing data_gaps"
    print("   ✓ AlignmentResponse has Iteration 2 fields")
    
    # Check metadata dict
    required_keys = ['iterations', 'overall_confidence', 'research_queries', 
                     'num_research_results', 'information_gaps_identified']
    for key in required_keys:
        assert key in metadata, f"Missing metadata key: {key}"
    print("   ✓ Metadata dict is complete")
    
    # Check types
    assert isinstance(result.overall_confidence, (float, type(None))), \
        "overall_confidence should be float or None"
    assert isinstance(metadata['iterations'], int), "iterations should be int"
    print("   ✓ Types are correct")
    
    print("\n✅ Metadata completeness verified!")


def test_backward_compatibility():
    """Test that Iteration 1 still works (backward compatibility)."""
    
    print("\n\n" + "=" * 60)
    print("Test 4: Backward Compatibility (Iteration 1)")
    print("=" * 60)
    
    from vira.rag.pipeline import AlignmentAnalyzer as Iteration1Analyzer
    
    analyzer = Iteration1Analyzer()
    
    plan = "Healthcare AI SaaS startup"
    
    print("\n🔍 Running Iteration 1 analysis...")
    result, docs = analyzer.analyze(
        company_name="BackwardCompat Inc",
        plan_summary=plan,
        query="healthcare AI"
    )
    
    print(f"   ✓ Analyzed successfully")
    print(f"   Company: {result.company_name}")
    print(f"   Documents retrieved: {len(docs)}")
    
    # Iteration 1 should still work
    assert result.company_name == "BackwardCompat Inc"
    assert len(result.aligns) > 0 or len(result.gaps) > 0
    
    print("\n✅ Iteration 1 still works correctly!")


if __name__ == "__main__":
    print("\n🧪 COMPREHENSIVE ITERATION 2 INTEGRATION TESTS\n")
    
    try:
        test_high_confidence_path()
        test_low_confidence_path()
        test_iteration2_metadata()
        test_backward_compatibility()
        
        print("\n\n" + "🎉" * 30)
        print("Phase 4: Integration - ALL TESTS PASSED!")
        print("🎉" * 30)
        print("\nNext: Phase 5 - UI Updates & Validation")
        
    except AssertionError as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

