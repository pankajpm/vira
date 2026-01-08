# Operations Runbook

**Version:** 1.0

---

## Daily Operations

### Starting Services
```bash
./start_chainlit_ui.sh
# or
./start_react_stack.sh
```

### Stopping Services
```bash
./stop_all.sh
# or
pkill -f "chainlit"
pkill -f "uvicorn"
```

### Checking Health
```bash
curl http://localhost:8001/health
# Expected: {"status": "ok"}
```

---

## Data Refresh

### Update VC Content (Monthly)
```bash
# 1. Backup current data
cp data/raw/a16z_raw.jsonl data/raw/a16z_raw_$(date +%Y%m%d).jsonl
cp -r data/processed/chroma data/processed/chroma_backup

# 2. Run incremental crawl
python -m vira.ingestion.runner crawl --config-path config/crawl_settings.yaml

# 3. Re-process and re-embed
python -m vira.processing.cli ingest --raw-path data/raw/a16z_raw.jsonl

# 4. Verify
# Run test query and check results
```

---

## Database Maintenance

### Clear Old Sessions
```bash
python scripts/clear_sessions.py --older-than 30d
```

### Backup Database
```bash
cp data/vira_sessions.db backups/vira_sessions_$(date +%Y%m%d).db
```

---

## Troubleshooting

### High Memory Usage
- Restart services
- Check vector DB size
- Reduce batch size in processing

### Slow Queries
- Check LLM API latency
- Verify retrieval performance
- Enable caching (future)

---

**See logs:** `/tmp/chainlit.log` or backend stdout
