# Iteration 2: Reflective Agent Architecture

This document visualizes the multi-agent architecture of VIRA's Iteration 2, which adds reflection and autonomous research capabilities to the basic RAG pipeline.

## 🏗️ High-Level Architecture

```mermaid
graph TB
    subgraph "User Input"
        A[Company Name + Business Plan]
    end
    
    subgraph "Iteration 2: Reflective Agent System"
        B[ReflectiveAnalyzer]
        C[LangGraph Workflow]
    end
    
    subgraph "Output"
        D[Enhanced AlignmentResponse]
        E[Metadata: Confidence + Research + Gaps]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    
    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#e8f5e9
    style E fill:#e8f5e9
```

## 🔄 LangGraph Workflow

```mermaid
graph TD
    START([Entry Point]) --> INIT[Initial Analysis Node]
    
    INIT --> |Run Iteration 1 RAG| REFLECT[Reflection Node]
    
    REFLECT --> |Assess confidence<br/>Identify gaps| DECISION{Should Research?}
    
    DECISION --> |Low confidence<br/>OR gaps found<br/>AND iterations < max| RESEARCH[Research Node]
    DECISION --> |High confidence<br/>OR no gaps<br/>OR max iterations| END([End])
    
    RESEARCH --> |Web search via Serper API| REGEN[Regeneration Node]
    
    REGEN --> |Re-run analysis<br/>with research context| DECISION2{Should Research Again?}
    
    DECISION2 --> |Still low confidence<br/>AND iterations < max| REFLECT
    DECISION2 --> |Confidence improved<br/>OR max iterations| END
    
    style INIT fill:#bbdefb
    style REFLECT fill:#fff9c4
    style RESEARCH fill:#c8e6c9
    style REGEN fill:#f8bbd0
    style DECISION fill:#ffe0b2
    style DECISION2 fill:#ffe0b2
    style START fill:#e0e0e0
    style END fill:#e0e0e0
```

## 🎯 Agent Nodes Detailed

```mermaid
flowchart LR
    subgraph "Node 1: Initial Analysis"
        IA1[AlignmentAnalyzer<br/>Iteration 1 RAG]
        IA2[Retrieve VC Docs]
        IA3[Generate Initial<br/>Explanation]
        
        IA1 --> IA2
        IA2 --> IA3
    end
    
    subgraph "Node 2: Reflection"
        R1[For each claim:<br/>Assess Confidence]
        R2[Calculate<br/>Overall Confidence]
        R3[Identify<br/>Information Gaps]
        R4[Categorize Gaps]
        
        R1 --> R2
        R2 --> R3
        R3 --> R4
    end
    
    subgraph "Node 3: Research"
        RE1[Generate<br/>Search Queries]
        RE2[WebSearchTool<br/>Serper API]
        RE3[Parse Results]
        RE4[Format Snippets]
        
        RE1 --> RE2
        RE2 --> RE3
        RE3 --> RE4
    end
    
    subgraph "Node 4: Regeneration"
        RG1[Merge Research<br/>with RAG Docs]
        RG2[Re-run Analysis<br/>with Context]
        RG3[Update State]
        
        RG1 --> RG2
        RG2 --> RG3
    end
    
    IA3 --> R1
    R4 --> RE1
    RE4 --> RG1
    RG3 --> R1
    
    style IA1 fill:#e3f2fd
    style R1 fill:#fff9c4
    style RE1 fill:#c8e6c9
    style RG1 fill:#f8bbd0
```

## 🧠 Reflection Agent Components

```mermaid
graph TB
    subgraph "reflection.py Module"
        A[assess_claim_confidence]
        B[identify_information_gaps]
        C[reflect_on_explanation]
    end
    
    subgraph "Inputs"
        I1[AlignmentResponse<br/>aligns + gaps]
        I2[Retrieved Documents]
        I3[LLM: gpt-4o-mini]
    end
    
    subgraph "Outputs"
        O1[ReflectionResult]
        O2[overall_confidence: float]
        O3[information_gaps: List]
    end
    
    I1 --> C
    I2 --> C
    I3 --> A
    
    C --> A
    C --> B
    
    A --> O1
    B --> O1
    O1 --> O2
    O1 --> O3
    
    style C fill:#fff9c4
    style O1 fill:#e8f5e9
```

### Confidence Scoring

