# VIRA Data Layer Architecture
## Web Scraping, Storage, Transformation & Reusability

**Version:** 1.0  
**Date:** November 4, 2025  
**Purpose:** Complete specification of data ingestion, storage, and transformation pipeline

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Data Pipeline Overview](#2-data-pipeline-overview)
3. [Layer 1: Web Scraping & Raw Data](#3-layer-1-web-scraping--raw-data)
4. [Layer 2: Processing & Chunking](#4-layer-2-processing--chunking)
5. [Layer 3: Vector Storage](#5-layer-3-vector-storage)
6. [Data Format Specifications](#6-data-format-specifications)
7. [Reusability in Other Projects](#7-reusability-in-other-projects)
8. [Transformation Capabilities](#8-transformation-capabilities)
9. [Data Governance & Maintenance](#9-data-governance--maintenance)

---

## 1. Executive Summary

VIRA's data architecture consists of **three distinct layers**, each with specific formats, storage locations, and transformation capabilities:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ARCHITECTURE LAYERS                     │
└─────────────────────────────────────────────────────────────────┘

Layer 1: RAW DATA          Layer 2: PROCESSED      Layer 3: VECTOR STORE
(Web Scraping)             (Chunked)               (Embeddings)
─────────────────         ─────────────────        ─────────────────
./data/raw/               In-memory only           ./data/processed/chroma/
a16z_raw.jsonl            (transient)              ├── chroma.sqlite3
                                                   └── [uuid]/*.bin

Format: JSONL             Format: Dict[]           Format: Binary
Size: ~500 pages          Size: ~10K chunks        Size: Embeddings + Index
Reusable: ✅ YES         Reusable: ⚠️ Transient   Reusable: ✅ YES
```

### Key Characteristics

| Aspect | Details |
|--------|---------|
| **Raw Data Preservation** | ✅ Complete HTML/text stored in JSONL |
| **Lossless Extraction** | ✅ All metadata preserved (URL, date, status) |
| **Multi-Project Reusability** | ✅ Raw data can be reprocessed for any use case |
| **Format Flexibility** | ✅ Can export to CSV, JSON, SQL, Parquet, etc. |
| **Update Strategy** | Incremental (crawl → append to JSONL) |
| **Storage Efficiency** | ~2-5 MB per 100 pages (compressed text) |

---

## 2. Data Pipeline Overview

### 2.1 End-to-End Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA PIPELINE ARCHITECTURE                 │
└────────────────────────────────────────────────────────────────────────┘

STAGE 1: INGESTION (Offline, Periodic)
═══════════════════════════════════════

                    Web Sources
                    (a16z.com)
                        │
                        ▼
        ┌───────────────────────────────┐
        │     Scrapy Spider             │
        │  (A16ZSpider)                 │
        │                               │
        │  • Seed URLs (18 starting)    │
        │  • Domain filtering           │
        │  • Exclusion patterns         │
        │  • Rate limiting (1s delay)   │
        │  • Max 400 pages              │
        └───────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   HTML Extraction             │
        │                               │
        │  • Title from <title>         │
        │  • Body from <article>, <main>│
        │  • Metadata (URL, status)     │
        │  • Timestamp (UTC)            │
        └───────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │   RAW DATA STORAGE                    │
        │   ./data/raw/a16z_raw.jsonl           │
        │                                       │
        │   Format: JSON Lines (JSONL)          │
        │   - One record per line               │
        │   - Append-only (no overwrites)       │
        │   - ~400 records (pages)              │
        │   - ~50-500 KB per record             │
        │   - Total: ~50-200 MB uncompressed    │
        └───────────────────────────────────────┘
                        │
                        │ (Reusable Checkpoint #1)
                        │
════════════════════════╪════════════════════════════════════════
STAGE 2: PROCESSING (On-Demand)
════════════════════════╪════════════════════════════════════
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Load JSONL                  │
        │   (load_raw_jsonl)            │
        │                               │
        │   • Read line-by-line         │
        │   • Parse JSON                │
        │   • Validate structure        │
        └───────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Text Chunking               │
        │   (RecursiveCharacterSplitter)│
        │                               │
        │   • Chunk size: 900 chars     │
        │   • Overlap: 150 chars        │
        │   • Separators: \n\n, \n, .   │
        │   • Preserve metadata         │
        │   • Add chunk_index           │
        └───────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────┐
        │   CHUNKED DATA (In-Memory)             │
        │                                        │
        │   Format: List[Dict]                   │
        │   - ~10,000 chunks total               │
        │   - Each: {content, metadata}          │
        │   - Transient (not persisted)          │
        └────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Convert to Documents        │
        │   (build_documents)           │
        │                               │
        │   • LangChain Document format │
        │   • Flatten nested metadata   │
        │   • Add page_content field    │
        └───────────────────────────────┘
                        │
                        │ (Reusable Checkpoint #2)
                        │
════════════════════════╪════════════════════════════════════
STAGE 3: EMBEDDING & INDEXING (On-Demand)
════════════════════════╪════════════════════════════════════
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Embedding Generation        │
        │   (OpenAI API)                │
        │                               │
        │   • Model: text-embedding-3   │
        │   • Dimensions: 1536          │
        │   • Batch: 2000 docs          │
        │   • Rate limit: 3000 RPM      │
        │   • Cost: ~$0.26 for 10K      │
        └───────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────┐
        │   Vector Database (Chroma)             │
        │   ./data/processed/chroma/             │
        │                                        │
        │   ├── chroma.sqlite3                   │
        │   │   - Metadata storage               │
        │   │   - Collection management          │
        │   │                                    │
        │   └── [collection-uuid]/               │
        │       ├── data_level0.bin              │
        │       │   - Vector data                │
        │       ├── header.bin                   │
        │       │   - Index header               │
        │       ├── index_metadata.pickle        │
        │       │   - HNSW index config          │
        │       ├── length.bin                   │
        │       │   - Vector lengths             │
        │       └── link_lists.bin               │
        │           - HNSW graph structure       │
        └────────────────────────────────────────┘
                        │
                        │ (Reusable Checkpoint #3)
                        │
════════════════════════╪════════════════════════════════════
STAGE 4: QUERY & RETRIEVAL (Real-Time)
════════════════════════╪════════════════════════════════════
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Hybrid Retrieval            │
        │   (HybridRetriever)           │
        │                               │
        │   • Semantic search (Chroma)  │
        │   • Keyword search (BM25)     │
        │   • Score fusion              │
        └───────────────────────────────┘
```

### 2.2 Data Flow States

| Stage | State | Persistence | Accessibility | Reusability |
|-------|-------|-------------|--------------|-------------|
| **Web Scraping** | Raw HTML/Text | Disk (JSONL) | Direct file access | ✅ High |
| **Chunking** | Processed chunks | Memory only | Python objects | ⚠️ Transient |
| **Embedding** | Vector embeddings | Disk (Chroma) | Database API | ✅ High |
| **Retrieval** | Retrieved docs | Memory only | API response | ⚠️ Transient |

---

## 3. Layer 1: Web Scraping & Raw Data

### 3.1 Scraping Configuration

**Location:** `/config/crawl_settings.yaml`

```yaml
seed_urls:
  - https://a16z.com/ai/
  - https://a16z.com/enterprise/
  - https://a16z.com/bio-health/
  # ... 15 more seed URLs

allowed_domains:
  - a16z.com

exclusion_patterns:
  - "?s="              # Search results
  - "/tag/"            # Tag pages
  - "/category/"       # Category pages
  - "/author/"         # Author pages

max_pages: 400
download_delay: 1.0
concurrent_requests: 2
user_agent: "VIRAPrototypeBot/0.1"
output_dir: ./data/raw
```

### 3.2 Raw Data Storage

**Location:** `./data/raw/a16z_raw.jsonl`

**Format:** JSON Lines (JSONL)
- One JSON object per line
- Newline-separated
- No commas between records
- Append-only file

**Advantages of JSONL:**
- ✅ Streamable (process line-by-line, low memory)
- ✅ Appendable (incremental crawls without rewriting)
- ✅ Human-readable (can inspect with text editors)
- ✅ Language-agnostic (parseable in any language)
- ✅ Error-tolerant (corrupted line doesn't break entire file)

### 3.3 Raw Record Structure

Each line in `a16z_raw.jsonl` is a complete JSON object:

```json
{
  "url": "https://a16z.com/posts/ai-healthcare-thesis-2024/",
  "status": 200,
  "scraped_at": "2024-11-01T15:23:45.123456",
  "title": "Our Healthcare AI Investment Thesis",
  "content": "We invest in early-stage healthcare companies leveraging AI...\n\n[Full extracted text, 5-50KB]",
  "metadata": {
    "url": "https://a16z.com/posts/ai-healthcare-thesis-2024/",
    "status": 200,
    "scraped_at": "2024-11-01T15:23:45.123456",
    "title": "Our Healthcare AI Investment Thesis",
    "content_type": "text/html; charset=UTF-8",
    "meta_organization": "a16z",
    "meta_iteration": 1
  }
}
```

**Field Descriptions:**

| Field | Type | Source | Purpose | Nullable |
|-------|------|--------|---------|----------|
| `url` | string | Scrapy | Canonical page URL | No |
| `status` | integer | HTTP | Response code (200, 404, etc.) | No |
| `scraped_at` | ISO 8601 | System clock | UTC timestamp | No |
| `title` | string | `<title>` tag | Page title | Yes (empty string) |
| `content` | string | `<article>`, `<main>`, `<body>` | Extracted text | Yes (empty string) |
| `metadata` | object | Mixed | Flattened metadata dict | No |

### 3.4 Content Extraction Logic

**Extraction Strategy:** CSS Selectors with fallback hierarchy

```python
# From spider.py lines 68-72
body = "\n".join(
    part.strip()
    for part in response.css("article, main, body").xpath("string()").getall()
    if part.strip()
)
```

**Selector Hierarchy:**
1. `<article>` - Primary content container (blog posts, articles)
2. `<main>` - Main content area (if no article)
3. `<body>` - Entire page body (fallback)

**Text Cleaning:**
- Strip leading/trailing whitespace per section
- Join sections with newlines
- Remove empty sections
- Preserve internal structure (paragraphs, lists)

### 3.5 Storage Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **File Format** | JSONL | One JSON object per line |
| **Encoding** | UTF-8 | Unicode support |
| **Compression** | None | Plain text (can gzip externally) |
| **Average Record Size** | 50-500 KB | Depends on page length |
| **Total Records** | ~400 pages | Configurable via `max_pages` |
| **Total File Size** | 50-200 MB | Uncompressed |
| **Write Mode** | Append | Incremental crawls supported |

### 3.6 Running the Crawler

**Command:**
```bash
python -m vira.ingestion.runner crawl --config-path ./config/crawl_settings.yaml
```

**Process:**
1. Load configuration from YAML
2. Initialize Scrapy crawler process
3. Start spider with seed URLs
4. Follow links within allowed domains
5. Extract content from each page
6. Write records to JSONL (one per line)
7. Respect rate limits and max pages
8. Exit gracefully on completion

**Output:**
```
2024-11-01 15:20:00 [scrapy.core.engine] INFO: Spider opened
2024-11-01 15:20:05 [scrapy.core.engine] INFO: Crawled (200) <GET https://a16z.com/ai/>
2024-11-01 15:20:10 [scrapy.core.engine] INFO: Crawled (200) <GET https://a16z.com/posts/ai-thesis/>
...
2024-11-01 16:45:30 [scrapy.core.engine] INFO: Spider closed (finished)
```

---

## 4. Layer 2: Processing & Chunking

### 4.1 Loading Raw Data

**Function:** `load_raw_jsonl()` in `src/vira/processing/pipeline.py`

```python
def load_raw_jsonl(path: Path) -> List[dict[str, str]]:
    """Load JSONL records emitted by the crawler."""
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]
```

**Process:**
1. Open JSONL file in UTF-8 mode
2. Read line-by-line
3. Parse each line as JSON
4. Accumulate in list
5. Return all records

**Memory Note:** Loads entire file into RAM. For large datasets (>1GB), consider streaming/batching.

### 4.2 Chunking Strategy

**Purpose:** Split long documents into retrievable units

**Why Chunking?**
- Long documents exceed LLM context windows
- Smaller chunks improve retrieval precision
- Overlap preserves context across boundaries
- Enables semantic unit matching

**Configuration:**

```python
@dataclass
class ChunkParams:
    chunk_size: int = 900           # Characters per chunk
    chunk_overlap: int = 150        # Overlap between chunks
    separators: Sequence[str] = (   # Split priority order
        "\n\n",  # Paragraphs (highest priority)
        "\n",    # Lines
        ".",     # Sentences
        "?",     # Questions
        "!",     # Exclamations
        " ",     # Words (lowest priority)
    )
```

**Chunking Algorithm:** Recursive Character Text Splitter

```
Document: "Paragraph 1...\n\nParagraph 2...\n\nParagraph 3..."
                    ↓
Try split on "\n\n" (paragraphs)
                    ↓
If chunk > 900 chars, split on "\n" (lines)
                    ↓
If still > 900 chars, split on "." (sentences)
                    ↓
Continue recursively until chunk_size satisfied
                    ↓
Add 150-char overlap from previous chunk
```

**Example:**

```
Original Document (2500 chars):
┌──────────────────────────────────────────────────────────┐
│ We invest in AI companies [... 2500 chars total ...]     │
└──────────────────────────────────────────────────────────┘

After Chunking:
┌────────────────────┐
│ Chunk 0 (900 chars)│  "We invest in AI companies that..."
└────────────────────┘
         ↓ (150 char overlap)
┌────────────────────┐
│ Chunk 1 (900 chars)│  "...companies that focus on healthcare..."
└────────────────────┘
         ↓ (150 char overlap)
┌────────────────────┐
│ Chunk 2 (700 chars)│  "...healthcare and deliver real impact..."
└────────────────────┘
```

### 4.3 Chunk Metadata Enrichment

**Process:** Each chunk inherits original document metadata + chunk-specific fields

```python
{
    "content": "We invest in AI companies that...",
    "chunk_index": "0",
    "url": "https://a16z.com/posts/ai-thesis/",
    "status": "200",
    "scraped_at": "2024-11-01T15:23:45.123456",
    "title": "Our AI Investment Thesis",
    "meta_organization": "a16z",
    "meta_iteration": "1"
}
```

**Added Fields:**
- `chunk_index`: Sequential number within document (0, 1, 2, ...)
- All original metadata preserved

**Metadata Flattening:** Nested dicts are flattened with underscore prefixes:
```python
# Before
{"metadata": {"organization": "a16z"}}

# After
{"metadata_organization": "a16z"}
```

### 4.4 Document Conversion

**Function:** `build_documents()` in `src/vira/processing/pipeline.py`

**Purpose:** Convert chunked dicts to LangChain `Document` format

```python
Document(
    page_content="We invest in AI companies...",
    metadata={
        "url": "https://a16z.com/posts/ai-thesis/",
        "chunk_index": "0",
        "title": "Our AI Investment Thesis",
        # ... other metadata
    }
)
```

**Why LangChain Documents?**
- Standard format for LangChain ecosystem
- Compatible with all LangChain vectorstores
- Built-in serialization/deserialization
- Metadata filtering support

### 4.5 Processing Pipeline Flow

```
JSONL File (400 records)
        ↓
load_raw_jsonl()
        ↓
Raw Records List (400 items)
        ↓
chunk_documents()
        ↓
Chunked Records (10,000 items)
        ↓
build_documents()
        ↓
LangChain Documents (10,000 items)
        ↓
ingest_documents()
        ↓
Vector Store (embedded & indexed)
```

**Typical Ratios:**
- 400 pages → ~10,000 chunks (25 chunks per page avg)
- Depends on page length and chunk size

---

## 5. Layer 3: Vector Storage

### 5.1 Vector Database: Chroma

**Location:** `./data/processed/chroma/`

**Chroma Architecture:**

```
./data/processed/chroma/
├── chroma.sqlite3                      # Metadata & collection info
└── 20ad7008-2481-4714-90b4-e86f63d88af9/  # Collection UUID
    ├── data_level0.bin                 # Vector data (1536-dim floats)
    ├── header.bin                      # Index header metadata
    ├── index_metadata.pickle           # HNSW configuration
    ├── length.bin                      # Vector length normalization
    └── link_lists.bin                  # HNSW graph links
```

### 5.2 Storage Components

#### 5.2.1 SQLite Metadata Store

**File:** `chroma.sqlite3`

**Purpose:** Store metadata, collection info, document IDs

**Tables:**
- `collections`: Collection names, UUIDs, configuration
- `embeddings`: Document IDs, metadata, pointers to vectors
- `metadata`: Key-value pairs for filtering

**Access:** SQLite database, queryable with standard SQL

```bash
# Inspect metadata
sqlite3 ./data/processed/chroma/chroma.sqlite3

# Example queries
SELECT * FROM collections;
SELECT COUNT(*) FROM embeddings;
SELECT * FROM embeddings WHERE metadata_url LIKE '%ai-thesis%' LIMIT 5;
```

#### 5.2.2 Vector Binary Files

**Format:** Binary (not human-readable)

| File | Content | Size | Purpose |
|------|---------|------|---------|
| `data_level0.bin` | Vector embeddings (float32) | ~60 MB for 10K docs | Raw embedding data |
| `link_lists.bin` | HNSW graph structure | ~20 MB | Fast similarity search |
| `index_metadata.pickle` | Index configuration | ~5 KB | Reconstruction metadata |
| `header.bin` | File headers | ~1 KB | Version & format info |
| `length.bin` | Vector norms | ~40 KB | Normalization data |

**Total Storage:** ~80-100 MB for 10K documents (1536-dim embeddings)

### 5.3 Embedding Process

**Function:** `ingest_documents()` in `src/vira/vectorstore/manager.py`

**Process:**
1. Batch documents (2000 per batch)
2. For each batch:
   - Generate embeddings via OpenAI API
   - Store embeddings in Chroma
   - Update HNSW index
   - Persist to disk
3. Return total document count

**Embedding Model:** `text-embedding-3-small`
- Dimensions: 1536
- Context length: 8192 tokens
- Cost: $0.02 per 1M tokens
- Speed: ~1000 docs/minute

**Batching Strategy:**
- Batch size: 2000 documents
- Prevents memory overflow
- Enables progress tracking
- Optimizes API usage

### 5.4 Collection Configuration

**Collection Name:** `a16z_content`

**Settings:**
```python
Chroma(
    collection_name="a16z_content",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./data/processed/chroma"
)
```

**Index Type:** HNSW (Hierarchical Navigable Small World)
- Distance metric: Cosine similarity
- M (connections per node): 16 (default)
- ef_construction: 200 (default)

### 5.5 Retrieval Capabilities

**Vector Similarity Search:**
```python
vectorstore.similarity_search(query, k=6)
```

**Vector Search with Scores:**
```python
vectorstore.similarity_search_with_score(query, k=6)
```

**Metadata Filtering:**
```python
vectorstore.similarity_search(
    query,
    k=6,
    filter={"url": {"$regex": "healthcare"}}
)
```

**Raw Data Extraction:**
```python
snapshot = vectorstore.get(include=["documents", "metadatas", "embeddings"])
# Returns: {"documents": [...], "metadatas": [...], "embeddings": [...]}
```

---

## 6. Data Format Specifications

### 6.1 Format Comparison Matrix

| Format | Layer | Persistence | Human-Readable | Size (10K docs) | Query Speed | Reusability |
|--------|-------|-------------|----------------|-----------------|-------------|-------------|
| **JSONL** | Raw | Disk | ✅ Yes | 50-200 MB | N/A | ⭐⭐⭐⭐⭐ |
| **Python Dict** | Processing | Memory | ⚠️ Limited | ~100 MB RAM | N/A | ⭐⭐ |
| **LangChain Doc** | Processing | Memory | ⚠️ Limited | ~120 MB RAM | N/A | ⭐⭐⭐ |
| **Chroma DB** | Vector | Disk | ❌ No | 80-100 MB | <100ms | ⭐⭐⭐⭐ |

### 6.2 Export Capabilities from Raw JSONL

The raw JSONL data can be easily converted to any format:

#### CSV Export

```python
import json
import csv

with open("data/raw/a16z_raw.jsonl") as f:
    records = [json.loads(line) for line in f]

with open("output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["url", "title", "content", "scraped_at"])
    writer.writeheader()
    for rec in records:
        writer.writerow({
            "url": rec["url"],
            "title": rec["title"],
            "content": rec["content"][:500],  # Truncate
            "scraped_at": rec["scraped_at"]
        })
```

#### SQL Database Export

```python
import sqlite3
import json

conn = sqlite3.connect("a16z_content.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        content TEXT,
        scraped_at TEXT,
        status INTEGER
    )
""")

with open("data/raw/a16z_raw.jsonl") as f:
    for line in f:
        rec = json.loads(line)
        cursor.execute("""
            INSERT OR REPLACE INTO pages (url, title, content, scraped_at, status)
            VALUES (?, ?, ?, ?, ?)
        """, (rec["url"], rec["title"], rec["content"], rec["scraped_at"], rec["status"]))

conn.commit()
conn.close()
```

#### Parquet Export (for Big Data)

```python
import pandas as pd
import json

records = []
with open("data/raw/a16z_raw.jsonl") as f:
    for line in f:
        records.append(json.loads(line))

df = pd.DataFrame(records)
df.to_parquet("a16z_content.parquet", engine="pyarrow", compression="snappy")
```

#### Elasticsearch Bulk Import

```python
from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch(["http://localhost:9200"])

def generate_actions():
    with open("data/raw/a16z_raw.jsonl") as f:
        for line in f:
            rec = json.loads(line)
            yield {
                "_index": "a16z_content",
                "_id": rec["url"],
                "_source": rec
            }

helpers.bulk(es, generate_actions())
```

### 6.3 Structured Data Extraction

The raw content can be parsed to extract structured attributes:

#### Entity Extraction

```python
import re
import json

def extract_entities(content):
    """Extract structured entities from raw content."""
    return {
        "company_names": re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content),
        "dollar_amounts": re.findall(r'\$\d+(?:\.\d+)?[BMK]?', content),
        "percentages": re.findall(r'\d+(?:\.\d+)?%', content),
        "years": re.findall(r'\b20\d{2}\b', content),
        "urls": re.findall(r'https?://[^\s]+', content),
        "email_addresses": re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
    }

with open("data/raw/a16z_raw.jsonl") as f:
    for line in f:
        rec = json.loads(line)
        entities = extract_entities(rec["content"])
        print(f"URL: {rec['url']}")
        print(f"Entities: {entities}")
        print("---")
```

#### LLM-Based Extraction

```python
from openai import OpenAI

client = OpenAI()

def extract_structured_data(content):
    """Use GPT to extract structured attributes."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract structured data from VC firm content."},
            {"role": "user", "content": f"Extract investment criteria, focus areas, and stage preferences from: {content[:3000]}"}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

with open("data/raw/a16z_raw.jsonl") as f:
    for line in f:
        rec = json.loads(line)
        structured = extract_structured_data(rec["content"])
        print(f"URL: {rec['url']}")
        print(f"Structured: {structured}")
```

---

## 7. Reusability in Other Projects

### 7.1 Cross-Project Use Cases

The raw JSONL data is **highly reusable** for various applications:

#### Use Case 1: Competitive Intelligence Platform

```
Goal: Track VC firm trends, portfolio evolution, investment themes

Data Needed:
- Portfolio company announcements
- Investment thesis blog posts
- Partner commentary

Extraction:
- Filter JSONL for blog posts, portfolio pages
- Extract: company names, funding amounts, sectors
- Time-series analysis of focus areas

Tools: pandas, spaCy NER, visualization libraries
```

#### Use Case 2: Knowledge Graph Construction

```
Goal: Build graph of relationships (VCs → Portfolio → Sectors)

Data Needed:
- All page content
- URLs (as entity IDs)
- Metadata (categories, dates)

Extraction:
- Entity extraction (companies, people, concepts)
- Relationship extraction (invested in, partnered with)
- Graph storage (Neo4j, NetworkX)

Tools: spaCy, OpenIE, graph databases
```

#### Use Case 3: Content Recommendation System

```
Goal: Recommend relevant VC articles to founders

Data Needed:
- Article content
- Topics, categories
- Related companies

Extraction:
- Topic modeling (LDA, BERTopic)
- Similarity matching
- Collaborative filtering

Tools: scikit-learn, Gensim, FAISS
```

#### Use Case 4: Sentiment Analysis Dashboard

```
Goal: Track VC sentiment toward industries over time

Data Needed:
- Blog posts, partner commentary
- Dates, sectors

Extraction:
- Sentiment scoring per document
- Aggregate by sector and time
- Trend visualization

Tools: VADER, TextBlob, Plotly
```

#### Use Case 5: Search Engine / Q&A Bot

```
Goal: Answer questions about VC firm focus areas

Data Needed:
- All content
- Q&A pairs (synthetic or extracted)

Extraction:
- Index in search engine (Elasticsearch)
- Build Q&A dataset for fine-tuning
- Deploy as chatbot

Tools: Elasticsearch, GPT fine-tuning, Rasa
```

### 7.2 Portability Features

**Why VIRA's Data is Highly Portable:**

1. **JSONL Format:**
   - Universal (parseable in any language)
   - No proprietary dependencies
   - Can be streamed/chunked for large files

2. **Complete Metadata:**
   - URL (for deduplication, linking)
   - Timestamps (for temporal analysis)
   - Status codes (for quality filtering)

3. **Raw Content Preservation:**
   - No information loss
   - Can re-chunk with different parameters
   - Can extract new fields without re-scraping

4. **Separation of Concerns:**
   - Raw data (Layer 1) independent of processing (Layer 2)
   - Processing independent of vectorization (Layer 3)
   - Can swap vector DB without re-scraping

### 7.3 Migration Scenarios

#### Scenario 1: Migrate to Different Vector DB

```
Current: Chroma
New: Pinecone, Weaviate, or Qdrant

Steps:
1. Keep raw JSONL unchanged
2. Re-run chunking (or load from existing chunks)
3. Generate embeddings (or export from Chroma)
4. Ingest into new vector DB

Cost: Only new DB indexing (no re-scraping)
```

#### Scenario 2: Change Chunking Strategy

```
Current: 900 chars, 150 overlap
New: 500 chars, 100 overlap (more granular)

Steps:
1. Keep raw JSONL unchanged
2. Re-chunk with new parameters
3. Re-generate embeddings
4. Re-ingest into Chroma

Cost: Re-embedding (~$0.26 per 10K docs)
```

#### Scenario 3: Add New VC Firms

```
Current: a16z only
New: a16z + Sequoia + Bessemer

Steps:
1. Create new crawl configs (sequoia_settings.yaml)
2. Crawl new firms → new JSONL files
3. Combine JSONL files (cat a16z.jsonl sequoia.jsonl > combined.jsonl)
4. Re-process combined data
5. Ingest into same Chroma collection (or separate)

Cost: Incremental (only new data)
```

#### Scenario 4: Export to Data Warehouse

```
Current: Local files
New: BigQuery, Snowflake, or Redshift

Steps:
1. Convert JSONL → Parquet (schema-optimized)
2. Upload to cloud storage (S3, GCS)
3. Load into warehouse
4. Run SQL analytics, join with other datasets

Cost: Storage + query costs (cloud provider)
```

### 7.4 API Wrapper for Reuse

Create a simple API to serve raw data to other projects:

```python
from fastapi import FastAPI
import json
from pathlib import Path

app = FastAPI()

@app.get("/pages")
def list_pages(limit: int = 100, offset: int = 0):
    """Return paginated list of scraped pages."""
    pages = []
    with open("data/raw/a16z_raw.jsonl") as f:
        for i, line in enumerate(f):
            if i < offset:
                continue
            if len(pages) >= limit:
                break
            pages.append(json.loads(line))
    return {"total": len(pages), "pages": pages}

@app.get("/pages/search")
def search_pages(query: str, limit: int = 10):
    """Search pages by keyword."""
    results = []
    with open("data/raw/a16z_raw.jsonl") as f:
        for line in f:
            rec = json.loads(line)
            if query.lower() in rec["content"].lower():
                results.append(rec)
            if len(results) >= limit:
                break
    return {"query": query, "count": len(results), "results": results}

@app.get("/pages/by-url")
def get_page_by_url(url: str):
    """Get specific page by URL."""
    with open("data/raw/a16z_raw.jsonl") as f:
        for line in f:
            rec = json.loads(line)
            if rec["url"] == url:
                return rec
    return {"error": "Page not found"}
```

---

## 8. Transformation Capabilities

### 8.1 Schema Transformation

**Convert flat JSONL to nested JSON:**

```python
import json

def transform_to_nested(jsonl_path, output_path):
    """Convert JSONL to nested JSON structure."""
    data = {
        "organization": "a16z",
        "scraped_at": None,
        "pages": []
    }
    
    with open(jsonl_path) as f:
        for line in f:
            rec = json.loads(line)
            if data["scraped_at"] is None:
                data["scraped_at"] = rec["scraped_at"]
            
            data["pages"].append({
                "url": rec["url"],
                "title": rec["title"],
                "content": rec["content"],
                "metadata": rec["metadata"]
            })
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

transform_to_nested("data/raw/a16z_raw.jsonl", "data/a16z_nested.json")
```

### 8.2 Content Enrichment

**Add NLP features to each record:**

```python
import json
import spacy

nlp = spacy.load("en_core_web_sm")

def enrich_with_nlp(jsonl_path, output_path):
    """Add NLP features: entities, keywords, sentiment."""
    with open(jsonl_path) as f_in, open(output_path, "w") as f_out:
        for line in f_in:
            rec = json.loads(line)
            doc = nlp(rec["content"][:100000])  # Limit for memory
            
            rec["nlp"] = {
                "entities": [{"text": ent.text, "label": ent.label_} for ent in doc.ents[:50]],
                "keywords": [chunk.text for chunk in doc.noun_chunks[:30]],
                "sentence_count": len(list(doc.sents)),
                "token_count": len(doc)
            }
            
            f_out.write(json.dumps(rec) + "\n")

enrich_with_nlp("data/raw/a16z_raw.jsonl", "data/a16z_enriched.jsonl")
```

### 8.3 Aggregation & Analytics

**Generate summary statistics:**

```python
import json
from collections import Counter, defaultdict
from datetime import datetime

def analyze_corpus(jsonl_path):
    """Generate corpus analytics."""
    stats = {
        "total_pages": 0,
        "total_chars": 0,
        "avg_page_length": 0,
        "urls_by_domain": Counter(),
        "pages_by_date": defaultdict(int),
        "content_types": Counter(),
        "status_codes": Counter()
    }
    
    with open(jsonl_path) as f:
        for line in f:
            rec = json.loads(line)
            stats["total_pages"] += 1
            stats["total_chars"] += len(rec["content"])
            
            # Extract domain from URL
            domain = rec["url"].split("/")[2]
            stats["urls_by_domain"][domain] += 1
            
            # Group by date
            date = rec["scraped_at"][:10]  # YYYY-MM-DD
            stats["pages_by_date"][date] += 1
            
            stats["content_types"][rec["metadata"].get("content_type", "unknown")] += 1
            stats["status_codes"][rec["status"]] += 1
    
    stats["avg_page_length"] = stats["total_chars"] // stats["total_pages"]
    
    return stats

stats = analyze_corpus("data/raw/a16z_raw.jsonl")
print(json.dumps(stats, indent=2, default=str))
```

### 8.4 Deduplication

**Remove duplicate pages (by URL or content):**

```python
import json
import hashlib

def deduplicate_by_url(jsonl_path, output_path):
    """Remove duplicate URLs, keeping first occurrence."""
    seen_urls = set()
    
    with open(jsonl_path) as f_in, open(output_path, "w") as f_out:
        for line in f_in:
            rec = json.loads(line)
            if rec["url"] not in seen_urls:
                seen_urls.add(rec["url"])
                f_out.write(line)

def deduplicate_by_content(jsonl_path, output_path):
    """Remove duplicate content, using content hash."""
    seen_hashes = set()
    
    with open(jsonl_path) as f_in, open(output_path, "w") as f_out:
        for line in f_in:
            rec = json.loads(line)
            content_hash = hashlib.md5(rec["content"].encode()).hexdigest()
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                f_out.write(line)

deduplicate_by_url("data/raw/a16z_raw.jsonl", "data/a16z_deduped.jsonl")
```

### 8.5 Filtering & Sampling

**Extract subsets of data:**

```python
import json
import random

def filter_by_keyword(jsonl_path, output_path, keyword):
    """Keep only pages containing keyword."""
    with open(jsonl_path) as f_in, open(output_path, "w") as f_out:
        for line in f_in:
            rec = json.loads(line)
            if keyword.lower() in rec["content"].lower():
                f_out.write(line)

def filter_by_status(jsonl_path, output_path, status=200):
    """Keep only pages with specific HTTP status."""
    with open(jsonl_path) as f_in, open(output_path, "w") as f_out:
        for line in f_in:
            rec = json.loads(line)
            if rec["status"] == status:
                f_out.write(line)

def sample_random(jsonl_path, output_path, n=50):
    """Random sample of N pages."""
    with open(jsonl_path) as f:
        lines = f.readlines()
    
    sampled = random.sample(lines, min(n, len(lines)))
    
    with open(output_path, "w") as f:
        f.writelines(sampled)

# Usage
filter_by_keyword("data/raw/a16z_raw.jsonl", "data/healthcare_only.jsonl", "healthcare")
filter_by_status("data/raw/a16z_raw.jsonl", "data/success_only.jsonl", 200)
sample_random("data/raw/a16z_raw.jsonl", "data/sample_50.jsonl", 50)
```

---

## 9. Data Governance & Maintenance

### 9.1 Update Strategy

**Incremental Crawling:**

```
Step 1: Initial Crawl
    → Generates: a16z_raw.jsonl (400 pages)

Step 2: Update Crawl (1 month later)
    → Rename old: a16z_raw_2024-11.jsonl
    → New crawl: a16z_raw.jsonl (400 pages, may overlap)

Step 3: Merge & Deduplicate
    → Combine: cat a16z_raw_2024-11.jsonl a16z_raw.jsonl > combined.jsonl
    → Dedupe: deduplicate_by_url(combined.jsonl, a16z_raw_final.jsonl)

Step 4: Re-process
    → Re-chunk and re-embed only NEW pages
    → Add to existing Chroma collection
```

**Versioning Strategy:**

```
./data/raw/
├── a16z_raw_v1_2024-11-01.jsonl    # Initial crawl
├── a16z_raw_v2_2024-12-01.jsonl    # Update crawl
├── a16z_raw_v3_2025-01-01.jsonl    # Update crawl
└── a16z_raw_latest.jsonl           # Symlink to latest
```

### 9.2 Data Quality Checks

**Validation Script:**

```python
import json
from pathlib import Path

def validate_jsonl(path: Path):
    """Validate JSONL file integrity."""
    issues = []
    
    with open(path) as f:
        for i, line in enumerate(f, start=1):
            try:
                rec = json.loads(line)
                
                # Check required fields
                required = ["url", "status", "scraped_at", "title", "content", "metadata"]
                for field in required:
                    if field not in rec:
                        issues.append(f"Line {i}: Missing field '{field}'")
                
                # Check URL format
                if not rec["url"].startswith("http"):
                    issues.append(f"Line {i}: Invalid URL '{rec['url']}'")
                
                # Check status code
                if not 100 <= rec["status"] < 600:
                    issues.append(f"Line {i}: Invalid status code {rec['status']}")
                
                # Check content length
                if len(rec["content"]) < 100:
                    issues.append(f"Line {i}: Content too short ({len(rec['content'])} chars)")
                
            except json.JSONDecodeError as e:
                issues.append(f"Line {i}: JSON parse error - {e}")
    
    return issues

issues = validate_jsonl(Path("data/raw/a16z_raw.jsonl"))
if issues:
    print(f"Found {len(issues)} issues:")
    for issue in issues[:10]:
        print(f"  - {issue}")
else:
    print("✅ JSONL file is valid!")
```

### 9.3 Backup & Recovery

**Backup Strategy:**

```bash
# Compress raw data
gzip -c data/raw/a16z_raw.jsonl > backups/a16z_raw_2024-11-01.jsonl.gz

# Backup Chroma database
tar -czf backups/chroma_2024-11-01.tar.gz data/processed/chroma/

# Upload to cloud storage
aws s3 cp backups/ s3://vira-backups/ --recursive
```

**Recovery:**

```bash
# Restore raw data
gunzip -c backups/a16z_raw_2024-11-01.jsonl.gz > data/raw/a16z_raw.jsonl

# Restore Chroma database
tar -xzf backups/chroma_2024-11-01.tar.gz -C data/processed/

# Or re-process from raw
python -m vira.processing.cli ingest --raw-path data/raw/a16z_raw.jsonl
```

### 9.4 Storage Optimization

**Compression Ratios:**

| Format | Uncompressed | Gzip | Brotli | Savings |
|--------|-------------|------|--------|---------|
| JSONL | 150 MB | 25 MB | 20 MB | 83-87% |
| Chroma DB | 100 MB | 60 MB | 55 MB | 40-45% |

**Best Practices:**
- ✅ Compress archived JSONL files (gzip -9)
- ✅ Keep latest JSONL uncompressed for fast access
- ✅ Don't compress Chroma DB (actively used)
- ✅ Use cloud archival storage (S3 Glacier) for old versions

---

## Appendix A: Complete File Structure

```
vira/
├── config/
│   └── crawl_settings.yaml         # Crawler configuration
│
├── data/
│   ├── raw/                        # Layer 1: Raw scraped data
│   │   ├── a16z_raw.jsonl         # 400 pages, ~150 MB
│   │   └── .gitkeep
│   │
│   └── processed/                  # Layer 3: Vector storage
│       └── chroma/                 # Chroma database
│           ├── chroma.sqlite3      # Metadata
│           └── [uuid]/             # Vector binary files
│               ├── data_level0.bin
│               ├── header.bin
│               ├── index_metadata.pickle
│               ├── length.bin
│               └── link_lists.bin
│
├── src/vira/
│   ├── ingestion/
│   │   ├── spider.py               # Scrapy spider
│   │   ├── runner.py               # Crawler CLI
│   │   └── crawl_config.py         # Config loader
│   │
│   ├── processing/
│   │   ├── pipeline.py             # Layer 2: Processing
│   │   └── chunker.py              # Text chunking
│   │
│   └── vectorstore/
│       └── manager.py              # Chroma management
│
└── backups/                        # Backups (not in repo)
    ├── a16z_raw_2024-11-01.jsonl.gz
    └── chroma_2024-11-01.tar.gz
```

---

## Appendix B: Reusability Checklist

**Can I use VIRA's data for...**

| Use Case | Feasible? | Data Source | Complexity |
|----------|-----------|-------------|------------|
| Build competitor analysis tool | ✅ Yes | Raw JSONL | Low |
| Create custom search engine | ✅ Yes | Raw JSONL | Medium |
| Train ML model for classification | ✅ Yes | Raw JSONL | Medium |
| Build knowledge graph | ✅ Yes | Raw JSONL | High |
| Generate embeddings for different model | ✅ Yes | Raw JSONL | Low |
| Export to data warehouse | ✅ Yes | Raw JSONL | Low |
| Build recommendation system | ✅ Yes | Raw JSONL + Chroma | Medium |
| Create Q&A bot (different stack) | ✅ Yes | Raw JSONL | Medium |
| Analyze sentiment over time | ✅ Yes | Raw JSONL | Low |
| Extract structured entity database | ✅ Yes | Raw JSONL | Medium |
| Build browser extension | ✅ Yes | Raw JSONL + API | Medium |
| Feed into existing LLM pipeline | ✅ Yes | Raw JSONL | Low |

**Key Takeaway:** Raw JSONL format enables nearly unlimited reuse scenarios!

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-04 | VIRA Team | Initial data architecture documentation |

---

**End of Document**

