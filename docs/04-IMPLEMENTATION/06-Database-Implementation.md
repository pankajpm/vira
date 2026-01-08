# Database Implementation

**Version:** 1.0

---

## SQLite Schema

### Tables
- `sessions` - Chat sessions
- `messages` - Message history
- `business_plans` - Versioned plans
- `analyses` - Analysis results

### Initialization
```python
from vira.ui.database.session_manager import SessionManager

db = SessionManager("./data/vira_sessions.db")
session = db.create_session()
plan = db.save_business_plan(session.id, content, version=1)
```

### Migrations
Currently manual (create tables on first run).

**Future:** Use Alembic for migrations.

---

**See models:** `src/vira/ui/database/models.py`
