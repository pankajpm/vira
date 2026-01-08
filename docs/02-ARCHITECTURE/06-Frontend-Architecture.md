# VIRA: Frontend Architecture

**Version:** 1.0  
**Last Updated:** November 25, 2025  
**Status:** ✅ Chainlit Implemented, React Available

---

## Overview

VIRA provides two frontend implementations:
1. **Chainlit** (Primary) - Chat-based UI with session management
2. **React** (Alternative) - Component-based modern UI

### Why Two UIs?

- **Chainlit:** Optimized for conversational workflows, built-in session handling
- **React:** Flexible for custom components, better for complex UIs

---

## Chainlit Implementation (Primary)

### Structure

```
src/vira/ui/
├── chainlit_app.py               # Main app (497 lines)
├── components/
│   ├── chat_history.py           # Session list sidebar
│   ├── business_plan_editor.py   # Plan viewer/editor
│   └── debug_panel.py            # Performance metrics
├── database/
│   ├── models.py                 # SQLAlchemy models
│   └── session_manager.py        # DB operations
├── state/
│   └── context_manager.py        # Chat context
└── utils/
    ├── token_counter.py          # Token estimation
    └── langsmith_integration.py  # Observability
```

### Main Application

**File:** `src/vira/ui/chainlit_app.py`

```python
import chainlit as cl
from vira.ui.database.session_manager import SessionManager
from vira.ui.state.context_manager import ContextManager
from vira.ui.components.debug_panel import DebugPanel
from vira.config.settings import get_settings

settings = get_settings()
db = SessionManager("./data/vira_sessions.db")

# Initialize analyzers
from vira.rag.pipeline import AlignmentAnalyzer
analyzer_v1 = AlignmentAnalyzer()

if settings.enable_reflection:
    from vira.agents.analyzer import ReflectiveAnalyzer
    analyzer_v2 = ReflectiveAnalyzer()
else:
    analyzer_v2 = None

active_analyzer = analyzer_v2 or analyzer_v1

@cl.on_chat_start
async def start():
    """
    Initialize new chat session.
    
    Flow:
    1. Create database session
    2. Initialize context manager
    3. Send welcome message
    """
    # Create session in DB
    session = db.create_session()
    
    # Initialize context manager
    context = ContextManager(session.id)
    cl.user_session.set("context", context)
    
    # Welcome message
    await cl.Message(
        content="Welcome to VIRA! Paste your business plan to begin analysis.",
        author="VIRA"
    ).send()
    
    # Show session ID for reference
    await cl.Message(
        content=f"Session ID: `{session.id}`\nType `/help` for available commands.",
        author="System"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming user messages.
    
    Message Types:
    - First message → Save as business plan
    - Commands (/ prefix) → Execute command
    - "analyze" / "yes" → Run analysis
    - Other → General chat (future)
    """
    context = cl.user_session.get("context")
    
    # Handle file uploads
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.File):
                await handle_file_upload(element, context)
                return
    
    # Check if first message (business plan)
    if not context.has_plan():
        # Save plan
        plan = db.save_business_plan(
            session_id=context.session_id,
            content=message.content,
            version=1
        )
        context.set_plan(plan)
        
        # Extract company name
        company_name = extract_company_name(message.content)
        if company_name:
            db.update_session(context.session_id, company_name=company_name)
        
        await cl.Message(
            content="✅ Business plan saved! Type `analyze` or `yes` to begin analysis.",
            author="VIRA"
        ).send()
        return
    
    # Handle commands
    if message.content.startswith('/'):
        await handle_command(message.content, context)
        return
    
    # Handle analysis trigger
    if message.content.lower() in ['analyze', 'yes', 'ok']:
        await run_analysis(context)
        return
    
    # Future: General conversation
    await cl.Message(
        content="I can analyze your business plan. Type `analyze` to begin.",
        author="VIRA"
    ).send()

async def run_analysis(context: ContextManager):
    """
    Run alignment analysis with progress steps.
    
    Steps shown to user:
    1. Retrieving relevant VC criteria
    2. Analyzing alignment
    3. (Iteration 2) Reflecting on analysis
    4. (Iteration 2) Conducting research
    5. Generating final report
    """
    # Retrieve plan and session
    plan = db.get_latest_plan(context.session_id)
    session = db.get_session(context.session_id)
    
    if not plan or not session:
        await cl.Message(
            content="❌ Error: Could not retrieve plan or session.",
            author="System"
        ).send()
        return
    
    # Show progress
    async with cl.Step(name="Analyzing alignment...", type="run") as main_step:
        
        # Step 1: Retrieval
        async with cl.Step(name="Retrieving VC criteria", type="tool") as step:
            step.output = "Searching vector database..."
        
        # Step 2: Analysis
        async with cl.Step(name="Generating analysis", type="llm") as step:
            if analyzer_v2:
                # Iteration 2: Show reflection steps
                result, metadata = await run_iteration2_analysis(
                    session.company_name, 
                    plan.content
                )
            else:
                # Iteration 1: Basic RAG
                result, docs = active_analyzer.analyze(
                    company_name=session.company_name,
                    plan_summary=plan.content[:1500],
                    query=plan.content[:1500]
                )
                metadata = {"num_docs": len(docs)}
            
            step.output = "Analysis complete"
        
        main_step.output = "✅ Analysis finished"
    
    # Format and send results
    formatted = format_two_column_analysis(result)
    await cl.Message(
        content=formatted,
        author="VIRA"
    ).send()
    
    # Show debug panel if enabled
    if settings.developer_mode:
        debug_html = DebugPanel.render(metadata)
        await cl.Message(
            content=debug_html,
            author="Debug"
        ).send()
    
    # Save analysis to DB
    db.save_analysis(
        session_id=context.session_id,
        plan_version=plan.version,
        result=result.model_dump_json(),
        metadata=metadata
    )

async def handle_command(command: str, context: ContextManager):
    """
    Handle slash commands.
    
    Commands:
    - /help → Show help message
    - /versions → Show plan version history
    - /sessions → List recent sessions
    - /load <id> → Load previous session
    - /editor → Show plan editor
    - /diff <v1> <v2> → Compare plan versions
    """
    parts = command.split()
    cmd = parts[0].lower()
    
    if cmd == '/help':
        await show_help()
    
    elif cmd == '/versions':
        versions = db.get_all_plan_versions(context.session_id)
        version_list = "\n".join([
            f"v{v.version}: {v.created_at} ({len(v.content)} chars)"
            for v in versions
        ])
        await cl.Message(
            content=f"**Plan Versions:**\n{version_list}",
            author="System"
        ).send()
    
    elif cmd == '/sessions':
        sessions = db.list_sessions(limit=20)
        session_list = "\n".join([
            f"• {s.id[:8]}: {s.company_name or 'Unnamed'} ({s.created_at})"
            for s in sessions
        ])
        await cl.Message(
            content=f"**Recent Sessions:**\n{session_list}",
            author="System"
        ).send()
    
    # ... other commands
```

