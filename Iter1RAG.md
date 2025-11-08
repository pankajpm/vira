# Iteration 1: RAG Pipeline Architecture

This document visualizes VIRA's Iteration 1 architecture, which implements a basic RAG (Retrieval-Augmented Generation) pipeline with hybrid retrieval and document classification for VC-business plan alignment analysis.

## 🏗️ High-Level Architecture

```mermaid
graph TB
    subgraph "User Input"
        A[Company Name + Business Plan]
    end
    
    subgraph "Iteration 1: RAG Pipeline"
        B[AlignmentAnalyzer]
        C[Hybrid Retriever]
        D[Document Classifier]
        E[LLM Chain]
    end
    
    subgraph "Knowledge Base"
        F[ChromaDB Vectorstore]
        G[VC Criteria Embeddings]
    end
    
    subgraph "Output"
        H[AlignmentResponse]
        I[Aligns + Gaps + Summary]
    end
    
    A --> B
    B --> C
    C --> F
    F --> C
    C --> D
    D --> E
    E --> H
    E --> I
    
    F <--> G
    
    style B fill:#e3f2fd
    style C fill:#fff9c4
    style D fill:#c8e6c9
    style E fill:#f8bbd0
    style F fill:#ffe0b2
    style H fill:#e8f5e9
```

## 🔄 End-to-End Pipeline Flow

```mermaid
flowchart TD
    START([User Query]) --> PREP[Prepare Query<br/>Extract company name<br/>Truncate plan to 1500 chars]
    
    PREP --> RETRIEVE[Hybrid Retrieval<br/>Semantic + BM25]
    
    RETRIEVE --> CLASSIFY[Document Classification<br/>Alignment / Gap / Neutral]
    
    CLASSIFY --> FORMAT[Format Contexts<br/>Separate alignment & gap evidence]
    
    FORMAT --> GENERATE[LLM Generation<br/>Structured JSON Output]
    
    GENERATE --> PARSE[Parse Response<br/>AlignmentResponse model]
    
    PARSE --> RETURN([Return:<br/>AlignmentResponse + Retrieved Docs])
    
    style RETRIEVE fill:#fff9c4
    style CLASSIFY fill:#c8e6c9
    style GENERATE fill:#f8bbd0
    style RETURN fill:#4caf50
```

## 🔍 Hybrid Retrieval Deep Dive

```mermaid
graph TB
    subgraph "Hybrid Retriever (70/30 weight)"
        A[Query String]
    end
    
    subgraph "Semantic Search (70%)"
        B[OpenAI Embeddings<br/>text-embedding-3-small]
        C[ChromaDB<br/>Vector Similarity]
        D[Top-K=6 Results]
    end
    
    subgraph "Keyword Search (30%)"
        E[BM25 Retriever<br/>TF-IDF based]
        F[Top-K=8 Results]
    end
    
    subgraph "Fusion & Ranking"
        G[Score Combination<br/>Weighted by position]
        H[Deduplication]
        I[Final Ranked Results]
    end
    
    A --> B
    A --> E
    
    B --> C
    C --> D
    
    E --> F
    
    D --> G
    F --> G
    
    G --> H
    H --> I
    
    style B fill:#e3f2fd
    style E fill:#e3f2fd
    style G fill:#fff9c4
    style I fill:#4caf50
```

### Scoring Algorithm

```mermaid
flowchart LR
    subgraph "Semantic Results"
        S1["Rank 1: Score = 1.0 × 0.7"]
        S2["Rank 2: Score = 0.83 × 0.7"]
        S3["Rank 3: Score = 0.67 × 0.7"]
    end
    
    subgraph "Keyword Results"
        K1["Rank 1: Score = 1.0 × 0.3"]
        K2["Rank 2: Score = 0.88 × 0.3"]
        K3["Rank 3: Score = 0.75 × 0.3"]
    end
    
    subgraph "Combined Scores"
        C[Aggregate by<br/>Document Content]
        R[Sort Descending]
        T[Top-N Results]
    end
    
    S1 --> C
    S2 --> C
    S3 --> C
    K1 --> C
    K2 --> C
    K3 --> C
    
    C --> R
    R --> T
    
    style C fill:#fff9c4
    style T fill:#4caf50
```

