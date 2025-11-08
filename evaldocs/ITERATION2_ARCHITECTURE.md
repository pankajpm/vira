# Iteration 2: Reflective Agent Architecture

## Overview

Iteration 2 adds a reflective agent system on top of the Iteration 1 RAG pipeline. The system uses LangGraph to orchestrate a multi-step workflow with reflection, research, and regeneration capabilities.

## System Flow

```
User Input (Business Plan)
         ↓
[Initial Analysis Node]
  - Uses Iteration 1 RAG pipeline
  - Generates initial alignment explanation
         ↓
[Reflection Node]
  - Assesses confidence in each claim
  - Identifies information gaps
  - Calculates overall confidence score
         ↓
    Confidence >= 0.7? ──Yes──> [END]
         │
         No
         ↓
[Research Node]
  - Generates search queries from gaps
  - Executes web searches (max 5)
  - Parses and structures results
         ↓
[Regenerate Node]
  - Combines: original docs + research results
  - Generates improved explanation
  - Updates confidence scores
         ↓
    Iteration < 2? ──Yes──> [Reflection Node]
         │
         No
         ↓
      [END]
```

## State Management

The system uses LangGraph's state graph with the following state structure:

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
    reflection_result: ReflectionResult
    overall_confidence: float
    
    # Research results
    research_queries: list[str]
    research_results: list[ResearchResult]
    
    # Final output
    final_explanation: AlignmentResponse
    iteration_count: int
```

## Key Components

### 1. Reflection Agent (`agents/reflection.py`)
- **Purpose**: Meta-assessment of explanation quality
- **Functions**:
  - `assess_claim_confidence()`: Score individual claims (0-1)
  - `identify_information_gaps()`: Find missing information
  - `reflect_on_explanation()`: Main orchestration
- **Output**: `ReflectionResult` with confidence scores and gaps

### 2. Research Agent (`agents/research.py`)
- **Purpose**: Autonomous gap-filling via web search
- **Functions**:
  - `WebSearchTool`: Serper API integration
  - `generate_research_queries()`: Query generation from gaps
  - `parse_search_results()`: Result parsing
  - `conduct_research()`: Main orchestration
- **Output**: `list[ResearchResult]` with findings
- **Budget**: Max 5 searches per analysis

### 3. State Definitions (`agents/state.py`)
- **Purpose**: Type-safe state for LangGraph
- **Models**:
  - `AgentState`: Main state TypedDict
  - `ReflectionResult`: Reflection outputs
  - `InformationGap`: Gap representation
  - `ResearchResult`: Research findings

### 4. Graph Orchestration (`agents/graph.py`)
- **Purpose**: Wire nodes together with conditional routing
- **Nodes**:
  - `initial_analysis_node`: Iteration 1 pipeline
  - `reflection_node`: Confidence assessment
  - `research_node`: Gap-filling
  - `regenerate_node`: Improved explanation
- **Routing**: Conditional based on confidence threshold

## Confidence Scoring

Evidence quality grades:
- **0.8-1.0 (Strong ✓✓✓)**: Explicit statement with multiple sources
- **0.6-0.8 (Medium ✓✓)**: Clear inference from source
- **0.4-0.6 (Weak ✓)**: Single ambiguous reference
- **0.0-0.4 (Insufficient ?)**: No clear evidence

## Information Gap Categories

1. **team_info**: Founder/team background, experience
2. **market_data**: TAM, growth rates, market dynamics
3. **competitive_landscape**: Competitors, funding, positioning
4. **vc_preferences**: Investment thesis, portfolio patterns

## Research Budget Control

- Max 5 web searches per analysis
- Max 2 searches per information gap
- Prioritize by gap importance (1=critical, 2=supporting, 3=nice-to-have)
- Early stopping if confidence threshold reached

## Backward Compatibility

Iteration 2 is opt-in via configuration:
- `ENABLE_REFLECTION=false` (default): Uses Iteration 1 pipeline
- `ENABLE_REFLECTION=true`: Uses reflective agent system

API supports both:
- `/analyze` endpoint: Routes based on `ENABLE_REFLECTION` flag
- `/analyze/v2` endpoint (optional): Explicitly uses Iteration 2

## Configuration

New environment variables:
```bash
# Research API
SERPER_API_KEY=your_key_here

# Reflection settings
ENABLE_REFLECTION=false
REFLECTION_CONFIDENCE_THRESHOLD=0.7
MAX_RESEARCH_QUERIES=5
MAX_REFLECTION_ITERATIONS=2
```

## Success Metrics

Target validation criteria:
1. **40%+ gaps filled correctly** by research
2. **30% reduction** in user follow-up questions
3. **Confidence correlation r > 0.65** with human quality ratings

## Implementation Status

- [x] Phase 0: Dependencies and module structure
- [ ] Phase 1: State management and models
- [ ] Phase 2: Reflection agent
- [ ] Phase 3: Research agent
- [ ] Phase 4: Integration and graph wiring
- [ ] Phase 5: UI updates and validation

## Breaking Changes

None expected - Iteration 2 is additive and backward compatible.

New response fields:
- `overall_confidence: float`
- `research_conducted: list[dict]`
- `data_gaps: list[str]`

Old clients can ignore these fields.

---

**Document Version**: 1.0  
**Last Updated**: November 5, 2025