```mermaid
flowchart TD
    START[Claim + Evidence] --> LLM[LLM Evaluates<br/>Evidence Strength]
    
    LLM --> SCORE{Confidence Score}
    
    SCORE --> |0.8 - 1.0| STRONG[Strong<br/>Well-supported]
    SCORE --> |0.6 - 0.79| MEDIUM[Medium<br/>Partially supported]
    SCORE --> |0.4 - 0.59| WEAK[Weak<br/>Limited evidence]
    SCORE --> |0.0 - 0.39| INSUFF[Insufficient<br/>No clear evidence]
    
    STRONG --> AGG[Aggregate<br/>Overall Confidence]
    MEDIUM --> AGG
    WEAK --> AGG
    INSUFF --> AGG
    
    style STRONG fill:#4caf50
    style MEDIUM fill:#ffeb3b
    style WEAK fill:#ff9800
    style INSUFF fill:#f44336
    style AGG fill:#2196f3
```

### Gap Identification

```mermaid
graph TB
    subgraph "Gap Detection Logic"
        A[Scan Aligns + Gaps<br/>for Missing Info]
        B{Categorize Gap}
        
        B --> C[team_info<br/>Founder/team details]
        B --> D[market_data<br/>TAM/growth metrics]
        B --> E[competitive_landscape<br/>Competitor info]
        B --> F[vc_preferences<br/>VC criteria match]
        B --> G[other<br/>General missing data]
    end
    
    subgraph "Gap Priority"
        H[Critical: Impacts alignment]
        I[Important: Adds context]
        J[Nice-to-have: Supplementary]
    end
    
    A --> B
    C --> H
    D --> H
    E --> I
    F --> I
    G --> J
    
    style A fill:#fff9c4
    style C fill:#e3f2fd
    style D fill:#e3f2fd
    style E fill:#e3f2fd
    style F fill:#e3f2fd
    style G fill:#e3f2fd
```

## 🔍 Research Agent Components

```mermaid
graph TB
    subgraph "research.py Module"
        A[generate_research_queries]
        B[WebSearchTool.search]
        C[parse_search_results]
        D[conduct_research]
    end
    
    subgraph "Inputs"
        I1[Information Gaps]
        I2[Company Name]
        I3[Max Queries: 5]
    end
    
    subgraph "External API"
        E[Serper API<br/>Google Search]
    end
    
    subgraph "Outputs"
        O1[ResearchResult List]
        O2[query: str]
        O3[snippets: List]
        O4[sources: List]
    end
    
    I1 --> D
    I2 --> D
    I3 --> D
    
    D --> A
    A --> B
    B --> E
    E --> B
    B --> C
    C --> O1
    
    O1 --> O2
    O1 --> O3
    O1 --> O4
    
    style D fill:#c8e6c9
    style B fill:#81c784
    style E fill:#ffcc80
    style O1 fill:#e8f5e9
```

### Query Generation Strategy

```mermaid
flowchart TD
    GAP[Information Gap] --> CAT{Gap Category}
    
    CAT --> |team_info| T1["CEO founder background LinkedIn"]
    CAT --> |team_info| T2["founding team experience"]
    
    CAT --> |market_data| M1["target market size TAM"]
    CAT --> |market_data| M2["industry market growth rate"]
    
    CAT --> |competitive| C1["competitors funding"]
    CAT --> |competitive| C2["similar companies space"]
    
    CAT --> |vc_preferences| V1["a16z investment thesis"]
    CAT --> |vc_preferences| V2["venture capital criteria"]
    
    T1 --> DEDUP[Remove Duplicates]
    T2 --> DEDUP
    M1 --> DEDUP
    M2 --> DEDUP
    C1 --> DEDUP
    C2 --> DEDUP
    V1 --> DEDUP
    V2 --> DEDUP
    
    DEDUP --> LIMIT[Limit to<br/>MAX_QUERIES]
    LIMIT --> OUT[Query List]
    
    style CAT fill:#fff9c4
    style DEDUP fill:#e3f2fd
    style OUT fill:#c8e6c9
```

## 📊 State Management

```mermaid
classDiagram
    class AgentState {
        +str company_name
        +str plan_summary
        +str query
        +list~Document~ initial_docs
        +AlignmentResponse initial_explanation
        +ReflectionResult reflection_result
        +float overall_confidence
        +list~str~ research_queries
        +list~ResearchResult~ research_results
        +AlignmentResponse final_explanation
        +int iteration_count
        +str error
    }
    
    class ReflectionResult {
        +float overall_confidence
        +str confidence_grade
        +dict confidence_by_claim
        +list~InformationGap~ information_gaps
        +str reasoning
    }
    
    class InformationGap {
        +str description
        +str category
        +str related_claim
    }
    
    class ResearchResult {
        +str query
        +list~str~ snippets
        +list~str~ sources
        +str gap_addressed
    }
    
    AgentState --> ReflectionResult
    AgentState --> ResearchResult
    ReflectionResult --> InformationGap
    
    style AgentState fill:#e3f2fd
    style ReflectionResult fill:#fff9c4
    style InformationGap fill:#ffe0b2
    style ResearchResult fill:#c8e6c9
```

