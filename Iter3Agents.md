# Iteration 3: Multi-Agent Investment Committee Architecture

This document visualizes the multi-agent architecture of VIRA's Iteration 3, which implements a full investment committee simulation with specialized agents, consensus synthesis, and proactive strategic recommendations.

## 🏗️ High-Level Architecture

```mermaid
graph TB
    subgraph "User Input"
        A[Company Name + Business Plan + VC Criteria]
    end
    
    subgraph "Iteration 3: Multi-Agent Investment Committee"
        B[Coordinator Agent]
        C[4 Specialist Agents]
        D[Synthesis Agent]
        E[Strategy Agent]
        F[Dialogue Agent]
    end
    
    subgraph "Output"
        G[Multi-Perspective Investment Report]
        H[Positioning Strategy + Benchmarks]
        I[Interactive Q&A Interface]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> G
    E --> H
    F --> I
    
    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#e8f5e9
    style E fill:#f3e5f5
    style F fill:#fff9c4
    style G fill:#c8e6c9
    style H fill:#c8e6c9
    style I fill:#c8e6c9
```

## 🔄 Multi-Agent Workflow

```mermaid
graph TB
    START([User Query]) --> COORD[Coordinator Agent<br/>Task Planning]
    
    COORD --> PARALLEL{Parallel Execution}
    
    PARALLEL --> MARKET[Market Agent]
    PARALLEL --> PRODUCT[Product Agent]
    PARALLEL --> TEAM[Team Agent]
    PARALLEL --> FINANCE[Financial Agent]
    
    MARKET --> |Market data<br/>Competition<br/>Timing| MEMORY[Shared Working Memory]
    PRODUCT --> |Tech moat<br/>Defensibility<br/>PMF signals| MEMORY
    TEAM --> |Founder exp<br/>Track record<br/>Domain expertise| MEMORY
    FINANCE --> |Unit econ<br/>Business model<br/>Capital efficiency| MEMORY
    
    MEMORY --> SYNTH[Synthesis Agent<br/>Consensus + Disagreements]
    
    SYNTH --> STRAT[Strategy Agent<br/>Positioning + Benchmarks]
    
    STRAT --> DIAL{Interactive Mode?}
    
    DIAL --> |Yes| DIALOGUE[Dialogue Agent<br/>Q&A with Agents]
    DIAL --> |No| REPORT[Final Report]
    
    DIALOGUE --> REPORT
    
    REPORT --> END([Multi-Perspective Analysis])
    
    style COORD fill:#e3f2fd
    style MARKET fill:#ffccbc
    style PRODUCT fill:#c8e6c9
    style TEAM fill:#f8bbd0
    style FINANCE fill:#fff9c4
    style MEMORY fill:#e0e0e0
    style SYNTH fill:#ce93d8
    style STRAT fill:#90caf9
    style DIALOGUE fill:#fff59d
    style REPORT fill:#81c784
```

## 🎯 Specialist Agent Details

```mermaid
graph LR
    subgraph "Market Agent"
        M1[TAM/SAM Analysis]
        M2[Competitive Landscape]
        M3[Market Timing]
        M4[Growth Trends]
        
        M1 --> MT[Market Tools]
        M2 --> MT
        M3 --> MT
        M4 --> MT
        
        MT --> MC[Crunchbase API<br/>Web Search<br/>Industry Reports]
    end
    
    subgraph "Product Agent"
        P1[Tech Stack Analysis]
        P2[Defensibility Assessment]
        P3[PMF Signals]
        P4[Innovation Score]
        
        P1 --> PT[Product Tools]
        P2 --> PT
        P3 --> PT
        P4 --> PT
        
        PT --> PC[GitHub API<br/>Patent Search<br/>Tech Blogs]
    end
    
    subgraph "Team Agent"
        T1[Founder Backgrounds]
        T2[Domain Expertise]
        T3[Prior Outcomes]
        T4[Advisory Board]
        
        T1 --> TT[Team Tools]
        T2 --> TT
        T3 --> TT
        T4 --> TT
        
        TT --> TC[LinkedIn API<br/>Crunchbase<br/>News Search]
    end
    
    subgraph "Financial Agent"
        F1[Unit Economics]
        F2[Business Model]
        F3[Capital Efficiency]
        F4[Growth Metrics]
        
        F1 --> FT[Finance Tools]
        F2 --> FT
        F3 --> FT
        F4 --> FT
        
        FT --> FC[Financial DBs<br/>Benchmark Data<br/>Model Parsers]
    end
    
    style M1 fill:#ffccbc
    style P1 fill:#c8e6c9
    style T1 fill:#f8bbd0
    style F1 fill:#fff9c4
```

