# VIRA Cursor Rules - Quick Start Guide

**Version**: 2.1  
**Last Updated**: January 8, 2026

---

## Decision Tree: Which Rules Apply?

```
START
  |
  ├─ Writing Python backend code?
  │   ├─ Basic Python patterns? → 01-python-backend.mdc [CRITICAL sections]
  │   ├─ LangGraph agents? → 02-langgraph-agents.mdc [CRITICAL sections]
  │   └─ Configuration? → 05-configuration.mdc [CRITICAL sections]
  |
  ├─ Writing React/TypeScript frontend?
  │   ├─ Basic React patterns? → 03-typescript-react.mdc [CRITICAL sections]
  │   ├─ WebSocket/real-time? → 04-realtime-ui.mdc [CRITICAL sections]
  │   └─ API integration? → 03-typescript-react.mdc [API section]
  |
  ├─ Handling errors/logging?
  │   └─ All errors/logging → 06-error-handling.mdc [CRITICAL sections]
  |
  ├─ Writing documentation?
  │   └─ Docs/comments → 07-documentation.mdc [IMPORTANT sections]
  |
  ├─ Managing iterations/features?
  │   └─ Feature flags → 08-iteration-dev.mdc [CRITICAL sections]
  |
  ├─ Code cleanup/quality?
  │   └─ Refactoring/TODOs → 09-code-quality.mdc [IMPORTANT sections]
  |
  ├─ Writing prompts for LLMs?
  │   └─ Prompt engineering → 10-prompt-engineering.mdc [IMPORTANT sections]
  |
  ├─ Writing tests?
  │   └─ Testing → 11-testing-patterns.mdc [IMPORTANT sections]
  |
  └─ Committing code/creating PRs?
      └─ Git/GitHub → 12-git-github.mdc [CRITICAL & IMPORTANT sections]
```

---

## Priority System

### CRITICAL (Always Enforce)
These rules prevent bugs, security issues, or system failures. **Never skip these.**

### IMPORTANT (Domain-Specific Enforcement)
These rules improve code quality and maintainability. **Enforce during code review.**

### GUIDANCE (Style & Convention)
These rules improve consistency. **Apply when convenient, don't block progress.**

---

## Top 10 Critical Rules (Must Know)

### Backend
1. **[CRITICAL] Type Safety**: Use `str | None` not `Optional[str]` (Python 3.10+)
2. **[CRITICAL] Error Handling**: Never raise in LangGraph nodes - set `state["error"]`
3. **[CRITICAL] State Management**: Use TypedDict for AgentState
4. **[CRITICAL] Async Patterns**: Use async/await for all I/O operations
5. **[CRITICAL] Feature Flags**: Check flags before using iteration-specific features

### Frontend
6. **[CRITICAL] WebSocket Cleanup**: Always cleanup in useEffect return functions
7. **[CRITICAL] Type Safety**: Avoid `any` - use `unknown` with type guards
8. **[CRITICAL] Optimistic Updates**: Implement rollback logic on errors

### General
9. **[CRITICAL] Security**: Validate inputs, use env vars for secrets, parameterized queries
10. **[CRITICAL] Structured Logging**: Use logger with semantic tags (phase, status), never use print
11. **[CRITICAL] Commit Messages**: Use Conventional Commits (feat, fix, refactor, etc.)
12. **[CRITICAL] Pre-Commit Cleanup**: Remove prints, commented code; run black, isort, ruff

---

## Common Task Quick Reference

### Task: Create a new LangGraph agent node

**Rules**: 02-langgraph-agents.mdc [CRITICAL]

**Pattern**:
```python
import logging
from typing import TypedDict

logger = logging.getLogger(__name__)

class AgentState(TypedDict, total=False):
    input_data: str
    result: dict | None
    error: str | None

def my_node(state: AgentState) -> AgentState:
    """Process data in this node."""
    logger.info("Node started", extra={"phase": "processing", "status": "started"})
    
    try:
        result = process(state["input_data"])
        state["result"] = result
        logger.info("Node completed", extra={"phase": "processing", "status": "completed"})
    except Exception as e:
        logger.error("Node failed", extra={"phase": "processing", "status": "failed", "error": str(e)})
        state["error"] = str(e)
    
    return state
```

### Task: Create a React component with WebSocket

**Rules**: 03-typescript-react.mdc, 04-realtime-ui.mdc [CRITICAL]

**Pattern**:
```typescript
import { useEffect, useRef } from 'react';

const Component: React.FC<Props> = ({ sessionId }) => {
  const wsRef = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    if (!sessionId) return;
    
    const ws = new WebSocket(`ws://localhost:8001/ws/${sessionId}`);
    wsRef.current = ws;
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleMessage(data);
    };
    
    // CRITICAL: Cleanup
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [sessionId]);
  
  return <div>...</div>;
};
```

### Task: Add a feature flag for new iteration

**Rules**: 08-iteration-dev.mdc [CRITICAL]

**Pattern**:
```python
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Iteration 3: Multi-agent committee
    enable_multi_agent: bool = Field(default=False, alias="ENABLE_MULTI_AGENT")

