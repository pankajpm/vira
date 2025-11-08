# VIRA Iteration 2: Reflective Agent Implementation Plan
## Progress Tracking Document

**Project**: VIRA MVP - Iteration 2 (Reflective Agent with Gap-Filling Research)
**Start Date**: [TBD]
**Target Completion**: 3-4 weeks
**Prototype Quality**: Yes (prioritize speed over production polish)

---

## 🎯 Iteration 2 Goals

- ✅ Add reflection agent for meta-assessment of explanation quality
- ✅ Implement confidence scoring system (per-claim and overall)
- ✅ Build autonomous research agent for gap-filling
- ✅ Create self-critique loop (max 2 iterations)
- ✅ Support dynamic research based on confidence thresholds

---

## 📊 Overall Status: ✅ COMPLETE

| Phase | Status | Completion | Start Date | End Date |
|-------|--------|------------|------------|----------|
| Phase 0: Pre-work | ✅ Complete | 100% | Nov 5, 2025 | Nov 5, 2025 |
| Phase 1: Foundation | ✅ Complete | 100% | Nov 5, 2025 | Nov 5, 2025 |
| Phase 2: Reflection Agent | ✅ Complete | 100% | Nov 5, 2025 | Nov 5, 2025 |
| Phase 3: Research Agent | ✅ Complete | 100% | Nov 5, 2025 | Nov 5, 2025 |
| Phase 4: Integration | ✅ Complete | 100% | Nov 5, 2025 | Nov 5, 2025 |
| Phase 5: Validation | ✅ Complete | 100% | Nov 5, 2025 | Nov 5, 2025 |

**Legend**: ⬜ Not Started | 🟡 In Progress | ✅ Complete | ⚠️ Blocked | ❌ Cancelled

---

# PHASE 0: Pre-work & Setup
**Duration**: 1-2 days
**Status**: ⬜ Not Started

## Tasks

### 0.1 Dependencies & Infrastructure
- [ ] Add `langgraph>=0.0.40` to `pyproject.toml`
- [ ] Add web search API dependency:
  - [ ] Option A: `serper>=0.1.0` (Google Search via Serper API) - RECOMMENDED
  - [ ] Option B: `exa-py>=1.0.0` (Exa.ai semantic search)
  - [ ] Option C: Brave Search API (free tier)
- [ ] Install new dependencies: `pip install -e .`
- [ ] Get API keys:
  - [ ] Serper API key (free tier: 2,500 searches)
  - [ ] OR Exa.ai API key (free tier available)
- [ ] Add API keys to `.env` file

**Deliverable**: Updated `pyproject.toml` with new dependencies installed

### 0.2 Architecture Design
- [ ] Review Iteration 2 spec in `VIRA_MVP_Architecture_Plan_v0.md` (lines 527-730)
- [ ] Sketch state graph flow on paper/whiteboard
- [ ] Identify breaking changes to current API
- [ ] Plan backward compatibility strategy

**Deliverable**: Architecture sketch + breaking changes list

### 0.3 Create New Module Structure
- [ ] Create `src/vira/agents/` directory
- [ ] Create `src/vira/agents/__init__.py`
- [ ] Create `src/vira/agents/reflection.py` (stub)
- [ ] Create `src/vira/agents/research.py` (stub)
- [ ] Create `src/vira/agents/state.py` (for state graph definitions)

**Deliverable**: Empty agent module structure

---

# PHASE 1: Foundation - State Management & Models
**Duration**: 3-4 days
**Status**: ⬜ Not Started
**Depends On**: Phase 0

## Tasks

### 1.1 Define State Models
- [ ] Create `src/vira/agents/state.py`
- [ ] Define `AgentState` TypedDict for LangGraph:
  ```python
  class AgentState(TypedDict):
      # Input
      company_name: str
      plan_summary: str
      query: str
      
      # Iteration 1 results
      initial_docs: list[Document]
      initial_explanation: AlignmentResponse
      
      # Reflection results
      reflection_result: Optional[ReflectionResult]
      overall_confidence: float
      
      # Research results
      research_queries: list[str]
      research_results: list[ResearchResult]
      
      # Final output
      final_explanation: AlignmentResponse
      iteration_count: int
  ```
