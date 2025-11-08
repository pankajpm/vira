# VIRA Chainlit UI - Quick Start Guide

**Version:** 1.0  
**Date:** November 4, 2025

---

## Overview

The new VIRA Chainlit UI provides a multi-turn conversational interface for analyzing business plan alignment with VC investment criteria.

### Key Features

✅ **Persistent Chat Sessions** - All conversations saved to SQLite database  
✅ **Business Plan Editor** - Edit and version-track your business plan  
✅ **Manual Analysis Trigger** - Explicit `/analyze` command or button click  
✅ **Developer Debug Mode** - View retrieval metrics, LangSmith traces, token counts  
✅ **Session History** - Load previous conversations from dropdown  
✅ **Version Control** - Track changes to business plan with diff summaries  

---

## Installation

### 1. Install Dependencies

```bash
# If using pip
pip install -e .

# If using poetry
poetry install
```

New dependencies added:
- `chainlit>=1.0.0` - Multi-turn chat framework
- `sqlalchemy>=2.0.0` - Database ORM
- `aiosqlite>=0.19.0` - Async SQLite adapter

### 2. Initialize Database

The database will be automatically created on first run at:
```
./data/vira_sessions.db
```

To manually initialize:
```bash
python -c "from vira.ui.database.models import create_tables; create_tables()"
```

---

## Running the App

### Start Chainlit Server

```bash
# From project root
chainlit run src/vira/ui/chainlit_app.py -w

# The -w flag enables auto-reload on file changes
```

Expected output:
```
Chainlit: Hi there, We are collecting anonymous telemetry... [TELEMETRY DISABLED]
Chainlit: Server started on http://localhost:8000
```

### Open in Browser

Navigate to: **http://localhost:8000**

---

## Usage Guide

### First Time Setup

1. **Start New Session**
   - Opens automatically on first visit
   - Enter your company name when prompted
   - Welcome message appears with instructions

2. **Add Business Plan**
   - Click **✏️ Edit Plan** button
   - Paste your business plan content
   - Click **💾 Save** (auto-versioned)

3. **Run Analysis**
   - Type `/analyze` in chat, OR
   - Click **🔍 Analyze** button
   - Wait for agent to process (shows step-by-step progress)
   - View structured alignment report

### Multi-Turn Conversation

The system supports several interaction patterns:

#### Basic Commands

| Command | Action |
|---------|--------|
| `/analyze` | Run full business plan analysis |
| `analyze` | Same as `/analyze` |
| _Any other text_ | General conversation (future: enhanced with LLM) |

#### Business Plan Actions

- **✏️ Edit Plan** - Modify your business plan
- **🔍 Analyze** - Trigger alignment analysis
- **📜 Versions** - View plan edit history with diffs

### Loading Previous Sessions

1. Click **Settings** icon (top right)
2. Open **Session** dropdown
3. Select previous session by name/date
4. Chat history and business plan automatically restored

### Developer Debug Mode

Enable in settings to see:
- ✅ Retrieval latency (ms)
- ✅ LLM generation latency (ms)
- ✅ Retrieved document previews with URLs
- ✅ Token counts (input/output)
- ✅ Estimated cost per query
- ✅ LangSmith trace links (when configured)

---

## Database Schema

### Tables

```
sessions          - Chat sessions (id, company_name, created_at, status)
messages          - Chat messages (session_id, role, content, metadata)
business_plans    - Versioned plans (session_id, version, content, diff)
analyses          - Analysis runs (message_id, tokens, latency, traces)
```

### Querying the Database

```bash
# Open SQLite CLI
sqlite3 ./data/vira_sessions.db

# View all sessions
SELECT id, company_name, created_at FROM sessions ORDER BY created_at DESC;

# View messages for a session
SELECT role, content, created_at FROM messages WHERE session_id = '<uuid>' ORDER BY created_at;

# View plan versions
SELECT version, created_at, diff_summary FROM business_plans WHERE session_id = '<uuid>' ORDER BY version DESC;
```

---

## Architecture

### Component Overview

