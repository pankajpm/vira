"""
Quick corpus spot check to validate gap evidence exists.
Run this to check if vector store contains gap-relevant content.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vira.vectorstore.manager import load_vectorstore
from vira.retrieval.hybrid import HybridRetriever


def spot_check_corpus():
    """Manual spot check queries to validate gap evidence availability."""
    
    print("Loading vector store...")
    vectorstore = load_vectorstore()
    retriever = HybridRetriever(vectorstore, k=10)
    
    # Test queries designed to find gap/misalignment evidence
    test_queries = [
        "What does a16z avoid investing in",
        "Red flags for venture capital investors",
        "Why investors pass on deals",
        "Investment criteria that lead to rejection",
        "What makes a business plan unattractive to VCs",
    ]
    
    print("\n" + "="*80)
    print("CORPUS GAP EVIDENCE SPOT CHECK")
    print("="*80)
    
    gap_evidence_count = 0
    
    for query in test_queries:
        print(f"\n{'─'*80}")
        print(f"Query: {query}")
        print(f"{'─'*80}")
        
        docs = retriever.get_relevant_documents(query)
        
        print(f"\nRetrieved {len(docs)} documents:\n")
        
        for i, doc in enumerate(docs[:5], 1):  # Show top 5
            source = doc.metadata.get("url", "unknown")
            snippet = doc.page_content[:200].replace('\n', ' ')
            print(f"{i}. [{source}]")
            print(f"   {snippet}...\n")
            
            # Simple heuristic: check if content contains gap-indicating keywords
            gap_keywords = ['avoid', 'not invest', 'red flag', 'reject', 'pass on', 
                          'concern', 'risk', 'challenge', 'weakness', 'gap']
            if any(keyword in doc.page_content.lower() for keyword in gap_keywords):
                gap_evidence_count += 1
    
    print(f"\n{'='*80}")
    print(f"SUMMARY: Found ~{gap_evidence_count} chunks with potential gap evidence")
    print(f"         across {len(test_queries)} test queries")
    
    if gap_evidence_count >= 10:
        print("✓ GOOD: Sufficient gap evidence exists in corpus")
        print("  → Proceed with classification approach")
    elif gap_evidence_count >= 5:
        print("⚠ MODERATE: Some gap evidence exists but limited")
        print("  → Proceed with caution, may need synthetic generation later")
    else:
        print("✗ INSUFFICIENT: Very little gap evidence found")
        print("  → Consider two-pass retrieval or synthetic gap generation")
    print(f"{'='*80}\n")
    
    return gap_evidence_count


if __name__ == "__main__":
    spot_check_corpus()

