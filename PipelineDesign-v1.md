# VIRA Pipeline Design: Alignment vs Misalignment Detection

**Document:** Pipeline Design Specification  
**Focus:** How `pipeline.py` categorizes business plan attributes as alignments or gaps  
**Date:** November 4, 2025

---

## Executive Summary

**Key Insight:** The code doesn't directly categorize chunks as alignment vs misalignment. Instead, it uses a **two-stage process** where retrieval is neutral and the LLM performs the categorization.

```
Stage 1: Neutral Retrieval → Returns relevant VC criteria (no categorization)
Stage 2: LLM Comparison → Compares plan to criteria, categorizes as align/gap
```

---

## Table of Contents

1. [How Alignment Checking Works](#how-alignment-checking-works)
2. [Stage 1: Neutral Retrieval](#stage-1-neutral-retrieval)
3. [Stage 2: Context Formatting](#stage-2-context-formatting)
4. [Stage 3: LLM Categorization](#stage-3-llm-categorization)
5. [LLM Decision Process](#llm-decision-process)
6. [Visual Flow Diagram](#visual-flow-diagram)
7. [Key Design Points](#key-design-points)
8. [Potential Issues](#potential-issues)
9. [Summary](#summary)

---

## How Alignment Checking Works

### Overview

The alignment checking process in `src/vira/rag/pipeline.py` follows a three-stage pipeline:

```
Input (Query + Business Plan)
    ↓
Stage 1: Neutral Retrieval (HybridRetriever)
    ↓
Stage 2: Context Formatting (with source URLs)
    ↓
Stage 3: LLM Categorization (GPT-4o-mini)
    ↓
Output (Structured: aligns + gaps + summary)
```

---

## Stage 1: Neutral Retrieval

**Code Location:** Lines 80-84 in `pipeline.py`

```python
def analyze(self, company_name: str, plan_summary: str, query: str) -> tuple[AlignmentResponse, List[Document]]:
    """Retrieve contextual documents, run the chain, and return structured output."""
    
    docs = self.retriever.get_relevant_documents(query)  # ← Neutral retrieval
    context = self._format_context(docs)
```

### What Happens

**Input Query:**
```
"AI healthcare Series A investment criteria"
```

**Retrieval Process:**
```
HybridRetriever (semantic + keyword search)
    ↓
Returns 8 most RELEVANT chunks
    ↓
NO categorization at this stage!
```

### Example Retrieved Chunks

```
Chunk 1: "We invest in AI healthcare companies at Series A stage..."
Chunk 2: "Team must have 10+ years healthcare domain expertise..."
Chunk 3: "We prefer Bay Area-based companies for close collaboration..."
Chunk 4: "Series A companies should have $1M+ ARR..."
Chunk 5: "Healthcare AI requires FDA regulatory pathway..."
Chunk 6: "We look for technical co-founders with PhD backgrounds..."
Chunk 7: "Our sweet spot is $15-20M Series A rounds..."
Chunk 8: "Portfolio companies need strong go-to-market plans..."
```

### Critical Point

**All chunks are just "VC criteria"** - there's no classification of which are alignments or gaps. The retrieval is purely based on **relevance to the query**, not on whether they'll match or contradict the business plan.

---

## Stage 2: Context Formatting

**Code Location:** Lines 96-101 in `pipeline.py`

```python
@staticmethod
def _format_context(documents: List[Document]) -> str:
    formatted_chunks = []
    for doc in documents:
        source = doc.metadata.get("url", "unknown source")
        formatted_chunks.append(f"Source: {source}\nSnippet: {doc.page_content.strip()[:800]}")
    return "\n\n".join(formatted_chunks)
```

### Output Format

```
Source: https://a16z.com/posts/healthcare-ai-thesis/
Snippet: We invest in AI healthcare companies at Series A stage...

Source: https://a16z.com/posts/team-criteria/
Snippet: Team must have 10+ years healthcare domain expertise...

Source: https://a16z.com/posts/geography-preferences/
Snippet: We prefer Bay Area-based companies for close collaboration...

[... 5 more chunks ...]
```

### Key Point

Still **no categorization** - just formatting chunks with source attribution for citation purposes. All chunks are presented neutrally to the LLM.

---

## Stage 3: LLM Categorization

**Code Location:** Lines 85-92 in `pipeline.py`

```python
response_dict = self.chain.invoke(
    {
        "context": context,              # ← All 8 VC criteria chunks (neutral)
        "plan_summary": plan_summary,    # ← Business plan details
        "company_name": company_name,
    }
)
response = AlignmentResponse(**response_dict)
```

### The Magic Happens Here

This is where the **LLM compares** the business plan against the VC criteria and performs categorization.

### What the LLM Receives

**Prompt Template (Lines 38-57):**

```
You are an analyst at a venture capital firm. Using the retrieved context, create a structured
alignment analysis between the VC focus areas and the founder's business plan.

Retrieved VC Context:
Source: https://a16z.com/posts/healthcare-ai-thesis/
Snippet: We invest in AI healthcare companies at Series A stage...

Source: https://a16z.com/posts/team-criteria/
Snippet: Team must have 10+ years healthcare domain expertise...

[... 6 more chunks ...]

Business Plan (company: HealthTech AI):
We are building AI-powered diagnostic tools for hospitals. Our team consists of 
ex-Google engineers with ML expertise. We are based in Austin, Texas. Currently 
pre-seed stage with 5 design partners. No healthcare industry experience on the team.
Seeking Series A funding of $15M...

Instructions:
- Provide 3-5 ways the plan aligns with the VC criteria ("aligns").
- Provide 3-5 gaps or misalignments ("gaps").
- Each entry must cite at least one source URL from the retrieved context.
- Write a neutral summary (80-120 words) balancing strengths and gaps.
- Do NOT make investment recommendations or assign scores.

Respond in JSON with keys: company_name, aligns, gaps, summary.
Each item in aligns/gaps must contain title, explanation, sources.
```

---

## LLM Decision Process

The LLM performs **attribute-by-attribute comparison** between the business plan and VC criteria:

### Decision Matrix

| VC Criterion (from chunk) | Business Plan Attribute | Match? | Category | Reasoning |
|---------------------------|-------------------------|--------|----------|-----------|
| "AI healthcare companies" | "AI-powered diagnostic tools for hospitals" | ✅ | **ALIGN** | Domain matches perfectly |
| "Series A stage" | "Seeking Series A funding" | ✅ | **ALIGN** | Stage matches |
| "10+ years healthcare expertise" | "Ex-Google engineers with ML expertise" | ❌ | **GAP** | No healthcare background |
| "Bay Area-based" | "Austin, Texas" | ❌ | **GAP** | Geography mismatch |
| "$15-20M Series A rounds" | "Seeking Series A funding of $15M" | ✅ | **ALIGN** | Amount in range |
| "Strong go-to-market plans" | Not mentioned in plan | ❌ | **GAP** | Missing information |

### LLM Output (Structured JSON)

```json
{
  "company_name": "HealthTech AI",
  "aligns": [
    {
      "title": "Healthcare AI Focus",
      "explanation": "The company's AI-powered diagnostic tools directly align with a16z's stated investment priority in AI healthcare companies. The VC explicitly mentions investing in this space at Series A.",
      "sources": ["https://a16z.com/posts/healthcare-ai-thesis/"]
    },
    {
      "title": "Stage Match",
      "explanation": "Company is seeking Series A funding, which matches the VC's Series A focus mentioned in their investment criteria.",
      "sources": ["https://a16z.com/posts/healthcare-ai-thesis/"]
    },
    {
      "title": "Funding Amount Alignment",
      "explanation": "The $15M Series A round sought aligns with a16z's typical check size of $15-20M for Series A investments.",
      "sources": ["https://a16z.com/posts/series-a-criteria/"]
    }
  ],
  "gaps": [
    {
      "title": "Team Domain Expertise",
      "explanation": "a16z requires teams with 10+ years healthcare domain expertise. The founding team consists of ex-Google engineers with ML backgrounds but no mentioned healthcare industry experience, which is a significant gap.",
      "sources": ["https://a16z.com/posts/team-criteria/"]
    },
    {
      "title": "Geographic Preference",
      "explanation": "The VC prefers Bay Area-based companies for close collaboration and portfolio support. HealthTech AI is based in Austin, Texas, which may present challenges for hands-on partnership.",
      "sources": ["https://a16z.com/posts/geography-preferences/"]
    },
    {
      "title": "Go-to-Market Strategy",
      "explanation": "a16z looks for strong go-to-market plans as a key criterion. The business plan does not detail the GTM strategy, leaving this critical area unaddressed.",
      "sources": ["https://a16z.com/posts/series-a-criteria/"]
    }
  ],
  "summary": "HealthTech AI shows strong alignment with a16z's healthcare AI investment thesis and Series A stage focus. The funding amount and product domain are well-matched. However, significant gaps exist in team healthcare expertise and geographic location preferences. The absence of a detailed go-to-market strategy also needs addressing before investor conversations."
}
```

---

## Visual Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│            HOW ALIGNMENT CATEGORIZATION WORKS                  │
└────────────────────────────────────────────────────────────────┘

INPUT:
├─ Query: "AI healthcare Series A criteria"
├─ Business Plan: "We build AI diagnostic tools..."
└─ Company: "HealthTech AI"
        │
        ▼
┌─────────────────────────────────────────┐
│ STEP 1: NEUTRAL RETRIEVAL               │
│ (HybridRetriever.get_relevant_documents)│
│                                         │
│ Returns 8 chunks based on relevance:   │
│ ✓ Chunk A: "AI healthcare investment"  │
│ ✓ Chunk B: "Team expertise required"   │
│ ✓ Chunk C: "Bay Area preference"       │
│ ✓ Chunk D: "Series A criteria"         │
│ ✓ Chunk E: "Go-to-market importance"   │
│ ... (3 more)                            │
│                                         │
│ NO CATEGORIZATION YET!                  │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│ STEP 2: FORMAT CONTEXT                  │
│ (_format_context)                       │
│                                         │
│ Format: "Source: [URL]\nSnippet: [...]"│
│                                         │
│ Still neutral - just formatting!        │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: LLM COMPARISON & CATEGORIZATION                     │
│ (GPT-4o-mini via build_chain)                               │
│                                                             │
│ LLM Receives:                                               │
│ ├─ All 8 VC criteria chunks (neutral)                      │
│ ├─ Complete business plan                                  │
│ └─ Instructions: Find alignments AND gaps                  │
│                                                             │
│ LLM Internal Reasoning:                                     │
│                                                             │
│ ┌─────────────────────────────────────────────┐           │
│ │ For each VC criterion chunk:                │           │
│ │                                             │           │
│ │ Chunk A: "AI healthcare investment"         │           │
│ │ ├─ Business plan: "AI diagnostic tools"     │           │
│ │ ├─ Match? YES                               │           │
│ │ └─ Category: ALIGN ✅                       │           │
│ │                                             │           │
│ │ Chunk B: "Team expertise required"          │           │
│ │ ├─ Business plan: "Ex-Google engineers"     │           │
│ │ ├─ Match? NO (no healthcare background)     │           │
│ │ └─ Category: GAP ❌                         │           │
│ │                                             │           │
│ │ Chunk C: "Bay Area preference"              │           │
│ │ ├─ Business plan: "Austin, Texas"           │           │
│ │ ├─ Match? NO                                │           │
│ │ └─ Category: GAP ❌                         │           │
│ │                                             │           │
│ │ Chunk D: "Series A criteria"                │           │
│ │ ├─ Business plan: "Seeking Series A"        │           │
│ │ ├─ Match? YES                               │           │
│ │ └─ Category: ALIGN ✅                       │           │
│ │                                             │           │
│ │ ... continue for remaining chunks ...       │           │
│ └─────────────────────────────────────────────┘           │
│                                                             │
│ LLM Aggregates & Structures:                                │
│ ├─ Group alignments → "aligns" list                        │
│ ├─ Group gaps → "gaps" list                                │
│ ├─ Write neutral summary                                   │
│ └─ Cite sources for each claim                             │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
OUTPUT (AlignmentResponse):
{
  "aligns": [
    {"title": "Healthcare AI Focus", "explanation": "...", "sources": [...]},
    {"title": "Stage Match", ...},
    {"title": "Funding Amount", ...}
  ],
  "gaps": [
    {"title": "Team Domain Expertise", "explanation": "...", "sources": [...]},
    {"title": "Geographic Preference", ...},
    {"title": "Go-to-Market Strategy", ...}
  ],
  "summary": "Strong alignment on domain and stage, gaps in team and geography..."
}
```

---

## Key Design Points

### 1. No Rule-Based Logic

The code doesn't have if-statements like:

```python
# ❌ NOT how it works!
if business_plan.domain == vc_criteria.domain:
    category = "align"
else:
    category = "gap"
```

Instead, all comparison logic is delegated to the LLM's natural language understanding.

### 2. Retrieval is Agnostic

The `HybridRetriever` just finds the most **relevant** chunks. It doesn't know or care if they'll become alignments or gaps:

```python
# Just returns relevant docs - no categorization
docs = self.retriever.get_relevant_documents(query)
```

**Why this matters:**
- Simpler retrieval logic
- Same chunks can be used for multiple purposes
- No need to predict align/gap during retrieval
- Retrieval focuses purely on relevance

### 3. LLM Does the Heavy Lifting

All comparison logic happens inside the LLM (GPT-4o-mini):

- ✅ Parses business plan attributes
- ✅ Parses VC criteria from chunks
- ✅ Compares attribute-by-attribute
- ✅ Categorizes as align/gap
- ✅ Generates explanations
- ✅ Cites sources

**Advantages:**
- No hard-coded business logic
- Handles nuanced comparisons
- Adapts to different VC criteria
- Natural language reasoning

**Disadvantages:**
- LLM may hallucinate
- Non-deterministic (slight variations between runs)
- No explainability of decision process
- Depends on LLM quality

### 4. Prompt Engineering is Critical

The prompt (lines 48-53) explicitly instructs the LLM:

```python
- Provide 3-5 ways the plan aligns with the VC criteria ("aligns").
- Provide 3-5 gaps or misalignments ("gaps").
- Each entry must cite at least one source URL from the retrieved context.
- Write a neutral summary (80-120 words) balancing strengths and gaps.
- Do NOT make investment recommendations or assign scores.
```

**Without this clear instruction**, the LLM wouldn't know to:
- Separate alignments from gaps
- Provide balanced analysis
- Cite sources for each claim
- Stay neutral (no recommendations)

### 5. Structured Output Enforcement

The Pydantic schema (lines 18-32) ensures the response has both:

```python
class AlignmentResponse(BaseModel):
    company_name: str
    aligns: List[AlignmentSection]  # Must have this
    gaps: List[AlignmentSection]     # Must have this
    summary: str
```

**Benefits:**
- Type safety
- Validation (ensures required fields)
- Consistent output format
- Easy to parse and display in UI

---

## Potential Issues

### ⚠️ Problem 1: LLM Hallucination

**Issue:** The LLM might categorize incorrectly if:
- Business plan is ambiguous
- VC criteria are vague
- Information is missing

**Example:**
```
VC Criterion: "We prefer strong teams"
Business Plan: "Our team has 5 years of experience"

Ambiguity: Is 5 years "strong"? LLM must make subjective judgment.
```

**Mitigation:**
- Use higher quality LLMs (GPT-4 instead of GPT-4o-mini)
- Add few-shot examples to prompt
- Implement confidence scoring (Iteration 2)

### ⚠️ Problem 2: Artificial Balance

**Issue:** Prompt asks for "3-5 aligns" and "3-5 gaps". What if there are genuinely 10 alignments and only 1 gap? The LLM might artificially create gaps to satisfy the requirement.

**Example:**
```
Reality: Company is a perfect fit (9 alignments, 1 gap)
Output: LLM artificially finds 3 gaps to meet "3-5" requirement
Result: Misleading analysis suggesting more concerns than exist
```

**Mitigation:**
- Change prompt to "at least 2" instead of "3-5"
- Allow asymmetric outputs
- Add confidence levels per claim

### ⚠️ Problem 3: No Confidence Scores

**Issue:** The system doesn't indicate certainty. A strong alignment gets same treatment as a weak one.

**Example:**
```
Alignment 1: "Company is in AI healthcare" (100% certain)
Alignment 2: "Company might have network effects" (30% certain)

Both presented equally without confidence indicators.
```

**Mitigation:**
- Add confidence field to `AlignmentSection`
- Prompt LLM to self-assess certainty
- Use evidence strength indicators (✓✓✓ strong → ? weak)

### ⚠️ Problem 4: Chunks Don't Self-Label

**Issue:** If retrieval misses key criteria, gaps won't be identified.

**Example:**
```
VC requires: "Patent portfolio" (not in retrieved chunks)
Business plan: No patents mentioned
Result: Gap NOT detected because criterion wasn't retrieved
```

**Mitigation:**
- Retrieve more chunks (increase k)
- Use query expansion (multiple search queries)
- Implement "exhaustive criteria checklist" approach
- Add reflection agent to identify missing criteria (Iteration 2)

### ⚠️ Problem 5: Context Length Limitations

**Issue:** Only 8 chunks retrieved (800 chars each = ~6400 chars). May miss important criteria.

**Example:**
```
VC has 20 distinct criteria across different pages
Only 8 chunks retrieved
12 criteria never evaluated
```

**Mitigation:**
- Increase retrieval k (10-15 chunks)
- Implement hierarchical retrieval (broad → specific)
- Use summarization for long documents
- Multiple retrieval rounds for different aspects

---

## Summary

### The Core Answer

**The code doesn't decide which chunks indicate alignment vs misalignment.** Instead:

1. **Retrieval stage** (line 83): Returns relevant VC criteria chunks (neutral, no categorization)
2. **Formatting stage** (lines 96-101): Adds source URLs (still neutral)
3. **LLM stage** (lines 85-92): Compares business plan to ALL retrieved chunks and categorizes each as align/gap based on attribute matching
4. **Structured output** (lines 26-32): Forces separation into two lists via Pydantic schema

### Key Insight

**The categorization is entirely LLM-driven reasoning**, guided by:
- Prompt instructions (lines 48-53) to identify both alignments and gaps
- Retrieved context (all VC criteria chunks)
- Business plan details
- Pydantic schema enforcement

### Design Philosophy

This approach prioritizes:
- ✅ **Flexibility** - Works with any VC firm's criteria without code changes
- ✅ **Explainability** - Each align/gap has textual explanation with sources
- ✅ **Simplicity** - No complex rule engine required
- ✅ **Natural Language** - Handles nuanced comparisons that rules can't

Trade-offs:
- ⚠️ **Non-deterministic** - LLM may give slightly different results
- ⚠️ **Less precise** - No numeric confidence scores
- ⚠️ **LLM-dependent** - Quality depends on model capability

---

## Code Reference

### Main Functions

```python
# Line 80-93: Main analysis orchestration
def analyze(self, company_name: str, plan_summary: str, query: str):
    docs = self.retriever.get_relevant_documents(query)  # Neutral retrieval
    context = self._format_context(docs)                 # Add sources
    response_dict = self.chain.invoke({                  # LLM categorization
        "context": context,
        "plan_summary": plan_summary,
        "company_name": company_name,
    })
    return AlignmentResponse(**response_dict), docs

# Lines 96-101: Context formatting
def _format_context(documents: List[Document]) -> str:
    formatted_chunks = []
    for doc in documents:
        source = doc.metadata.get("url", "unknown source")
        formatted_chunks.append(f"Source: {source}\nSnippet: {doc.page_content.strip()[:800]}")
    return "\n\n".join(formatted_chunks)

# Lines 35-58: Prompt template (critical for categorization)
def build_prompt() -> ChatPromptTemplate:
    template = """
    You are an analyst at a venture capital firm...
    
    Instructions:
    - Provide 3-5 ways the plan aligns with the VC criteria ("aligns").
    - Provide 3-5 gaps or misalignments ("gaps").
    - Each entry must cite at least one source URL from the retrieved context.
    """
    return ChatPromptTemplate.from_template(template)
```

---

**Document Version:** 1.0  
**Last Updated:** November 4, 2025  
**Related Files:**
- `src/vira/rag/pipeline.py` - Main implementation
- `src/vira/retrieval/hybrid.py` - Retrieval logic
- `VIRA-Iter1Arch-v1.md` - Complete system architecture

---

**End of Document**

