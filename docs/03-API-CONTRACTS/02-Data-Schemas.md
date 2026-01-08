# VIRA: Data Schemas

**Version:** 1.0  
**Last Updated:** November 25, 2025

---

## Core Data Models

### AlignmentPoint
```python
class AlignmentPoint(BaseModel):
    description: str      # What aligns or doesn't
    evidence: str        # Supporting evidence
    source: str          # Source URL
```

### AlignmentResponse
```python
class AlignmentResponse(BaseModel):
    company_name: str
    aligns: List[AlignmentPoint]
    gaps: List[AlignmentPoint]
    summary: str
    sources: List[str]
```

### Session
```python
class Session(Base):
    id: str (UUID)
    company_name: Optional[str]
    status: str  # active, archived
    created_at: DateTime
    updated_at: DateTime
```

### BusinessPlan
```python
class BusinessPlan(Base):
    id: int
    session_id: str
    version: int
    content: Text
    created_at: DateTime
```

---

**See model definitions in:**
- Backend: `src/vira/backend/models.py`
- Database: `src/vira/ui/database/models.py`
