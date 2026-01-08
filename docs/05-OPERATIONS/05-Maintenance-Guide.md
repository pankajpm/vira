# Maintenance Guide

**Version:** 1.0

---

## Regular Maintenance

### Weekly
- Review logs for errors
- Check disk space
- Monitor API costs

### Monthly
- Update VC content (crawl + re-embed)
- Backup databases
- Review evaluation metrics
- Update dependencies

### Quarterly
- Comprehensive system review
- Performance optimization
- Security audit
- User feedback analysis

---

## Dependency Updates

### Check for Updates
```bash
pip list --outdated
```

### Update Dependencies
```bash
pip install --upgrade langchain langchain-openai chromadb
# Test thoroughly before deploying
```

---

## Data Maintenance

### Vector DB Optimization
```bash
# Rebuild vector DB from scratch (if corruption suspected)
rm -rf data/processed/chroma
python -m vira.processing.cli ingest --raw-path data/raw/a16z_raw.jsonl
```

### Session DB Cleanup
```bash
# Archive old sessions (>90 days)
python scripts/archive_old_sessions.py --days 90

# Vacuum database
sqlite3 data/vira_sessions.db "VACUUM;"
```

---

## Monitoring Checklist

- [ ] API latency < 5s (Iter 1), < 30s (Iter 2)
- [ ] Error rate < 1%
- [ ] Disk usage < 80%
- [ ] Memory usage < 80%
- [ ] API costs within budget

---

## Emergency Procedures

### Service Down
1. Check logs
2. Restart services
3. Verify database connectivity
4. Test with health endpoint

### Data Corruption
1. Stop services
2. Restore from backup
3. Verify data integrity
4. Resume services

---

**Contact:** Engineering team for critical issues