### Two-Column Layout

```python
def format_two_column_analysis(result: AlignmentResponse) -> str:
    """
    Format analysis as HTML two-column layout.
    
    Uses CSS Grid for responsive design:
    - Desktop: 2 columns side-by-side
    - Mobile: Stacked single column
    """
    return f"""
<div style="margin-bottom: 20px;">
    <h2>Alignment Analysis: {result.company_name} vs a16z</h2>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
    <div style="border: 2px solid #27ae60; border-radius: 8px; padding: 15px;">
        <h3 style="color: #27ae60;">✓ HOW THIS PLAN ALIGNS</h3>
        <ul>
            {"".join([f"<li><strong>{a.description}</strong><br/>{a.evidence}<br/><a href='{a.source}' target='_blank'>{a.source}</a></li>" for a in result.aligns])}
        </ul>
    </div>
    
    <div style="border: 2px solid #e74c3c; border-radius: 8px; padding: 15px;">
        <h3 style="color: #e74c3c;">✗ HOW THIS PLAN DOESN'T ALIGN</h3>
        <ul>
            {"".join([f"<li><strong>{g.description}</strong><br/>{g.evidence}<br/><a href='{g.source}' target='_blank'>{g.source}</a></li>" for g in result.gaps])}
        </ul>
    </div>
</div>

<div style="border: 1px solid #3498db; border-radius: 8px; padding: 15px; margin-top: 20px;">
    <h3 style="color: #3498db;">SUMMARY</h3>
    <p>{result.summary}</p>
</div>
"""
```

---

## Database Layer

### SQLAlchemy Models

**File:** `src/vira/ui/database/models.py`

```python
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Session(Base):
    """Chat session model."""
    __tablename__ = 'sessions'
    
    id = Column(String, primary_key=True)
    company_name = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    status = Column(String, default='active')  # active, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    """Chat message model."""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_messages_session', 'session_id'),
    )

class BusinessPlan(Base):
    """Versioned business plan model."""
    __tablename__ = 'business_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(String, default='user')  # user, system
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_business_plans_session', 'session_id'),
    )

class Analysis(Base):
    """Analysis run metadata model."""
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False)
    plan_version = Column(Integer, nullable=False)
    result = Column(Text, nullable=False)  # JSON serialized AlignmentResponse
    metadata = Column(Text, nullable=True)  # Performance metrics, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_analyses_session', 'session_id'),
    )
```

### Session Manager

