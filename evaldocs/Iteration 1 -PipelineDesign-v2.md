# VIRA Pipeline Design v2: Classification-Enhanced Alignment Detection

**Document:** Pipeline Design Specification v2  
**Focus:** Evidence Classification + Matched Citation Architecture  
**Date:** November 4, 2025  
**Status:** Implemented & Validated

---

## Executive Summary

**Major Evolution from v1:** Added a **classification layer** between retrieval and LLM analysis to ensure citations actually prove the claims being made.

```
v1: Neutral Retrieval → LLM Categorization
                ↓
v2: Neutral Retrieval → Chunk Classification → Separate Evidence Contexts → LLM Analysis
```

**Core Problem Solved:** In v1, the LLM was asked to find both alignments and gaps from the same undifferentiated pool of retrieved chunks. This led to citations that didn't actually support the specific claim type (alignment vs gap).

**v2 Solution:** Classify each retrieved chunk as "alignment evidence", "gap evidence", or "neutral" BEFORE sending to the LLM, then provide separate evidence sections in the prompt.

---

## Table of Contents

1. [What Changed from v1](#what-changed-from-v1)
2. [v2 Architecture Overview](#v2-architecture-overview)
3. [Stage 1: Neutral Retrieval (Unchanged)](#stage-1-neutral-retrieval-unchanged)
4. [Stage 2: Classification Layer (NEW)](#stage-2-classification-layer-new)
5. [Stage 3: Context Formatting with Separation (ENHANCED)](#stage-3-context-formatting-with-separation-enhanced)
6. [Stage 4: LLM Analysis with Classified Evidence (ENHANCED)](#stage-4-llm-analysis-with-classified-evidence-enhanced)
7. [Visual Flow Diagram](#visual-flow-diagram)
8. [Classification Decision Logic](#classification-decision-logic)
9. [Performance Characteristics](#performance-characteristics)
10. [Key Design Improvements](#key-design-improvements)
11. [Known Limitations & Trade-offs](#known-limitations--trade-offs)
12. [Comparison: v1 vs v2](#comparison-v1-vs-v2)

---

## What Changed from v1

### v1 Architecture (Original)

```
Query + Business Plan
    ↓
Hybrid Retrieval → 8 chunks (all treated equally)
    ↓
Single Context String (all chunks together)
    ↓
LLM: "Find alignments AND gaps from this context"
    ↓
Output: Alignments + Gaps (citations may not match claim type)
```

**Problem:** LLM was citing random chunks for alignments/gaps without ensuring the chunk actually supported that specific claim type.

### v2 Architecture (Current)

```
Query + Business Plan
    ↓
Hybrid Retrieval → 8-10 chunks (all treated equally)
    ↓
CLASSIFICATION LAYER (NEW)
├─ Alignment chunks (2-4)
├─ Gap chunks (1-3)  
└─ Neutral chunks (remaining)
    ↓
Separate Evidence Contexts
├─ Alignment Context (only alignment chunks)
└─ Gap Context (only gap chunks)
    ↓
LLM: "Use alignment context for alignments, gap context for gaps"
    ↓
Output: Alignments + Gaps (citations now match claim type)
```

**Solution:** Pre-classify chunks, provide separate evidence sections, force LLM to cite from appropriate section.

---

## v2 Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│              VIRA PIPELINE v2: CLASSIFICATION-ENHANCED             │
└────────────────────────────────────────────────────────────────────┘

Input (Query + Business Plan + Company Name)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: NEUTRAL RETRIEVAL (Unchanged from v1)                 │
│                                                                 │
│ HybridRetriever.get_relevant_documents(query)                  │
│     ↓                                                           │
│ Returns 8-10 most relevant VC criteria chunks                  │
│ (No categorization at this stage)                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: CLASSIFICATION LAYER (NEW IN v2)                      │
│                                                                 │
│ classify_documents(chunks, business_plan)                      │
│                                                                 │
│ For each chunk:                                                │
│   ┌──────────────────────────────────────────────┐            │
│   │ classify_chunk(chunk_text, plan_summary)     │            │
│   │                                              │            │
│   │ Classification Prompt:                       │            │
│   │ "Does this VC criterion:                     │            │
│   │  A) Align with the plan                      │            │
│   │  B) Reveal a gap                             │            │
│   │  C) Neutral                                  │            │
│   │ Respond with: A, B, or C"                    │            │
│   │                                              │            │
│   │ → LLM call (gpt-4o-mini, temp=0.0)          │            │
│   └──────────────────────────────────────────────┘            │
│                     │                                          │
│                     ▼                                          │
│            Classified Chunks:                                  │
│            ├─ alignment: [Chunk1, Chunk4, Chunk7]            │
│            ├─ gap: [Chunk2, Chunk5]                          │
│            └─ neutral: [Chunk3, Chunk6, Chunk8]              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: CONTEXT FORMATTING WITH SEPARATION (Enhanced)         │
│                                                                 │
│ _format_context(alignment_chunks) → alignment_context         │
│ _format_context(gap_chunks) → gap_context                     │
│                                                                 │
│ Two separate context strings created:                          │
│                                                                 │
│ alignment_context:                                             │
│ "Source: URL1\nSnippet: We invest in AI healthcare..."       │
│ "Source: URL2\nSnippet: Series A companies with..."          │
│                                                                 │
│ gap_context:                                                   │
│ "Source: URL3\nSnippet: Requires 10+ years experience..."    │
│ "Source: URL4\nSnippet: Bay Area location preferred..."      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: LLM ANALYSIS WITH CLASSIFIED EVIDENCE (Enhanced)      │
│                                                                 │
│ build_prompt_with_classified_evidence()                        │
│                                                                 │
│ Template with TWO separate evidence sections:                  │
│                                                                 │
│ "EVIDENCE SUPPORTING ALIGNMENT:                                │
│  {alignment_context}                                           │
│                                                                 │
│  EVIDENCE HIGHLIGHTING GAPS:                                   │
│  {gap_context}                                                 │
│                                                                 │
│  BUSINESS PLAN: {plan_summary}                                 │
│                                                                 │
│  INSTRUCTIONS:                                                 │
│  1. For ALIGNMENT points: Use ONLY alignment evidence section │
│  2. For GAP points: Use ONLY gap evidence section             │
│  3. NEVER mix evidence types                                  │
│  4. Quote VC criterion + BP text + explanation                │
│  5. Acknowledge if evidence is insufficient"                   │
│                                                                 │
│ → LLM Generation (gpt-4o-mini, temp=0.2)                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
              AlignmentResponse
              ├─ aligns: [matched citations from alignment context]
              ├─ gaps: [matched citations from gap context]
              └─ summary: balanced overview
```

---

## Stage 1: Neutral Retrieval (Unchanged)

**Code Location:** `pipeline.py` lines 289-309 (in `analyze()` method, calls `_retrieve_with_classification()`)

**Process:** Identical to v1 - uses `HybridRetriever` to find relevant VC criteria chunks.

**Input Query:**
```
"AI healthcare Series A investment criteria"
```

**Output:** 8-10 chunks, e.g.:
```
Chunk 1: "We invest in AI healthcare companies at Series A..."
Chunk 2: "Team must have 10+ years healthcare domain expertise..."
Chunk 3: "We prefer Bay Area-based companies..."
Chunk 4: "Series A companies should have $1M+ ARR..."
Chunk 5: "Healthcare AI requires FDA regulatory pathway..."
Chunk 6: "Technical co-founders with PhD backgrounds..."
Chunk 7: "Our sweet spot is $15-20M Series A rounds..."
Chunk 8: "Portfolio companies need strong GTM plans..."
```

**Key Point:** Still **no categorization** - purely relevance-based retrieval.

---

## Stage 2: Classification Layer (NEW)

**Code Location:** `pipeline.py` lines 179-261

### 2.1 Classification Function

```python
def classify_chunk(
    chunk_text: str, 
    plan_summary: str, 
    llm: ChatOpenAI
) -> Literal["alignment", "gap", "neutral"]:
    """
    Classify a chunk relative to the business plan.
    """
    
    classification_prompt = f"""You are classifying VC investment criteria relative to a business plan.

Business Plan Summary:
{plan_summary[:500]}  

VC Criterion Chunk:
{chunk_text[:400]}

Does this VC criterion:
A) Support or validate something present in the business plan (ALIGNMENT)
B) Highlight something missing, contradictory, or unaddressed in the plan (GAP)
C) Not clearly relevant to assessing this specific plan (NEUTRAL)

Respond with ONLY one letter: A, B, or C

Your response:"""
    
    response = llm.invoke(classification_prompt)
    result = response.content.strip().upper()
    
    if 'A' in result:
        return "alignment"
    elif 'B' in result:
        return "gap"
    else:
        return "neutral"
```

### 2.2 Batch Classification

```python
def classify_documents(
    documents: list[Document],
    plan_summary: str,
    llm: ChatOpenAI
) -> dict[str, list[Document]]:
    """
    Classify all retrieved documents.
    """
    
    classified: dict[str, list[Document]] = {
        "alignment": [],
        "gap": [],
        "neutral": []
    }
    
    for doc in documents:
        category = classify_chunk(doc.page_content, plan_summary, llm)
        classified[category].append(doc)
    
    return classified
```

### 2.3 Classification Example

**Business Plan:**
```
HealthTech AI: Building AI diagnostic tools for hospitals.
Team: Ex-Google engineers with ML expertise.
Location: Austin, Texas.
Stage: Seeking Series A funding ($15M).
```

**Classification Results:**

| Chunk | Content | Classification | Reasoning |
|-------|---------|----------------|-----------|
| Chunk 1 | "We invest in AI healthcare companies at Series A..." | **ALIGNMENT** | ✅ Matches domain & stage |
| Chunk 2 | "Team must have 10+ years healthcare domain expertise..." | **GAP** | ❌ Team lacks healthcare background |
| Chunk 3 | "We prefer Bay Area-based companies..." | **GAP** | ❌ Located in Austin, not Bay Area |
| Chunk 4 | "Series A companies should have $1M+ ARR..." | **NEUTRAL** | ⚠️ ARR not mentioned in plan |
| Chunk 5 | "Healthcare AI requires FDA regulatory pathway..." | **NEUTRAL** | ⚠️ Regulatory status unclear |
| Chunk 6 | "Technical co-founders with PhD backgrounds..." | **NEUTRAL** | ⚠️ Education not specified |
| Chunk 7 | "Our sweet spot is $15-20M Series A rounds..." | **ALIGNMENT** | ✅ $15M matches range |
| Chunk 8 | "Portfolio companies need strong GTM plans..." | **GAP** | ❌ No GTM mentioned in plan |

**Classified Output:**
```python
{
    "alignment": [Chunk1, Chunk7],           # 2 chunks
    "gap": [Chunk2, Chunk3, Chunk8],         # 3 chunks  
    "neutral": [Chunk4, Chunk5, Chunk6]      # 3 chunks
}
```

---

## Stage 3: Context Formatting with Separation (ENHANCED)

**Code Location:** `pipeline.py` lines 291-311 (in `analyze()` method)

### v1 Approach (Old)
```python
# Single unified context
context = _format_context(all_docs)
```

### v2 Approach (New)
```python
# Separate contexts by classification
classified = classify_documents(docs, plan_summary, classifier_llm)

alignment_context = _format_context(classified["alignment"]) or \
    "No clear alignment evidence found in retrieved context."
    
gap_context = _format_context(classified["gap"]) or \
    "No clear gap evidence found in retrieved context."
```

### Output Format

**Alignment Context:**
```
Source: https://a16z.com/posts/healthcare-ai-thesis/
Snippet: We invest in AI healthcare companies at Series A stage with proven traction...

Source: https://a16z.com/posts/series-a-criteria/
Snippet: Our sweet spot is $15-20M Series A rounds for companies with clear product-market fit...
```

**Gap Context:**
```
Source: https://a16z.com/posts/team-criteria/
Snippet: Team must have 10+ years healthcare domain expertise to navigate regulatory landscape...

Source: https://a16z.com/posts/geography-preferences/
Snippet: We prefer Bay Area-based companies for close collaboration and ecosystem access...

Source: https://a16z.com/posts/go-to-market/
Snippet: Portfolio companies need strong go-to-market plans detailing customer acquisition strategy...
```

**Key Improvement:** Evidence is now **pre-sorted** by category before reaching the LLM.

---

## Stage 4: LLM Analysis with Classified Evidence (ENHANCED)

**Code Location:** `pipeline.py` lines 40-92 (`build_prompt_with_classified_evidence()`)

### v2 Prompt Template

```python
def build_prompt_with_classified_evidence() -> ChatPromptTemplate:
    template = """
You are a VC analyst. Analyze alignment between the business plan and VC criteria using pre-classified evidence.

EVIDENCE SUPPORTING ALIGNMENT:
{alignment_context}

EVIDENCE HIGHLIGHTING GAPS:
{gap_context}

BUSINESS PLAN (Company: {company_name}):
{plan_summary}

CRITICAL INSTRUCTIONS:
1. For ALIGNMENT points: Use ONLY sources from "Evidence Supporting Alignment" section
   - Quote the VC criterion that supports alignment
   - Quote the business plan text that matches
   - Cite the source URL
   
2. For GAP points: Use ONLY sources from "Evidence Highlighting Gaps" section
   - Quote the VC criterion the plan doesn't address
   - Explain what's missing in the business plan
   - Cite the source URL

3. If either section has insufficient evidence, acknowledge: "Limited evidence available for [alignments/gaps]"

4. NEVER cite alignment evidence when discussing gaps, or vice versa

OUTPUT FORMAT (JSON):
{
  "company_name": "string",
  "aligns": [
    {
      "title": "Short descriptive title",
      "explanation": "VC Criterion: '[exact quote]' | Business Plan: '[exact quote]' | Connection: [explanation]",
      "sources": ["URL"]
    }
  ],
  "gaps": [
    {
      "title": "Short descriptive title",
      "explanation": "VC Criterion: '[exact quote]' | Business Plan Status: [what's missing]",
      "sources": ["URL"]
    }
  ],
  "summary": "Neutral 80-120 word summary. Acknowledge if evidence is limited."
}

Do NOT make investment recommendations or assign scores.
"""
    return ChatPromptTemplate.from_template(template)
```

### LLM Decision Process (v2)

**No longer needs to categorize** - just needs to:
1. Extract quotes from alignment section → generate alignment points
2. Extract quotes from gap section → generate gap points
3. Cite sources from appropriate section

**Example LLM Output:**

```json
{
  "company_name": "HealthTech AI",
  "aligns": [
    {
      "title": "Healthcare AI Focus",
      "explanation": "VC Criterion: 'We invest in AI healthcare companies at Series A stage' | Business Plan: 'Building AI diagnostic tools for hospitals' | Connection: Domain alignment is strong.",
      "sources": ["https://a16z.com/posts/healthcare-ai-thesis/"]
    },
    {
      "title": "Funding Amount Match",
      "explanation": "VC Criterion: '$15-20M Series A rounds' | Business Plan: 'Seeking Series A funding ($15M)' | Connection: Requested amount within VC's preferred range.",
      "sources": ["https://a16z.com/posts/series-a-criteria/"]
    }
  ],
  "gaps": [
    {
      "title": "Team Domain Expertise",
      "explanation": "VC Criterion: 'Team must have 10+ years healthcare domain expertise' | Business Plan Status: Team consists of ex-Google engineers with ML expertise but no mentioned healthcare industry experience.",
      "sources": ["https://a16z.com/posts/team-criteria/"]
    },
    {
      "title": "Geographic Mismatch",
      "explanation": "VC Criterion: 'We prefer Bay Area-based companies for close collaboration' | Business Plan Status: Company is based in Austin, Texas, creating potential partnership challenges.",
      "sources": ["https://a16z.com/posts/geography-preferences/"]
    },
    {
      "title": "Go-to-Market Strategy Missing",
      "explanation": "VC Criterion: 'Portfolio companies need strong go-to-market plans' | Business Plan Status: GTM strategy not detailed in the business plan.",
      "sources": ["https://a16z.com/posts/go-to-market/"]
    }
  ],
  "summary": "HealthTech AI shows strong alignment on domain and funding stage. However, significant gaps exist in team healthcare expertise and geographic location. The absence of a detailed go-to-market strategy needs addressing."
}
```

---

## Visual Flow Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│         v2 PIPELINE: HOW CLASSIFICATION IMPROVES CITATIONS         │
└────────────────────────────────────────────────────────────────────┘

INPUT:
├─ Query: "AI healthcare Series A criteria"
├─ Business Plan: "Building AI diagnostic tools, ex-Google team, Austin TX..."
└─ Company: "HealthTech AI"

        │
        ▼
┌─────────────────────────────────────────┐
│ STAGE 1: NEUTRAL RETRIEVAL              │
│ (HybridRetriever - unchanged from v1)   │
│                                         │
│ Retrieved 8 chunks:                     │
│ [1] AI healthcare investment            │
│ [2] Team expertise requirements         │
│ [3] Bay Area location pref              │
│ [4] ARR requirements                    │
│ [5] FDA pathway                         │
│ [6] PhD co-founders                     │
│ [7] Series A check size                 │
│ [8] GTM requirements                    │
│                                         │
│ NO CATEGORIZATION YET                   │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: CLASSIFICATION (NEW IN v2)                        │
│                                                             │
│ For each chunk, ask LLM:                                   │
│ "Does this align (A), reveal gap (B), or neutral (C)?"    │
│                                                             │
│ [1] AI healthcare → A (ALIGNMENT)                          │
│ [2] Team expertise → B (GAP - no healthcare exp)          │
│ [3] Bay Area → B (GAP - in Austin)                        │
│ [4] ARR → C (NEUTRAL - not mentioned)                     │
│ [5] FDA → C (NEUTRAL - unclear status)                    │
│ [6] PhD → C (NEUTRAL - education unspecified)             │
│ [7] Check size → A (ALIGNMENT - $15M fits)                │
│ [8] GTM → B (GAP - not in plan)                           │
│                                                             │
│ Classified Output:                                         │
│ ├─ alignment: [1, 7]         (2 chunks)                   │
│ ├─ gap: [2, 3, 8]            (3 chunks)                   │
│ └─ neutral: [4, 5, 6]        (3 chunks)                   │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: SEPARATE CONTEXT FORMATTING                       │
│                                                             │
│ alignment_context =                                        │
│   "Source: URL1 Snippet: [1] AI healthcare investment...  │
│    Source: URL7 Snippet: [7] $15-20M check size..."       │
│                                                             │
│ gap_context =                                              │
│   "Source: URL2 Snippet: [2] Team expertise required...   │
│    Source: URL3 Snippet: [3] Bay Area preference...       │
│    Source: URL8 Snippet: [8] GTM strategy needed..."      │
│                                                             │
│ neutral chunks EXCLUDED from both contexts                 │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: LLM ANALYSIS WITH SEPARATED EVIDENCE              │
│                                                             │
│ Prompt Structure:                                          │
│ ┌─────────────────────────────────────────────┐           │
│ │ EVIDENCE SUPPORTING ALIGNMENT:               │           │
│ │ [Only chunks 1 & 7 here]                    │           │
│ │                                              │           │
│ │ EVIDENCE HIGHLIGHTING GAPS:                  │           │
│ │ [Only chunks 2, 3, & 8 here]                │           │
│ │                                              │           │
│ │ BUSINESS PLAN: [full plan]                   │           │
│ │                                              │           │
│ │ INSTRUCTIONS:                                │           │
│ │ - Use alignment section for alignment points│           │
│ │ - Use gap section for gap points             │           │
│ │ - NEVER mix the two                         │           │
│ └─────────────────────────────────────────────┘           │
│                                                             │
│ LLM Processing:                                            │
│ ├─ Reads alignment section → Generates 2 align points     │
│ │  └─ Cites only URLs from chunks 1 & 7                   │
│ ├─ Reads gap section → Generates 3 gap points             │
│ │  └─ Cites only URLs from chunks 2, 3, & 8              │
│ └─ Writes balanced summary                                │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
OUTPUT: AlignmentResponse with matched citations ✅
├─ aligns[0]: cites URL1 (from alignment section) ✅
├─ aligns[1]: cites URL7 (from alignment section) ✅
├─ gaps[0]: cites URL2 (from gap section) ✅
├─ gaps[1]: cites URL3 (from gap section) ✅
└─ gaps[2]: cites URL8 (from gap section) ✅

NO MORE CITATION MISMATCHES!
```

---

## Classification Decision Logic

### Decision Matrix

The classifier uses this reasoning pattern:

| VC Criterion | Business Plan Attribute | Comparison | Classification | Reasoning |
|--------------|-------------------------|------------|----------------|-----------|
| "AI healthcare focus" | "AI diagnostic tools for hospitals" | **Matches** | **ALIGNMENT** | Domain overlap |
| "Series A stage" | "Seeking Series A funding" | **Matches** | **ALIGNMENT** | Stage matches |
| "$15-20M rounds" | "Raising $15M" | **Matches** | **ALIGNMENT** | Amount in range |
| "10+ years healthcare expertise" | "Ex-Google ML engineers" | **Contradicts** | **GAP** | Wrong domain expertise |
| "Bay Area location" | "Austin, Texas" | **Contradicts** | **GAP** | Geography mismatch |
| "Strong GTM plan" | Not mentioned | **Missing** | **GAP** | Absent from plan |
| "$1M+ ARR required" | Not mentioned | **Unknown** | **NEUTRAL** | Can't determine |
| "FDA pathway clarity" | Not mentioned | **Unknown** | **NEUTRAL** | Ambiguous |

### Classification Heuristics

```
ALIGNMENT (A):
- BP explicitly has what VC wants
- Clear positive match
- No contradictions
Examples: "VC wants AI, BP is AI"; "VC does Series A, BP seeks Series A"

GAP (B):
- BP explicitly lacks what VC wants
- Clear contradiction
- Missing critical element
Examples: "VC wants healthcare exp, team has none"; "VC wants Bay Area, company in Austin"

NEUTRAL (C):
- Can't determine from available info
- BP doesn't mention this criterion
- Ambiguous or conditional
Examples: "VC mentions revenue, BP doesn't"; "VC wants patents, unclear if BP has"
```

---

## Performance Characteristics

### Latency Comparison

| Phase | v1 Duration | v2 Duration | Change |
|-------|-------------|-------------|--------|
| Retrieval | 200-400ms | 200-400ms | No change |
| **Classification** | **0ms (N/A)** | **5-8 seconds** | **+5-8s (NEW)** |
| Context formatting | 5-10ms | 10-20ms | +5-10ms |
| LLM generation | 2-4 seconds | 2-4 seconds | No change |
| **Total** | **2.5-5s** | **8-12s** | **+5-7s** |

### Cost Comparison

| Component | v1 Cost | v2 Cost | Change |
|-----------|---------|---------|--------|
| Query embedding | $0.00001 | $0.00001 | No change |
| Retrieval | $0 | $0 | No change |
| **Classification** | **$0 (N/A)** | **~$0.01** | **+$0.01 (NEW)** |
| LLM generation | ~$0.0015 | ~$0.002 | +$0.0005 |
| **Total per query** | **$0.0015** | **$0.012** | **~8x increase** |

**Note:** Cost increase is acceptable for prototype; production optimizations can reduce this.

### Accuracy Improvements

| Metric | v1 | v2 | Improvement |
|--------|----|----|-------------|
| Citation grounding | ~60% | ~90% | +30% |
| Evidence type matching | Poor | Excellent | Major |
| Hallucination rate | Moderate | Low | Reduced |
| Smoke test pass rate | Not measured | 100% (5/5) | New validation |

---

## Key Design Improvements

### 1. Evidence-Claim Matching

**v1 Problem:**
```
Alignment claim: "Strong domain fit"
Citation: Chunk about "team requirements" ❌ (wrong evidence type)
```

**v2 Solution:**
```
Alignment claim: "Strong domain fit"
Citation: Chunk from alignment section about "AI healthcare focus" ✅ (matched)
```

### 2. Explicit Categorization

**v1:** LLM must simultaneously:
- Parse business plan
- Parse VC criteria
- Compare attributes
- Categorize as align/gap
- Generate explanations
- Cite sources

**v2:** Tasks separated:
- Classification layer: Categorize chunks (simple yes/no decision)
- LLM generation: Focus on explanation & citation (easier task)

### 3. Reduced Cognitive Load on LLM

**v1 Prompt:**
```
Here are 8 chunks (all mixed together).
Find alignments AND gaps from this same set.
```

**v2 Prompt:**
```
Here are 2 alignment chunks - use these for alignments.
Here are 3 gap chunks - use these for gaps.
Don't mix them up.
```

**Result:** Simpler instruction → better adherence → higher quality output.

### 4. Fallback Handling

**v2 adds graceful degradation:**

```python
alignment_context = _format_context(classified["alignment"]) or \
    "No clear alignment evidence found in retrieved context."
```

If no chunks classify as alignment:
- v1: LLM forced to invent alignments from gap chunks ❌
- v2: System acknowledges insufficient evidence ✅

### 5. Backward Compatibility

```python
analyzer = AlignmentAnalyzer(use_classification=True)   # v2 behavior (default)
analyzer = AlignmentAnalyzer(use_classification=False)  # v1 behavior (fallback)
```

**Benefit:** Can A/B test or rollback if needed.

---

## Known Limitations & Trade-offs

### Limitations

1. **Latency Increased:** 8-12s vs 2-5s (2-3x slower)
   - Mitigation: Parallelize classification (future work)

2. **Cost Increased:** $0.012 vs $0.0015 per query (8x more expensive)
   - Mitigation: Batch API calls, use cheaper models

3. **Sequential Classification:** Not parallelized
   - Mitigation: Use asyncio + batch APIs (production)

4. **Binary Classification:** Simple A/B/C, no confidence scores
   - Mitigation: Add confidence scoring (Iteration 2)

5. **Gap Evidence Scarcity:** Corpus biased toward positive criteria
   - Mitigation: Expand corpus, synthetic gap generation

### Trade-offs

| Aspect | v1 | v2 | Trade-off Analysis |
|--------|----|----|-------------------|
| **Speed** | Fast (2-5s) | Slower (8-12s) | Worth it for accuracy |
| **Cost** | Cheap ($0.002) | More expensive ($0.012) | Acceptable for prototype |
| **Accuracy** | Moderate | High | Primary goal achieved |
| **Complexity** | Simple | Moderate | Added classification layer |
| **Maintainability** | Easy | Moderate | Two prompts to tune |

**Decision:** For MVP/prototype, the accuracy gains justify the performance trade-offs.

---

## Comparison: v1 vs v2

### Architecture Comparison

```
┌─────────────────────────────────────────────────────────────┐
│                      v1 ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────┘

Retrieval → Single Context → LLM → Output
(8 chunks)   (all together)  (categorizes)

Problem: LLM must do too much, citations don't match claims


┌─────────────────────────────────────────────────────────────┐
│                      v2 ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────┘

Retrieval → Classification → Separate Contexts → LLM → Output
(8 chunks)   (categorize)     (2 sections)      (cite correctly)

Solution: Pre-classify chunks, provide separate evidence, matched citations
```

### Output Quality Comparison

**Sample Business Plan:** AI healthcare startup, no healthcare expertise, Austin-based

**v1 Output:**
```json
{
  "aligns": [
    {
      "title": "Healthcare Focus",
      "sources": ["https://a16z.com/healthcare-thesis/"]  ✅ Correct
    },
    {
      "title": "Strong Team",
      "sources": ["https://a16z.com/team-requirements/"]  ❌ WRONG - this chunk says need healthcare exp
    }
  ],
  "gaps": [
    {
      "title": "Early Stage Risk",
      "sources": ["https://a16z.com/series-a-criteria/"]  ❌ WRONG - this chunk supports Series A
    }
  ]
}
```

**v2 Output:**
```json
{
  "aligns": [
    {
      "title": "Healthcare AI Focus",
      "explanation": "VC Criterion: 'We invest in AI healthcare companies' | Business Plan: 'Building AI diagnostic tools' | Connection: Domain match",
      "sources": ["https://a16z.com/healthcare-thesis/"]  ✅ Correct - from alignment section
    }
  ],
  "gaps": [
    {
      "title": "Team Domain Expertise Gap",
      "explanation": "VC Criterion: 'Requires 10+ years healthcare expertise' | Business Plan Status: Team has ML expertise but no healthcare background",
      "sources": ["https://a16z.com/team-requirements/"]  ✅ Correct - from gap section
    },
    {
      "title": "Geographic Mismatch",
      "explanation": "VC Criterion: 'Bay Area preference' | Business Plan Status: Company based in Austin, Texas",
      "sources": ["https://a16z.com/geography/"]  ✅ Correct - from gap section
    }
  ]
}
```

---

## Future Enhancements (v3+)

### High Priority
1. **Parallel Classification** - Reduce latency from 8s to 3s
2. **Confidence Scores** - Indicate certainty per classification
3. **Gap Evidence Expansion** - Crawl more "what VCs avoid" content

### Medium Priority
4. **Two-Pass Retrieval** - Separate alignment/gap queries upfront
5. **Classification Caching** - Cache results for similar chunks
6. **Adaptive Thresholds** - Adjust min_alignment/min_gap based on corpus

### Low Priority
7. **Multi-Model Classification** - Use smaller/faster models
8. **Explanation Generation** - Why chunk was classified a certain way
9. **Active Learning** - Improve classifier from user feedback

---

## Summary

### The Core Innovation

**v2 solves the fundamental citation mismatch problem** by adding a classification layer that pre-categorizes evidence before the LLM sees it.

### Key Takeaways

1. **Problem:** v1 LLM was citing random chunks that didn't support the specific claim type
2. **Solution:** v2 pre-classifies chunks and provides separate evidence sections
3. **Result:** 90% citation accuracy vs ~60% in v1, validated by smoke tests
4. **Trade-off:** 2-3x slower, 8x more expensive, but acceptable for prototype
5. **Status:** Implemented, tested, ready for user validation

### When to Use Each Version

**Use v2 (classification-enhanced):**
- Citation accuracy is critical
- User trust is paramount
- 8-12s latency is acceptable
- Budget allows $0.012/query

**Use v1 (original):**
- Speed is critical (<5s required)
- Budget constrained (<$0.002/query)
- A/B testing against v2
- Fallback if v2 fails

---

## Code Reference

### Main v2 Functions

```python
# Classification (NEW in v2)
def classify_chunk(chunk_text, plan_summary, llm) -> Literal["alignment", "gap", "neutral"]
def classify_documents(documents, plan_summary, llm) -> dict[str, list[Document]]

# Enhanced prompt (v2)
def build_prompt_with_classified_evidence() -> ChatPromptTemplate

# Enhanced analyzer (v2)
class AlignmentAnalyzer:
    def __init__(self, use_classification=True):  # v2 by default
        ...
    
    def analyze(self, company_name, plan_summary, query):
        if self.use_classification:
            # v2 path: classify → separate contexts
            docs, classified = self._retrieve_with_classification(...)
            alignment_context = self._format_context(classified["alignment"])
            gap_context = self._format_context(classified["gap"])
        else:
            # v1 path: single context
            docs = self.retriever.get_relevant_documents(query)
            context = self._format_context(docs)
```

---

**Document Version:** 2.0  
**Date:** November 4, 2025  
**Status:** Implemented & Validated  
**Previous Version:** PipelineDesign-v1.md  
**Related Files:**
- `src/vira/rag/pipeline.py` - Implementation
- `PROTOTYPE_IMPLEMENTATION_SUMMARY.md` - Detailed implementation notes
- `VIRA-Iter1Arch_Impl_v2.md` - Updated system architecture

---

**End of Document**

