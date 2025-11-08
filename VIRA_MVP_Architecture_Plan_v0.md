# VIRA MVP: Architecture & Design Documentation
## 3 Iterations - Detailed System Design

---

# ITERATION 1: Explanation-Only System

## 1. Architecture & Design

### New Features
- **Hybrid retrieval system** for VC criteria extraction from firm content
- **Structured explanation generator** producing matches and gaps analysis
- **No-scoring approach** - system provides evidence, users make decisions
- **Trust-first design** emphasizing transparency over automation
- **Fast criteria surfacing** from business plan analysis

### Usage Paradigm
**Retrieval-Augmented Generation (RAG)**

This iteration uses basic RAG with hybrid retrieval (semantic + keyword) to find relevant VC criteria chunks, then generates structured explanations without classification or scoring.

### Architecture Diagram Description

```
┌─────────────────┐
│  Founder Input  │
│  (Web UI)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI        │
│  Backend        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   RAG Pipeline (LangChain)          │
│  ┌──────────────────────────────┐   │
│  │ 1. Parse business plan       │   │
│  │ 2. Generate search queries   │   │
│  │ 3. Retrieve from vector DB   │   │
│  │ 4. Rank & rerank chunks      │   │
│  │ 5. Construct prompt          │   │
│  │ 6. LLM generates analysis    │   │
│  └──────────────────────────────┘   │
└────────┬────────────┬────────────────┘
         │            │
         ▼            ▼
┌─────────────┐  ┌──────────────┐
│ Weaviate/   │  │ Ollama/      │
│ Chroma      │  │ GPT-4o-mini  │
│ Vector DB   │  │ (LLM)        │
└─────────────┘  └──────────────┘
         ▲
         │
    ┌────┴─────┐
    │ a16z     │
    │ Content  │
    │ Store    │
    └──────────┘
```

**System Overview:**
```
Founder → Web UI → FastAPI Backend → RAG Pipeline → Response
                         ↓
              [a16z.com Content Store]
                         ↓
              [Vector Database + LLM]
```

**Key Components:**
- Web scraping layer (Scrapy + BeautifulSoup4)
- Document parser (business plan ingestion)
- Vector database (VC criteria embeddings)
- Hybrid retrieval engine (semantic + BM25)
- LLM explanation generator
- Structured output formatter

### Technology Stack (Free/Open Source Options)

#### 1. Content Ingestion & Storage

**Web Scraping: Scrapy + BeautifulSoup4**
- Industry-standard Python scraping framework, completely free
- Systematic crawling of a16z.com (blog posts, portfolio, team bios, investment theses)
- Extract and parse HTML content

```python
# Simple a16z crawler
import scrapy

class A16zSpider(scrapy.Spider):
    name = 'a16z'
    allowed_domains = ['a16z.com']
    start_urls = ['https://a16z.com/posts/', 
                  'https://a16z.com/portfolio/',
                  'https://a16z.com/team/']
```

**Document Processing: LangChain (Open Source)**
- Text chunking with RecursiveCharacterTextSplitter
- Metadata extraction (author, date, category, tags)
- Store chunks with source URLs for citations

#### 2. Vector Database Options


**Option B: Chroma DB**
- Pure Python, no Docker required
- Runs in-memory or persists to disk
- Perfect for prototypes <100K documents

```python
import chromadb
from chromadb.config import Settings

# Initialize Chroma
client = chromadb.Client(Settings(
    persist_directory="./chroma_db"
))

collection = client.create_collection(
    name="a16z_content",
    metadata={"hnsw:space": "cosine"}
)
```

#### 3. Embeddings

**Option C: OpenAI**
- text-embedding-3-small: $0.13 per 1M tokens
- text-embedding-3-large: $0.13 per 1M tokens (3,072 dimensions)
- Higher quality for production

#### 4. LLM for RAG
```

**Option B: OpenAI GPT-4o-mini - RECOMMENDED FOR PRODUCTION**
- $0.15/$0.60 per 1M tokens (very cheap for testing)
- $5 credit gets ~8,000 queries with 500-token responses
- Better quality for Iteration 1 validation


#### 5. RAG Orchestration: LangChain (Open Source)

Industry standard with 111K+ GitHub stars, free forever

```python
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain_community.llms import Ollama

# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=Ollama(model="llama3.2:3b"),
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

# Query
result = qa_chain({"query": "What sectors does a16z invest in?"})
```

**Key RAG Components:**
1. **Retriever:** Fetch top-5 relevant chunks from Chroma
2. **Prompt Template:**
```
Context: {retrieved_chunks}
VC Focus Areas: [from a16z site]

Founder's Business Plan: {plan_text}

Task: Analyze if this plan aligns with a16z's investment thesis.
Consider: sector focus, stage, business model, team background.
```
3. **Response Generator:** LLM synthesizes alignment score + reasoning

#### 6. Web Application

**Backend: FastAPI (Python)**
- Modern, async Python web framework
- Auto-generated API docs
- Easy integration with LangChain

```python
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

app = FastAPI()

class BusinessPlan(BaseModel):
    text: str
    company_name: str

