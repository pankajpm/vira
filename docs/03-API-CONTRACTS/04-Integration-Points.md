# VIRA: Integration Points

**Version:** 1.0  
**Last Updated:** November 25, 2025

---

## External Services

### OpenAI API
- **Purpose:** LLM + Embeddings
- **Authentication:** API Key
- **Models:** gpt-4o-mini, text-embedding-3-small
- **Cost:** ~$0.002 per query

### Serper API (Iteration 2+)
- **Purpose:** Web search
- **Authentication:** API Key
- **Cost:** $2.50 per 1K searches

### LangSmith (Optional)
- **Purpose:** Observability
- **Authentication:** API Key
- **Setup:** Set `LANGSMITH_API_KEY` env var

---

**Configuration:** `.env` file at project root