**Position-Based Scoring Formula:**
```
score(position, total) = 1 - (position / max(total, 1))
final_score = (semantic_score × 0.7) + (keyword_score × 0.3)
```

## 📋 Document Classification

```mermaid
flowchart TD
    DOCS[Retrieved Documents] --> LOOP{For each document}
    
    LOOP --> CLASSIFY[classify_chunk]
    
    CLASSIFY --> LLM[LLM Classification<br/>gpt-4o-mini<br/>temp=0.0]
    
    LLM --> PROMPT["Prompt:<br/>- VC chunk content<br/>- Business plan summary<br/>- Classify: alignment/gap/neutral"]
    
    PROMPT --> DECISION{Category?}
    
    DECISION --> |Supports alignment| ALIGN[Alignment Bucket]
    DECISION --> |Highlights gap| GAP[Gap Bucket]
    DECISION --> |Neither| NEUTRAL[Neutral Bucket]
    
    LOOP --> MORE{More docs?}
    MORE --> |Yes| LOOP
    MORE --> |No| RESULT[Classified Documents<br/>Dict]
    
    ALIGN --> RESULT
    GAP --> RESULT
    NEUTRAL --> RESULT
    
    style CLASSIFY fill:#c8e6c9
    style LLM fill:#81c784
    style RESULT fill:#4caf50
```

### Classification Prompt Logic

```mermaid
graph TB
    subgraph "Input to Classifier"
        A[VC Chunk:<br/>Criteria/Portfolio info]
        B[Business Plan:<br/>Company strategy]
    end
    
    subgraph "Classification Rules"
        C{Does chunk contain<br/>criteria the plan<br/>satisfies?}
        D{Does chunk contain<br/>criteria the plan<br/>lacks?}
        E{Is chunk<br/>ambiguous or<br/>general?}
    end
    
    subgraph "Output Categories"
        F[alignment<br/>Evidence supporting fit]
        G[gap<br/>Evidence of missing elements]
        H[neutral<br/>Not directly relevant]
    end
    
    A --> C
    B --> C
    A --> D
    B --> D
    A --> E
    B --> E
    
    C --> |Yes| F
    D --> |Yes| G
    E --> |Yes| H
    
    style C fill:#fff9c4
    style D fill:#fff9c4
    style E fill:#fff9c4
    style F fill:#c8e6c9
    style G fill:#ffab91
    style H fill:#e0e0e0
```

## 🎯 LLM Generation Chain

```mermaid
sequenceDiagram
    participant C as Caller (API/UI)
    participant A as AlignmentAnalyzer
    participant R as HybridRetriever
    participant D as Classifier
    participant L as LLM Chain
    
    C->>A: analyze(company, plan, query)
    
    Note over A: Step 1: Retrieval
    A->>R: get_relevant_documents(query)
    R-->>A: docs (12-14 chunks)
    
    Note over A: Step 2: Classification
    A->>D: classify_documents(docs, plan)
    loop For each doc
        D->>D: classify_chunk (LLM call)
    end
    D-->>A: classified = {alignment, gap, neutral}
    
    Note over A: Step 3: Context Formatting
    A->>A: _format_context(alignment_docs)
    A->>A: _format_context(gap_docs)
    
    Note over A: Step 4: Generation
    A->>L: invoke({alignment_context, gap_context, plan})
    L->>L: ChatPromptTemplate
    L->>L: LLM (gpt-4o-mini)
    L->>L: JsonOutputParser
    L-->>A: AlignmentResponse (structured)
    
    A-->>C: (AlignmentResponse, retrieved_docs)
```

## 📝 Prompt Engineering