@app.post("/analyze")
async def analyze_plan(plan: BusinessPlan):
    # RAG query logic here
    alignment_result = qa_chain({"query": f"Analyze: {plan.text}"})
    return {
        "alignment_score": extract_score(alignment_result),
        "reasoning": alignment_result["result"],
        "sources": alignment_result["source_documents"]
    }
```

**Frontend Options:**

**Option A: Streamlit (Fastest for prototype) - RECOMMENDED**
```python
import streamlit as st

st.title("a16z Alignment Checker")

uploaded_file = st.file_uploader("Upload Business Plan (PDF/TXT)")
plan_text = st.text_area("Or paste your plan here:")

if st.button("Analyze Alignment"):
    result = analyze_plan(plan_text)
    st.metric("Alignment Score", f"{result['score']}/10")
    st.write(result['reasoning'])
```

**Option B: React UI**
- React frontend → FastAPI backend
- Deploy frontend on Vercel (free), backend on Render (free tier)

### Sample Inputs

**Primary Input:**
- **Business Plan Document** (PDF/DOCX, 10-50 pages)
  - Company overview
  - Market analysis
  - Product/service description
  - Team backgrounds
  - Financial projections
  - Go-to-market strategy

**Context Input:**
- **VC Firm Content** (pre-indexed from web scraping)
  - Investment thesis documents
  - Partner blog posts
  - Portfolio company descriptions
  - Sector focus statements
  - Stage preferences
  - Deal criteria
  - 200-500 key pages crawled from a16z.com
  - ~10K chunks after processing

**Processing Input:**
Create a chatbot style interface where the user can type in their business plan as text 
The Chatbot will  respond in a single turn only for Iteration 1

### Expected Outputs

**Structured Explanation Format:**

```
ALIGNMENT ANALYSIS: [Company Name] vs a16z

HOW THIS PLAN ALIGNS:
1. Market Focus: [Specific match with evidence from both plan and VC criteria]
   Source: a16z blog post "Enterprise Software Thesis" (2024)
2. Stage Fit: [Evidence of stage alignment]
   Source: a16z portfolio analysis
3. Technology Approach: [Alignment on tech strategy]
   Source: Partner interview on AI strategy
4. [Additional 2-3 matches]

HOW THIS PLAN DOESN'T ALIGN:
1. Geographic Preference: [Specific gap with evidence]
   Source: a16z investment patterns (0% in [region])
2. Business Model: [Divergence explanation]
   Source: a16z investment thesis page
3. Team Background: [Missing criteria]
   Source: Portfolio company founder backgrounds
4. [Additional 2-3 gaps]

SUMMARY: 
Neutral summary highlighting strongest matches and most significant gaps without recommendation.

