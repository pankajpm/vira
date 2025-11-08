I'll help you find a quick ROI solution for the VIRA alignment analysis issue. Let me first examine the current implementation to understand the problem better.6 stepsSearched project for “pipeline.py buildprompt code implementation”4 resultsState-of-the-Art Research Agent Technology for Venture Capital Investment Workflows: 2025 Production Maturity Analysis.mdtextpart3.py3 relevant sectionstextVIRA_MVP_Architecture_Design_Doc.md3 relevant sectionstextVIRA_MVP_Architecture_Design_Doc.mdtextDiagnosed RAG architecture flaw, formulated pragmatic implementation solutions.I see part3.py but it doesn't seem to be the pipeline.py they're referring to. Let me check if they might be referring to code that's described in the documentation rather than an actual file in the project. Let me look more carefully at the problem description they gave me and focus on providing solutions.
The core problem is clear:

The current system retrieves documents based on semantic similarity to the business plan
When it says "Alignment" or "Gap/Misalignment", it cites those retrieved documents
But those documents were retrieved for semantic match, NOT specifically because they demonstrate alignment or misalignment
So the citations don't actually prove the alignment/gap claim being made

This is a fundamental RAG architecture issue. They need quick ROI solutions.
Let me propose practical solutions that can be implemented quickly.Based on the project knowledge and the problem you've described, I can see the core issue: your retrieval is semantically matching content, but not explicitly determining whether that content supports alignment OR misalignment. Here are quick ROI solutions, ordered by implementation speed:
Solution 1: Two-Pass Retrieval with Explicit Alignment Queries (Fastest - 1-2 days)
Instead of one semantic search, do two targeted retrievals:
pythondef buildprompt_with_alignment_retrieval(business_plan, vc_criteria_db):
    # Pass 1: Retrieve for ALIGNMENT evidence
    alignment_query = f"VC investment criteria that match: {business_plan_summary}"
    alignment_chunks = retrieve(alignment_query, top_k=5)
    
    # Pass 2: Retrieve for MISALIGNMENT evidence  
    misalignment_query = f"VC investment criteria that would reject: {business_plan_summary}"
    # OR use negation patterns: "VC avoids: [business_plan_attributes]"
    misalignment_chunks = retrieve(misalignment_query, top_k=5)
    
    # Pass 3: (Optional) Retrieve for general context
    context_chunks = retrieve(business_plan_summary, top_k=3)
    
    return {
        'alignment_evidence': alignment_chunks,
        'misalignment_evidence': misalignment_chunks,
        'general_context': context_chunks
    }
In AlignmentAnalyzer:
pythonprompt = f"""
EVIDENCE SUPPORTING ALIGNMENT:
{alignment_chunks}

EVIDENCE SUGGESTING GAPS:
{misalignment_chunks}

GENERAL CONTEXT:
{context_chunks}

Task: Analyze alignment using ONLY the evidence provided in each section.
- Cite alignment points using sources from ALIGNMENT section
- Cite gaps using sources from MISALIGNMENT section
"""
Pros: Quick to implement, forces explicit categorization
Cons: Requires good query formulation, may miss nuanced criteria

Solution 2: Post-Retrieval Alignment Classification (Quick - 2-3 days)
After retrieving chunks, classify each one as supporting alignment, misalignment, or neutral:
pythondef classify_chunks_for_alignment(business_plan, retrieved_chunks):
    classified_chunks = {
        'supports_alignment': [],
        'suggests_gaps': [],
        'neutral': []
    }
    
    for chunk in retrieved_chunks:
        # Use fast LLM call (gpt-4o-mini, ~$0.001/call)
        classification_prompt = f"""
        Business Plan Key Points: {plan_summary}
        VC Criterion Chunk: {chunk.text}
        
        Does this criterion: A) Align with the plan, B) Reveal a gap, C) Neutral
        Respond with ONLY: A, B, or C
        """
        
        category = llm_classify(classification_prompt)  # Fast, cheap call
        
        if category == 'A':
            classified_chunks['supports_alignment'].append(chunk)
        elif category == 'B':
            classified_chunks['suggests_gaps'].append(chunk)
        else:
            classified_chunks['neutral'].append(chunk)
    
    return classified_chunks
