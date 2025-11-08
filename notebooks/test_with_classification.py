"""
Test the full pipeline with classification enabled.
This validates that classification improves alignment/gap citation quality.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vira.rag.pipeline import AlignmentAnalyzer


def test_with_classification():
    """Test the pipeline with classification enabled vs disabled."""
    
    print("\n" + "="*80)
    print("TESTING CLASSIFICATION-ENHANCED PIPELINE")
    print("="*80 + "\n")
    
    # Sample business plan - AI fintech
    test_plan = """
    Company: FinAI
    
    We are building an AI-powered financial planning platform for millennials.
    
    Product: Mobile-first app that uses machine learning to analyze spending patterns 
    and automatically optimize savings and investments. We leverage GPT-4 for 
    personalized financial advice.
    
    Market: Targeting 50M millennials in the US who lack access to affordable 
    financial advisors. $20B TAM.
    
    Business Model: Freemium SaaS - $9.99/month premium subscription with AI advisor.
    Unit economics: $50 CAC, $600 LTV.
    
    Traction: 10K users, 2K paying subscribers, $20K MRR, 15% month-over-month growth.
    
    Team: CEO (ex-Google AI), CTO (ex-Stripe), CFO (ex-Goldman Sachs).
    
    Fundraising: Raised $500K pre-seed, raising $3M seed round.
    
    Gaps we haven't addressed: Limited distribution strategy, no clear competitive moat,
    no regulatory compliance mentioned.
    """
    
    query = "AI fintech investment criteria venture capital"
    
    print("Business Plan:")
    print("-" * 80)
    print(test_plan)
    print("\n" + "="*80 + "\n")
    
    # Test WITH classification
    print("RUNNING WITH CLASSIFICATION ENABLED...")
    print("-" * 80 + "\n")
    
    analyzer_with_classification = AlignmentAnalyzer(model_name="gpt-4o-mini", use_classification=True)
    
    try:
        response, docs = analyzer_with_classification.analyze(
            company_name="FinAI",
            plan_summary=test_plan,
            query=query
        )
        
        print(f"\nRetrieved {len(docs)} total documents")
        
        print("\n" + "="*80)
        print("RESULTS WITH CLASSIFICATION")
        print("="*80 + "\n")
        
        print(f"Company: {response.company_name}\n")
        
        print("ALIGNMENTS:")
        print("-" * 80)
        if response.aligns:
            for i, align in enumerate(response.aligns, 1):
                print(f"\n{i}. {align.title}")
                print(f"   {align.explanation[:300]}...")
                print(f"   Sources: {', '.join(align.sources)}")
        else:
            print("None found")
        
        print("\n\nGAPS:")
        print("-" * 80)
        if response.gaps:
            for i, gap in enumerate(response.gaps, 1):
                print(f"\n{i}. {gap.title}")
                print(f"   {gap.explanation[:300]}...")
                print(f"   Sources: {', '.join(gap.sources)}")
        else:
            print("None found")
        
        print("\n\nSUMMARY:")
        print("-" * 80)
        print(response.summary)
        
        print("\n" + "="*80)
        print("EVALUATION:")
        print("="*80)
        print(f"✓ Alignments found: {len(response.aligns)}")
        print(f"✓ Gaps found: {len(response.gaps)}")
        print("✓ Check if explanations contain VC Criterion quotes")
        print("✓ Check if alignment explanations include BP quotes")
        print("✓ Check if gap explanations explain what's missing")
        print("✓ Verify sources are valid URLs")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


def compare_with_without_classification():
    """Compare results with and without classification."""
    
    print("\n" + "="*80)
    print("COMPARISON: WITH vs WITHOUT CLASSIFICATION")
    print("="*80 + "\n")
    
    test_plan = """
    Company: DeepHardware
    
    We build custom AI chips for edge computing devices.
    
    Product: ASIC chips optimized for running large language models on mobile devices.
    5x more efficient than NVIDIA GPUs for inference.
    
    Market: Edge AI market, targeting smartphone and IoT manufacturers. $50B TAM by 2027.
    
    Business Model: B2B licensing to hardware manufacturers. $10M minimum contracts.
    
    Capital Requirements: Need $100M+ for fab capacity and R&D.
    Long development cycles (3-4 years to production).
    
    Team: CEO (ex-Intel chip designer), CTO (MIT PhD in computer architecture).
    
    Current Status: Prototype chip working, 2 LOIs from smartphone manufacturers.
    """
    
    query = "hardware semiconductor chip investment criteria"
    
    print("Business Plan:")
    print("-" * 80)
    print(test_plan)
    print("\n" + "="*80 + "\n")
    
    # WITHOUT classification
    print("1. WITHOUT CLASSIFICATION:")
    print("-" * 80)
    
    analyzer_no_class = AlignmentAnalyzer(model_name="gpt-4o-mini", use_classification=False)
    
    try:
        response_no_class, _ = analyzer_no_class.analyze(
            company_name="DeepHardware",
            plan_summary=test_plan,
            query=query
        )
        print(f"Alignments: {len(response_no_class.aligns)}")
        print(f"Gaps: {len(response_no_class.gaps)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. WITH CLASSIFICATION:")
    print("-" * 80)
    
    analyzer_with_class = AlignmentAnalyzer(model_name="gpt-4o-mini", use_classification=True)
    
    try:
        response_with_class, _ = analyzer_with_class.analyze(
            company_name="DeepHardware",
            plan_summary=test_plan,
            query=query
        )
        print(f"Alignments: {len(response_with_class.aligns)}")
        print(f"Gaps: {len(response_with_class.gaps)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)
    print("Compare the quality of citations between the two approaches.")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("PROTOTYPE VALIDATION: CLASSIFICATION ENHANCEMENT")
    print("="*80)
    
    test_with_classification()
    
    print("\n\n")
    
    # Uncomment to run comparison
    # compare_with_without_classification()

