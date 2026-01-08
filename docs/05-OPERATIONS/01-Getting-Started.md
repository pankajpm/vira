# Getting Started with VIRA

**Version:** 1.0  
**Last Updated:** November 25, 2025

---

## Prerequisites

- Python 3.10+
- OpenAI API key
- (Optional) Serper API key for Iteration 2

---

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd vira
```

### 2. Install Dependencies
```bash
pip install -e .
# or
uv pip install -r <(uv pip compile pyproject.toml)
```

### 3. Configure Environment
```bash
cp config/.env.template .env
# Edit .env and add:
# OPENAI_API_KEY=sk-...
# SERPER_API_KEY=...  # Optional, for Iteration 2
```

### 4. Run Crawler (One-Time Setup)
```bash
python -m vira.ingestion.runner crawl --config-path config/crawl_settings.yaml
# Output: ./data/raw/a16z_raw.jsonl (~150MB, 400 pages)
```

### 5. Process & Embed Content
```bash
python -m vira.processing.cli ingest --raw-path data/raw/a16z_raw.jsonl
# Output: ./data/processed/chroma/ (~100MB, 10K chunks)
```

---

## Running the Application

### Option 1: Chainlit UI (Recommended)
```bash
chainlit run src/vira/ui/chainlit_app.py --port 8000
# Open: http://localhost:8000
```

### Option 2: React UI
```bash
# Terminal 1: Backend
uvicorn vira.backend.api:app --reload --port 8001

# Terminal 2: Frontend
cd frontend
npm install
npm start
# Open: http://localhost:3000
```

### Option 3: All-in-One Script
```bash
./start_chainlit_ui.sh  # Chainlit + Backend
# or
./start_react_stack.sh  # React + Backend
```

---

## First Analysis

1. Open UI (http://localhost:8000)
2. Paste business plan in chat
3. Type `analyze` or `yes`
4. View two-column alignment analysis

---

## Troubleshooting

**Import errors:** Clear Python cache
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
```

**Database errors:** Recreate database
```bash
rm ./data/vira_sessions.db
# Restart application (will auto-create)
```

**Vector DB errors:** Re-run processing
```bash
rm -rf ./data/processed/chroma
python -m vira.processing.cli ingest --raw-path data/raw/a16z_raw.jsonl
```