## 🧠 Coordinator Agent Orchestration

```mermaid
sequenceDiagram
    participant U as User
    participant C as Coordinator Agent
    participant M as Market Agent
    participant P as Product Agent
    participant T as Team Agent
    participant F as Financial Agent
    participant SM as Shared Memory
    participant SY as Synthesis Agent
    
    U->>C: Business Plan + VC Criteria
    
    Note over C: Task Planning & Dispatch
    C->>C: Analyze complexity
    C->>C: Assign research budgets
    
    par Parallel Execution (20-30s)
        C->>M: Analyze market fit
        C->>P: Analyze product fit
        C->>T: Analyze team fit
        C->>F: Analyze financial fit
    end
    
    Note over M,F: Each agent conducts autonomous research
    
    M->>SM: Store market findings
    P->>SM: Store product findings
    T->>SM: Store team findings
    F->>SM: Store financial findings
    
    Note over SM: Cross-Agent Communication
    M->>P: "Found patent focus in competitors"
    P->>M: "Checked - no patents filed"
    
    SM->>SY: All agent perspectives
    
    Note over SY: Identify consensus + disagreements
    SY->>SY: Map strengths & risks
    SY->>SY: Prioritize findings
    
    SY-->>U: Multi-Perspective Report
```

## 📊 Shared Working Memory

```mermaid
graph TB
    subgraph "Shared Memory Architecture"
        A[Vector Memory<br/>Embeddings of findings]
        B[Key-Value Store<br/>Structured data]
        C[Agent Notes<br/>Cross-agent messages]
        D[Research Cache<br/>Avoid redundant searches]
    end
    
    subgraph "Agent Interactions"
        E[Agent 1 writes findings]
        F[Agent 2 reads context]
        G[Agent 3 requests info]
        H[Agent 4 supplements]
    end
    
    E --> A
    E --> B
    F --> A
    F --> B
    G --> C
    H --> C
    
    A --> D
    B --> D
    C --> D
    
    style A fill:#e3f2fd
    style B fill:#fff9c4
    style C fill:#c8e6c9
    style D fill:#f8bbd0
```

## 🔍 Inter-Agent Communication

```mermaid
flowchart LR
    subgraph "Communication Patterns"
        A[Request Info]
        B[Share Finding]
        C[Ask Opinion]
        D[Verify Claim]
    end
    
    subgraph "Example Flow"
        M[Market Agent:<br/>"Found 3 competitors<br/>with patents"]
        
        M --> |Request| P[Product Agent:<br/>Check our patent status]
        
        P --> |Share| M[Product Agent:<br/>0 granted, 1 provisional]
        
        M --> |Ask| F[Financial Agent:<br/>Impact on valuation?]
        
        F --> |Verify| M[Financial Agent:<br/>IP moat worth 20-30%<br/>premium typically]
    end
    
    A --> M
    B --> P
    C --> F
    
    style M fill:#ffccbc
    style P fill:#c8e6c9
    style F fill:#fff9c4
```

## 🎭 Synthesis Agent Logic

```mermaid
flowchart TD
    INPUT[4 Agent Perspectives] --> EXTRACT[Extract Assessments]
    
    EXTRACT --> CONSENSUS{Identify Consensus}
    
    CONSENSUS --> |3-4 agents agree| STRONG[Strong Consensus<br/>High confidence claims]
    CONSENSUS --> |2 agents agree| MODERATE[Moderate Consensus<br/>Medium confidence]
    CONSENSUS --> |1-1-1-1 split| DISAGREE[Disagreement Area<br/>Flag for human review]
    
    STRONG --> RISK[Risk Prioritization]
    MODERATE --> RISK
    DISAGREE --> RISK
    
    RISK --> RANK[Rank by:<br/>1. Impact<br/>2. Confidence<br/>3. Actionability]
    
    RANK --> OUTPUT[Synthesis Report:<br/>Consensus + Disagreements + Risks]
    
    style CONSENSUS fill:#fff9c4
    style STRONG fill:#4caf50
    style MODERATE fill:#ffeb3b
    style DISAGREE fill:#ff9800
    style OUTPUT fill:#e8f5e9
```

