# VIRA Chainlit Multi-Turn Chat Architecture

**Date:** November 4, 2025  
**Purpose:** Multi-turn conversational UI with persistent state and debug mode

---

## Requirements Summary

| Aspect | Decision |
|--------|----------|
| **Persistence** | SQLite database for chat history across sessions |
| **Analysis Trigger** | Manual - explicit "Analyze" button |
| **Debug Mode** | Developer view with traces, timings, LangSmith links |
| **Context** | Full session history + complete business plan always accessible |
| **Deployment** | Local development only |
| **Framework** | Chainlit for agentic system visualization |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CHAINLIT UI ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  LEFT PANE (20%)    │  CENTER PANE (50%)    │  RIGHT PANE (30%)     │
│  Chat History       │  Active Conversation  │  Business Plan        │
├─────────────────────┼───────────────────────┼───────────────────────┤
│                     │                       │                       │
│ 📊 Sessions List    │ 💬 Multi-turn Chat    │ 📝 Plan Editor        │
│                     │                       │                       │
│ ┌─────────────┐    │ User: "Analyze..."    │ ┌─────────────────┐  │
│ │● Session 1  │    │ Agent: "I found..."   │ │ Company: Acme   │  │
│ │  Nov 4, 3pm │    │                       │ │                 │  │
│ │  Acme Inc   │    │ [Analyze Button]      │ │ [Edit Mode]     │  │
│ └─────────────┘    │                       │ │                 │  │
│                     │ 🔍 Debug Panel        │ │ Problem: ...    │  │
│ ┌─────────────┐    │ └─ Retrieval: 150ms   │ │ Solution: ...   │  │
│ │○ Session 2  │    │ └─ LLM: 2.3s          │ │ Market: ...     │  │
│ │  Nov 3, 1pm │    │ └─ Trace: [Link]      │ │                 │  │
│ │  BioTech AI │    │                       │ └─────────────────┘  │
│ └─────────────┘    │                       │                       │
│                     │                       │ [Save Changes]        │
│ [New Session +]     │                       │ [View Versions]       │
│                     │                       │                       │
└─────────────────────┴───────────────────────┴───────────────────────┘
```

---

## Database Schema

### SQLite Tables

```sql
-- sessions table: track chat sessions
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,              -- UUID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    company_name TEXT NOT NULL,
    status TEXT DEFAULT 'active',     -- active, archived
    metadata JSON                      -- additional session data
);