SOURCES:
- https://a16z.com/posts/enterprise-software-thesis
- https://a16z.com/portfolio/company-x
- [Additional source URLs]
```

**Output Characteristics:**
- Bullet-pointed, scannable format
- Evidence-backed claims with source URLs
- Balanced presentation (no bias toward fit/no-fit)
- 300-500 words total
- Generated in <5 seconds
- Citations to specific a16z content

### Intermediate Steps / Notes

**RAG Pipeline Detailed Flow:**

1. **Parse Business Plan**
   - PDF/TXT parsing (PyPDF2, python-docx)
   - Section extraction: problem, solution, market, team, traction
   - Generate embedding for entire plan

2. **Generate Search Queries**
   - Extract key terms from business plan
   - Formulate semantic search queries
   - Example: "enterprise SaaS healthcare investment criteria"

3. **Retrieve from Vector DB**
   - Hybrid search: 70% semantic similarity + 30% BM25 keyword
   - Retrieve top-20 candidates
   - Filter by VC firm (a16z in this case)

4. **Rank & Rerank Chunks**
   - Re-rank top-20 to top-10 using cross-encoder (optional)
   - Group chunks by criteria category (market, team, product, etc.)
   - Ensure coverage across all key criteria areas

5. **Construct Prompt**
   - Template with retrieved context
   - Business plan summary
   - Instruction: "Analyze alignment WITHOUT making recommendations"
   - Chain-of-thought reasoning enabled

6. **LLM Generates Analysis**
   - Model identifies potential matches/gaps
   - Evidence extraction from both inputs
   - Balance enforcement: minimum 3 matches and 3 gaps
   - Structured output with citations

**Quality Controls:**
- Minimum 3 matches and 3 gaps required
- Evidence citation mandatory (no hallucinated claims)
- Tone calibration: neutral, not persuasive
- Length constraints: 50-100 words per match/gap
- Source URL verification

**Chunking Strategy:**
- Chunk size: 500-1000 tokens with overlap
- Semantic chunking (preserve section boundaries)
- Metadata: author, date, page type, source URL

**Retrieval Parameters:**
- Top-k: 5-10 chunks
- Similarity threshold: >0.7 for semantic search
- BM25 weight: 30% for keyword matching

### Implementation Roadmap (1-2 Weeks)

#### Week 1: Data Pipeline

**Days 1-2: Content Ingestion**
- Set up Scrapy spider for a16z.com
- Crawl 200-500 key pages (blog, portfolio, team)
- Parse and clean text with BeautifulSoup4
- Save as JSON with metadata

**Days 3-4: Vector Database Setup**
- Install Weaviate (Docker) or Chroma
- Generate embeddings with sentence-transformers
- Index all a16z content (~10K chunks)
- Test basic similarity search
- Verify hybrid search functionality

**Day 5: RAG Pipeline**
- Build LangChain retrieval chain
- Test with sample queries
- Tune chunk size (500-1000 tokens) and overlap
- Validate retrieval quality on test cases

#### Week 2: Application Layer

**Days 6-7: Business Plan Processing**
- Build PDF/TXT parser (PyPDF2, python-docx)
- Extract key sections: problem, solution, market, team, traction
- Generate embedding for entire plan
- Test with 5-10 sample business plans

**Days 8-9: Alignment Analysis Logic**
- Create prompt template for alignment checking
- Implement scoring logic (1-10 scale)
- Extract reasoning + supporting evidence from a16z content
- Ensure balanced output (matches and gaps)

**Days 10-11: UI Development**
- Build Streamlit prototype OR simple React + FastAPI REST API
- File upload functionality
- Text input option
- Results display with source citations
- Responsive design for mobile/desktop

**Day 12: Testing & Refinement**
- Test with 5-10 sample business plans
- Tune retrieval parameters (top-k, similarity threshold)
- Refine prompts for better output quality
- Gather user feedback
- Fix bugs and edge cases

### Additional Components

**Document Parsing:**
- **PyPDF2** or **PyMuPDF** for PDF extraction
- **python-docx** for DOCX files
- **docx2txt** as lightweight alternative

**Text Processing:**
- **LangChain RecursiveCharacterTextSplitter** for chunking
- Metadata extraction: section type, page number, source URL
- Preserve semantic boundaries (don't split mid-sentence)

**Caching (Optional for MVP):**
- Redis or in-memory cache for common queries
- Cache VC content embeddings (one-time generation)
- Cache frequent business plan sections

**Deployment Options:**
- **Local dev**: $0, fastest for prototyping
- **Render free tier**: FastAPI backend
- **Vercel free tier**: React frontend
- **Docker**: Self-hosted Weaviate

### Tool Usage

**Core Tools:**

**Content Ingestion:**
- **Scrapy**: Web crawling framework
- **BeautifulSoup4**: HTML parsing

**Vector Database:**
- **Weaviate** (Docker, self-hosted) OR
- **Chroma DB** (pure Python)

**Embeddings:**
- **Sentence-Transformers** (all-MiniLM-L6-v2) - FREE
- Alternative: OpenAI text-embedding-3-small

**LLM:**
- **Ollama** (Llama 3.2:3b) - FREE, local
- Alternative: GPT-4o-mini for better quality

**RAG Orchestration:**
- **LangChain**: RAG pipeline framework

**Backend:**
- **FastAPI**: Python web framework

**Frontend:**
- **Streamlit**: Rapid prototyping UI

**Document Parsing:**
- **PyPDF2** / **PyMuPDF**: PDF parsing
- **python-docx**: DOCX parsing

**No External Tool Calls:**
This iteration is self-contained - no web search, no external data lookups during query time (all VC content pre-indexed)

### Cost Breakdown (Iteration 1)

| Component | Tool | Cost |
|-----------|------|------|
| Web Scraping | Scrapy | $0 |
| Vector DB | Weaviate (self-hosted) | $0 |
| Embeddings | Sentence-Transformers | $0 |
| LLM | Ollama (local) | $0 |
| Backend | FastAPI (Python) | $0 |
| Frontend | Streamlit | $0 |
| Hosting | Local dev | $0 |
| **Total** | | **$0** |

**If you want better quality:**
- GPT-4o-mini: ~$10-20 for 1,000 test queries
- Weaviate Cloud sandbox: $0 (limited)
- OpenAI embeddings: ~$1-2 for indexing
- **Total for testing phase: $10-20**

**Cost per query (production with paid services):**
- Embedding: $0.00013 (OpenAI)
- LLM generation: $0.01-0.05 (GPT-4o-mini, depends on length)
- Vector DB: ~$0.0001 (Weaviate Cloud)
- **Total: ~$0.01-0.05 per evaluation**

### Key Metrics to Track

1. **Content Coverage**: % of a16z focus areas captured in vector DB
   - Target: 90%+ coverage of investment thesis, portfolio insights

2. **Retrieval Quality**: % of queries returning relevant chunks
   - Method: Manual evaluation on 50 test cases
   - Target: 80%+ relevance rate

3. **Alignment Accuracy**: LLM output vs manual human assessment
   - Method: Compare on 10-20 business plans with expert review
   - Target: 70%+ agreement with human analysts

4. **Response Time**: End-to-end latency
   - Target: <5 seconds per analysis
   - Breakdown: Retrieval (<1s) + LLM generation (<4s)

5. **User Trust**: % of users who trust explanations enough to take action
   - Method: User surveys after testing
   - Target: 70%+ trust threshold

6. **Time Reduction**: Speed vs manual research
   - Target: 10x faster than manual VC criteria research

### Validation Framework

**Manual Review Dashboard:**
- Sample 20-30 evaluations for quality assessment
- Expert review: Does explanation accurately reflect VC criteria?
- Citation verification: Are sources correctly attributed?

**A/B Testing:**
- Compare AI explanations vs manual analyst work
- Measure: accuracy, completeness, time saved
- Gather user preference data

**Error Analysis:**
- Track failure modes: hallucinations, irrelevant matches, missing gaps
- Iterate on prompts and retrieval parameters

---

# ITERATION 2: Reflective Agent with Gap-Filling Research

## 1. Architecture & Design

### New Features
- **Reflection Agent**: Meta-assessment of explanation quality and confidence
- **Autonomous Research Agent**: Proactive gap-filling through web search
- **Confidence Scoring System**: Evidence grading (✓✓✓ strong → ? insufficient)
- **Self-critique Loop**: System identifies and addresses its own limitations
- **Dynamic Research**: Adaptive information gathering based on reflection insights

### Usage Paradigm
**Agents (Level 2 - ReAct Pattern)**

Uses LangGraph with ReAct (Reasoning + Acting) pattern. Agent reasons about information gaps, acts by conducting research, observes results, and iterates.

### Architecture Diagram Description

```
Business Plan + VC Criteria
        ↓