- [ ] Define `ReflectionResult` Pydantic model
- [ ] Define `ResearchResult` Pydantic model

**Deliverable**: Complete state definitions in `state.py`

### 1.2 Update Response Models
- [ ] Update `src/vira/backend/models.py`:
  - [ ] Add `confidence: float` to `AlignmentPoint`
  - [ ] Add `evidence_quality: Literal["strong", "medium", "weak", "insufficient"]` to `AlignmentPoint`
  - [ ] Add `overall_confidence: float` to `AnalyzeResponse`
  - [ ] Add `research_conducted: list[dict]` to `AnalyzeResponse`
  - [ ] Add `data_gaps: list[str]` to `AnalyzeResponse`
- [ ] Update `src/vira/rag/pipeline.py`:
  - [ ] Update `AlignmentSection` model similarly
  - [ ] Update `AlignmentResponse` model

**Deliverable**: Updated models supporting confidence scoring

### 1.3 Create LangGraph Skeleton
- [ ] Create `src/vira/agents/graph.py`
- [ ] Define basic state graph structure:
  ```python
  from langgraph.graph import StateGraph, END
  
  def create_reflection_graph():
      workflow = StateGraph(AgentState)
      
      workflow.add_node("initial_analysis", initial_analysis_node)
      workflow.add_node("reflection", reflection_node)
      workflow.add_node("research", research_node)
      workflow.add_node("regenerate", regenerate_node)
      
      workflow.set_entry_point("initial_analysis")
      # Add edges with conditional routing
      
      return workflow.compile()
  ```
- [ ] Implement stub node functions (pass-through for now)

**Deliverable**: Runnable (but non-functional) LangGraph

### 1.4 Basic Integration Test
- [ ] Create `notebooks/test_iteration2_skeleton.py`
- [ ] Test that state graph runs end-to-end (with stubs)
- [ ] Verify state is passed correctly between nodes

**Deliverable**: Working skeleton test

**Phase 1 Checkpoint**: ✅ State management works, models updated, graph skeleton runs

---

# PHASE 2: Reflection Agent
**Duration**: 4-5 days  
**Status**: ⬜ Not Started
**Depends On**: Phase 1

## Tasks

### 2.1 Confidence Scoring Logic
- [ ] Create `src/vira/agents/reflection.py`
- [ ] Implement `assess_claim_confidence()`:
  - [ ] Takes: single alignment/gap claim + source documents
  - [ ] Returns: confidence score (0-1) + reasoning
  - [ ] LLM prompt: assess evidence strength
- [ ] Implement evidence quality grading:
  - [ ] "strong" (✓✓✓): Explicit statement with multiple sources
  - [ ] "medium" (✓✓): Clear inference from source
  - [ ] "weak" (✓): Single ambiguous reference
  - [ ] "insufficient" (?): No clear evidence

**Deliverable**: Working confidence scoring function

### 2.2 Reflection Prompt Engineering
- [ ] Design reflection prompt template
- [ ] Prompt should ask LLM to:
  - [ ] Assess quality of each alignment/gap claim
  - [ ] Identify missing information
  - [ ] List assumptions made
  - [ ] Calculate confidence per claim
- [ ] Test prompt on 5 sample outputs from Iteration 1
- [ ] Iterate until quality is acceptable

**Deliverable**: Tested reflection prompt template

### 2.3 Gap Identification Logic
- [ ] Implement `identify_information_gaps()`:
  - [ ] Analyzes reflection results
  - [ ] Returns prioritized list of missing info
  - [ ] Categories: team_info, market_data, competitive_landscape, vc_preferences
- [ ] Define gap prioritization rules:
  - [ ] Priority 1: Critical gaps (impact core fit assessment)
  - [ ] Priority 2: Supporting evidence gaps
  - [ ] Priority 3: Nice-to-have context