```mermaid
graph TB
    subgraph "Prompt Template (Classified Evidence)"
        A[EVIDENCE SUPPORTING ALIGNMENT:<br/>alignment_context]
        B[EVIDENCE HIGHLIGHTING GAPS:<br/>gap_context]
        C[BUSINESS PLAN:<br/>company_name + plan_summary]
    end
    
    subgraph "Instructions"
        D[1. For ALIGNMENT:<br/>Use ONLY alignment evidence]
        E[2. For GAPS:<br/>Use ONLY gap evidence]
        F[3. Format: VC Criterion | Business Plan | Connection]
        G[4. NEVER cross-cite evidence]
    end
    
    subgraph "Output Structure (JSON)"
        H["aligns: [title, explanation, sources]"]
        I["gaps: [title, explanation, sources]"]
        J["summary: overall assessment"]
    end
    
    A --> D
    B --> E
    C --> F
    
    D --> H
    E --> I
    F --> J
    G --> H
    G --> I
    
    style A fill:#c8e6c9
    style B fill:#ffab91
    style C fill:#e3f2fd
    style H fill:#4caf50
    style I fill:#ff9800
```

### Output Format Example

```mermaid
classDiagram
    class AlignmentResponse {
        +str company_name
        +list~AlignmentSection~ aligns
        +list~AlignmentSection~ gaps
        +str summary
    }
    
    class AlignmentSection {
        +str title
        +str explanation
        +list~str~ sources
    }
    
    AlignmentResponse --> "0..*" AlignmentSection : aligns
    AlignmentResponse --> "0..*" AlignmentSection : gaps
    
    style AlignmentResponse fill:#e3f2fd
    style AlignmentSection fill:#fff9c4
```

**Explanation Format:**
```
VC Criterion: '[exact quote from VC source]' | 
Business Plan: '[exact quote from plan]' | 
Connection: [how they align or don't align]
```

## 🗄️ Vectorstore Architecture

```mermaid
graph TB
    subgraph "Data Ingestion (Offline)"
        A[Raw VC Data<br/>a16z_raw.jsonl]
        B[Text Extraction<br/>url, content, metadata]
        C[Chunking<br/>512 tokens with overlap]
        D[Embedding<br/>OpenAI text-embedding-3-small]
    end
    
    subgraph "ChromaDB Storage"
        E[Vector Index<br/>HNSW algorithm]
        F[Metadata Store<br/>url, source_type]
        G[Document Store<br/>Original text chunks]
    end
    
    subgraph "Query Time (Online)"
        H[Query Embedding]
        I[Similarity Search<br/>Cosine distance]
        J[Retrieved Chunks]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
    
    H --> I
    E --> I
    I --> J
    F --> J
    G --> J
    
    style C fill:#fff9c4
    style D fill:#e3f2fd
    style E fill:#ffe0b2
    style I fill:#c8e6c9
```

### Chunking Strategy

```mermaid
flowchart LR
    DOC[Long Document<br/>5000 tokens] --> SPLIT[RecursiveCharacterTextSplitter]
    
    SPLIT --> C1[Chunk 1<br/>0-512 tokens]
    SPLIT --> C2[Chunk 2<br/>256-768 tokens]
    SPLIT --> C3[Chunk 3<br/>512-1024 tokens]
    
    C1 --> EMBED[Embed Each Chunk]
    C2 --> EMBED
    C3 --> EMBED
    
    EMBED --> STORE[Store in ChromaDB]
    
    style SPLIT fill:#fff9c4
    style EMBED fill:#e3f2fd
    style STORE fill:#ffe0b2
```

**Chunking Parameters:**
- **Chunk size**: 512 tokens
- **Overlap**: 256 tokens (50%)
- **Rationale**: Balance between context and granularity

## ⚙️ AlignmentAnalyzer Class