Cost: ~$0.10-0.20 per analysis (20 chunks × $0.001 per classification)
Speed: Adds 2-3 seconds latency

Solution 3: Hybrid of Your Suggested Approaches (Best ROI - 3-5 days)
Combine query expansion with bidirectional matching:
pythondef enhanced_alignment_retrieval(business_plan, vc_criteria_db):
    # Step 1: Extract key business plan claims
    bp_claims = extract_key_claims(business_plan)  # LLM call
    # Returns: ["strong network effects", "defensible moat via data", etc.]
    
    # Step 2: Query expansion for each claim
    expanded_queries = []
    for claim in bp_claims:
        # Generate 3-5 semantic variations per claim
        variations = generate_query_variations(claim)  # LLM call
        expanded_queries.extend(variations)
    
    # Step 3: Retrieve with RRF (Reciprocal Rank Fusion)
    all_results = []
    for query in expanded_queries:
        results = retrieve(query, top_k=3)
        all_results.append((query, results))
    
    # Merge using RRF
    merged_chunks = reciprocal_rank_fusion(all_results)
    
    # Step 4: Bidirectional scoring
    final_scored_chunks = []
    for chunk in merged_chunks:
        # Score both directions
        bp_to_vc_score = semantic_similarity(bp_claims, chunk.text)
        vc_to_bp_score = semantic_similarity(chunk.text, bp_claims)
        
        # Keep if EITHER direction scores high
        max_score = max(bp_to_vc_score, vc_to_bp_score)
        if max_score > threshold:
            final_scored_chunks.append({
                'chunk': chunk,
                'score': max_score,
                'direction': 'bp→vc' if bp_to_vc_score > vc_to_bp_score else 'vc→bp'
            })
    
    return final_scored_chunks

Solution 4: Simplest Quick Fix - Prompt Engineering (Hours, not days)
Fix it purely in the prompt without changing retrieval:
pythondef buildprompt_improved(business_plan, retrieved_chunks):
    prompt = f"""
You are analyzing alignment between a business plan and VC investment criteria.

RETRIEVED VC CRITERIA CONTEXT (for reference only):
{retrieved_chunks}

BUSINESS PLAN:
{business_plan}

CRITICAL INSTRUCTIONS:
1. For EACH alignment point you identify, you MUST:
   - Quote the specific VC criterion from the context that supports it
   - Quote the specific business plan text that matches it
   - If you cannot find supporting evidence in the context, DO NOT cite that point

2. For EACH gap you identify, you MUST:
   - Quote the specific VC criterion the plan is missing
   - Explain why the business plan doesn't address this
   - If you cannot find gap evidence in the context, DO NOT cite that point

3. ONLY cite points where you have explicit evidence in the retrieved context.

4. If you cannot find 3+ alignment points AND 3+ gaps with explicit evidence,
   acknowledge: "Limited evidence available in retrieved context for [alignment/gaps]"

OUTPUT FORMAT:
ALIGNMENTS:
1. [Point] - VC Source: "exact quote" | BP Source: "exact quote"

GAPS:  
1. [Point] - VC Criterion: "exact quote" | BP Status: [missing/unclear]
"""
Pros: Zero code changes, can implement immediately
Cons: Still relies on retrieved chunks having the right evidence

My Recommendation: Solution 2 + 4 Combined (2 days total)
Day 1: Implement post-retrieval classification (Solution 2)

Takes your existing retrieval
Adds a fast classification step
Separates alignment vs. gap evidence

Day 2: Enhance the prompt (Solution 4)

Forces explicit evidence citation
Prevents hallucinated alignments/gaps
Works with the classified chunks

Why this combo wins:

✅ Doesn't require changing your retrieval pipeline architecture
✅ Adds clear evidence categorization
✅ Low latency impact (~2-3 seconds)
✅ Low cost (~$0.10-0.20 per analysis)
✅ Can implement incrementally (try prompt first, add classification if needed)

Quick validation test:
python# Run on 10 test business plans
# Measure: % of cited alignments/gaps that actually have supporting evidence
# Target: >80% have clear supporting quotes from classified chunks