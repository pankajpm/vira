# VIRA Cursor Rules - Compact (Critical Rules Only)

**Version**: 2.1  
**Last Updated**: January 8, 2026  
**Purpose**: Context-optimized version containing only CRITICAL rules  
**Full Version**: See `.cursorrules` and `.cursor/rules/*.mdc` for complete details

---

## Usage

This file contains only CRITICAL rules - patterns that prevent bugs, security issues, or system failures. Use this when context window space is limited. For complete rules with examples and rationale, see the full rule files.

---

## Python Backend (CRITICAL)

### Type Safety
- **PY-001**: Use `str | None` not `Optional[str]` (Python 3.10+)
- **PY-002**: Type all function signatures with complete annotations
- **PY-003**: Use TypedDict for structured dicts, not `dict[str, Any]`
- **PY-004**: Use Pydantic models for API request/response validation

### Async Patterns
- **PY-005**: Use `async def` for all I/O operations (LLM, database, HTTP)
- **PY-006**: Use async context managers (`async with`) for resources
- **PY-007**: Proper exception handling in async code

### LangChain Integration
- **PY-008**: Always specify temperature when creating LLM instances
- **PY-009**: Log token usage for all LLM calls
- **PY-010**: Use structured outputs with Pydantic models

---

## LangGraph Agents (CRITICAL)

### State Management
- **LG-001**: Use TypedDict with `total=False` for AgentState
- **LG-002**: Never raise exceptions in nodes - set `state["error"]` instead
- **LG-003**: Node signature: `(state: AgentState) -> AgentState`
- **LG-004**: Return updated state, never mutate without returning

### Observability
- **LG-005**: Use structured logging with phase and status tags
  - `logger.info("msg", extra={"phase": "analysis", "status": "started"})`
- **LG-006**: Never use print statements - always use logger
- **LG-007**: Log all state transitions and routing decisions

### Routing
- **LG-008**: Use Literal types for routing return values
- **LG-009**: Always include END route in conditional edges
- **LG-010**: Document routing logic in router function docstrings

### Error Handling
- **LG-011**: Graceful error handling - continue workflow even when nodes fail
- **LG-012**: Validate required state fields before critical operations
- **LG-013**: Set `state["error"]` with descriptive message, never raise

---

## TypeScript/React (CRITICAL)

### Type Safety
- **TS-001**: Avoid `any` - use `unknown` with type guards
- **TS-002**: Type all component props with interfaces
- **TS-003**: Use discriminated unions for complex state
- **TS-004**: Type all function signatures completely

### WebSocket Management
- **TS-005**: Always cleanup WebSocket in useEffect return function
- **TS-006**: Use refs for WebSocket instances, not state
- **TS-007**: Implement connection error handling and reconnection logic

### State Management
- **TS-008**: Proper useEffect cleanup for all subscriptions
- **TS-009**: Cancel pending requests on component unmount (AbortController)
- **TS-010**: Use refs for tracking in-flight operations

---

## Real-Time UI (CRITICAL)

### Optimistic Updates
- **RT-001**: Implement rollback logic for failed optimistic updates
- **RT-002**: Use flags to prevent server state from overwriting optimistic state
- **RT-003**: Show loading states during server synchronization

### WebSocket Patterns
- **RT-004**: Queue messages during disconnection periods
- **RT-005**: Implement exponential backoff for reconnection
- **RT-006**: Always validate incoming WebSocket messages

---

## Configuration (CRITICAL)

### Feature Flags
- **CF-001**: Check feature flags before using iteration-specific features
- **CF-002**: Document which iteration introduces each feature flag
- **CF-003**: Use Settings fields for iteration control, not env vars directly

### Settings Management
- **CF-004**: Use Field with alias for env var mapping
- **CF-005**: Provide sensible defaults for all settings
- **CF-006**: Use Path type for file paths
- **CF-007**: Use get_settings() singleton, never create Settings() directly

---

## Error Handling (CRITICAL)

### Structured Logging
- **EH-001**: Use structured logging with semantic tags (phase, status)
- **EH-002**: Always include context (session_id, error, duration_ms)
- **EH-003**: Never use print statements - always use logger
- **EH-004**: Log errors with exc_info=True for stack traces

### Exception Handling
- **EH-005**: Catch specific exceptions, not bare except
- **EH-006**: Set state["error"] in agent nodes instead of raising
- **EH-007**: Always handle exceptions in async contexts
- **EH-008**: Log all exceptions with structured context

---

## Iteration Development (CRITICAL)

### Feature Flags
- **IT-001**: Gate new features behind feature flags in Settings
- **IT-002**: Check flags before using iteration-specific code
- **IT-003**: Iteration N must work with Iteration N-1 disabled

### Backward Compatibility
- **IT-004**: Add new fields as optional in Pydantic models
- **IT-005**: Use graceful degradation when features disabled
- **IT-006**: Test with all iteration flag combinations