```mermaid
classDiagram
    class AlignmentAnalyzer {
        +str model_name
        +bool use_classification
        +Settings settings
        +Chroma vectorstore
        +HybridRetriever retriever
        +LLMChain chain
        +ChatOpenAI classifier_llm
        
        +analyze(company_name, plan_summary, query) tuple
        -_retrieve_with_classification() tuple
        -_format_context(documents) str
    }
    
    class HybridRetriever {
        +Chroma vectorstore
        +int k
        +int bm25_k
        +float weight
        +BM25Retriever keyword_retriever
        +VectorStoreRetriever semantic_retriever
        
        +get_relevant_documents(query) List~Document~
        -_score(position, total) float
    }
    
    class ChromaVectorStore {
        +str collection_name
        +OpenAIEmbeddings embeddings
        
        +similarity_search(query, k) List~Document~
        +add_documents(documents) void
    }
    
    AlignmentAnalyzer --> HybridRetriever : uses
    HybridRetriever --> ChromaVectorStore : queries
    HybridRetriever --> BM25Retriever : combines_with
    
    style AlignmentAnalyzer fill:#e3f2fd
    style HybridRetriever fill:#fff9c4
    style ChromaVectorStore fill:#ffe0b2
```

## 🔁 Analyze Method Flow

```mermaid
flowchart TD
    START[analyze method called] --> CHECK{use_classification?}
    
    CHECK --> |True| RETRIEVE_CLASS[_retrieve_with_classification]
    CHECK --> |False| RETRIEVE_SIMPLE[Simple retrieval<br/>No classification]
    
    RETRIEVE_CLASS --> DOCS[Retrieved + Classified Docs]
    RETRIEVE_SIMPLE --> DOCS
    
    DOCS --> FORMAT_A[Format alignment context]
    DOCS --> FORMAT_G[Format gap context]
    
    FORMAT_A --> CHAIN_INPUT[Prepare chain input]
    FORMAT_G --> CHAIN_INPUT
    
    CHAIN_INPUT --> INVOKE[chain.invoke]
    
    INVOKE --> PARSE[JsonOutputParser]
    
    PARSE --> RESPONSE[AlignmentResponse object]
    
    RESPONSE --> RETURN[Return: result, docs]
    
    style RETRIEVE_CLASS fill:#c8e6c9
    style FORMAT_A fill:#c8e6c9
    style FORMAT_G fill:#ffab91
    style RESPONSE fill:#4caf50
```

### Adaptive Retrieval Logic

```mermaid
flowchart TD
    START[Start Retrieval] --> ATTEMPT1[Attempt 1:<br/>Retrieve initial docs]
    
    ATTEMPT1 --> CLASSIFY1[Classify docs]
    
    CLASSIFY1 --> CHECK{Enough evidence?<br/>min_alignment ≥ 2<br/>min_gap ≥ 2}
    
    CHECK --> |Yes| DONE[Return docs]
    CHECK --> |No| ATTEMPT2{More attempts left?}
    
    ATTEMPT2 --> |Yes| EXPAND[Expand query<br/>Retrieve more]
    ATTEMPT2 --> |No| DONE_PARTIAL[Return what we have]
    
    EXPAND --> CLASSIFY2[Classify new docs]
    CLASSIFY2 --> CHECK
    
    DONE_PARTIAL --> DONE
    
    style CLASSIFY1 fill:#c8e6c9
    style CHECK fill:#fff9c4
    style DONE fill:#4caf50
```

**Note**: In the prototype, we accept results after the first attempt. Production could implement multi-attempt retrieval.

## 🎛️ Configuration

```mermaid
graph TB
    subgraph "Environment Variables"
        A[OPENAI_API_KEY<br/>Required for embeddings + LLM]
        B[CHROMA_PATH<br/>./data/vectorstore_chroma]
        C[MODEL_NAME<br/>gpt-4o-mini]
    end
    
    subgraph "Runtime Settings"
        D[Hybrid Retrieval<br/>k=6, bm25_k=8, weight=0.7]
        E[Classification<br/>enabled by default]
        F[LLM Temperature<br/>gen=0.7, classify=0.0]
    end
    
    subgraph "AlignmentAnalyzer Initialization"
        G[Load Vectorstore]
        H[Initialize HybridRetriever]
        I[Build LLM Chain]
    end
    
    A --> G
    B --> G
    C --> I
    
    D --> H
    E --> I
    F --> I
    
    G --> H
    H --> I
    
    style A fill:#4caf50
    style G fill:#e3f2fd
    style H fill:#fff9c4
    style I fill:#f8bbd0
```

