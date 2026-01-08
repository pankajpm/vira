# Agent Workflows

**Version:** 1.0

---

## Iteration 2 Workflow

### State Transitions
```
INIT → ANALYSIS → REFLECTION → [Research?] → REGENERATION → END
```

### Decision Logic
```python
def should_research(state: AgentState) -> bool:
    return (
        state.overall_confidence < 0.7 and
        state.iteration_count < 2 and
        len(state.reflection_result.information_gaps) > 0
    )
```

### Iteration Control
- Max 2 reflection loops
- Stop early if confidence ≥ 0.7
- Research only if gaps exist

---

**See implementation:** `src/vira/agents/graph.py`