[Agent 1: Initial Retrieval & Explanation]
    (from Iteration 1)
        ↓
    Explanation Draft
        ↓
[Agent 2: Reflection & Critique]
    - Assess claim quality
    - Identify missing information
    - Grade evidence strength
    - Calculate confidence scores
        ↓
    Confidence < 0.7?
        Yes →
            [Agent 3: Research & Gap-Fill]
            - Web Search (5 max)
            - VC Content Deep Search
            - LinkedIn verification
            - Cross-reference portfolio
            ↓
        [Regenerate Explanation]
        (original context + research)
        No →
        [Final Output with Confidence]
```

**Agentic Behaviors:**
- Autonomous decision-making (research only if needed)
- Self-assessment of output quality
- Iterative refinement (max 2 reflection loops)

### Sample Inputs

**Same as Iteration 1, plus:**

**Reflection Agent Input:**
- Initial explanation from Agent 1
- Evidence mapping (which claims trace to which source chunks)
- Confidence threshold (0.7 default)

**Research Agent Input:**
- List of missing information (from reflection)
- Research priorities (ranked by importance)
- Query templates for different info types

**Example Research Trigger:**
```
Reflection Output:
- Confidence in alignment claims: 0.85 (High)
- Confidence in gap identification: 0.55 (Low - needs verification)
- Missing information: 
  1. Team background details (CTO prior experience)
  2. Competitive moat specifics (patent status unclear)
  3. Network effects evidence (mentioned but not explained)
```

### Expected Outputs

**Enhanced Explanation with Confidence Grading:**

```
ALIGNMENT ANALYSIS: [Company Name] vs [VC Firm]

HOW THIS PLAN ALIGNS:
1. ✓✓✓ Market Focus: SaaS for healthcare matches VC thesis (explicit in investment criteria doc p.3)
2. ✓✓ Stage Fit: Series A company aligns with VC stage preference (inferred from 8/10 recent portfolio deals)
3. ✓ Technology Approach: AI/ML component mentioned but details sparse (single reference in plan)

HOW THIS PLAN DOESN'T ALIGN:
1. ✓✓ Geographic Preference: Company based in Austin, VC prefers Bay Area (researched: VC has 0 Texas investments)
2. ? Business Model: Revenue model unclear in plan, unable to verify fit (insufficient data)
3. ✓✓✓ Team Background: No founder with healthcare domain expertise (verified via LinkedIn - founders from fintech)

META-ASSESSMENT:
Overall Confidence: 72%
Strong Evidence: 4/6 claims
Research Conducted: 3 web searches (team verification, geography analysis, portfolio review)
Data Gaps: Business model requires follow-up
```

**Additional Output Components:**
- **Confidence score** per claim (0-100%)
- **Evidence quality legend** (✓✓✓ = strong, ? = insufficient)
- **Research summary**: What was searched, what was found
- **Transparency note**: Highlighting assumptions vs verified facts

### Intermediate Steps / Notes

**Reflection Logic:**
```python
# Pseudo-code for reflection agent
def reflect_on_explanation(explanation, source_chunks):
    for claim in explanation.matches + explanation.gaps:
        evidence = find_supporting_evidence(claim, source_chunks)
        
        if evidence == "explicit statement":
            confidence = HIGH (✓✓✓)
        elif evidence == "multiple weak signals":
            confidence = MEDIUM (✓✓)
        elif evidence == "single ambiguous reference":
            confidence = LOW (✓)
        else:
            confidence = INSUFFICIENT (?)
            add_to_research_queue(claim)
    
    if overall_confidence < 0.7:
        trigger_research_agent()
