"""
Smoke test for the complete prototype pipeline.
Tests with diverse business plans to validate alignment/gap analysis quality.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vira.rag.pipeline import AlignmentAnalyzer


# Test business plans covering different scenarios
TEST_CASES = [
    {
        "name": "Strong Alignment - AI Fintech",
        "plan": """
        Company: FinAI
        
        AI-powered financial planning for millennials.
        
        Product: Mobile app using ML to optimize savings/investments. GPT-4 for advice.
        Market: 50M millennials, $20B TAM.
        Model: Freemium SaaS at $9.99/month.
        Traction: 10K users, 2K paid, $20K MRR, 15% MoM growth.
        Team: CEO (ex-Google AI), CTO (ex-Stripe), CFO (ex-Goldman).
        Fundraising: $500K pre-seed done, raising $3M seed.
        """,
        "query": "AI fintech SaaS investment criteria",
        "expected_alignments": 3,
        "expected_gaps": 2,
    },
    {
        "name": "Strong Gaps - Hardware Biotech",
        "plan": """
        Company: BioChip Labs
        
        Custom medical diagnostic chips for hospitals.
        
        Product: Hardware ASIC for blood test analysis.
        Market: Hospital equipment market, $5B TAM.
        Model: B2B hardware sales, $50K per device.
        Capital: Need $200M for fabrication facility.
        Timeline: 7-8 years to FDA approval and commercialization.
        Team: CEO (biology PhD), CTO (hardware engineer).
        Status: Early prototype, no customers yet.
        """,
        "query": "biotech hardware chip investment criteria",
        "expected_alignments": 1,
        "expected_gaps": 4,
    },
    {
        "name": "Mixed - Enterprise SaaS",
        "plan": """
        Company: DataFlow
        
        Enterprise data pipeline orchestration platform.
        
        Product: Cloud-based ETL/ELT tool for Fortune 500 companies.
        Market: $15B enterprise data management market.
        Model: Seats-based pricing, $1K/seat/year. 20 seats minimum.
        Traction: 15 enterprise customers, $2M ARR, 120% net retention.
        Team: CEO (ex-Snowflake), CTO (ex-Databricks).
        Fundraising: Raised $5M seed, raising $20M Series A.
        Challenges: Competitive market (Fivetran, Airbyte), sales cycle is 6-9 months.
        """,
        "query": "enterprise SaaS B2B infrastructure investment",
        "expected_alignments": 3,
        "expected_gaps": 2,
    },
    {
        "name": "Early Stage - Consumer Social",
        "plan": """
        Company: VibeTribe
        
        Social app for Gen Z to share music playlists.
        
        Product: Mobile app, TikTok-style feed for music discovery.
        Market: 70M Gen Z music listeners in US.
        Model: Ads (future), no revenue yet.
        Traction: 5K beta users, 30% DAU, viral coefficient 1.2.
        Team: CEO (24, first-time founder), CTO (recent CS grad).
        Fundraising: Bootstrapped, raising $500K pre-seed.
        """,
        "query": "consumer social mobile app investment",
        "expected_alignments": 2,
        "expected_gaps": 3,
    },
    {
        "name": "Edge Case - Vague Plan",
        "plan": """
        Company: InnovateTech
        
        We use AI to revolutionize business operations.
        
        Our platform helps companies work smarter with cutting-edge technology.
        Large market opportunity, experienced team.
        """,
        "query": "AI business software investment criteria",
        "expected_alignments": 1,
        "expected_gaps": 4,
    },
]


def run_smoke_tests():
    """Run smoke tests on diverse business plans."""
    
    print("\n" + "="*80)
    print("PROTOTYPE SMOKE TEST SUITE")
    print("="*80 + "\n")
    
    analyzer = AlignmentAnalyzer(model_name="gpt-4o-mini", use_classification=True)
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(TEST_CASES)}: {test_case['name']}")
        print(f"{'='*80}\n")
        
        print("Business Plan:")
        print("-" * 80)
        print(test_case["plan"])
        print()
        
        try:
            response, docs = analyzer.analyze(
                company_name=test_case["name"],
                plan_summary=test_case["plan"],
                query=test_case["query"]
            )
            
            num_alignments = len(response.aligns)
            num_gaps = len(response.gaps)
            
            print(f"Results:")
            print("-" * 80)
            print(f"Retrieved: {len(docs)} documents")
            print(f"Alignments: {num_alignments}")
            print(f"Gaps: {num_gaps}")
            print()
            
            # Show alignments
            if response.aligns:
                print("Top Alignments:")
                for j, align in enumerate(response.aligns[:2], 1):
                    print(f"  {j}. {align.title}")
                    # Check if has citations
                    has_vc_quote = "VC Criterion:" in align.explanation
                    has_bp_quote = "Business Plan:" in align.explanation
                    has_source = len(align.sources) > 0 and align.sources[0] != ""
                    print(f"     ✓ VC quote: {has_vc_quote}, BP quote: {has_bp_quote}, Source: {has_source}")
            else:
                print("  No alignments found")
            
            print()
            
            # Show gaps
            if response.gaps:
                print("Top Gaps:")
                for j, gap in enumerate(response.gaps[:2], 1):
                    print(f"  {j}. {gap.title}")
                    has_vc_quote = "VC Criterion:" in gap.explanation
                    has_missing = "missing" in gap.explanation.lower() or "lack" in gap.explanation.lower()
                    has_source = len(gap.sources) > 0 and gap.sources[0] != ""
                    print(f"     ✓ VC quote: {has_vc_quote}, Missing noted: {has_missing}, Source: {has_source}")
            else:
                print("  No gaps found")
            
            print()
            print("Summary:")
            print(f"  {response.summary[:150]}...")
            
            # Evaluate quality
            quality_checks = {
                "found_alignments": num_alignments > 0,
                "found_gaps": num_gaps > 0,
                "has_summary": len(response.summary) > 50,
                "alignments_have_sources": all(len(a.sources) > 0 for a in response.aligns),
                "reasonable_count": 1 <= num_alignments <= 6 and 1 <= num_gaps <= 6,
            }
            
            passed_checks = sum(quality_checks.values())
            total_checks = len(quality_checks)
            
            print(f"\nQuality Score: {passed_checks}/{total_checks} checks passed")
            
            results.append({
                "name": test_case["name"],
                "passed_checks": passed_checks,
                "total_checks": total_checks,
                "num_alignments": num_alignments,
                "num_gaps": num_gaps,
                "success": passed_checks >= total_checks * 0.6  # 60% threshold
            })
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "name": test_case["name"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*80)
    print("SMOKE TEST SUMMARY")
    print("="*80 + "\n")
    
    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    print(f"Tests Passed: {successful}/{total}\n")
    
    for result in results:
        status = "✓" if result.get("success", False) else "✗"
        print(f"{status} {result['name']}")
        if "error" in result:
            print(f"   Error: {result['error']}")
        elif "passed_checks" in result:
            print(f"   Quality: {result['passed_checks']}/{result['total_checks']}")
            print(f"   Alignments: {result['num_alignments']}, Gaps: {result['num_gaps']}")
    
    print("\n" + "="*80)
    
    if successful >= total * 0.8:  # 80% pass rate
        print("✓ PROTOTYPE VALIDATION SUCCESSFUL")
        print("  The enhanced pipeline is working as expected.")
    elif successful >= total * 0.6:  # 60% pass rate
        print("⚠ PROTOTYPE PARTIALLY WORKING")
        print("  Some improvements needed but core functionality works.")
    else:
        print("✗ PROTOTYPE NEEDS WORK")
        print("  Review failures and iterate on prompts/classification.")
    
    print("="*80 + "\n")
    
    return results


if __name__ == "__main__":
    run_smoke_tests()