-- messages table: chat history
CREATE TABLE messages (
    id TEXT PRIMARY KEY,              -- UUID
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,               -- user, assistant, system
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,                     -- tool calls, traces, etc.
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- business_plans table: versioned plan storage
CREATE TABLE business_plans (
    id TEXT PRIMARY KEY,              -- UUID
    session_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,                  -- system or user edit
    diff_summary TEXT,                -- what changed
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- analyses table: track analysis runs
CREATE TABLE analyses (
    id TEXT PRIMARY KEY,              -- UUID
    session_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    plan_version INTEGER NOT NULL,
    retrieved_docs INTEGER,
    tokens_used JSON,
    latency_ms JSON,
    langsmith_trace_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_messages_session ON messages(session_id, created_at);
CREATE INDEX idx_business_plans_session ON business_plans(session_id, version DESC);
CREATE INDEX idx_analyses_session ON analyses(session_id, created_at);
```

---

## Component Architecture

### 1. Chainlit App Structure

```
src/vira/ui/
├── chainlit_app.py              # Main Chainlit application
├── components/
│   ├── __init__.py
│   ├── chat_history.py          # Left pane: session list
│   ├── business_plan_editor.py  # Right pane: plan editor
│   └── debug_panel.py           # Collapsible debug view
├── database/
│   ├── __init__.py
│   ├── models.py                # SQLAlchemy models
│   ├── session_manager.py       # CRUD operations
│   └── migrations/
│       └── init_schema.sql
└── state/
    ├── __init__.py
    └── context_manager.py       # Session context handler
```

### 2. Session State Management

```python
# Chainlit user session (in-memory during active session)
cl.user_session.set("session_id", uuid)
cl.user_session.set("current_plan", BusinessPlan)
cl.user_session.set("conversation_history", List[Message])
cl.user_session.set("analyzer", AlignmentAnalyzer)
cl.user_session.set("debug_mode", bool)
```

### 3. Message Flow

```
User Action → Chainlit Handler → State Manager → Backend API → Database
                    ↓                                    ↓
              Update UI  ←────────  LangSmith Trace  ←────┘
```

---

## Implementation Details

### Chainlit Main App

```python
# src/vira/ui/chainlit_app.py

import chainlit as cl
from chainlit.input_widget import Select, Switch
from vira.ui.database.session_manager import SessionManager
from vira.ui.state.context_manager import ContextManager
from vira.rag.pipeline import AlignmentAnalyzer

db = SessionManager("./data/vira_sessions.db")
analyzer = AlignmentAnalyzer()

@cl.on_chat_start
async def start():
    """Initialize new chat session or restore existing one."""
    
    # Settings in sidebar
    settings = await cl.ChatSettings([
        Switch(id="debug_mode", label="Developer Mode", initial=False),
        Select(
            id="load_session",
            label="Load Previous Session",
            values=await get_session_list(),
            initial_value="new"
        )
    ]).send()
    
    # Initialize or load session
    session_id = await initialize_session(settings)
    
    # Load business plan into right pane
    await render_business_plan_editor(session_id)
    
    # Show chat history in left pane
    await render_chat_history_sidebar()
    
    # Welcome message
    await cl.Message(
        content="👋 Welcome to VIRA! Upload or edit your business plan in the right pane, then click **Analyze** to get alignment feedback.",
        author="VIRA"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages."""
    
    session_id = cl.user_session.get("session_id")
    debug_mode = cl.user_session.get("debug_mode", False)
    
    # Save user message to DB
    await db.add_message(session_id, role="user", content=message.content)
    
    # Check for special commands
    if message.content.strip().lower() == "/analyze":
        await handle_analysis_request(session_id, debug_mode)
    else:
        # Regular conversational response
        await handle_conversation(session_id, message.content, debug_mode)


async def handle_analysis_request(session_id: str, debug_mode: bool):
    """Execute business plan analysis with debug info."""
    
    # Get current business plan
    plan = await db.get_latest_plan(session_id)
    
    if not plan:
        await cl.Message(
            content="⚠️ No business plan found. Please add one in the right pane.",
            author="VIRA"
        ).send()
        return
    
    # Show thinking indicator
    async with cl.Step(name="🔍 Analyzing alignment", type="run") as step:
        import time
        start = time.time()
        
        # Retrieve context
        async with cl.Step(name="📚 Retrieving VC criteria", parent_id=step.id) as retrieve_step:
            query = plan.content[:1500]
            # ... retrieval logic
            retrieve_step.output = f"Found {len(docs)} relevant documents"
        
        # LLM analysis
        async with cl.Step(name="🤖 Generating analysis", parent_id=step.id) as llm_step:
            result, retrieved_docs = analyzer.analyze(
                company_name=plan.company_name,
                plan_summary=plan.content,
                query=query
            )
            llm_step.output = f"Generated {len(result.aligns)} alignments, {len(result.gaps)} gaps"
        
        latency = time.time() - start
        
        # Format response
        response = format_alignment_response(result)
        
        # Save to DB with metadata
        message_id = await db.add_message(
            session_id, 
            role="assistant", 
            content=response,
            metadata={
                "analysis_type": "full",
                "retrieved_docs": len(retrieved_docs),
                "latency_ms": latency * 1000
            }
        )
        
        step.output = response
    
    # Show debug panel if enabled
    if debug_mode:
        await render_debug_panel(session_id, message_id, latency, retrieved_docs)


async def render_debug_panel(session_id: str, message_id: str, latency: float, docs):
    """Display developer debug information."""
    
    analysis = await db.get_analysis(message_id)
    
    debug_info = f"""
### 🔍 Debug Information

**Performance:**
- Retrieval: {analysis['latency_ms']['retrieval']:.0f}ms
- LLM Generation: {analysis['latency_ms']['llm']:.0f}ms
- Total: {latency*1000:.0f}ms

**Tokens:**
- Input: {analysis['tokens_used']['input']}
- Output: {analysis['tokens_used']['output']}
- Cost: ${analysis['tokens_used']['cost']:.4f}

**Retrieved Documents:**
{format_retrieved_docs(docs)}

**LangSmith Trace:**
🔗 [View in LangSmith]({analysis['langsmith_trace_url']})
"""
    
    await cl.Message(
        content=debug_info,
        author="Debug",
        language="markdown"
    ).send()


@cl.on_settings_update
async def settings_update(settings):
    """Handle settings changes."""
    
    debug_mode = settings["debug_mode"]
    cl.user_session.set("debug_mode", debug_mode)
    
    if settings["load_session"] != "new":
        await load_session(settings["load_session"])
```

### Business Plan Editor Component

```python
# src/vira/ui/components/business_plan_editor.py

import chainlit as cl

async def render_business_plan_editor(session_id: str):
    """Render business plan editor in right pane using Chainlit's side panel."""
    
    # Get latest plan version
    plan = await db.get_latest_plan(session_id)
    
    # Create editable text area
    plan_element = cl.Text(
        name="business_plan",
        content=plan.content if plan else "",
        display="side",  # Display in side panel
        language="markdown"
    )
    
    await plan_element.send()
    
    # Add action buttons
    actions = [
        cl.Action(
            name="save_plan",
            value="save",
            label="💾 Save Changes",
            description="Save business plan edits"
        ),
        cl.Action(
            name="analyze_plan",
            value="analyze",
            label="🔍 Analyze",
            description="Run alignment analysis"
        ),
        cl.Action(
            name="view_versions",
            value="versions",
            label="📜 View Versions",
            description="See plan edit history"
        )
    ]
    
    await cl.Message(
        content="",
        actions=actions,
        author="Editor"
    ).send()


@cl.action_callback("save_plan")
async def on_save_plan(action: cl.Action):
    """Handle save button click."""
    
    session_id = cl.user_session.get("session_id")
    plan_content = action.value  # Get edited content
    
    # Create new version
    version = await db.save_plan_version(
        session_id=session_id,
        content=plan_content,
        created_by="user"
    )
    
    await cl.Message(
        content=f"✅ Business plan saved (version {version})",
        author="VIRA"
    ).send()


@cl.action_callback("analyze_plan")
async def on_analyze_plan(action: cl.Action):
    """Handle analyze button click."""
    
    session_id = cl.user_session.get("session_id")
    debug_mode = cl.user_session.get("debug_mode", False)
    
    await handle_analysis_request(session_id, debug_mode)
```

---

## Key Features

### 1. **Persistent Chat History**
- All sessions stored in SQLite
- Load previous conversations via dropdown
- Search across all sessions

### 2. **Business Plan Versioning**
- Track every edit
- Diff view between versions
- Rollback capability

### 3. **Developer Debug Mode**
- Toggle in settings
- Shows:
  - Retrieved chunks with scores
  - Token counts and costs
  - Latency breakdown (retrieval vs LLM)
  - LangSmith trace link
  - Intermediate agent steps

### 4. **Context Management**
- Agent always has access to:
  - Full current business plan
  - Entire conversation history
  - Previous analyses for comparison

### 5. **Manual Analysis Trigger**
- User explicitly clicks "Analyze" button
- Agent suggests re-analysis when plan changes detected
- Prevents unnecessary API calls

---

## LangSmith Integration

```python
from langsmith import trace

@trace(name="alignment_analysis")
async def analyze_with_tracing(session_id: str, plan: str, query: str):
    """Wrapped analysis function with LangSmith tracing."""
    
    result, docs = analyzer.analyze(
        company_name=plan.company_name,
        plan_summary=plan,
        query=query
    )
    
    # Get trace URL
    trace_url = cl.context.current_run.get_url()
    
    # Save to DB
    await db.save_analysis(
        session_id=session_id,
        langsmith_trace_url=trace_url,
        retrieved_docs=len(docs)
    )
    
    return result, docs, trace_url
```

---

## Development Workflow

### Setup
```bash
# Install Chainlit
poetry add chainlit sqlalchemy aiosqlite

# Initialize database
python -m vira.ui.database.migrations.init

# Run Chainlit app
chainlit run src/vira/ui/chainlit_app.py -w
```

### File Structure After Implementation
```
src/vira/ui/
├── chainlit_app.py              # 300 lines (main app)
├── components/
│   ├── business_plan_editor.py  # 150 lines
│   ├── debug_panel.py           # 100 lines
│   └── chat_history.py          # 100 lines
├── database/
│   ├── models.py                # 100 lines (SQLAlchemy)
│   ├── session_manager.py       # 200 lines (CRUD)
│   └── migrations/
│       └── init_schema.sql      # 50 lines
└── state/
    └── context_manager.py       # 150 lines

Total: ~1,150 lines of new code
```

---

## Next Steps

1. **Database Setup** - Create SQLite schema and session manager
2. **Chainlit Scaffold** - Basic 3-pane layout with mock data
3. **Business Plan Editor** - Integrate editable text area with versioning
4. **Analysis Pipeline** - Connect to existing `AlignmentAnalyzer`
5. **Debug Mode** - Add performance metrics and LangSmith links
6. **Polish** - Styling, error handling, loading states

**Estimated Time:** 1-2 days for MVP, 3-4 days for production-ready

---

**Ready to implement?** Let me know if you want me to:
1. Start with database schema + session manager
2. Build Chainlit scaffold first and iterate
3. Create a different component structure

Your call!

