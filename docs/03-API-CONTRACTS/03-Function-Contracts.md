# VIRA: Function Contracts

**Version:** 1.0  
**Last Updated:** November 25, 2025

---

## RAG Pipeline

### AlignmentAnalyzer.analyze()
```python
def analyze(
    company_name: str,
    plan_summary: str,
    query: str
) -> Tuple[AlignmentResponse, List[Document]]:
    """Run RAG analysis pipeline."""
```

## Retrieval

### HybridRetriever.retrieve()
```python
def retrieve(query: str, **kwargs) -> List[Document]:
    """Hybrid retrieval (semantic + keyword)."""
```

## Agent Layer (Iteration 2)

### ReflectiveAnalyzer.analyze()
```python
def analyze(
    company_name: str,
    plan_summary: str,
    query: str
) -> Tuple[AlignmentResponse, dict]:
    """Run reflective agent workflow."""
```

---

**See full signatures in:** `src/vira/` modules
