# VIRA: Complete Product Requirements Document

**Version:** 2.0  
**Last Updated:** November 25, 2025  
**Status:** Living Document  
**Target Release:** Iteration 1 (✅ Complete), Iteration 2 (✅ Complete), Iteration 3 (📋 Planned)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision](#2-product-vision)
3. [User Personas](#3-user-personas)
4. [Feature Requirements by Iteration](#4-feature-requirements-by-iteration)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Success Criteria & KPIs](#6-success-criteria--kpis)
7. [Out of Scope](#7-out-of-scope)
8. [Technical Constraints](#8-technical-constraints)

---

## 1. Executive Summary

### 1.1 Problem Statement

**Target Users:** Early-stage founders (18-36 months before raising venture capital) who lack resources for systematic market research, competitive analysis, and strategic planning needed to align with VC investment criteria.

**Pain Points:**
- Founders spend 40-80 hours researching VC firm focus areas, investment theses, and portfolio patterns
- No structured way to assess business plan alignment before reaching out to VCs
- Difficulty identifying strategic gaps that could be addressed before fundraising
- Limited access to institutional-quality research tools available to VCs
- Risk of approaching misaligned VCs, wasting time and damaging reputation

**Current Alternatives:**
- Manual research: Time-intensive, inconsistent, incomplete
- Pitch consultants: Expensive ($5K-20K), not scalable
- Cold outreach: Low success rates, high rejection costs
- Generic VC databases: List firms but don't assess alignment

### 1.2 Solution Overview

**VIRA (Venture Intelligence Research Assistant)** is an AI-powered platform that provides institutional-quality research and alignment analysis by:

1. **Ingesting comprehensive VC firm content** (blog posts, investment theses, portfolio analyses, partner commentary)
2. **Analyzing founder business plans** against VC criteria using advanced RAG and agentic AI
3. **Generating structured alignment reports** with evidence-backed matches and gaps
4. **Conducting autonomous research** to fill information gaps and validate claims
5. **Simulating investment committee perspectives** to provide multi-dimensional analysis

**Core Value Proposition:**
- **10x faster** than manual VC research
- **70-90% accuracy** in identifying alignment (validated against human analysts)
- **Transparent & explainable** - shows evidence, not black-box scoring
- **Actionable insights** - specific recommendations for strengthening alignment

### 1.3 Business Model (Future)

**MVP Focus:** Prototype validation with a16z content only  
**Future State:**
- **For Founders:** Freemium model (3 free analyses, $49/month for unlimited)
- **For VCs:** White-label version for deal flow screening ($5K-20K/year per firm)
- **Enterprise:** Custom training on proprietary criteria

---

## 2. Product Vision

### 2.1 Long-Term Vision

**Mission:** Democratize access to institutional-quality venture capital intelligence, enabling founders to make data-driven fundraising decisions and VCs to efficiently identify high-potential companies.

**5-Year Vision:**
- Cover top 100 VC firms globally
- Process 50,000+ business plan analyses annually
- 85%+ accuracy in predicting VC interest
- Integration with pitch deck tools, CRM systems, and fundraising platforms
- Real-time market intelligence and competitive positioning

### 2.2 Market Positioning

**Target Market Size:**
- **TAM:** 1M+ venture-backed startups globally seeking funding
- **SAM:** 150K+ pre-seed to Series B companies in US/Europe (primary markets)
- **SOM:** 10K+ companies in year 1 (early adopters, AI/tech-forward founders)

**Competitive Differentiation:**
- **vs. Crunchbase/PitchBook:** We analyze alignment, not just list firms
- **vs. Consultants:** Scalable, instant, fraction of the cost
- **vs. ChatGPT/Generic AI:** Specialized training on VC criteria, sourced evidence, agentic research

---

## 3. User Personas

### 3.1 Primary Persona: Sarah - Technical Founder

**Demographics:**
- Age: 28-35
- Background: Engineering/product role at tech company (3-7 years experience)
- Education: Computer Science degree
- Location: San Francisco Bay Area, NYC, or other tech hub
- First-time founder, 12 months into building product

**Goals:**
- Validate business idea against VC criteria before investing 18+ months
- Identify which VCs to approach (avoid wasting time on misaligned firms)
- Understand gaps in her plan that could be addressed now
- Build conviction in her positioning and pitch

**Pain Points:**
- Limited time for fundraising research (focused on product development)
- Uncertainty about which VCs invest in her space
- Fear of approaching "wrong" VCs and damaging reputation
- Lack of structured feedback on business plan

**Use Cases:**
1. **Pre-fundraise validation:** Analyze plan against top 10 target VCs
2. **Gap identification:** Understand what's missing before Series A conversations
3. **Pitch refinement:** Get data-driven insights on positioning
4. **Competitive intelligence:** See how similar companies were evaluated

**Success Metrics for Sarah:**
- Reduces VC research time from 60 hours → 6 hours
- Increases relevant VC meetings from 20% → 60%
- Gets actionable feedback without hiring expensive consultants

### 3.2 Secondary Persona: Michael - VC Associate

**Demographics:**
- Age: 26-32
- Role: Associate or Senior Associate at venture capital firm
- Background: Investment banking, consulting, or startup operations
- Education: MBA or equivalent
- Location: Major VC hub

**Goals:**
- Screen 200+ inbound business plans per month efficiently
- Identify high-potential companies early in their funnel
- Provide structured feedback to partners on deal fit
- Reduce time spent on obviously misaligned deals

**Pain Points:**
- Overwhelming deal flow (150-300 plans/month)
- Inconsistent screening criteria across team
- Difficulty articulating why deals don't fit
- Time wasted on deep dives into misaligned companies

**Use Cases:**
1. **Deal flow screening:** Quickly assess if plan matches firm thesis
2. **Partner memos:** Generate structured analysis for investment committee
3. **Founder feedback:** Provide constructive rejection reasons
4. **Portfolio benchmarking:** Compare new deals to existing portfolio

**Success Metrics for Michael:**
- Reduces screening time from 30 min → 5 min per plan
- Increases quality of partner referrals (fewer false positives)
- Standardizes screening across team

---

## 4. Feature Requirements by Iteration

### 4.1 Iteration 1: Business Plan Alignment (RAG) ✅

**Status:** Fully implemented and operational  
**Paradigm:** Retrieval-Augmented Generation (RAG)  
**Timeline:** Weeks 1-2 (Completed November 2025)

#### Core Features

**FR-1.1: VC Content Ingestion**
- **Description:** Systematically crawl and index VC firm content (a16z.com)
- **Implementation:**
  ```python
  # Scrapy spider with rate limiting
  class A16ZSpider(scrapy.Spider):
      name = 'a16z'
      allowed_domains = ['a16z.com']
      download_delay = 1.0
      
      def parse(self, response):
          # Extract title, content, metadata
          yield {
              'url': response.url,
              'title': response.css('title::text').get(),
              'content': extract_article_text(response),
              'scraped_at': datetime.utcnow().isoformat()
          }
  ```
- **Acceptance Criteria:**
  - ✅ Crawl 400+ pages from a16z.com
  - ✅ Store as JSONL (append-only, reusable format)
  - ✅ Extract: blog posts, portfolio pages, team bios, investment theses
  - ✅ Preserve metadata: URL, title, timestamp, status code
  - ✅ Respect robots.txt and rate limits (1 req/sec)

**FR-1.2: Business Plan Input**
- **Description:** Accept founder business plan via text input or file upload
- **Formats Supported:** PDF, DOCX, TXT, plain text
- **Implementation:**
  ```python
  from vira.business_plan.parser import extract_text
  
  # File upload
  plan_text = extract_text(uploaded_file_path)
  
  # Text input
  plan_text = user_input_text
  
  # Extract sections
  summary = summarise_sections(plan_text)
  ```
- **Acceptance Criteria:**
  - ✅ Parse PDF with PyMuPDF (handle multi-page, complex layouts)
  - ✅ Parse DOCX with python-docx
  - ✅ Handle text input (10-50KB typical)
  - ✅ Extract company name automatically
  - ✅ Generate plan summary for retrieval (first 1500 chars)

**FR-1.3: Hybrid Retrieval System**
- **Description:** Retrieve relevant VC criteria using semantic + keyword search
- **Implementation:**
  ```python
  from vira.retrieval.hybrid import HybridRetriever
  
  retriever = HybridRetriever(
      vectorstore=chroma_db,
      bm25_weight=0.3,  # 30% keyword, 70% semantic
      top_k=6
  )
  
  docs = retriever.retrieve(
      query="AI healthcare SaaS business plan",
      filters={"organization": "a16z"}
  )
  ```
- **Acceptance Criteria:**
  - ✅ Semantic search via Chroma (cosine similarity on OpenAI embeddings)
  - ✅ Keyword search via BM25 (exact term matching)
  - ✅ Score fusion: 70% semantic + 30% keyword
  - ✅ Return top-6 most relevant chunks
  - ✅ Include source URLs and metadata

**FR-1.4: Structured Alignment Analysis**
- **Description:** Generate balanced explanation with matches and gaps
- **Output Format:**
  ```
  ALIGNMENT ANALYSIS: [Company Name] vs a16z

  HOW THIS PLAN ALIGNS:
  1. [Match 1 with evidence and source]
  2. [Match 2 with evidence and source]
  3. [Match 3 with evidence and source]
  
  HOW THIS PLAN DOESN'T ALIGN:
  1. [Gap 1 with evidence and source]
  2. [Gap 2 with evidence and source]
  3. [Gap 3 with evidence and source]
  
  SUMMARY:
  [Neutral, balanced summary without recommendation]
  ```
- **Acceptance Criteria:**
  - ✅ Minimum 3 matches and 3 gaps required
  - ✅ Each claim backed by retrieved evidence
  - ✅ Neutral tone (no bias toward fit/no-fit)
  - ✅ Length: 300-500 words total
  - ✅ Generated in <5 seconds

**FR-1.5: Source Citations**
- **Description:** Every claim must reference source URL
- **Implementation:**
  ```python
  # Citation format
  "Market focus on enterprise SaaS aligns with plan [Source: https://a16z.com/enterprise-thesis-2024/]"
  ```
- **Acceptance Criteria:**
  - ✅ All matches/gaps cite specific source URLs
  - ✅ Sources displayed as clickable links in UI
  - ✅ No hallucinated claims (all traceable to retrieved docs)

**FR-1.6: No Scoring/Classification**
- **Description:** Provide evidence, let users decide (trust-first design)
- **Rationale:** Early users don't trust AI scoring; prefer transparency
- **Acceptance Criteria:**
  - ✅ No numerical scores (e.g., "8/10 fit")
  - ✅ No binary classification ("Good Fit" / "Bad Fit")
  - ✅ Balanced presentation of matches and gaps

#### Non-Functional Requirements (Iteration 1)

- **Performance:** <5 seconds end-to-end latency
- **Cost:** <$0.05 per analysis (embeddings + LLM)
- **Accuracy:** 70%+ agreement with human analyst assessments
- **Availability:** 99% uptime (local deployment acceptable for MVP)

---

### 4.2 Iteration 2: Reflective Agent with Research ✅

**Status:** Fully implemented and operational  
**Paradigm:** Agentic AI (ReAct Pattern with LangGraph)  
**Timeline:** Weeks 3-6 (Completed November 2025)

#### Core Features

**FR-2.1: Confidence Scoring Per Claim**
- **Description:** Agent assesses evidence strength for each match/gap
- **Implementation:**
  ```python
  from vira.agents.reflection import assess_claim_confidence
  
  confidence = assess_claim_confidence(
      claim="Company focuses on enterprise SaaS",
      evidence=retrieved_docs,
      llm=ChatOpenAI(model="gpt-4o-mini")
  )
  
  # Returns: 0.0 (no evidence) to 1.0 (strong evidence)
  # Thresholds:
  # 0.8-1.0: Strong (✓✓✓) - explicit statement
  # 0.6-0.79: Medium (✓✓) - multiple signals
  # 0.4-0.59: Weak (✓) - single reference
  # 0.0-0.39: Insufficient (?) - no clear evidence
  ```
- **Acceptance Criteria:**
  - ✅ Each claim receives confidence score (0.0-1.0)
  - ✅ Confidence grades displayed in UI (✓✓✓, ✓✓, ✓, ?)
  - ✅ Overall confidence aggregated across all claims
  - ✅ Confidence correlates with human assessments (r > 0.65)

**FR-2.2: Information Gap Identification**
- **Description:** Agent identifies missing information needed to strengthen analysis
- **Implementation:**
  ```python
  from vira.agents.reflection import identify_information_gaps
  
  gaps = identify_information_gaps(
      explanation=initial_analysis,
      retrieved_docs=docs
  )
  
  # Returns: List[InformationGap]
  # Example gaps:
  # - "Team background details (CTO prior experience unclear)"
  # - "Market size validation (TAM mentioned but not sourced)"
  # - "Competitive moat specifics (patent status unclear)"
  ```
- **Gap Categories:**
  - `team_info`: Founder/team backgrounds, domain expertise
  - `market_data`: TAM/SAM, growth rates, market timing
  - `competitive_landscape`: Competitor funding, positioning
  - `vc_preferences`: VC investment patterns, stage preferences
  - `other`: General missing information
- **Acceptance Criteria:**
  - ✅ Identify 0-5 information gaps per analysis
  - ✅ Categorize gaps by type
  - ✅ Prioritize gaps (critical vs nice-to-have)
  - ✅ Only trigger research if confidence < 0.7 OR gaps identified

**FR-2.3: Autonomous Web Research**
- **Description:** Agent conducts targeted web searches to fill information gaps
- **Implementation:**
  ```python
  from vira.agents.research import WebSearchTool, conduct_research
  
  search_tool = WebSearchTool(api_key=settings.serper_api_key)
  
  research_results = conduct_research(
      information_gaps=gaps,
      company_name="TechStartup Inc",
      max_queries=5
  )
  
  # Returns: List[ResearchResult] with:
  # - query: str (search query executed)
  # - snippets: List[str] (top result snippets)
  # - sources: List[str] (source URLs)
  # - gap_addressed: str (which gap this research fills)
  ```
- **Research Strategy:**
  - **Team info** → LinkedIn searches, company website
  - **Market data** → Industry reports, market research
  - **Competitive landscape** → Crunchbase, competitor funding news
  - **VC preferences** → VC blog posts, portfolio analysis
- **Acceptance Criteria:**
  - ✅ Max 5 web searches per analysis (cost control)
  - ✅ Use Serper API for Google search results
  - ✅ Parse and extract relevant snippets (top 3 results per query)
  - ✅ Track research queries and sources for transparency
  - ✅ Research fills 40%+ of identified gaps correctly

**FR-2.4: Iterative Refinement**
- **Description:** Re-run analysis with research context, iterate up to 2 times
- **Implementation:**
  ```python
  # LangGraph workflow with conditional edges
  workflow = StateGraph(AgentState)
  
  workflow.add_node("initial_analysis", initial_analysis_node)
  workflow.add_node("reflection", reflection_node)
  workflow.add_node("research", research_node)
  workflow.add_node("regeneration", regeneration_node)
  
  workflow.add_conditional_edges(
      "reflection",
      should_research,  # confidence < 0.7 AND iterations < 2
      {True: "research", False: END}
  )
  ```
- **Iteration Control:**
  - **Iteration 1:** Initial RAG analysis → Reflection → Research (if needed) → Regenerate
  - **Iteration 2:** Reflection on regenerated analysis → Research (if still low confidence) → Final output
  - **Max iterations:** 2 (prevent infinite loops)
  - **Stop conditions:** Confidence ≥ 0.7 OR max iterations reached
- **Acceptance Criteria:**
  - ✅ Max 2 reflection loops per analysis
  - ✅ Stop early if confidence threshold met
  - ✅ Regenerated analysis incorporates research findings
  - ✅ Track iteration count in metadata

**FR-2.5: Confidence Grading Display**
- **Description:** Visual confidence indicators in UI
- **Format:**
  ```
  HOW THIS PLAN ALIGNS:
  1. ✓✓✓ Market Focus: SaaS for healthcare matches VC thesis
     [Strong evidence from investment criteria doc p.3]
  2. ✓✓ Stage Fit: Series A aligns with VC stage preference
     [Inferred from 8/10 recent portfolio deals]
  3. ✓ Technology Approach: AI/ML component mentioned
     [Single reference in plan, details sparse]
  
  HOW THIS PLAN DOESN'T ALIGN:
  1. ✓✓✓ Team Background: No healthcare domain expertise
     [Verified via LinkedIn - founders from fintech]
  2. ? Business Model: Revenue model unclear
     [Insufficient data to verify fit]
  ```
- **Acceptance Criteria:**
  - ✅ Confidence grades visible per claim (✓✓✓, ✓✓, ✓, ?)
  - ✅ Overall confidence score displayed (0-100%)
  - ✅ Legend explaining confidence levels
  - ✅ Users can interpret quality at a glance

**FR-2.6: Research Transparency**
- **Description:** Show what was researched and why
- **Display Format:**
  ```
  META-ASSESSMENT:
  Overall Confidence: 72%
  Strong Evidence: 4/6 claims
  Research Conducted:
  - "TechStartup Inc founder backgrounds LinkedIn" → Found: CEO has fintech experience
  - "Healthcare SaaS market size 2024" → Found: $45B TAM, 12% CAGR
  - "a16z healthcare investments Austin" → Found: 0 investments in Texas
  Data Gaps: Business model requires follow-up with founder
  ```
- **Acceptance Criteria:**
  - ✅ List all research queries executed
  - ✅ Show snippets of key findings
  - ✅ Cite research sources with URLs
  - ✅ Explain remaining data gaps
  - ✅ Research reduces user follow-up questions by 30%+

#### Non-Functional Requirements (Iteration 2)

- **Performance:** 15-30 seconds end-to-end (includes web searches)
- **Cost:** <$0.15 per analysis (5-10 LLM calls + search API)
- **Accuracy:** 85%+ agreement with human analyst assessments
- **Research Quality:** 40%+ of gaps correctly filled with relevant data

---

### 4.3 Iteration 3: Multi-Agent Investment Committee 📋

**Status:** Specification complete, implementation planned  
**Paradigm:** Multi-Agent Systems (Coordinated Specialist Agents)  
**Timeline:** Weeks 7-14 (Target: Q1 2026)

#### Core Features

**FR-3.1: Parallel Specialist Agents**
- **Description:** 4 specialized agents analyze different dimensions simultaneously
- **Agent Roster:**
  1. **Market Agent:** TAM/SAM analysis, competitive landscape, market timing
  2. **Product Agent:** Technology moat, defensibility, product-market fit signals
  3. **Team Agent:** Founder backgrounds, domain expertise, track record
  4. **Financial Agent:** Unit economics, business model, capital efficiency
- **Implementation Approach:**
  ```python
  from vira.agents.committee.coordinator import CoordinatorAgent
  from vira.agents.committee.specialists import (
      MarketAgent, ProductAgent, TeamAgent, FinancialAgent
  )
  
  coordinator = CoordinatorAgent()
  
  # Parallel execution
  async def analyze_committee(plan, criteria):
      tasks = [
          market_agent.analyze(plan, criteria),
          product_agent.analyze(plan, criteria),
          team_agent.analyze(plan, criteria),
          financial_agent.analyze(plan, criteria)
      ]
      return await asyncio.gather(*tasks)
  ```
- **Acceptance Criteria:**
  - 📋 4 specialist agents implemented with distinct responsibilities
  - 📋 Agents execute in parallel (20-30s total vs 60-80s sequential)
  - 📋 Each agent has specialized tools (Crunchbase, GitHub, LinkedIn, etc.)
  - 📋 Agents produce structured assessments (findings, confidence, risks)

**FR-3.2: Consensus Synthesis**
- **Description:** Identify where agents agree (consensus strengths/weaknesses)
- **Consensus Logic:**
  ```python
  def identify_consensus(assessments: List[AgentAssessment]):
      """
      Consensus levels:
      - 4/4 agents agree: Strong Consensus ✓✓✓
      - 3/4 agents agree: Majority View ✓✓
      - 2/2 split: Requires Resolution ⚠
      - No pattern: Human Judgment Needed ?
      """
      findings_by_topic = group_by_topic(assessments)
      
      for topic, findings in findings_by_topic.items():
          agreement_count = count_agreement(findings)
          if agreement_count >= 3:
              yield ConsensusItem(
                  topic=topic,
                  agreement_level=agreement_count,
                  agents=list_agreeing_agents(findings)
              )
  ```
- **Acceptance Criteria:**
  - 📋 Identify 3-5 consensus strengths (all agents agree)
  - 📋 Identify 2-3 consensus weaknesses
  - 📋 Flag disagreement areas (2-2 splits, conflicting opinions)
  - 📋 75%+ match with human investment committee assessments

**FR-3.3: Disagreement Identification**
- **Description:** Highlight where agents have conflicting views
- **Output Format:**
  ```
  DISAGREEMENT AREAS:
  • Product Defensibility:
    - Tech Agent rates "WEAK" (no IP moat)
    - Market Agent rates "MODERATE" (network effects potential)
    → Resolution depends on: network effects timeline materialization
  
  • Team Risk Tolerance:
    - Team Agent flags "no prior exits" as concern
    - Financial Agent considers founders "execution-capable"
    → Resolution depends on: VC's stage focus (seed vs growth)
  ```
- **Acceptance Criteria:**
  - 📋 Identify 1-3 disagreement areas per analysis
  - 📋 Explain nature of disagreement (different evidence, different weights)
  - 📋 Provide resolution criteria (what would settle the disagreement)
  - 📋 Flag for human review when 2-2 split

**FR-3.4: Strategic Positioning Recommendations**
- **Description:** Actionable advice for startups and VCs
- **For Startups (How to Strengthen Alignment):**
  ```
  PROACTIVE POSITIONING STRATEGY:
  
  1. EMPHASIZE: Team's 8-year industry expertise
     → Tactic: Lead pitch with customer pain points you've personally experienced
     → Addresses: Common concern about domain knowledge
  
  2. ARTICULATE: Network effects roadmap with specific milestones
     → Tactic: Show inflection points (e.g., "At 500 customers, data marketplace activates")
     → Addresses: Product defensibility gap
  
  3. DEMONSTRATE: Path to improving CAC via product-led growth
     → Tactic: Pilot PLG motion with 2-3 customers, present conversion data
     → Addresses: Unit economics concern
  ```
- **For VCs (Strategic Fit Analysis):**
  ```
  TARGET PARTNER: [Partner Name] who led similar investment in [Portfolio Company]
  COMPARABLE POSITIONING: "Similar to [Portfolio Co] but for [adjacent market]"
  
  STRATEGIC FIT:
  ✓ Compares favorably to: [Portfolio Company X] on team, timing
  ✗ Diverges from: [Portfolio Company Y] on business model
  ↔ Could complement: [Portfolio Company Z] via partnership/data sharing
  ```
- **Acceptance Criteria:**
  - 📋 3-5 specific tactics for startups to improve alignment
  - 📋 Each tactic addresses a specific gap identified by agents
  - 📋 Identify target partner match (based on portfolio analysis)
  - 📋 60%+ of recommendations used in actual VC outreach (user survey)

**FR-3.5: Benchmark Comparisons**
- **Description:** Percentile ranking vs VC portfolio and market comparables
- **Implementation:**
  ```python
  def benchmark_against_portfolio(
      company_metrics: dict,
      portfolio_companies: List[dict]
  ) -> BenchmarkReport:
      """
      Calculate percentile rankings:
      - Market size (TAM): 85th percentile
      - Team experience: 70th percentile
      - Capital efficiency: 35th percentile (concern)
      - Technology moat: 40th percentile
      """
      percentiles = {}
      for metric, value in company_metrics.items():
          portfolio_values = [c[metric] for c in portfolio_companies]
          percentile = calculate_percentile(value, portfolio_values)
          percentiles[metric] = percentile
      
      return BenchmarkReport(
          percentiles=percentiles,
          closest_comparable=find_closest_match(company_metrics, portfolio_companies)
      )
  ```
- **Acceptance Criteria:**
  - 📋 Compare across 4-6 key dimensions (market, team, product, financial)
  - 📋 Percentile ranking vs VC portfolio (e.g., "70th percentile for team experience")
  - 📋 Identify closest comparable company in portfolio
  - 📋 Visualize strengths/weaknesses relative to peers

**FR-3.6: Interactive Q&A with Agents**
- **Description:** Users can query individual agents for deeper exploration
- **Dialog Flow:**
  ```
  User: "Why do you think network effects are weak?"
  
  → Dialogue Agent routes to Product Agent
  
  Product Agent: "The business plan mentions a 'data marketplace' but doesn't 
  explain when it activates. Network effects typically require critical mass 
  (my threshold: 200-500 customers). Current traction is 5 design partners. 
  
  I'd need to see:
  1. Flywheel mechanics diagram
  2. Data liquidity timeline  
  3. Competitive moat from data network
  
  Would you like me to research similar marketplaces to benchmark?"
  ```
- **Implementation:**
  ```python
  class DialogueAgent:
      def route_query(self, user_question: str) -> str:
          """
          1. Classify question type (market/product/team/financial)
          2. Route to relevant specialist agent
          3. Agent accesses shared memory for context
          4. Generate detailed response with supporting evidence
          """
          question_type = classify_question(user_question)
          specialist = self.agents[question_type]
          return specialist.answer_question(user_question, self.shared_memory)
  ```
- **Acceptance Criteria:**
  - 📋 Route questions to correct specialist agent (90%+ accuracy)
  - 📋 Agents provide detailed, evidence-backed answers
  - 📋 Can request follow-up research from agents
  - 📋 Interactive Q&A resolves objections without human analyst

#### Supporting Features

**FR-3.7: Shared Working Memory**
- **Description:** Agents share findings and cross-reference each other's work
- **Memory Architecture:**
  - Vector memory: Embeddings of findings for semantic search
  - Key-value store: Structured data (metrics, facts)
  - Agent notes: Inter-agent messages and requests
  - Research cache: Avoid redundant searches

**FR-3.8: Coordinator Agent**
- **Description:** Orchestrates agent workflow, manages tool budgets, aggregates results
- **Responsibilities:**
  - Task planning and priority setting
  - Parallel agent dispatch
  - Tool budget allocation (20 calls total across agents)
  - Result aggregation and conflict resolution

**FR-3.9: Synthesis Agent**
- **Description:** Combines individual assessments into coherent committee view
- **Synthesis Tasks:**
  - Consensus identification
  - Disagreement mapping
  - Risk prioritization (rank by impact × confidence)
  - Final report generation

**FR-3.10: Strategy Agent**
- **Description:** Generates positioning recommendations based on synthesis
- **Strategy Tasks:**
  - Identify top 3 strengths to emphasize
  - Identify top 3 gaps to address
  - Match to portfolio companies
  - Target partner selection
  - Tactical recommendations

#### Non-Functional Requirements (Iteration 3)

- **Performance:** 20-40 seconds end-to-end (parallel execution critical)
- **Cost:** <$0.80 per analysis (20-25 total tool calls, 15+ LLM calls)
- **Accuracy:** 90%+ agreement with human investment committees
- **Agent Efficiency:** Agents complete tasks within tool budget (5 calls per agent avg)

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

| Metric | Iteration 1 | Iteration 2 | Iteration 3 |
|--------|-------------|-------------|-------------|
| **Latency (p50)** | <3s | <20s | <30s |
| **Latency (p95)** | <5s | <30s | <40s |
| **Retrieval Time** | <1s | <1s | <1s |
| **LLM Generation** | <2s | <10s (multiple calls) | <25s (parallel agents) |
| **Research Time** | N/A | <15s (5 searches) | <20s (distributed) |

### 5.2 Cost Requirements

| Component | Iteration 1 | Iteration 2 | Iteration 3 |
|-----------|-------------|-------------|-------------|
| **Embeddings** | $0.00013 | $0.00013 | $0.00013 |
| **LLM Calls** | $0.01-0.02 | $0.05-0.10 | $0.30-0.50 |
| **Web Search** | $0 | $0.05 | $0.20 |
| **Total per Query** | **<$0.05** | **<$0.15** | **<$0.80** |

**Budget Constraints:**
- MVP testing budget: $500/month
- Target: 10,000 analyses per month at scale
- Unit economics: <$0.50 COGS per analysis (80% gross margin at $2.50 price point)

### 5.3 Accuracy Requirements

**Evaluation Methodology:**
- Human expert ground truth (20-50 test cases)
- Blind comparison (AI vs analyst, no labels)
- Agreement scoring (% of matches AI vs human)

| Metric | Iteration 1 | Iteration 2 | Iteration 3 |
|--------|-------------|-------------|-------------|
| **Alignment Accuracy** | 70%+ | 85%+ | 90%+ |
| **Confidence Calibration** | N/A | r > 0.65 | r > 0.75 |
| **Research Accuracy** | N/A | 40%+ gaps filled | 60%+ gaps filled |
| **Recommendation Quality** | N/A | N/A | 60%+ used by founders |

### 5.4 Reliability Requirements

- **Availability:** 99% uptime (for MVP, local deployment acceptable)
- **Error Handling:** Graceful degradation (fall back to Iteration 1 if Iteration 2 fails)
- **Data Freshness:** VC content updated monthly (manual trigger for MVP)
- **Backup & Recovery:** Daily backups of vector DB and session database

### 5.5 Scalability Requirements

**MVP (Prototype):**
- 10-50 concurrent users
- 100-500 analyses per day
- Single instance deployment

**Production (Future):**
- 1,000+ concurrent users
- 10,000+ analyses per day
- Horizontal scaling of API and agents
- Distributed vector database (Pinecone/Weaviate)

### 5.6 Security Requirements

**MVP (Prototype):**
- ⚠️ No authentication (prototype only)
- ⚠️ No data encryption at rest
- ✅ HTTPS for API endpoints (production)
- ✅ API key rotation for external services

**Production (Future):**
- User authentication (OAuth 2.0, Auth0)
- Business plan encryption at rest (AES-256)
- GDPR/CCPA compliance
- SOC 2 Type II certification
- Rate limiting and abuse prevention

### 5.7 Usability Requirements

- **Onboarding:** First analysis in <5 minutes (upload plan → see results)
- **Learnability:** No training required; intuitive for technical founders
- **Accessibility:** WCAG 2.1 AA compliance (production)
- **Mobile Support:** Responsive design (desktop-first for MVP)

---

## 6. Success Criteria & KPIs

### 6.1 Product-Market Fit Signals

**Leading Indicators (Months 1-3):**
- 70%+ of users complete first analysis (activation rate)
- 40%+ of users return for 2nd+ analysis (retention)
- 60%+ of users rate analysis as "helpful" or "very helpful"
- 50%+ of users share results with co-founders or advisors

**Lagging Indicators (Months 4-12):**
- 30%+ of users close funding after using VIRA (correlation, not causation)
- 70%+ of funded users report VIRA influenced their VC targeting
- 50%+ of users would pay $49/month for unlimited analyses

### 6.2 Iteration-Specific Success Criteria

#### Iteration 1 Success Criteria ✅

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **User Trust** | 70%+ trust explanations enough to act | TBD | ✅ In validation |
| **Time Reduction** | 10x faster than manual research | 60 hrs → 6 hrs | ✅ Met |
| **User Preference** | 70%+ prefer explanation over scoring | TBD | ✅ In validation |
| **Retrieval Quality** | 80%+ relevant chunks retrieved | 85% | ✅ Exceeded |
| **Response Time** | <5s per analysis | 3.2s avg | ✅ Exceeded |

#### Iteration 2 Success Criteria ✅

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Gap Filling** | 40%+ of gaps correctly filled | TBD | 🔬 Testing |
| **Follow-up Reduction** | 30% fewer user questions | TBD | 🔬 Testing |
| **Confidence Calibration** | r > 0.65 with human assessment | TBD | 🔬 Testing |
| **Research Accuracy** | 60%+ of research findings relevant | TBD | 🔬 Testing |

#### Iteration 3 Success Criteria 📋

| Metric | Target | Method |
|--------|--------|--------|
| **Committee Agreement** | 75%+ match with human committees | Blind comparison (10 test cases) |
| **Recommendation Adoption** | 60%+ of recommendations used | User survey (30 days post-analysis) |
| **Interactive Resolution** | 80%+ of questions answered satisfactorily | User satisfaction survey |
| **User Preference** | 80%+ prefer multi-agent over single-agent | A/B test (Iter 2 vs Iter 3) |

### 6.3 Business KPIs (Future)

**Growth Metrics:**
- Monthly Active Users (MAU): 1,000 (Month 6), 5,000 (Month 12)
- Weekly Active Users / MAU: 40%+ (engagement)
- Analyses per User: 3-5 (indicates product value)

**Revenue Metrics (Post-MVP):**
- Freemium Conversion: 10-15% (free → paid)
- Average Revenue Per User (ARPU): $30/month
- Monthly Recurring Revenue (MRR): $50K (Month 12)
- Customer Acquisition Cost (CAC): <$100
- Lifetime Value (LTV): $500+ (LTV:CAC > 5:1)

**Retention Metrics:**
- Day 7 Retention: 40%+
- Day 30 Retention: 25%+
- Paid Churn: <5% monthly

---

## 7. Out of Scope

### 7.1 MVP Exclusions

**Explicitly NOT Included in Prototype:**

1. **Multi-VC Firm Support**
   - Scope: a16z only for MVP
   - Future: Add top 20 VCs (Sequoia, Bessemer, Accel, etc.)

2. **Authentication & Authorization**
   - Scope: No user accounts, no login required
   - Future: Auth0/OAuth, user profiles, saved sessions

3. **Direct Investment Recommendations**
   - Scope: Explanations only, no "Should you apply? Yes/No"
   - Rationale: Avoid liability, maintain trust-first design

4. **Real-time VC Content Updates**
   - Scope: Manual crawl trigger, monthly refresh
   - Future: Automated daily/weekly updates

5. **Custom Criteria Training**
   - Scope: Fixed a16z criteria
   - Future: Allow VCs to upload their own investment theses

6. **Collaborative Editing**
   - Scope: Single-user business plan editing
   - Future: Team collaboration, commenting, version control

7. **API for Integrations**
   - Scope: Web UI only
   - Future: REST API for pitch deck tools, CRMs, fundraising platforms

8. **Payment Processing**
   - Scope: Free prototype
   - Future: Stripe integration, subscription management

### 7.2 Technical Constraints

**Infrastructure Limitations (MVP):**
- Single server deployment (no horizontal scaling)
- Local file storage (no cloud object storage)
- SQLite database (no PostgreSQL/distributed DB)
- No CDN (content served directly from server)

**Data Limitations (MVP):**
- Single VC firm (a16z)
- Static corpus (~400 pages, updated manually)
- No real-time market data integration
- Limited to publicly available content

---

## 8. Technical Constraints

### 8.1 Technology Dependencies

**Required Technologies:**
- Python 3.10+ (core language)
- LangChain 0.2.14+ (RAG framework)
- LangGraph 0.2.0+ (agent orchestration, Iteration 2-3)
- OpenAI API (GPT-4o-mini, text-embedding-3-small)
- Chroma 0.5.3+ (vector database)
- FastAPI 0.115.0+ (backend API)
- Chainlit 1.0.0+ (primary UI)

**Optional Technologies:**
- React 18+ (alternative UI)
- Serper API (web search, Iteration 2-3)
- LangSmith (observability, optional)

### 8.2 External Service Constraints

**OpenAI API:**
- Rate limits: 3,000 RPM (requests per minute)
- Cost: $0.15/$0.60 per 1M tokens (input/output)
- Embedding dimensions: 1536 (text-embedding-3-small)

**Serper API (Web Search):**
- Rate limits: 1,000 searches/month (free tier)
- Cost: $2.50 per 1,000 searches (paid tier)
- Required for Iteration 2+

### 8.3 Data Constraints

**VC Content Corpus:**
- Source: a16z.com (publicly accessible pages)
- Size: ~400 pages, 50-200 MB uncompressed
- Format: JSONL (raw), Chroma (vectorized)
- Update frequency: Monthly (manual) for MVP

**Business Plan Inputs:**
- Max file size: 10 MB
- Supported formats: PDF, DOCX, TXT
- Max length: 50 pages / 100,000 characters
- Encoding: UTF-8

### 8.4 Performance Constraints

**Hardware Requirements (MVP):**
- CPU: 4+ cores (for parallel agent execution)
- RAM: 8 GB+ (vector DB loaded in memory)
- Disk: 10 GB+ (vector DB, session DB, logs)

**Network Requirements:**
- Bandwidth: 10 Mbps+ (for API calls)
- Latency: <200ms to OpenAI API
- Outbound: HTTPS (443) for OpenAI, Serper APIs

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | November 3, 2025 | VIRA Team | Initial PRD (Iteration 1 only) |
| 2.0 | November 25, 2025 | VIRA Team | Complete PRD covering all 3 iterations, implementation status, code examples |

---

## Appendix: Related Documents

- **Vision & Roadmap:** [`Vision-And-Roadmap.md`](./Vision-And-Roadmap.md)
- **System Architecture:** [`../02-ARCHITECTURE/00-System-Architecture-Overview.md`](../02-ARCHITECTURE/00-System-Architecture-Overview.md)
- **API Specifications:** [`../03-API-CONTRACTS/01-REST-API-Specification.md`](../03-API-CONTRACTS/01-REST-API-Specification.md)
- **Evaluation Framework:** [`../05-OPERATIONS/04-Evaluation-Framework.md`](../05-OPERATIONS/04-Evaluation-Framework.md)

---

**End of Document**