# Usage
settings = get_settings()
if settings.enable_multi_agent:
    result = await multi_agent_analyzer.analyze(request)
else:
    result = await basic_analyzer.analyze(request)
```

### Task: Add structured error handling

**Rules**: 06-error-handling.mdc [CRITICAL]

**Pattern**:
```python
import logging

logger = logging.getLogger(__name__)

async def call_api(url: str) -> dict | None:
    """Call API with structured error handling."""
    logger.info("API call started", extra={"phase": "api", "status": "started", "url": url})
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            logger.info("API call succeeded", extra={"phase": "api", "status": "completed"})
            return response.json()
            
    except httpx.HTTPError as e:
        logger.error("API call failed", extra={
            "phase": "api", 
            "status": "failed", 
            "error": str(e),
            "url": url
        }, exc_info=True)
        return None
```

### Task: Write a module docstring

**Rules**: 07-documentation.mdc [IMPORTANT]

**Pattern**:
```python
"""Agent module for reflection and self-critique.

Iteration 2: Implements reflection agent that analyzes alignment explanations
for completeness and identifies information gaps requiring research.

This module is only active when ENABLE_REFLECTION=true.

Example:
    ```python
    from vira.agents.reflection import reflect_on_explanation
    
    reflection = reflect_on_explanation(explanation, docs, llm)
    if reflection.confidence < 0.7:
        gaps = reflection.information_gaps
    ```
"""
```

### Task: Create a commit or PR

**Rules**: 12-git-github.mdc [CRITICAL]

**Pattern**:
```bash
# Format code first
black src/ tests/
isort src/ tests/
ruff check --fix src/

# Commit with Conventional Commits format
git commit -m "feat(iter-2): Add reflection agent with confidence scoring

Implements the reflection agent that analyzes alignment explanations
for completeness and identifies information gaps requiring research.

Closes #42"

# Create PR with template
gh pr create --title "feat(iter-2): Add reflection agent" \
             --body "$(cat <<EOF
## Summary
Adds reflection agent for Iteration 2 self-aware analysis.

## Changes
- Add ReflectionAgent class
- Extend AgentState with reflection fields
- Add unit tests

## Phase Checklist
- [x] All CRITICAL rules followed
- [x] Tests added
- [x] Documentation updated

## Related Issues
Closes #42
EOF
)"
```

---

## File Organization Reference

### Backend Code
```
src/vira/
├── agents/          → 02-langgraph-agents.mdc
├── rag/             → 01-python-backend.mdc
├── backend/         → 01-python-backend.mdc
├── config/          → 05-configuration.mdc
└── retrieval/       → 01-python-backend.mdc
```

### Frontend Code
```
frontend/src/
├── components/      → 03-typescript-react.mdc
├── hooks/           → 03-typescript-react.mdc, 04-realtime-ui.mdc
├── api/             → 03-typescript-react.mdc
└── types/           → 03-typescript-react.mdc
```

---

## When in Doubt

1. **Check priority**: Focus on [CRITICAL] rules first
2. **Use the template**: Most files have complete working templates
3. **Search for examples**: All rules have good/bad code examples
4. **Check cross-references**: Rules link to related sections
5. **Ask for clarification**: Better to ask than guess

---

## Development Phase Guidelines

### Prototype/Spike
- Apply [CRITICAL] rules only
- Informal TODOs acceptable
- Focus on functionality

### Pre-Production (Before PR)
- Apply [CRITICAL] + [IMPORTANT] rules
- Add issue references to TODOs
- Add basic documentation

### Production (Deployed)
- Apply all rule tiers
- Full documentation
- Complete error handling
- No TODOs without issue references

---

## Quick Command Reference

```bash
# Pre-commit checks
black src/ tests/
isort src/ tests/
ruff check --fix src/ tests/
mypy src/

# Search for rule violations
rg "TODO(?!\(#\d+\))" --type py  # TODOs without issues
rg "print\(" --type py           # Print statements (use logger)
rg "Optional\[" --type py        # Old union syntax

# Git workflow
git checkout -b feature/my-feature
git commit -m "feat(scope): description"
gh pr create --title "feat(scope): description"

# Start services
./start_services.sh
```

---

## Getting More Details

- **Full rule set**: See `.cursor/rules/*.mdc` files
- **Main index**: See `.cursorrules`
- **Implementation summary**: See `.cursor/RULES_IMPLEMENTATION_SUMMARY.md`
- **Compact version**: See `.cursor/cursorrules-compact.md` (after Phase 4)

---

**Remember**: Rules exist to help, not hinder. When a rule conflicts with pragmatic needs, document why you're deviating and discuss in code review.