## 🔁 Iteration Loop

```mermaid
sequenceDiagram
    participant U as User
    participant A as ReflectiveAnalyzer
    participant G as LangGraph
    participant R as Reflection Agent
    participant S as Research Agent
    
    U->>A: analyze(company, plan, query)
    A->>G: invoke(initial_state)
    
    Note over G: Iteration 1
    G->>G: initial_analysis_node
    G->>R: reflection_node
    R-->>G: confidence=0.45, gaps=3
    
    Note over G: should_research() = True
    G->>S: research_node
    S-->>G: 3 research results
    
    G->>G: regenerate_node
    
    Note over G: Iteration 2
    G->>R: reflection_node (again)
    R-->>G: confidence=0.72, gaps=1
    
    Note over G: should_research() = False
    G-->>A: final_state
    A-->>U: (result, metadata)
    
    Note over U: Display enhanced analysis<br/>with confidence + research
```

## 🎛️ Configuration

```mermaid
graph LR
    subgraph "Environment Variables"
        A[ENABLE_REFLECTION<br/>true/false]
        B[REFLECTION_CONFIDENCE_THRESHOLD<br/>default: 0.7]
        C[MAX_RESEARCH_QUERIES<br/>default: 5]
        D[MAX_REFLECTION_ITERATIONS<br/>default: 2]
        E[SERPER_API_KEY<br/>required for research]
    end
    
    subgraph "Runtime Behavior"
        F{ENABLE_REFLECTION?}
        F -->|true| G[Use Iteration 2<br/>ReflectiveAnalyzer]
        F -->|false| H[Use Iteration 1<br/>AlignmentAnalyzer]
    end
    
    A --> F
    B --> G
    C --> G
    D --> G
    E --> G
    
    style A fill:#4caf50
    style G fill:#e3f2fd
    style H fill:#ffecb3
```

## 📈 Performance Characteristics

```mermaid
graph TB
    subgraph "Iteration 1: Basic RAG"
        I1A[Query Time: ~3-5s]
        I1B[API Calls: 1-2]
        I1C[Cost: $0.01-0.02]
    end
    
    subgraph "Iteration 2: Reflective Agent"
        I2A[Query Time: ~15-30s]
        I2B[API Calls: 5-10+]
        I2C[Cost: $0.05-0.15]
    end
    
    subgraph "Trade-offs"
        T1[Higher Latency]
        T2[More API Costs]
        T3[Better Accuracy]
        T4[Confidence Scores]
        T5[Gap Identification]
        T6[Autonomous Research]
    end
    
    I2A --> T1
    I2B --> T2
    I2C --> T2
    
    T3 --> VALUE[Higher Value Output]
    T4 --> VALUE
    T5 --> VALUE
    T6 --> VALUE
    
    style I1A fill:#e8f5e9
    style I2A fill:#fff9c4
    style VALUE fill:#4caf50
    style T1 fill:#ffccbc
    style T2 fill:#ffccbc
```

## 🔧 Implementation Files

| Component | File | Key Functions/Classes |
|-----------|------|----------------------|
| **Orchestration** | `src/vira/agents/graph.py` | `create_reflection_graph()`, `should_research()` |
| **State** | `src/vira/agents/state.py` | `AgentState`, `ReflectionResult`, `ResearchResult` |
| **Reflection** | `src/vira/agents/reflection.py` | `assess_claim_confidence()`, `identify_information_gaps()` |
| **Research** | `src/vira/agents/research.py` | `WebSearchTool`, `conduct_research()` |
| **Analyzer** | `src/vira/agents/analyzer.py` | `ReflectiveAnalyzer` |
| **API Integration** | `src/vira/backend/api.py` | `/analyze` endpoint (Iteration 2 mode) |
| **UI Integration** | `src/vira/backend/ui_routes.py` | `/api/sessions/{id}/analyze` |

## 🎯 Key Innovations

1. **Meta-Assessment**: Agent evaluates its own output quality
2. **Adaptive Retrieval**: Automatically identifies when more information is needed
3. **Autonomous Research**: Conducts external searches to fill gaps
4. **Confidence Quantification**: Provides numerical confidence scores
5. **Iterative Refinement**: Loops until confidence threshold met or max iterations
6. **Transparent Reasoning**: Shows research queries and gaps in UI

---

**See also:**
- `VIRA_MVP_Architecture_Plan_v0.md` (lines 527-730) - Original Iteration 2 spec
- `ITERATION2_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `ITERATION2_QUICKSTART.md` - Usage guide