### Consensus Algorithm

```mermaid
graph TB
    subgraph "Agreement Scoring"
        A["4/4 agents agree<br/>→ Strong Consensus ✓✓✓"]
        B["3/4 agents agree<br/>→ Majority View ✓✓"]
        C["2/2 split<br/>→ Requires Resolution ⚠"]
        D["No clear pattern<br/>→ Human Judgment Needed ?"]
    end
    
    subgraph "Conflict Resolution"
        E[Check evidence strength]
        F[Weight by agent confidence]
        G[Defer to domain expert agent]
        H[Flag for user decision]
    end
    
    C --> E
    C --> F
    C --> G
    D --> H
    
    style A fill:#4caf50
    style B fill:#8bc34a
    style C fill:#ff9800
    style D fill:#f44336
```

## 💡 Strategy Agent Components

```mermaid
graph TB
    subgraph "Strategy Agent Inputs"
        A[Synthesis Report]
        B[VC Portfolio Data]
        C[Comparable Companies]
    end
    
    subgraph "Strategy Generation"
        D[Positioning for Startup]
        E[Positioning for VC]
        F[Benchmark Analysis]
        G[Risk Mitigation]
    end
    
    subgraph "Outputs"
        H[Strengths to Emphasize]
        I[Gaps to Address]
        J[Target Partner Match]
        K[Comparable Positioning]
        L[Action Items]
    end
    
    A --> D
    A --> E
    B --> E
    C --> F
    
    D --> H
    D --> I
    E --> J
    F --> K
    D --> L
    E --> L
    
    style D fill:#e3f2fd
    style E fill:#c8e6c9
    style F fill:#fff9c4
    style G fill:#ffccbc
```

### Positioning Strategy Flow

```mermaid
flowchart TD
    START[Synthesis Results] --> STRENGTH{Identify Top 3<br/>Strengths}
    
    STRENGTH --> S1[Strength 1:<br/>How to emphasize]
    STRENGTH --> S2[Strength 2:<br/>How to emphasize]
    STRENGTH --> S3[Strength 3:<br/>How to emphasize]
    
    START --> GAPS{Identify Top 3<br/>Gaps}
    
    GAPS --> G1[Gap 1:<br/>Mitigation tactic]
    GAPS --> G2[Gap 2:<br/>Mitigation tactic]
    GAPS --> G3[Gap 3:<br/>Mitigation tactic]
    
    S1 --> MATCH[Match to Portfolio<br/>Companies]
    S2 --> MATCH
    S3 --> MATCH
    
    MATCH --> PARTNER[Identify Target<br/>Partner]
    
    G1 --> ACTIONS[Prioritized<br/>Action Items]
    G2 --> ACTIONS
    G3 --> ACTIONS
    
    PARTNER --> OUTPUT[Positioning<br/>Strategy]
    ACTIONS --> OUTPUT
    
    style STRENGTH fill:#c8e6c9
    style GAPS fill:#ffccbc
    style MATCH fill:#e3f2fd
    style OUTPUT fill:#4caf50
```

## 💬 Dialogue Agent Interface

```mermaid
sequenceDiagram
    participant U as User
    participant D as Dialogue Agent
    participant R as Router
    participant A as Specialist Agent
    participant M as Memory
    
    U->>D: "Why do you think the product is weak?"
    
    D->>R: Route query to relevant agent
    R->>R: Analyze question type
    
    Note over R: Product-related → Product Agent
    
    R->>A: Forward to Product Agent
    
    A->>M: Retrieve original assessment
    A->>A: Generate detailed explanation
    
    A-->>D: "The plan mentions AI but lacks:<br/>1. Architecture details<br/>2. Data moat explanation<br/>3. Competitive differentiation"
    
    D-->>U: Formatted response with context
    
    U->>D: "What would improve the score?"
    
    D->>A: Follow-up query
    A->>A: Generate recommendations
    
    A-->>D: "3 improvements:<br/>1. File provisional patent<br/>2. Show network effects timeline<br/>3. Demonstrate data advantage"
    
    D-->>U: Actionable recommendations
```

### Query Routing Logic