```

**Research Agent Decision Tree:**
1. **Information Type Classification:**
   - Team info → LinkedIn + company website
   - Market data → Web search + industry reports
   - Competitive landscape → Crunchbase + news search
   - VC preferences → VC website + partner blogs

2. **Research Prioritization:**
   - Critical gaps (impacts core fit assessment): Priority 1
   - Supporting evidence (strengthens claims): Priority 2
   - Nice-to-have context: Priority 3 (skip if search budget exhausted)

3. **Search Strategy:**
   - Max 5 searches per evaluation (cost control)
   - Parallel execution where possible
   - Stop early if confidence threshold reached

**Quality Control:**
- **Reflection Loop Limit:** Max 2 iterations to prevent infinite refinement
- **Research Validation:** Verify source credibility before incorporating
- **Confidence Calibration:** Test against 20 manual evaluations to calibrate thresholds

### Additional Components

**Beyond Iteration 1:**

**External Search APIs:**
- **Exa.ai**: Semantic web search ($2.50 per 1K queries)
  - Best for: "Find companies similar to [portfolio company]"
  - Returns: Embeddings-based relevance ranking
- **Brave Search API**: General web search (free tier available)
  - Best for: Recent news, company updates
  - Returns: Traditional web results

**Internal VC Content Corpus:**
- Indexed blog posts, partner interviews, press releases
- Searchable with same vector DB as criteria
- Enables queries like: "Has this VC invested in Austin-based companies?"

**Research Result Caching:**
- Cache common queries (e.g., "What is [company]'s revenue model?")
- Redis or in-memory cache
- Reduces redundant searches across evaluations

**Additional Infrastructure:**
- **Agent orchestration**: LangGraph for state management
- **Search result parsing**: BeautifulSoup for web scraping
- **LinkedIn scraper**: Automated profile data extraction (use cautiously - ToS concerns)

### Tool Usage

**Agent 1 Tools:**
- Same as Iteration 1 (retrieval + GPT-4)

**Agent 2 Tools:**
- **GPT-4** for reflection and critique
- **Custom confidence calculator** (rule-based + LLM)

**Agent 3 Tools:**
- **Exa.ai API**: Semantic web search
- **Brave Search API**: Traditional web search  
- **Internal VC Content Search**: Vector similarity search
- **LinkedIn API/scraper**: Founder background verification
- **Crunchbase API** (optional): Funding and competitor data

**Tool Call Limits:**
- Max 5 web searches per evaluation
- Max 2 LinkedIn lookups
- Max 3 internal VC content searches
- Total research tool budget: ~$0.10-0.15 per evaluation

**Validation Framework:**
- 20-case manual validation set
- Metrics: Research accuracy (% of gaps correctly filled), confidence calibration (do scores match human agreement?), user satisfaction (follow-up question reduction)

---

# ITERATION 3: Multi-Agent Investment Committee with Proactive Strategy

## 1. Architecture & Design

### New Features
- **Multi-Agent System**: 4 specialized agents mimicking investment committee roles
- **Investment Committee Synthesis**: Consensus vs. disagreement identification
- **Proactive Positioning Strategy**: Recommendations for both startups and VCs
- **Interactive Dialogue Mode**: Users can query agents directly
- **Comparable Benchmarking**: Automatic comparison to portfolio companies
- **Strategic Recommendations**: Beyond fit assessment to actionable next steps

### Usage Paradigm
**Multi-Agent Systems**

Uses CrewAI or AutoGen for multi-agent orchestration. Agents work in parallel with shared memory, communicate findings, and synthesize perspectives.

### Architecture Diagram Description

```
                    User Query
                        ↓
            [Coordinator Agent]
            (Orchestration & Planning)
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓               ↓
[Market Agent]  [Product Agent]  [Team Agent]  [Financial Agent]
    - TAM/SAM       - Tech moat      - Founder      - Unit econ
    - Competition   - Defensibility   - Track record - Business model
    - Timing        - PMF signals     - Domain exp   - Capital efficiency
        ↓               ↓               ↓               ↓
    [Web Search]    [GitHub API]    [LinkedIn API]  [Financial DB]
    [Crunchbase]    [Patent Search] [Prior Outcomes][Comp. Metrics]
        ↓               ↓               ↓               ↓
        └───────────────┼───────────────┘
                        ↓
            [Shared Working Memory]
            - Cross-agent findings
            - Collaborative notes
                        ↓
            [Synthesis Agent]
            - Consensus strengths
            - Disagreement areas
            - Risk prioritization
                        ↓
            [Strategy Agent]
            - Positioning for startup
            - Positioning for VC
            - Comparable benchmarks
                        ↓
            [Dialogue Agent]
            - Interactive Q&A
            - Agent perspective queries
                        ↓
            Final Multi-Perspective Report
