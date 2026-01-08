# Iteration 2: Reflective Agent Implementation

**Version:** 1.0  
**Status:** ✅ Complete

---

## Implementation Overview

Iteration 2 adds agentic capabilities via LangGraph:
1. Initial RAG analysis
2. Reflection (assess confidence, identify gaps)
3. Research (web search to fill gaps)
4. Regeneration (updated analysis with research)

### Key Files
- `src/vira/agents/analyzer.py` - ReflectiveAnalyzer
- `src/vira/agents/graph.py` - LangGraph workflow
- `src/vira/agents/reflection.py` - Confidence assessment
- `src/vira/agents/research.py` - Web search tool

### Running Iteration 2
```bash
# Set environment
export ENABLE_REFLECTION=true
export SERPER_API_KEY=your_key_here

# Start API (automatically uses Iteration 2)
uvicorn vira.backend.api:app --reload --port 8001
```

### LangGraph Workflow
```python
workflow = StateGraph(AgentState)
workflow.add_node("initial_analysis", ...)
workflow.add_node("reflection", ...)
workflow.add_node("research", ...)
workflow.add_node("regeneration", ...)
workflow.add_conditional_edges("reflection", should_research, ...)
```

---

**See:** `../02-ARCHITECTURE/03-Agent-Architecture.md` for detailed design
