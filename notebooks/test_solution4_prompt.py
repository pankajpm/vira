"""
Test Solution 4: Enhanced prompt with strict citation requirements.
Quick validation that the improved prompt produces better citations.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vira.rag.pipeline import AlignmentAnalyzer


def test_enhanced_prompt():
    """Test the enhanced prompt with a sample business plan."""
    
    print("\n" + "="*80)
    print("TESTING SOLUTION 4: ENHANCED PROMPT WITH STRICT CITATIONS")
    print("="*80 + "\n")
    
    # Sample business plan - AI-powered fintech (should align with a16z)
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
    
    We've raised a $500K pre-seed round and are raising a $3M seed.
    """
    
    query = "AI fintech investment criteria venture capital"
    
    print("Business Plan Summary:")
    print("-" * 80)
    print(test_plan)
    print("\n" + "="*80 + "\n")
    
    # Run analysis
    analyzer = AlignmentAnalyzer(model_name="gpt-4o-mini")
    print("Running alignment analysis with enhanced prompt...\n")
    
    try:
        response, docs = analyzer.analyze(
            company_name="FinAI",
            plan_summary=test_plan,
            query=query
        )
        
        print("Retrieved Documents:")
        print("-" * 80)
        for i, doc in enumerate(docs[:5], 1):
            source = doc.metadata.get("url", "unknown")
            snippet = doc.page_content[:150].replace('\n', ' ')
            print(f"{i}. {source}")
            print(f"   {snippet}...\n")
        
        print("\n" + "="*80)
        print("ALIGNMENT ANALYSIS RESULTS")
        print("="*80 + "\n")
        
        print(f"Company: {response.company_name}\n")
        
        print("ALIGNMENTS:")
        print("-" * 80)
        if response.aligns:
            for i, align in enumerate(response.aligns, 1):
                print(f"\n{i}. {align.title}")
                print(f"   {align.explanation}")
                print(f"   Sources: {', '.join(align.sources)}")
        else:
            print("None found or insufficient evidence")
        
        print("\n\nGAPS:")
        print("-" * 80)
        if response.gaps:
            for i, gap in enumerate(response.gaps, 1):
                print(f"\n{i}. {gap.title}")
                print(f"   {gap.explanation}")
                print(f"   Sources: {', '.join(gap.sources)}")
        else:
            print("None found or insufficient evidence")
        
        print("\n\nSUMMARY:")
        print("-" * 80)
        print(response.summary)
        
        print("\n" + "="*80)
        print("EVALUATION CHECKLIST:")
        print("="*80)
        print("✓ Review each alignment/gap point")
        print("✓ Check if explanation contains explicit quotes")
        print("✓ Check if sources are actually cited")
        print("✓ Look for 'Limited evidence' acknowledgments if applicable")
        print("✓ Verify quotes match retrieved documents")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_enhanced_prompt()