```

**Key Architectural Principles:**
- **Parallel execution**: 4 agents work simultaneously (20s total vs 60s sequential)
- **Shared memory**: Agents can reference each other's findings
- **Autonomous planning**: Each agent decides its research depth
- **Inter-agent communication**: Agents request info from peers

### Sample Inputs

**Primary Inputs (same as previous iterations):**
- Business Plan
- VC Firm Criteria

**Additional Context Inputs:**
- **VC Portfolio Companies** (for benchmarking)
  - Company descriptions
  - Founding team profiles
  - Investment thesis for each
  - Performance metrics (if available)
- **Comparable Company Universe** (for market analysis)
  - Competitor funding data
  - Market positioning
  - Technology stacks

**Agent-Specific Inputs:**

**Market Agent:**
- Industry reports (pre-indexed)
- Competitive landscape data (Crunchbase)

**Product Agent:**
- Technical documentation from business plan
- GitHub repos (if public)
- Patent databases

**Team Agent:**
- Founder LinkedIn profiles
- Prior company outcomes
- Educational backgrounds

**Financial Agent:**
- Financial projections from business plan
- Comparable company metrics
- Industry benchmark data

**User Query Examples:**
- "Evaluate this plan for [VC Firm] and tell me how to position it"
- "Compare this company to [VC's] portfolio and find best fit partner"
- "What are the biggest risks and how can we mitigate them?"

### Expected Outputs

**Comprehensive Investment Committee Report:**

```
MULTI-AGENT INVESTMENT ANALYSIS
Company: [Name] vs VC: [Firm Name]

═══════════════════════════════════════════════════════

INDIVIDUAL AGENT ASSESSMENTS

[Market Agent - Perspective 1/4]
✓ Market Assessment: $2.3B TAM (bottom-up), 18% YoY growth
✓ Competitive Landscape: 3 competitors, $120M combined funding
✓ Entry Timing: FAVORABLE - incumbents slow to innovate
⚠ Risk: Market shows signs of crowding (5 new entrants in 6 months)
Confidence: 78%

[Product Agent - Perspective 2/4]
✓ Technology Stack: Modern (verified via job postings)
✓ Network Effects: Present but early-stage
⚠ Defensibility: MODERATE - No patent moat, limited technical differentiation
✗ Product-Market Fit: Unclear validation (only 5 design partners mentioned)
Confidence: 65%

[Team Agent - Perspective 3/4]
✓✓ CEO Background: 8 years target industry experience
✓✓ CTO Credentials: Led engineering at [Notable Company]
✓ Advisory Board: 2 industry veterans
⚠ Founding Team: No prior exits (elevated risk for late-stage fund)
Confidence: 82%

[Financial Agent - Perspective 4/4]
✓ Gross Margins: 72% (strong for SaaS)
⚠ Unit Economics: $2.5K ACV with 15-month sales cycle (high CAC risk)
⚠ Capital Efficiency: Below peer median (burn rate concerning)
✓ Path to Profitability: Series B timeframe (reasonable)
Confidence: 71%

═══════════════════════════════════════════════════════

INVESTMENT COMMITTEE SYNTHESIS

CONSENSUS STRENGTHS (All 4 Agents Agree):
1. Market timing is favorable (window of opportunity)
2. Team has strong domain expertise (3/4 strong, 1/4 moderate)
3. Gross margins indicate healthy unit economics potential

DISAGREEMENT AREAS:
• Product Defensibility: Tech agent rates "WEAK" (no IP moat) vs Market agent rates "MODERATE" (network effects potential)
  → Resolution depends on: network effects timeline materialization
• Team Risk Tolerance: Team agent flags "no prior exits" vs Financial agent considers founders "execution-capable"
  → Resolution depends on: VC's stage focus (seed vs growth)

HIGHEST PRIORITY RISKS:
1. [Financial Agent] High CAC relative to early-stage norms
2. [Market Agent] Competitive funding activity suggests crowded space
3. [Product Agent] Limited technical moat requires fast execution

═══════════════════════════════════════════════════════

PROACTIVE POSITIONING STRATEGY

FOR THE STARTUP (How to Strengthen VC Fit):
1. EMPHASIZE: Team's 8-year industry expertise
   → Addresses: Common early-stage concern about domain knowledge
   → Tactic: Lead pitch with customer pain points you've personally experienced

2. ARTICULATE: Network effects roadmap with specific milestones
   → Addresses: Product defensibility gap
   → Tactic: Show inflection points (e.g., "At 500 customers, data marketplace activates")

3. DEMONSTRATE: Path to improving CAC via product-led growth
   → Addresses: Unit economics concern
   → Tactic: Pilot PLG motion with 2-3 customers, present conversion data

TARGET PARTNER: [Partner Name] who led similar investment in [Portfolio Company]
COMPARABLE POSITIONING: "Similar to [Portfolio Co] but for [adjacent market]"

FOR THE VC (Strategic Fit Analysis):
✓ COMPARES FAVORABLY TO: [Portfolio Company X] on team expertise, market timing
✗ DIVERGES FROM: [Portfolio Company Y] on business model (transactional vs subscription)
↔ STRATEGIC FIT: Could complement [Portfolio Company Z] via partnership/data sharing

BENCHMARK DATA:
- Market size: 85th percentile vs VC portfolio median
- Team experience: 70th percentile
- Capital efficiency: 35th percentile (concern area)
- Technology moat: 40th percentile

═══════════════════════════════════════════════════════

INTERACTIVE DIALOGUE (Sample Q&A)

User: "Why do you think network effects are weak?"
Product Agent: "The business plan mentions a 'data marketplace' but doesn't explain when it activates. Network effects typically require critical mass (my threshold: 200-500 customers). Current traction is 5 design partners. I'd need to see: (1) flywheel mechanics diagram, (2) data liquidity timeline, (3) competitive moat from data network."

