# ADR-002: Use JSONL for Raw Data Storage

**Date:** 2025-11-01  
**Status:** Accepted  
**Context:** Need format for scraped VC content

---

## Decision
Store raw scraped data as JSONL (JSON Lines).

## Rationale
- **Streamability:** Process line-by-line (low memory)
- **Appendability:** Incremental crawls without rewriting
- **Human-readable:** Easy inspection and debugging
- **Language-agnostic:** Parse in any language
- **Git-friendly:** Line-based diffs

## Consequences
✅ High reusability (export to CSV, SQL, Parquet)  
✅ Lossless (all metadata preserved)  
⚠️ Larger file size than binary formats

## Alternatives Considered
- **SQLite:** Less portable, harder to version control
- **Parquet:** Not human-readable, requires libraries
- **CSV:** Doesn't handle nested metadata well

---

**Result:** JSONL enables multi-project reuse