## 📊 Data Flow Example

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI Endpoint
    participant AA as AlignmentAnalyzer
    participant HR as HybridRetriever
    participant VS as ChromaDB
    participant CL as Classifier
    participant LLM as OpenAI GPT-4o-mini
    
    U->>API: POST /analyze<br/>{company, plan_text}
    API->>API: Extract query (first 1500 chars)
    
    API->>AA: analyze(company, plan, query)
    
    Note over AA: Phase 1: Retrieval
    AA->>HR: get_relevant_documents(query)
    HR->>VS: semantic_search(query, k=6)
    VS-->>HR: 6 vector results
    HR->>HR: bm25_search(query, k=8)
    HR->>HR: merge + rank by weighted scores
    HR-->>AA: 12-14 combined docs
    
    Note over AA: Phase 2: Classification
    loop For each doc
        AA->>CL: classify_chunk(doc, plan)
        CL->>LLM: "Is this alignment/gap/neutral?"
        LLM-->>CL: category
        CL-->>AA: category
    end
    
    Note over AA: Phase 3: Generation
    AA->>AA: Format contexts (alignment + gap)
    AA->>LLM: Generate structured analysis
    LLM-->>AA: JSON response
    AA->>AA: Parse to AlignmentResponse
    
    AA-->>API: (AlignmentResponse, docs)
    API-->>U: JSON response with aligns/gaps/summary
```

## 📈 Performance Characteristics

```mermaid
graph TB
    subgraph "Latency Breakdown"
        A[Total: 3-5 seconds]
        B[Retrieval: 0.5-1s]
        C[Classification: 1-2s]
        D[Generation: 1-2s]
    end
    
    subgraph "API Calls"
        E[Embeddings: 1 call]
        F[Classification LLM: 12-14 calls]
        G[Generation LLM: 1 call]
    end
    
    subgraph "Cost Estimation"
        H[Per Query: $0.01-0.02]
        I[Embeddings: ~$0.001]
        J[Classification: ~$0.005]
        K[Generation: ~$0.005]
    end
    
    A --> B
    A --> C
    A --> D
    
    E --> I
    F --> J
    G --> K
    
    I --> H
    J --> H
    K --> H
    
    style A fill:#e3f2fd
    style H fill:#c8e6c9
    style B fill:#fff9c4
    style C fill:#fff9c4
    style D fill:#fff9c4
```

### Optimization Opportunities

```mermaid
graph LR
    subgraph "Current (Prototype)"
        A[Sequential Classification]
        B[Single Retrieval Attempt]
        C[Fixed Chunk Size]
    end
    
    subgraph "Future Improvements"
        D[Batch Classification<br/>Lower latency]
        E[Adaptive Retrieval<br/>Better coverage]
        F[Dynamic Chunking<br/>Context-aware]
        G[Caching<br/>Reduce redundant calls]
    end
    
    A -.->|Optimize| D
    B -.->|Enhance| E
    C -.->|Improve| F
    A -.->|Add| G
    
    style A fill:#ffccbc
    style B fill:#ffccbc
    style C fill:#ffccbc
    style D fill:#c8e6c9
    style E fill:#c8e6c9
    style F fill:#c8e6c9
    style G fill:#c8e6c9