User: "What would change your assessment to 'strong fit'?"
Synthesis: "Three concrete improvements would shift to STRONG FIT:
1. Reduce CAC by 30% (show PLG pilot data)
2. Secure 1 strategic customer in top 10 target accounts (validation signal)
3. File provisional patent on core data processing method (defensibility)
Current assessment: 68% fit. These changes would push to 85%+."

User: "Show me comparable companies for financial benchmarking"
Financial Agent: [Returns table]
| Company | Stage | ACV | Sales Cycle | CAC:LTV | Burn Rate |
| This Startup | Seed | $2.5K | 15mo | TBD | $150K/mo |
| Comp A | Series A | $5K | 12mo | 1:4 | $200K/mo |
| Comp B | Seed | $1.8K | 18mo | 1:3.5 | $120K/mo |
Analysis: Startup's ACV is mid-range but sales cycle is long. Focus on reducing cycle or increasing ACV.
```

**Output Characteristics:**
- **Multi-perspective**: 4 distinct agent viewpoints
- **Synthesis**: Clear consensus vs disagreement mapping
- **Actionable**: Specific recommendations with tactics
- **Interactive**: Q&A capability for deeper exploration
- **Benchmarked**: Portfolio and market comparisons
- **Confidence-graded**: Each agent reports certainty
- **Length**: 1,500-2,500 words (comprehensive)
- **Generation time**: 20-40 seconds

### Intermediate Steps / Notes

**Coordinator Agent Logic:**
```python
# Orchestration flow
def coordinate_analysis(business_plan, vc_criteria):
    # 1. Parallel agent dispatch
    tasks = [
        market_agent.analyze(business_plan, vc_criteria),
        product_agent.analyze(business_plan, vc_criteria),
        team_agent.analyze(business_plan, vc_criteria),
        financial_agent.analyze(business_plan, vc_criteria)
    ]
    
    results = await asyncio.gather(*tasks)  # Parallel execution
    
    # 2. Cross-agent communication
    # If one agent identifies gap, others can supplement
    shared_memory.store(results)
    
    # 3. Synthesis
    synthesis = synthesize_perspectives(results)
    
    # 4. Strategy generation
    strategy = generate_positioning(synthesis, vc_portfolio)
    
    # 5. Dialogue mode activation
    return InteractiveReport(synthesis, strategy, agents=all_agents)
```

**Agent Behaviors:**

**Autonomous Planning:**
- Each agent decides research depth based on initial findings
- If high confidence (>80%), agent does shallow research (2-3 tool calls)
- If ambiguous (<60%), agent does deep research (8-10 tool calls)

**Inter-Agent Communication:**
```
Market Agent → Product Agent: "I found competitors using patent portfolios. Can you check if our startup has patents?"
Product Agent → Market Agent: "Verified - 0 granted patents, 1 provisional. This affects market positioning."
```

**Adaptive Depth:**
- Agents don't rigidly follow scripts
- If initial searches yield limited info, agents reformulate queries
- If findings are high-quality, agents stop early (don't waste tool calls)

**Quality Control:**
- **Max iterations per agent**: 3 research loops
- **Tool call budget**: 20 total across all 4 agents (5 per agent avg)
- **Consensus threshold**: If 3/4 agents agree, mark as "consensus"
- **Disagreement handling**: If 2-2 split, flag as "requires human judgment"

### Additional Components

**Beyond Iteration 2:**

**Multi-Agent Orchestration Framework:**
- **CrewAI** or **AutoGen** for agent coordination
- Supports:
  - Parallel execution
  - Shared memory/context
  - Inter-agent messaging
  - Dynamic task routing

**Expanded Tool Ecosystem (15+ tools):**

**Market Agent Tools:**
- Crunchbase API (competitor funding)
- SimilarWeb (web traffic analysis)
- Google Trends (market interest signals)
- Industry report databases (Gartner, CB Insights)

**Product Agent Tools:**
- GitHub API (tech stack analysis)
- Stack Overflow (technology adoption signals)
- Patent databases (USPTO, Google Patents)
- Technical blog crawlers (engineering quality signals)

**Team Agent Tools:**
- LinkedIn API (founder backgrounds)
- Crunchbase (prior company outcomes)
- University verification (educational credentials)
- Social media scrapers (founder reputation)

**Financial Agent Tools:**
- Financial databases (CapIQ, PitchBook)
- SaaS metrics benchmarks (OpenView, SaaS Capital)
- Comparable company APIs
- Excel/model parsers (for financial projections)

**Shared Infrastructure:**
- **Vector memory**: Agents store findings for cross-reference
- **Collaborative workspace**: Agents leave "notes" for each other
  - Example: "Market Agent: I found competitor X. Product Agent, can you analyze their tech stack?"
- **Result caching**: Avoid redundant searches across agents

**Interactive Dialogue System:**
- **Streamlit or Gradio UI**: Chat interface for Q&A
- **Agent routing**: User questions directed to relevant agent
- **Follow-up logic**: Agents can clarify or drill deeper on request

### Tool Usage

**Coordinator Agent:**
- **LangGraph/CrewAI**: Orchestration framework
- **GPT-4**: High-level coordination and synthesis

**Market Agent:**
- Crunchbase API
- Web search (Exa.ai/Brave)
- Industry report databases

**Product Agent:**
- GitHub API
- Patent search (USPTO)
- Technical documentation parsers

**Team Agent:**
- LinkedIn API/scraper
- Crunchbase (prior exits)
- News search (team announcements)

**Financial Agent:**
- Financial databases (if available)
- Comparable company metrics APIs
- Excel/PDF parsers (for projections)

**Synthesis Agent:**
- GPT-4 (high-stakes reasoning)
- Custom consensus algorithms

**Strategy Agent:**
- GPT-4 (strategic recommendations)
- Portfolio company database (internal)

**Dialogue Agent:**
- GPT-4 (interactive Q&A)
- Agent state management (tracks conversation context)

**Total Tool Call Budget:**
- **Max 20 tool calls per evaluation** across all agents
- **Avg 5 per agent**: 2 initial research + 2 follow-up + 1 verification
- **Parallel execution**: Reduces latency from 60s (sequential) to 20-30s

**Cost Structure:**
- **Agentic overhead**: ~$0.30 per evaluation (LLM calls for coordination)
- **Tool calls**: ~$0.20 per evaluation (APIs, searches)
- **Total**: ~$0.50-0.80 per evaluation
- **Research-intensive cases**: Could reach $1.50

---

# APPENDIX: Cross-Iteration Comparison

## Progressive Value Curve

```
Iteration 1: Basic retrieval + explanation
    ↓ [+Trust via self-awareness]
    Value: 10x time reduction, 70% trust threshold