**File:** `src/vira/ui/database/session_manager.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DBSession
from vira.ui.database.models import Base, Session, Message, BusinessPlan, Analysis
import uuid

class SessionManager:
    """Manage database operations for chat sessions."""
    
    def __init__(self, db_path: str):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_session(self, company_name: str = None, user_id: str = None) -> Session:
        """Create new chat session."""
        db = self.SessionLocal()
        try:
            session = Session(
                id=str(uuid.uuid4()),
                company_name=company_name,
                user_id=user_id
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session
        finally:
            db.close()
    
    def get_session(self, session_id: str) -> Session:
        """Get session by ID."""
        db = self.SessionLocal()
        try:
            return db.query(Session).filter(Session.id == session_id).first()
        finally:
            db.close()
    
    def save_business_plan(
        self, 
        session_id: str, 
        content: str, 
        version: int = 1
    ) -> BusinessPlan:
        """Save business plan version."""
        db = self.SessionLocal()
        try:
            plan = BusinessPlan(
                session_id=session_id,
                version=version,
                content=content
            )
            db.add(plan)
            db.commit()
            db.refresh(plan)
            return plan
        finally:
            db.close()
    
    def get_latest_plan(self, session_id: str) -> BusinessPlan:
        """Get latest plan version."""
        db = self.SessionLocal()
        try:
            return db.query(BusinessPlan).filter(
                BusinessPlan.session_id == session_id
            ).order_by(BusinessPlan.version.desc()).first()
        finally:
            db.close()
```

---

## React Implementation (Alternative)

### Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.tsx                    # Main app component
│   ├── components/
│   │   ├── BusinessPlanInput.tsx  # Plan input form
│   │   ├── AnalysisDisplay.tsx    # Results display
│   │   └── SessionList.tsx        # Session sidebar
│   ├── services/
│   │   └── api.ts                 # Backend API client
│   ├── types/
│   │   └── index.ts               # TypeScript types
│   └── index.tsx                  # Entry point
├── package.json
└── tsconfig.json
```

### Main App Component

**File:** `frontend/src/App.tsx`

```typescript
import React, { useState } from 'react';
import BusinessPlanInput from './components/BusinessPlanInput';
import AnalysisDisplay from './components/AnalysisDisplay';
import { analyzeBusinessPlan } from './services/api';
import { AnalysisResponse } from './types';

function App() {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const handleAnalyze = async (companyName: string, planText: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await analyzeBusinessPlan(companyName, planText);
      setAnalysis(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="App">
      <header>
        <h1>VIRA - Venture Intelligence Research Assistant</h1>
      </header>
      
      <main>
        <BusinessPlanInput onAnalyze={handleAnalyze} loading={loading} />
        
        {error && (
          <div className="error">
            Error: {error}
          </div>
        )}
        
        {analysis && (
          <AnalysisDisplay analysis={analysis} />
        )}
      </main>
    </div>
  );
}

export default App;
```

### API Client

**File:** `frontend/src/services/api.ts`

```typescript
const API_BASE_URL = 'http://localhost:8001';

export interface AnalysisRequest {
  company_name: string;
  plan_text: string;
}

export interface AnalysisResponse {
  company_name: string;
  aligns: AlignmentPoint[];
  gaps: AlignmentPoint[];
  summary: string;
  sources: string[];
}

export async function analyzeBusinessPlan(
  companyName: string, 
  planText: string
): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      company_name: companyName,
      plan_text: planText,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }
  
  return await response.json();
}
```

---

## State Management

### Context Manager

**File:** `src/vira/ui/state/context_manager.py`

```python
class ContextManager:
    """Manage conversation context within a session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._plan = None
        self._analysis_history = []
    
    def has_plan(self) -> bool:
        """Check if business plan has been provided."""
        return self._plan is not None
    
    def set_plan(self, plan: BusinessPlan):
        """Set current business plan."""
        self._plan = plan
    
    def get_plan(self) -> BusinessPlan:
        """Get current business plan."""
        return self._plan
    
    def add_analysis(self, analysis: dict):
        """Add analysis to history."""
        self._analysis_history.append(analysis)
    
    def get_latest_analysis(self) -> dict:
        """Get most recent analysis."""
        return self._analysis_history[-1] if self._analysis_history else None
```

---

## Performance Considerations

### Token Counting

**File:** `src/vira/ui/utils/token_counter.py`

```python
import tiktoken

def estimate_tokens_accurate(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Accurately count tokens using tiktoken.
    
    Args:
        text: Input text
        model: Model name for encoding
        
    Returns:
        Token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimate
        return len(text) // 4

def calculate_cost(
    input_tokens: int, 
    output_tokens: int,
    model: str = "gpt-4o-mini"
) -> float:
    """
    Calculate cost for OpenAI API call.
    
    GPT-4o-mini pricing:
    - Input: $0.15 per 1M tokens
    - Output: $0.60 per 1M tokens
    """
    if model == "gpt-4o-mini":
        input_cost = (input_tokens / 1_000_000) * 0.15
        output_cost = (output_tokens / 1_000_000) * 0.60
        return input_cost + output_cost
    else:
        return 0.0
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | November 25, 2025 | VIRA Team | Initial frontend architecture documentation |

---

## Related Documents

- **System Architecture:** [`00-System-Architecture-Overview.md`](./00-System-Architecture-Overview.md)
- **Backend Architecture:** [`05-Backend-Architecture.md`](./05-Backend-Architecture.md)
- **UI Implementation:** [`../04-IMPLEMENTATION/05-UI-Implementation.md`](../04-IMPLEMENTATION/05-UI-Implementation.md)

---

**End of Document**