```mermaid
flowchart TD
    QUERY[User Question] --> CLASSIFY{Classify Question Type}
    
    CLASSIFY --> |Market/Competition| MARKET[Route to Market Agent]
    CLASSIFY --> |Product/Tech| PRODUCT[Route to Product Agent]
    CLASSIFY --> |Team/Founders| TEAM[Route to Team Agent]
    CLASSIFY --> |Financials/Metrics| FINANCE[Route to Financial Agent]
    CLASSIFY --> |Overall/Synthesis| SYNTH[Route to Synthesis Agent]
    CLASSIFY --> |Strategy/Positioning| STRAT[Route to Strategy Agent]
    
    MARKET --> RESPOND[Generate Response]
    PRODUCT --> RESPOND
    TEAM --> RESPOND
    FINANCE --> RESPOND
    SYNTH --> RESPOND
    STRAT --> RESPOND
    
    RESPOND --> CONTEXT[Add Context<br/>from Memory]
    CONTEXT --> OUTPUT[Formatted Answer]
    
    style CLASSIFY fill:#fff9c4
    style RESPOND fill:#c8e6c9
    style OUTPUT fill:#4caf50
```

## 📈 Agent Research Workflows

### Market Agent Research Flow

```mermaid
flowchart LR
    START[Business Plan<br/>Market Section] --> Q1[Generate TAM Query]
    START --> Q2[Generate Competitor Query]
    START --> Q3[Generate Timing Query]
    
    Q1 --> |Crunchbase API| R1[Market Size Data]
    Q2 --> |Web Search| R2[Competitor List + Funding]
    Q3 --> |Google Trends| R3[Market Interest Signals]
    
    R1 --> ANALYZE[Market Analysis]
    R2 --> ANALYZE
    R3 --> ANALYZE
    
    ANALYZE --> CONF{Confidence<br/>Check}
    
    CONF --> |High >80%| DONE[Complete]
    CONF --> |Low <60%| DEEP[Deep Dive<br/>2-3 more searches]
    
    DEEP --> ANALYZE
    
    style START fill:#ffccbc
    style ANALYZE fill:#fff9c4
    style DONE fill:#4caf50
```

### Team Agent Research Flow

```mermaid
flowchart LR
    START[Business Plan<br/>Team Section] --> EXTRACT[Extract Founder Names]
    
    EXTRACT --> L1[LinkedIn Search:<br/>CEO Background]
    EXTRACT --> L2[LinkedIn Search:<br/>CTO Background]
    
    L1 --> |LinkedIn API| E1[Experience Data]
    L2 --> |LinkedIn API| E2[Experience Data]
    
    E1 --> CHECK{Domain<br/>Expertise?}
    E2 --> CHECK
    
    CHECK --> |Yes| PRIOR[Search Prior<br/>Company Outcomes]
    CHECK --> |No| FLAG[Flag as Risk]
    
    PRIOR --> |Crunchbase| OUTCOMES[Exit Data]
    
    OUTCOMES --> ASSESS[Team Assessment]
    FLAG --> ASSESS
    
    style START fill:#f8bbd0
    style CHECK fill:#fff9c4
    style ASSESS fill:#4caf50
```

## 🎯 Benchmark Comparison Engine

```mermaid
graph TB
    subgraph "Input Data"
        A[Target Company Metrics]
        B[VC Portfolio Companies]
        C[Market Comparables]
    end
    
    subgraph "Comparison Dimensions"
        D[Market Size Percentile]
        E[Team Experience Percentile]
        F[Capital Efficiency Percentile]
        G[Tech Moat Percentile]
    end
    
    subgraph "Benchmark Report"
        H[Ranking vs Portfolio]
        I[Strengths Relative to Peers]
        J[Gaps Relative to Peers]
        K[Closest Comparable Match]
    end
    
    A --> D
    A --> E
    A --> F
    A --> G
    
    B --> D
    B --> E
    B --> F
    B --> G
    
    C --> D
    C --> F
    
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> I
    H --> J
    H --> K
    
    style D fill:#e3f2fd
    style H fill:#c8e6c9
    style K fill:#4caf50
```

### Percentile Calculation

