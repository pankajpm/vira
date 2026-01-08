# Deployment Guide

**Version:** 1.0

---

## Local Deployment

### Development
```bash
# Backend (port 8001)
uvicorn vira.backend.api:app --reload --port 8001

# Chainlit (port 8000)
chainlit run src/vira/ui/chainlit_app.py --port 8000
```

### Production (Local)
```bash
# Use gunicorn for production WSGI
pip install gunicorn
gunicorn vira.backend.api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

---

## Cloud Deployment (Future)

### Backend (Render/Railway/Fly.io)
1. Containerize with Docker
2. Deploy to cloud platform
3. Set environment variables
4. Configure persistent storage for vector DB

### Frontend (Vercel/Netlify)
1. Build React app: `npm run build`
2. Deploy build folder
3. Configure API URL

---

## Environment Variables

**Required:**
- `OPENAI_API_KEY`

**Optional:**
- `SERPER_API_KEY` (Iteration 2)
- `LANGSMITH_API_KEY` (Observability)
- `ENABLE_REFLECTION=true` (Enable Iteration 2)

---

## Monitoring

**Logs:**
- Backend: stdout/stderr
- Chainlit: `/tmp/chainlit.log`

**LangSmith:** Set `LANGSMITH_API_KEY` for trace monitoring