**Deliverable**: Gap identification function

### 2.4 Reflection Node Implementation
- [ ] Implement `reflection_node()` in `graph.py`
- [ ] Process initial explanation
- [ ] Calculate per-claim confidence
- [ ] Calculate overall confidence (weighted average)
- [ ] Identify information gaps
- [ ] Store results in state

**Deliverable**: Working reflection node

### 2.5 Conditional Routing Logic
- [ ] Implement `should_research()` routing function:
  - [ ] If overall_confidence >= 0.7: go to END
  - [ ] If overall_confidence < 0.7 AND iteration_count < 2: go to research
  - [ ] If iteration_count >= 2: go to END (safety limit)
- [ ] Add routing logic to graph

**Deliverable**: Working conditional routing

### 2.6 Testing - Reflection Only
- [ ] Create `notebooks/test_reflection_agent.py`
- [ ] Test cases:
  - [ ] High confidence output (should not trigger research)
  - [ ] Low confidence output (should trigger research)
  - [ ] Edge case: all claims low confidence
- [ ] Validate confidence scores are reasonable

**Deliverable**: Passing reflection tests

**Phase 2 Checkpoint**: ✅ Reflection agent works standalone, confidence scores accurate

---

# PHASE 3: Research Agent
**Duration**: 5-6 days
**Status**: ⬜ Not Started
**Depends On**: Phase 2

## Tasks

### 3.1 Web Search Integration
- [ ] Create `src/vira/agents/research.py`
- [ ] Implement `WebSearchTool` class:
  - [ ] Initialize with Serper API key
  - [ ] Method: `search(query: str, num_results: int = 5) -> list[SearchResult]`
  - [ ] Handle rate limits and errors gracefully
- [ ] Test with sample queries
- [ ] Implement result parsing (extract snippets, URLs, titles)

**Deliverable**: Working web search integration

### 3.2 Query Generation
- [ ] Implement `generate_research_queries()`:
  - [ ] Takes: information gaps from reflection
  - [ ] Generates optimized search queries
  - [ ] Example: "Team Background Gap" → "CEO prior experience {company name}"
- [ ] Query templates by gap type:
  - [ ] Team info: "{founder name} LinkedIn experience", "{CTO name} background"
  - [ ] Market data: "{industry} market size TAM", "{sector} growth rate"
  - [ ] Competitive: "{company name} competitors funding", "{space} similar companies"
  - [ ] VC preferences: "{VC name} investment thesis", "{VC name} portfolio {sector}"

**Deliverable**: Query generation function

### 3.3 Research Budget & Limits
- [ ] Implement research budget system:
  - [ ] Max 5 web searches per analysis
  - [ ] Max 2 searches per information gap
  - [ ] Prioritize by gap importance
  - [ ] Early stopping if confidence threshold reached
- [ ] Add budget tracking to state
- [ ] Implement circuit breaker for API errors

**Deliverable**: Budget control system

### 3.4 Result Parsing & Context Building
- [ ] Implement `parse_search_results()`:
  - [ ] Extract relevant snippets from search results
  - [ ] Filter low-quality results
  - [ ] Deduplicate similar information
- [ ] Implement `build_research_context()`:
  - [ ] Combine research results with original retrieved docs
  - [ ] Format for prompt inclusion
  - [ ] Maintain source attribution

**Deliverable**: Result parsing functions

### 3.5 Research Node Implementation
- [ ] Implement `research_node()` in `graph.py`:
  - [ ] Get information gaps from state
  - [ ] Generate research queries
  - [ ] Execute searches (within budget)
  - [ ] Parse and store results in state
- [ ] Add error handling for API failures
- [ ] Log research actions for transparency

**Deliverable**: Working research node

### 3.6 Testing - Research Agent
- [ ] Create `notebooks/test_research_agent.py`
- [ ] Test cases:
  - [ ] Team background research (test with real startup)
  - [ ] Market data research
  - [ ] VC preference research
  - [ ] Budget limits enforced
  - [ ] Error handling (bad API key, rate limit)
