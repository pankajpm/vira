# Development Phase Guidelines

**Version**: 2.1  
**Last Updated**: January 8, 2026

---

## Overview

VIRA follows a phased development approach where different levels of code quality and documentation are expected depending on the phase. This document defines what rules apply at each phase.

---

## Phase Definitions

### Phase 0: Spike/Exploration
**Duration**: Hours to days  
**Purpose**: Validate ideas, test feasibility, explore solutions  
**Team**: Individual developer

**Rules Applied**: **NONE**
- No rule enforcement
- Quick and dirty code acceptable
- No documentation required
- No tests required
- Code may be thrown away

**Exit Criteria**:
- Feasibility validated OR
- Approach rejected
- Decision to proceed or pivot

---

### Phase 1: Prototype
**Duration**: Days to 1-2 weeks  
**Purpose**: Build working MVP, validate approach  
**Team**: 1-2 developers

**Rules Applied**: **CRITICAL only**
- Type safety (use `str | None`, TypedDict)
- Error handling in nodes (set `state["error"]`)
- Structured logging (no print statements)
- WebSocket cleanup in useEffect
- Feature flags for new functionality
- Security basics (env vars, input validation)

**NOT Required**:
- Documentation (beyond minimal docstrings)
- Tests (can defer)
- TODOs with issue references (informal OK)
- Code organization perfection
- Performance optimization

**Deliverables**:
- Working prototype demonstrating core functionality
- Basic README with setup instructions
- Identified risks and unknowns

**Exit Criteria**:
- Core functionality works end-to-end
- Product owner approves approach
- Ready to harden for alpha testing

---

### Phase 2: Alpha/Pre-Production
**Duration**: 1-3 weeks  
**Purpose**: Harden code, add testing, prepare for real users  
**Team**: 2-4 developers

**Rules Applied**: **CRITICAL + IMPORTANT**
- All CRITICAL rules (from Phase 1)
- Async patterns (proper async/await)
- LangGraph best practices (routing, state management)
- React patterns (proper hooks, type safety)
- Error recovery and graceful degradation
- Basic documentation (module docstrings)
- Issue references for all TODOs
- Code organization (reasonable file sizes)

**NOW Required**:
- Unit tests for critical paths
- Integration tests for workflows
- Module-level documentation
- TODOs reference GitHub issues
- Code review before merge

**Deliverables**:
- Tested codebase with >60% coverage on critical paths
- Module docstrings for all major components
- Architecture documentation (if new patterns)
- Deployment guide

**Exit Criteria**:
- All CRITICAL and IMPORTANT rules pass
- Tests cover critical user paths
- Code reviewed and approved
- Ready for beta testing with real users

---

### Phase 3: Production
**Duration**: Ongoing  
**Purpose**: Maintain high quality, reliability, and observability  
**Team**: Full team

**Rules Applied**: **ALL (CRITICAL + IMPORTANT + GUIDANCE)**
- All rules from Phase 2
- Complete documentation (ADRs, API docs)
- High test coverage (>80% on critical paths)
- Performance optimization
- Monitoring and observability
- Code quality standards (no commented code, organized imports)
- Refactoring for maintainability

**NOW Required**:
- Comprehensive test suite
- Complete API documentation
- ADRs for architectural decisions
- Performance benchmarks
- Monitoring dashboards
- Production readiness checklist

**Deliverables**:
- Production-ready codebase
- Complete documentation
- Monitoring and alerting configured
- Runbooks for operations
- Performance SLAs defined

**Maintenance**:
- Regular dependency updates
- Quarterly code quality reviews
- Performance monitoring
- Security audits

---

## Phase Transition Checklist

### Phase 0 → Phase 1 (Spike to Prototype)

- [ ] Spike validated feasibility
- [ ] Core approach approved by tech lead
- [ ] Create feature branch
- [ ] Apply CRITICAL rules
- [ ] Add structured logging
- [ ] Add basic error handling
- [ ] Create minimal README

### Phase 1 → Phase 2 (Prototype to Alpha)

- [ ] Prototype demonstrates core functionality
- [ ] Product owner approved approach
- [ ] Add unit tests for nodes
- [ ] Add integration test for workflow
- [ ] Add module docstrings
- [ ] Convert informal TODOs to issue references
- [ ] Code review completed
- [ ] Fix all CRITICAL and IMPORTANT linter errors
- [ ] Document any architectural decisions

### Phase 2 → Phase 3 (Alpha to Production)

- [ ] Beta testing completed successfully
- [ ] Test coverage >80% on critical paths
- [ ] All documentation complete
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Monitoring configured
- [ ] Deployment automation tested
- [ ] Runbooks created
- [ ] Production readiness review passed

---

## Rule Priority by Phase

| Priority Level | Phase 0 | Phase 1 | Phase 2 | Phase 3 |
|----------------|---------|---------|---------|---------|
| CRITICAL       | No      | **Yes** | **Yes** | **Yes** |
| IMPORTANT      | No      | No      | **Yes** | **Yes** |
| GUIDANCE       | No      | No      | No      | **Yes** |

---

## Examples by Phase

### Example: Adding a New Agent Node

#### Phase 0 (Spike)
```python
# Quick and dirty - just proving it works
def my_node(state):
    result = some_api_call()
    state["result"] = result
    return state
```

