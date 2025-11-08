# VIRA Quick Start Guide 🚀

## ✅ Your React + FastAPI Stack is Ready!

---

## 🎯 What You Have

**3-Pane React UI** with full TypeScript  
**FastAPI Backend** with 20+ endpoints  
**90% Code Reuse** from existing Chainlit backend  
**WebSocket Support** for real-time updates  

---

## 🚀 Start the Application

### Option 1: Use the startup script (Recommended)

```bash
cd /Users/pankaj/projects/vira
./start_react_stack.sh
```

### Option 2: Manual start

```bash
# Terminal 1: Backend
cd /Users/pankaj/projects/vira
source .venv/bin/activate
uvicorn vira.backend.api:app --reload --port 8001

# Terminal 2: Frontend  
cd /Users/pankaj/projects/vira/frontend
npm start
```

---

## 🌐 Access Points

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8001  
- **API Docs:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/health

---

## 📖 First Steps

### 1. Create a Session
1. Open http://localhost:3000
2. Click **[+ New Session]** in left sidebar
3. Enter company name

### 2. Upload Business Plan
1. Click **[📁 Upload]** in right pane
2. Select .txt or .md file
3. Or paste content directly and click **[💾 Save]**

### 3. Run Analysis
1. Type **"analyze"** in chat
   OR
2. Click **[🔍 Analyze]** button
3. View results in center pane

### 4. Enable Debug Mode
1. Toggle **[🔧 Developer Mode]** (top right)
2. Run analysis again
3. See metrics: latency, tokens, cost

---

## 🎨 UI Overview

```
┌─────────────────────────────────────────────────────────────┐
│  VIRA         [🔧 Developer Mode ☐]    [TaskFlow AI]        │
├──────────┬─────────────────────────────────┬────────────────┤
│ Sessions │ Chat Panel                      │ Plan Editor    │
│ (20%)    │ (50%)                           │ (30%)          │
│          │                                 │                │
│ [Search] │ 💬 Conversation                 │ 📝 Version 3   │
│ [+ New]  │                                 │                │
│          │ User: paste plan               │ [✏️ Edit]      │
│ ● Active │ VIRA: ✅ Saved!                │ [📜 Versions]  │
│ ○ Old    │                                 │ [📁 Upload]    │
│          │ User: analyze                   │                │
│          │ VIRA: 🔍 Analyzing...          │ [Business      │
│          │                                 │  plan          │
│          │ ✅ Strengths | ⚠️ Gaps          │  content...]   │
│          │ ...analysis...                  │                │
│          │                                 │                │
│          │ [Type message...] [Send] [🔍]   │ [💾 Save]      │
└──────────┴─────────────────────────────────┴────────────────┘
```

---

## 🛠️ Development

### Frontend
```bash
cd frontend

# Install deps
npm install

# Dev server with hot reload
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Backend
```bash
cd /Users/pankaj/projects/vira
source .venv/bin/activate

# Dev server with auto-reload
uvicorn vira.backend.api:app --reload --port 8001

# View interactive API docs
open http://localhost:8001/docs

# Run tests
pytest
```

---

## 📡 API Endpoints

### Sessions
- `POST /api/sessions` - Create session
- `GET /api/sessions` - List sessions
- `GET /api/sessions/{id}` - Get session
- `GET /api/sessions/search?term=...` - Search

### Messages
- `GET /api/sessions/{id}/messages` - List
- `POST /api/sessions/{id}/messages` - Create

### Business Plans
- `POST /api/sessions/{id}/plan` - Save
- `GET /api/sessions/{id}/plan` - Get latest
- `GET /api/sessions/{id}/plan/versions` - List versions
- `POST /api/sessions/{id}/plan/rollback` - Rollback

### Analysis
- `POST /api/sessions/{id}/analyze` - Analyze
- `GET /api/analyses/{message_id}` - Get metrics

### WebSocket
- `WS /ws?session_id={id}` - Real-time updates

---

## 🐛 Troubleshooting

### Backend not starting?
```bash
# Check if port 8001 is in use
lsof -i :8001

# Kill process if needed
pkill -f "uvicorn vira.backend"

# Check logs
tail -f /tmp/vira-backend.log
```

### Frontend not loading?
```bash
# Check if port 3000 is in use
lsof -i :3000

# Kill process if needed
pkill -f "react-scripts"

# Check logs
tail -f /tmp/vira-frontend.log

# Clear npm cache if needed
cd frontend && rm -rf node_modules && npm install
```

### CORS errors?
The backend is configured to allow all origins for local development.
Check `src/vira/backend/api.py` line 25-30.

### Database errors?
```bash
# Check database exists
ls -la ./data/vira_sessions.db

# Recreate if needed
python -c "from vira.ui.database.models import create_tables; create_tables()"
```

---

## 📊 Tech Stack

**Frontend:**
- React 19 + TypeScript
- React Query (TanStack)
- Axios for API calls
- Custom CSS (Tailwind-like utilities)

**Backend:**
- FastAPI
- SQLAlchemy + SQLite
- WebSockets
- Existing RAG pipeline (unchanged!)

---

## 🚀 Next Features

Immediate improvements you can add:

1. **Monaco Editor** - Rich code editing for plans
2. **react-markdown** - Render formatted analysis
3. **react-dropzone** - Drag & drop upload
4. **react-hot-toast** - Notifications
5. **Dark mode** - Theme switcher

---

## 📝 Notes

- Frontend runs on port **3000**
- Backend runs on port **8001**
- Database: `./data/vira_sessions.db`
- Logs: `/tmp/vira-backend.log` and `/tmp/vira-frontend.log`
- Chainlit version still available at `src/vira/ui/chainlit_app.py`

---

## ✅ Benefits Over Chainlit

| Feature | Chainlit | React Version |
|---------|----------|---------------|
| 3-Pane Layout | ❌ | ✅ |
| Session History | Clutters chat | Dedicated pane |
| Plan Editor | Separate flow | Integrated |
| Customization | Limited | Unlimited |
| TypeScript | ❌ | ✅ |
| Component Reuse | ❌ | ✅ |

---

**Enjoy building! 🎉**

For detailed documentation, see `REACT_MIGRATION_COMPLETE.md`