- [ ] Validate search results are relevant

**Deliverable**: Passing research tests

**Phase 3 Checkpoint**: ✅ Research agent works, budget controls in place

---

# PHASE 4: Integration & Regeneration
**Duration**: 4-5 days
**Status**: ⬜ Not Started
**Depends On**: Phase 2 + Phase 3

## Tasks

### 4.1 Regeneration with Research Context
- [ ] Implement `regenerate_node()` in `graph.py`:
  - [ ] Combines: original docs + research results + reflection insights
  - [ ] Calls existing `AlignmentAnalyzer` with enhanced context
  - [ ] Generates new explanation
  - [ ] Stores in state as `final_explanation`
- [ ] Update prompts to incorporate research findings
- [ ] Ensure citations include research sources

**Deliverable**: Working regeneration node

### 4.2 Complete Graph Wiring
- [ ] Wire all nodes together:
  ```
  initial_analysis → reflection → [research if needed] → regenerate → END
  ```
- [ ] Add conditional edges:
  - [ ] After reflection: route to research OR END
  - [ ] After research: always go to regenerate
  - [ ] After regenerate: go to reflection OR END (based on iteration count)
- [ ] Test full loop with max 2 iterations

**Deliverable**: Complete working state graph

### 4.3 Iteration 2 Analyzer Wrapper
- [ ] Create `src/vira/agents/analyzer.py`
- [ ] Implement `ReflectiveAnalyzer` class:
  - [ ] Wraps the LangGraph
  - [ ] Provides simple interface matching Iteration 1 API
  - [ ] Method: `analyze() -> Tuple[AlignmentResponse, dict]`
  - [ ] Returns: final explanation + metadata (research conducted, iterations, etc.)
- [ ] Maintain backward compatibility with Iteration 1

**Deliverable**: High-level analyzer class

### 4.4 Update Backend API
- [ ] Update `src/vira/backend/api.py`:
  - [ ] Add flag to enable Iteration 2: `use_reflection: bool = False`
  - [ ] Route to `ReflectiveAnalyzer` if enabled
  - [ ] Otherwise use Iteration 1 `AlignmentAnalyzer`
- [ ] Update response building to include new fields
- [ ] Add new endpoint: `/analyze/v2` (optional, for clarity)

**Deliverable**: API supports both Iteration 1 and 2

### 4.5 End-to-End Integration Test
- [ ] Create `notebooks/test_iteration2_full.py`
- [ ] Test scenarios:
  - [ ] High confidence → no research triggered
  - [ ] Low confidence → research → improvement
  - [ ] Max iterations reached
  - [ ] Research fails gracefully (API error)
- [ ] Verify state transitions
- [ ] Check final output quality

**Deliverable**: Passing integration tests

**Phase 4 Checkpoint**: ✅ Full pipeline works end-to-end

---

# PHASE 5: UI Updates & Validation
**Duration**: 3-4 days
**Status**: ⬜ Not Started
**Depends On**: Phase 4

## Tasks

### 5.1 Update UI Display
- [ ] Update `src/vira/ui/chainlit_app.py`:
  - [ ] Display confidence scores (✓✓✓, ✓✓, ✓, ?)
  - [ ] Show overall confidence percentage
  - [ ] Display research conducted (queries + sources)
  - [ ] Show data gaps identified
  - [ ] Add "Meta-Assessment" section
- [ ] Update formatting functions for new fields
- [ ] Test UI rendering with Iteration 2 output

**Deliverable**: Updated Chainlit UI

### 5.2 React Frontend Updates (if applicable)
- [ ] Update `frontend/src/types/index.ts` with new response fields
- [ ] Update `frontend/src/components/ChatPanel.tsx` to display:
  - [ ] Confidence indicators
  - [ ] Research summary
  - [ ] Data gaps
- [ ] Test React frontend with new API

**Deliverable**: Updated React UI