```
src/vira/ui/
├── chainlit_app.py              # Main Chainlit application (500 lines)
├── database/
│   ├── models.py                # SQLAlchemy models
│   └── session_manager.py       # CRUD operations
└── [future] components/
    ├── debug_panel.py           # Enhanced debug visualization
    └── chat_history.py          # Left sidebar session list
```

### Session Flow

```
User visits → @cl.on_chat_start
    ↓
Choose new/existing session
    ↓
Initialize session state (session_id, analyzer, debug_mode)
    ↓
Render business plan editor
    ↓
User edits plan → Save to DB with versioning
    ↓
User clicks Analyze → Run AlignmentAnalyzer
    ↓
Display results + save to messages table
    ↓
[Optional] Show debug panel
```

---

## Configuration

### Environment Variables

Ensure these are set in `.env`:

```bash
# OpenAI API (required)
OPENAI_API_KEY=sk-...

# LangSmith (optional - for tracing)
LANGSMITH_API_KEY=ls__...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=vira-chainlit

# Database (optional - defaults to ./data/vira_sessions.db)
VIRA_DB_PATH=./data/vira_sessions.db

# Backend (optional - for hybrid mode with FastAPI)
STREAMLIT_BACKEND_URL=http://localhost:8000
```

### Chainlit Settings

Edit `.chainlit` file in project root:

```toml
[project]
telemetry = false
name = "VIRA"

[UI]
name = "VIRA"
description = "Venture Intelligence Research Assistant"
default_theme = "dark"
```

---

## Comparison: Streamlit vs Chainlit

| Feature | Streamlit (Old) | Chainlit (New) |
|---------|----------------|----------------|
| **Session Persistence** | ❌ In-memory only | ✅ SQLite database |
| **Multi-turn Chat** | ❌ Single-shot | ✅ Full conversation |
| **Business Plan Editing** | ⚠️ One-time input | ✅ Persistent editor |
| **Debug Mode** | ❌ None | ✅ Full metrics |
| **Version Control** | ❌ No history | ✅ Complete diffs |
| **Agent Steps** | ❌ Hidden | ✅ Visualized |
| **Loading States** | ⚠️ Generic | ✅ Step-by-step |

---

## Troubleshooting

### Issue: "Session not initialized"
**Solution:** Refresh page and start new session

### Issue: Database locked
**Solution:** Close other connections to `vira_sessions.db`

### Issue: LangSmith trace not showing
**Solution:** 
1. Check `LANGSMITH_API_KEY` is set
2. Verify `LANGSMITH_TRACING=true`
3. Update `langsmith_trace_url` extraction in `chainlit_app.py` (TODO)

### Issue: Analyze button does nothing
**Solution:** Check logs for errors. Ensure:
- Business plan is saved
- OpenAI API key is valid
- Vector database exists at `./data/processed/chroma/`

---

## Future Enhancements

### Planned for Next Iteration

- [ ] **True 3-pane layout** - Left sidebar for session list (Chainlit limitation workaround)
- [ ] **Enhanced conversation** - LLM-powered follow-up Q&A
- [ ] **Plan section analysis** - Analyze specific sections only
- [ ] **Comparison mode** - Compare plan versions side-by-side
- [ ] **Export functionality** - Download chat transcripts + analysis
- [ ] **Real-time collaboration** - Multiple users, shared sessions
- [ ] **Agent memory** - RAG over previous conversations
- [ ] **Reflection agent** - Self-critique analysis quality

---

## Development Workflow

### File Watching

```bash
# Chainlit auto-reloads on file changes with -w flag
chainlit run src/vira/ui/chainlit_app.py -w
```

### Testing Database Changes

```bash
# Reset database (WARNING: deletes all sessions)
rm ./data/vira_sessions.db
python -c "from vira.ui.database.models import create_tables; create_tables()"
```

### Debugging

1. Enable **Developer Mode** in UI settings
2. Check terminal logs for detailed error traces
3. Query database directly with SQLite CLI
4. Use LangSmith dashboard for LLM traces

---

## Support

For issues or questions:
1. Check `VIRA-Chainlit-Architecture.md` for technical details
2. Review database schema in `src/vira/ui/database/models.py`
3. Inspect session manager logic in `src/vira/ui/database/session_manager.py`

---

**Last Updated:** November 4, 2025  
**Next Review:** After first agentic backend integration