```mermaid
flowchart TD
    METRIC[Company Metric:<br/>e.g., Market Size] --> GATHER[Gather Portfolio<br/>Company Data]
    
    GATHER --> SORT[Sort in<br/>Ascending Order]
    
    SORT --> POSITION[Find Position<br/>of Target Company]
    
    POSITION --> CALC[Calculate:<br/>Percentile = Position/Total × 100]
    
    CALC --> INTERPRET{Interpret Result}
    
    INTERPRET --> |>75%| TOP[Top Quartile<br/>Strong Signal ✓✓✓]
    INTERPRET --> |50-75%| ABOVE[Above Average<br/>Positive Signal ✓✓]
    INTERPRET --> |25-50%| BELOW[Below Average<br/>Concern ⚠]
    INTERPRET --> |<25%| BOTTOM[Bottom Quartile<br/>Red Flag ✗]
    
    style CALC fill:#fff9c4
    style TOP fill:#4caf50
    style ABOVE fill:#8bc34a
    style BELOW fill:#ff9800
    style BOTTOM fill:#f44336
```

## 📊 Output Report Structure

```mermaid
classDiagram
    class InvestmentCommitteeReport {
        +str company_name
        +str vc_firm
        +List~AgentAssessment~ agent_perspectives
        +SynthesisResult synthesis
        +PositioningStrategy strategy
        +DialogueInterface dialogue
    }
    
    class AgentAssessment {
        +str agent_name
        +List~Finding~ findings
        +float overall_confidence
        +List~Risk~ risks_identified
    }
    
    class Finding {
        +str category
        +str claim
        +str evidence
        +str confidence_grade
    }
    
    class SynthesisResult {
        +List~str~ consensus_strengths
        +List~Disagreement~ disagreement_areas
        +List~PrioritizedRisk~ top_risks
    }
    
    class Disagreement {
        +str topic
        +Dict~str,str~ agent_opinions
        +str resolution_approach
    }
    
    class PositioningStrategy {
        +List~str~ startup_tactics
        +List~str~ vc_fit_analysis
        +BenchmarkData benchmarks
        +str target_partner
    }
    
    class BenchmarkData {
        +Dict~str,float~ percentiles
        +str closest_comparable
        +List~str~ portfolio_matches
    }
    
    InvestmentCommitteeReport --> "4" AgentAssessment
    InvestmentCommitteeReport --> SynthesisResult
    InvestmentCommitteeReport --> PositioningStrategy
    AgentAssessment --> "*" Finding
    SynthesisResult --> "*" Disagreement
    PositioningStrategy --> BenchmarkData
    
    style InvestmentCommitteeReport fill:#e3f2fd
    style AgentAssessment fill:#fff9c4
    style SynthesisResult fill:#ce93d8
    style PositioningStrategy fill:#90caf9
```

## ⚙️ Configuration & Control

```mermaid
graph TB
    subgraph "Configuration Settings"
        A[ENABLE_ITERATION_3<br/>true/false]
        B[MAX_TOOL_CALLS_PER_AGENT<br/>default: 5]
        C[TOTAL_TOOL_BUDGET<br/>default: 20]
        D[CONSENSUS_THRESHOLD<br/>default: 0.75]
        E[PARALLEL_EXECUTION<br/>default: true]
    end
    
    subgraph "Runtime Behavior"
        F{ENABLE_ITERATION_3?}
        F -->|true| G[Use Multi-Agent<br/>Committee System]
        F -->|false| H[Fall back to<br/>Iteration 2]
    end
    
    subgraph "Agent Control"
        I[Research Budget<br/>per Agent]
        J[Confidence<br/>Thresholds]
        K[Iteration Limits]
    end
    
    A --> F
    B --> I
    C --> I
    D --> J
    E --> G
    
    G --> I
    G --> J
    G --> K
    
    style A fill:#4caf50
    style G fill:#e3f2fd
    style I fill:#fff9c4
```

## 🔧 Implementation Files

| Component | File | Key Functions/Classes |
|-----------|------|----------------------|
| **Orchestration** | `src/vira/agents/committee/coordinator.py` | `CoordinatorAgent`, `dispatch_parallel()` |
| **Specialist Agents** | `src/vira/agents/committee/specialists.py` | `MarketAgent`, `ProductAgent`, `TeamAgent`, `FinancialAgent` |
| **Shared Memory** | `src/vira/agents/committee/memory.py` | `SharedMemory`, `store_finding()`, `retrieve_context()` |
| **Synthesis** | `src/vira/agents/committee/synthesis.py` | `SynthesisAgent`, `identify_consensus()`, `resolve_conflicts()` |
| **Strategy** | `src/vira/agents/committee/strategy.py` | `StrategyAgent`, `generate_positioning()`, `benchmark_analysis()` |
| **Dialogue** | `src/vira/agents/committee/dialogue.py` | `DialogueAgent`, `route_query()`, `interactive_qa()` |
| **State** | `src/vira/agents/committee/state.py` | `CommitteeState`, `AgentAssessment`, `SynthesisResult` |
| **API Integration** | `src/vira/backend/api.py` | `/analyze` endpoint (Iteration 3 mode) |