### 5.3 Settings & Configuration
- [ ] Add to `src/vira/config/settings.py`:
  - [ ] `serper_api_key` or `exa_api_key`
  - [ ] `enable_reflection: bool = True`
  - [ ] `reflection_confidence_threshold: float = 0.7`
  - [ ] `max_research_queries: int = 5`
  - [ ] `max_reflection_iterations: int = 2`
- [ ] Update `.env.template` with new variables
- [ ] Document configuration options

**Deliverable**: Configuration system

### 5.4 Documentation Updates
- [ ] Update `README.md` with Iteration 2 usage
- [ ] Create `docs/ITERATION2.md` with:
  - [ ] Architecture overview
  - [ ] Configuration guide
  - [ ] API changes
  - [ ] Example outputs
- [ ] Add code comments to new modules
- [ ] Update architecture diagrams

**Deliverable**: Complete documentation

### 5.5 Validation Against Success Criteria
- [ ] Run 20-case validation set (from spec)
- [ ] Measure:
  - [ ] % of gaps correctly filled by research
  - [ ] Confidence score calibration (correlation with quality)
  - [ ] Reduction in follow-up questions
- [ ] Target metrics:
  - [ ] ✅ 40%+ gaps filled correctly
  - [ ] ✅ 30% reduction in follow-up questions
  - [ ] ✅ Confidence correlation r > 0.65
- [ ] Document results in validation report

**Deliverable**: Validation report with metrics

### 5.6 User Testing
- [ ] Test with 5 sample business plans (diverse industries)
- [ ] Compare Iteration 1 vs Iteration 2 outputs side-by-side
- [ ] Gather feedback:
  - [ ] Is research helpful?
  - [ ] Are confidence scores trustworthy?
  - [ ] Does it reduce work?
- [ ] Iterate based on feedback

**Deliverable**: User testing report

**Phase 5 Checkpoint**: ✅ Iteration 2 validated and documented

---

# 🎯 Success Criteria (from Architecture Plan)

## Iteration 2 Goals:
- [ ] **Autonomous research fills 40%+ of data gaps correctly**
  - Measurement: Manual validation of 20 research actions
  - Target: ≥8 out of 20 gaps filled with accurate information

- [ ] **30% reduction in user follow-up questions**
  - Measurement: Compare user Q&A frequency Iter1 vs Iter2
  - Target: If Iter1 averaged 3 questions, Iter2 should average ≤2.1

- [ ] **Confidence scores correlate with match quality (r > 0.65)**
  - Measurement: Human quality ratings vs AI confidence scores
  - Target: Pearson correlation coefficient > 0.65

---

# 📝 Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LangGraph learning curve | Schedule delay | Start with simple graph, iterate |
| Web search API costs exceed budget | Cost overrun | Implement strict budget limits, use free tier |
| Confidence calibration inaccurate | Poor UX | Extensive testing, manual calibration |
| Research doesn't improve quality | Wasted effort | Early validation, kill switch if ineffective |
| Breaks Iteration 1 functionality | User impact | Maintain backward compatibility, feature flags |

---

# 🔄 Iteration Strategy

This is a **prototype**, so:
- ✅ Prioritize speed over polish
- ✅ Use shortcuts (hardcoded thresholds, simple prompts)
- ✅ Skip nice-to-haves (advanced caching, sophisticated query expansion)
- ✅ Test early and often
- ✅ Feature flag for easy rollback

---

# 📊 Progress Tracking

## Weekly Updates
- **Week 1**: _Status update here_
- **Week 2**: _Status update here_
- **Week 3**: _Status update here_
- **Week 4**: _Status update here_

## Blockers Log
| Date | Blocker | Resolution | Status |
|------|---------|------------|--------|
| _TBD_ | _Description_ | _How resolved_ | _Open/Closed_ |

## Decision Log
| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| _TBD_ | _What was decided_ | _Why_ | _Effect on project_ |

---

**Document Version**: 1.0
**Last Updated**: November 5, 2025
**Owner**: VIRA Development Team