```

## 🧪 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Hybrid Retrieval (70/30)** | Semantic captures meaning, BM25 handles exact terms. 70/30 weight balances both. |
| **Document Classification** | Prevents mixing alignment and gap evidence in citations. Improves accuracy. |
| **Separate Evidence Contexts** | LLM gets pre-classified evidence, reducing hallucination and citation errors. |
| **Structured JSON Output** | Pydantic models ensure type safety and consistent API contracts. |
| **512-token chunks with 50% overlap** | Balance between context preservation and retrieval granularity. |
| **gpt-4o-mini model** | Cost-effective for MVP, sufficient quality for alignment analysis. |
| **Temperature 0.0 for classification** | Deterministic classification, reduces randomness. |
| **Temperature 0.7 for generation** | Allows some creativity while maintaining accuracy. |

## 🗂️ File Structure

| Component | File | Key Functions/Classes |
|-----------|------|----------------------|
| **Main Pipeline** | `src/vira/rag/pipeline.py` | `AlignmentAnalyzer`, `build_chain()`, `classify_documents()` |
| **Hybrid Retrieval** | `src/vira/retrieval/hybrid.py` | `HybridRetriever`, `get_relevant_documents()` |
| **Vectorstore** | `src/vira/vectorstore/manager.py` | `load_vectorstore()`, `initialize_vectorstore()` |
| **API Endpoint** | `src/vira/backend/api.py` | `/analyze` POST endpoint |
| **UI Routes** | `src/vira/backend/ui_routes.py` | `/api/sessions/{id}/analyze` |
| **Models** | `src/vira/backend/models.py` | `AnalyzeRequest`, `AnalyzeResponse` |
| **Settings** | `src/vira/config/settings.py` | `Settings` (Pydantic) |

## 🔄 Iteration 1 vs Iteration 2

```mermaid
graph TB
    subgraph "Iteration 1: RAG Pipeline"
        I1A[Fixed retrieval]
        I1B[Single-pass analysis]
        I1C[No confidence scoring]
        I1D[No external research]
    end
    
    subgraph "Iteration 2: Reflective Agent"
        I2A[Adaptive retrieval]
        I2B[Multi-pass with reflection]
        I2C[Confidence quantification]
        I2D[Autonomous web search]
    end
    
    I1A -.Evolves to.-> I2A
    I1B -.Evolves to.-> I2B
    I1C -.Evolves to.-> I2C
    I1D -.Evolves to.-> I2D
    
    style I1A fill:#e3f2fd
    style I1B fill:#e3f2fd
    style I1C fill:#e3f2fd
    style I1D fill:#e3f2fd
    
    style I2A fill:#c8e6c9
    style I2B fill:#c8e6c9
    style I2C fill:#c8e6c9
    style I2D fill:#c8e6c9
```

## 💡 Example Query Flow

```mermaid
flowchart TD
    START["User Input:<br/>Company: 'PawsPerfect'<br/>Plan: Mobile pet grooming..."] --> QUERY[Extract Query:<br/>'Mobile pet grooming...']
    
    QUERY --> HYBRID[Hybrid Retrieval]
    
    HYBRID --> SEM["Semantic Results:<br/>- a16z marketplace criteria<br/>- pet industry investment<br/>- service business models"]
    
    HYBRID --> KEY["Keyword Results:<br/>- 'mobile' + 'pet'<br/>- 'grooming' + 'service'<br/>- 'convenience' + 'market'"]
    
    SEM --> MERGE[Merge + Rank]
    KEY --> MERGE
    
    MERGE --> CLASS[Classify 12 docs]
    
    CLASS --> A["Alignment (5 docs):<br/>Market demand evidence"]
    CLASS --> G["Gap (4 docs):<br/>Team experience criteria"]
    CLASS --> N["Neutral (3 docs):<br/>General industry info"]
    
    A --> GEN[Generate Analysis]
    G --> GEN
    
    GEN --> OUT["Output:<br/>✅ 2 alignment points<br/>⚠️ 3 gap points<br/>📝 Summary"]
    
    style HYBRID fill:#fff9c4
    style CLASS fill:#c8e6c9
    style GEN fill:#f8bbd0
    style OUT fill:#4caf50
```

---

**See also:**
- `VIRA_MVP_Architecture_Plan_v0.md` (lines 273-526) - Original Iteration 1 spec
- `Iter2Agents.md` - Iteration 2 architecture diagrams
- `VIRA-Iter1 Chainlit-Arch v1.md` - Chainlit UI architecture