## 📈 Performance Characteristics

```mermaid
graph TB
    subgraph "Iteration 2: Reflective Agent"
        I2A[Query Time: ~15-30s]
        I2B[API Calls: 5-10]
        I2C[Cost: $0.05-0.15]
        I2D[Single Perspective]
    end
    
    subgraph "Iteration 3: Multi-Agent Committee"
        I3A[Query Time: ~20-40s]
        I3B[API Calls: 15-25]
        I3C[Cost: $0.30-0.80]
        I3D[4 Perspectives + Synthesis]
    end
    
    subgraph "Value Add"
        V1[Multi-dimensional Analysis]
        V2[Consensus Identification]
        V3[Strategic Recommendations]
        V4[Benchmark Comparisons]
        V5[Interactive Q&A]
        V6[Investment Committee Grade]
    end
    
    I3A --> V1
    I3B --> V2
    I3C --> V3
    I3D --> V4
    I3D --> V5
    
    V1 --> GRADE[75% Match with<br/>Human Committees]
    V2 --> GRADE
    V3 --> GRADE
    V4 --> GRADE
    V5 --> GRADE
    V6 --> GRADE
    
    style I3A fill:#fff9c4
    style I3C fill:#ffccbc
    style GRADE fill:#4caf50
    style V1 fill:#e3f2fd
```

## 🎯 Key Innovations

1. **Parallel Agent Execution**: 4 agents work simultaneously (20-30s vs 60-80s sequential)
2. **Shared Working Memory**: Cross-agent communication and context sharing
3. **Consensus Synthesis**: Automatic identification of agreement vs. disagreement
4. **Multi-Perspective Analysis**: Investment committee simulation with specialist views
5. **Strategic Positioning**: Actionable recommendations for both startups and VCs
6. **Benchmark Engine**: Percentile ranking vs. portfolio and market comparables
7. **Interactive Dialogue**: Q&A with individual agents for deeper exploration
8. **Adaptive Research**: Agents autonomously decide research depth based on confidence

## 🆚 Iteration Comparison

```mermaid
graph TB
    subgraph "Iteration 1: Basic RAG"
        I1A[Single Pass]
        I1B[No Confidence]
        I1C[No Research]
        I1D[Explanation Only]
    end
    
    subgraph "Iteration 2: Reflective Agent"
        I2A[Reflection Loop]
        I2B[Confidence Scoring]
        I2C[Gap-Filling Research]
        I2D[Enhanced Explanation]
    end
    
    subgraph "Iteration 3: Multi-Agent Committee"
        I3A[Parallel Agents]
        I3B[Consensus Synthesis]
        I3C[Strategic Positioning]
        I3D[Committee-Grade Report]
    end
    
    I1A -.Evolves to.-> I2A
    I1B -.Evolves to.-> I2B
    I1C -.Evolves to.-> I2C
    I1D -.Evolves to.-> I2D
    
    I2A -.Evolves to.-> I3A
    I2B -.Evolves to.-> I3B
    I2C -.Evolves to.-> I3C
    I2D -.Evolves to.-> I3D
    
    style I1A fill:#e0e0e0
    style I1B fill:#e0e0e0
    style I1C fill:#e0e0e0
    style I1D fill:#e0e0e0
    
    style I2A fill:#e3f2fd
    style I2B fill:#e3f2fd
    style I2C fill:#e3f2fd
    style I2D fill:#e3f2fd
    
    style I3A fill:#c8e6c9
    style I3B fill:#c8e6c9
    style I3C fill:#c8e6c9
    style I3D fill:#c8e6c9
```

---

**See also:**
- `Iter1RAG.md` - Iteration 1 RAG architecture diagrams
- `Iter2Agents.md` - Iteration 2 reflective agent diagrams
- `VIRA_MVP_Architecture_Plan_v0.md` (lines 733-1116) - Original Iteration 3 spec