---

## Security (CRITICAL)

### Input Validation
- **SEC-001**: Validate all user inputs before processing
- **SEC-002**: Sanitize inputs to prevent injection attacks
- **SEC-003**: Use parameterized queries, never string interpolation

### Secret Management
- **SEC-004**: Use environment variables for all secrets/API keys
- **SEC-005**: Never commit secrets to version control
- **SEC-006**: Validate environment variables on startup

### Authentication & Authorization
- **SEC-007**: Check permissions before allowing operations
- **SEC-008**: Validate session tokens on all protected endpoints
- **SEC-009**: Use HTTPS for all external communications

---

## Testing (CRITICAL)

### LLM Testing
- **TEST-001**: Mock all LLM calls with pre-recorded responses
- **TEST-002**: Never make actual API calls in tests
- **TEST-003**: Test with different LLM configurations

### State Testing
- **TEST-004**: Test each LangGraph node in isolation
- **TEST-005**: Test all routing decisions with various states
- **TEST-006**: Test error paths and state["error"] handling

### Integration Testing
- **TEST-007**: Test complete agent workflows end-to-end
- **TEST-008**: Verify workflows handle errors gracefully
- **TEST-009**: Test WebSocket connections and cleanup

---

## Code Quality (CRITICAL)

### Import Organization
- **CQ-001**: Run isort before committing (automated)
- **CQ-002**: Use absolute imports over relative when possible

### TODO Management (Phase-Based)
- **CQ-003**: Prototype: Informal TODOs acceptable
- **CQ-004**: Pre-Production: All TODOs must reference issues
- **CQ-005**: Production: No TODOs without issue references

### Debugging
- **CQ-006**: Remove all print statements before committing
- **CQ-007**: Use logger.debug() for debugging, not print()
- **CQ-008**: Remove debug code before committing

---

## Phase-Based Rule Application

| Phase | Rules Applied | Description |
|-------|---------------|-------------|
| Phase 0 (Spike) | NONE | Rapid exploration |
| Phase 1 (Prototype) | CRITICAL | Working MVP |
| Phase 2 (Alpha) | CRITICAL + IMPORTANT | Tested & documented |
| Phase 3 (Production) | ALL | Production-ready |

See `.cursor/DEVELOPMENT_PHASES.md` for complete phase guidelines.

---

## Quick Reference Template

### LangGraph Node Template
```python
import logging
from typing import TypedDict

logger = logging.getLogger(__name__)

class MyState(TypedDict, total=False):
    input: str
    result: dict | None
    error: str | None

def my_node(state: MyState) -> MyState:
    logger.info("Node started", extra={"phase": "processing", "status": "started"})
    try:
        state["result"] = process(state["input"])
        logger.info("Node completed", extra={"phase": "processing", "status": "completed"})
    except Exception as e:
        logger.error("Node failed", extra={"phase": "processing", "status": "failed", "error": str(e)})
        state["error"] = str(e)
    return state
```

### React Component with WebSocket
```typescript
import { useEffect, useRef } from 'react';

const Component: React.FC<Props> = ({ sessionId }) => {
  const wsRef = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    if (!sessionId) return;
    const ws = new WebSocket(`ws://localhost:8001/ws/${sessionId}`);
    wsRef.current = ws;
    
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [sessionId]);
  
  return <div>...</div>;
};
```

### Feature Flag Usage
```python
from vira.config.settings import get_settings

settings = get_settings()
if settings.enable_new_feature:
    result = await new_implementation()
else:
    result = await legacy_implementation()
```

---

## Common Violations to Watch For

1. Using `print()` instead of `logger` - **Violation of EH-003**
2. Using `Optional[T]` instead of `T | None` - **Violation of PY-001**
3. Forgetting WebSocket cleanup - **Violation of TS-005**
4. Raising exceptions in nodes - **Violation of LG-002**
5. Not checking feature flags - **Violation of CF-001**
6. Missing type hints - **Violation of PY-002**
7. Using `any` in TypeScript - **Violation of TS-001**
8. Not logging with structured tags - **Violation of EH-001**

---

## Getting More Details

- **Quick Start**: `.cursor/QUICKSTART.md` (2-page guide)
- **Full Rules**: `.cursor/rules/*.mdc` (11 detailed files)
- **Main Index**: `.cursorrules` (consolidated overview)
- **Development Phases**: `.cursor/DEVELOPMENT_PHASES.md`
- **Testing**: `.cursor/rules/11-testing-patterns.mdc`

---

**Total Critical Rules**: 70+  
**Rule Format**: `DOMAIN-NNN` (e.g., PY-001, LG-002, TS-003)  
**Enforcement**: CRITICAL rules always enforced, regardless of phase (except Phase 0)