Iteration 2: Self-critique + autonomous research  
    ↓ [+Comprehensiveness + expertise]
    Value: 40% fewer follow-ups, 30-50% gap filling

Iteration 3: Multi-agent committee + strategy
    ↓ [+Multi-dimensional analysis + action orientation]
    Value: 75% match with human committees, 60% recommendations used
```

## Complexity vs Value Matrix

| Iteration | Paradigm | Tool Calls | Cost | Latency | Value Add |
|-----------|----------|------------|------|---------|-----------|
| 1 | RAG | 0 | $0.05 | <5s | Fast criteria surfacing |
| 2 | Agents | 5 | $0.20 | 10-15s | Gap filling + confidence |
| 3 | Multi-Agent | 20 | $0.60 | 20-30s | Strategic recommendations |

## When to Use Each Iteration

**Iteration 1:** 
- Use when: Users distrust AI scoring, need quick initial screening
- Best for: High-volume deal flow, early filtering
- Limitation: No depth, no research

**Iteration 2:**
- Use when: Users want AI to "think through" analysis rigorously
- Best for: Mid-funnel diligence, reducing analyst grunt work  
- Limitation: Single perspective, limited strategic insight

**Iteration 3:**
- Use when: Users want investment committee-grade analysis
- Best for: Final-stage evaluation, preparing for partner meetings
- Limitation: Higher cost/latency, overkill for quick screening

---

# VALIDATION METRICS ACROSS ITERATIONS

## Iteration 1 Success Criteria
✓ 70%+ of users trust explanations enough to take action  
✓ 10x time reduction vs manual research  
✓ Users prefer explanation format over scoring  

**Validation Method:**
- 3 pilot VCs with 10 evaluations each
- User surveys (trust, usability)
- Time-to-decision tracking

## Iteration 2 Success Criteria
✓ Autonomous research fills 40%+ of data gaps correctly  
✓ 30% reduction in user follow-up questions  
✓ Confidence scores correlate with match quality (r > 0.65)  

**Validation Method:**
- 20 evaluations with manual validation
- Research accuracy scoring (% gaps correctly filled)
- Confidence calibration analysis

## Iteration 3 Success Criteria
✓ Multi-agent assessments match human investment committees 75%+ of time  
✓ Strategic recommendations used in 60%+ of actual VC outreach  
✓ Interactive Q&A resolves objections without human analyst  

**Validation Method:**
- 10 test cases curated for multi-agent validation
- Committee decision comparison (blind human vs AI)
- Recommendation adoption tracking
- User preference surveys (80%+ prefer multi-perspective)

---

# IMPLEMENTATION TIMELINE & MILESTONES

## Iteration 1: Weeks 1-2
- Week 1: RAG infrastructure + embedding pipeline
- Week 2: Explanation generation + user testing

## Iteration 2: Weeks 3-6  
- Week 3-4: Reflection agent + confidence scoring
- Week 5: Research agent + tool integrations
- Week 6: Loop logic + validation

## Iteration 3: Weeks 7-14
- Week 7-9: Multi-agent framework + specialist agents
- Week 10-11: Synthesis + strategy layer
- Week 12-13: Interactive dialogue + UI
- Week 14: End-to-end testing + refinement

**Total Timeline:** 14 weeks (3.5 months) for full MVP progression

---

*Document Version: 1.0*  
*Last Updated: [Current Date]*  
*Project: VIRA MVP - VC Investment Research Agent*