#### Phase 1 (Prototype)
```python
import logging
from typing import TypedDict

logger = logging.getLogger(__name__)

class MyState(TypedDict, total=False):
    result: dict | None
    error: str | None

def my_node(state: MyState) -> MyState:
    """Process data in this node."""
    logger.info("Node started", extra={"phase": "processing", "status": "started"})
    
    try:
        result = some_api_call()
        state["result"] = result
        logger.info("Node completed", extra={"phase": "processing", "status": "completed"})
    except Exception as e:
        logger.error("Node failed", extra={"phase": "processing", "status": "failed", "error": str(e)})
        state["error"] = str(e)
    
    return state
```

#### Phase 2 (Alpha)
```python
"""Agent node for data processing.

Iteration 3: Processes data with validation and structured error handling.

This node is active when ENABLE_NEW_FEATURE=true.
"""
import logging
from typing import TypedDict

logger = logging.getLogger(__name__)

class MyState(TypedDict, total=False):
    """State for my agent workflow.
    
    Attributes:
        input_data: Input to process
        result: Processing result
        error: Error message if processing failed
    """
    input_data: str
    result: dict | None
    error: str | None

def my_node(state: MyState) -> MyState:
    """Process data with validation and error handling.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with result or error
    """
    logger.info("Node started", extra={"phase": "processing", "status": "started"})
    
    # Validate input
    if "input_data" not in state:
        error_msg = "Missing required field: input_data"
        logger.error("Validation failed", extra={"phase": "validation", "error": error_msg})
        state["error"] = error_msg
        return state
    
    try:
        result = some_api_call(state["input_data"])
        state["result"] = result
        logger.info("Node completed", extra={
            "phase": "processing",
            "status": "completed",
            "result_size": len(result)
        })
    except APIError as e:
        logger.error("API call failed", extra={
            "phase": "processing",
            "status": "failed",
            "error": str(e),
            "error_type": "api_error"
        }, exc_info=True)
        state["error"] = f"API error: {str(e)}"
    except Exception as e:
        logger.error("Unexpected error", extra={
            "phase": "processing",
            "status": "failed",
            "error": str(e)
        }, exc_info=True)
        state["error"] = f"Unexpected error: {str(e)}"
    
    return state

# Tests added
def test_my_node_success():
    """Test node processes data successfully."""
    state = {"input_data": "test"}
    result = my_node(state)
    assert "result" in result
    assert result.get("error") is None

def test_my_node_missing_input():
    """Test node handles missing input."""
    state = {}
    result = my_node(state)
    assert "error" in result
    assert result["error"] is not None
```

#### Phase 3 (Production)
- All Phase 2 code
- Plus: ADR document explaining design decisions
- Plus: Performance benchmarks
- Plus: Monitoring dashboard with metrics
- Plus: Integration test with full workflow
- Plus: Property-based tests for edge cases

---

## Determining Current Phase

### Questions to Ask

1. **Is this new code or existing code?**
   - New: Start at Phase 0 or 1
   - Existing: Match the phase of surrounding code

2. **Is this being deployed to users?**
   - No: Phase 0-1 OK
   - Yes (beta): Phase 2 required
   - Yes (production): Phase 3 required

3. **How critical is this functionality?**
   - Experimental: Phase 0-1
   - Important but not critical: Phase 2
   - Business-critical: Phase 3

4. **How long will this code live?**
   - Days: Phase 0-1
   - Weeks-months: Phase 2
   - Long-term: Phase 3

---

## Code Review by Phase

### Phase 1 Review Focus
- Does it work?
- Are CRITICAL rules followed?
- Are there obvious bugs?
- Is the approach sound?

### Phase 2 Review Focus
- All Phase 1 checks
- Are tests adequate?
- Is documentation clear?
- Are IMPORTANT rules followed?
- Can another developer maintain this?

### Phase 3 Review Focus
- All Phase 2 checks
- Is performance acceptable?
- Are all edge cases handled?
- Are GUIDANCE rules followed?
- Is monitoring in place?
- Are there any technical debt concerns?

---

## Common Mistakes

### Mistake 1: Over-engineering Prototypes
**Problem**: Spending days on perfect documentation and tests for Phase 1 prototype that may be thrown away.

**Solution**: Apply only CRITICAL rules in Phase 1. Add quality incrementally as code stabilizes.

### Mistake 2: Rushing to Production
**Problem**: Deploying Phase 1 code directly to production without hardening.

**Solution**: Always go through Phase 2 (Alpha) before production. Add tests and documentation.

### Mistake 3: Unclear Phase Status
**Problem**: Team members unsure whether code is prototype or production-ready.

**Solution**: Tag code with phase markers in comments or use branch naming conventions (prototype/*, alpha/*, production/*).

### Mistake 4: Phase Mixing
**Problem**: Some files at Phase 3 quality, others at Phase 1, causing confusion.

**Solution**: Upgrade entire features/modules together. Don't leave mixed-quality code.

---

## Summary

- **Phase 0: Spike/Exploration**: No rules, rapid exploration
- **Phase 1: Prototype**: CRITICAL rules, working prototype
- **Phase 2: Alpha**: CRITICAL + IMPORTANT, tested and documented
- **Phase 3: Production**: All rules, production-ready

**Key Principle**: Add quality incrementally as code matures. Don't over-engineer early, but don't under-engineer for production.

**When Working on Features**
**Just tell me the phrase:**

"Let's prototype this" → Phase 1 rules + Conventional Commits
"Make this PR-ready" → Phase 2 checklist + proper cleanup
"This needs production quality" → Phase 3 complete review
I'll handle:
Proper commit messages
Pre-commit cleanup
PR templates with checklists
