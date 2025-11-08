# Iteration 2: Quick Start Guide

## 🚀 Getting Started with Reflective Agent

### 1. Install Dependencies (if not already done)

```bash
cd /Users/pankaj/projects/vira
source .venv/bin/activate
pip install -e .
```

The new dependencies (`langgraph` and `google-search-results`) are now installed.

### 2. Configure Environment

Edit your `.env` file (or create from `config/env.template`):

```bash
# Core (required)
OPENAI_API_KEY=your_openai_key_here

# Iteration 2: Enable Reflection Agent
ENABLE_REFLECTION=true

# Optional: Enable Research (requires Serper API key)
SERPER_API_KEY=your_serper_key_here

# Optional: Tune reflection settings
REFLECTION_CONFIDENCE_THRESHOLD=0.7
MAX_RESEARCH_QUERIES=5
MAX_REFLECTION_ITERATIONS=2
```

**Get Serper API Key** (Optional):
- Visit https://serper.dev/
- Sign up for free (2,500 searches/month)
- Copy API key to `.env`

### 3. Test the System

**Run Integration Test:**
```bash
python notebooks/test_iteration2_integration.py
```

Expected output:
```
✅ High confidence path working!
✅ Research path working!
✅ Metadata completeness verified!
✅ Iteration 1 still works correctly!

🎉 Phase 4: Integration - ALL TESTS PASSED!
```

### 4. Usage Examples

#### Option A: Direct Python Usage

```python
from vira.agents.analyzer import ReflectiveAnalyzer

# Initialize
analyzer = ReflectiveAnalyzer()

# Analyze
result, metadata = analyzer.analyze(
    company_name="HealthTech AI",
    plan_summary="AI-powered healthcare SaaS platform...",
    query="healthcare AI investment criteria"
)

# Access results
print(f"Confidence: {result.overall_confidence}")
print(f"Alignments: {len(result.aligns)}")
print(f"Gaps: {len(result.gaps)}")
print(f"Research conducted: {len(result.research_conducted or [])}")

# Access metadata
print(f"Iterations: {metadata['iterations']}")
print(f"Research queries: {metadata['research_queries']}")
```

#### Option B: Via API

**Start the API:**
```bash
uvicorn vira.backend.api:app --reload
```

**Send Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "My Startup",
    "plan_text": "We are building an AI platform for healthcare providers..."
  }'
```

**Response includes:**
```json
{
  "company_name": "My Startup",
  "aligns": [...],
  "gaps": [...],
  "summary": "...",
  "overall_confidence": 0.82,
  "research_conducted": [...],
  "data_gaps": [...]
}
```

### 5. Toggle Between Iterations

**Use Iteration 2** (Reflection + Research):
```bash
# In .env
ENABLE_REFLECTION=true
```

**Use Iteration 1** (Basic RAG):
```bash
# In .env
ENABLE_REFLECTION=false
```

The API automatically routes to the appropriate analyzer.

---

## 📊 What to Expect

### High Confidence Scenario

```
Input: Well-documented healthcare AI plan with clear team experience

Flow:
1. Initial Analysis → 3 alignments, 2 gaps
2. Reflection → Confidence: 0.82 (HIGH)
3. Decision → Skip research (high confidence)
4. Output → Analysis with confidence scores

Time: ~5-10 seconds
```

### Low Confidence Scenario

```
Input: Vague business plan with limited details

Flow:
1. Initial Analysis → 1 alignment, 3 gaps
2. Reflection → Confidence: 0.55 (LOW)
3. Decision → Trigger research
4. Research → 3 web searches for missing info
5. Regeneration → Enhanced analysis with research
6. Output → Analysis + research metadata

Time: ~15-25 seconds (with research)
```

### No API Key Scenario

```
Input: Any business plan
SERPER_API_KEY: Not configured

Flow:
1. Initial Analysis → Works normally
2. Reflection → Works normally
3. Decision → May trigger research
4. Research → Gracefully skips (no API key)
5. Output → Analysis with confidence, no research

Still provides value through confidence scoring!
```

---

## 🔧 Troubleshooting

### Issue: "Serper API key not provided"
**Solution**: Research will be skipped. System still works without it.
- Add `SERPER_API_KEY` to `.env` if you want research
- Or ignore - confidence scoring still provides value

### Issue: "Module 'langgraph' not found"
**Solution**: 
```bash
pip install langgraph google-search-results
```

### Issue: Tests fail with API errors
**Solution**: Check your OpenAI API key is valid and has credits.

### Issue: Analysis is slow
**Solution**: 
- Reflection adds 5-10s overhead
- Research adds 10-15s per query
- Disable if speed is critical: `ENABLE_REFLECTION=false`

---

## 📈 Performance Tips

1. **For Speed**: Set `ENABLE_REFLECTION=false` (use Iteration 1)
2. **For Quality**: Set `ENABLE_REFLECTION=true` + configure Serper API
3. **For Cost Control**: Reduce `MAX_RESEARCH_QUERIES` to 2-3
4. **For Thoroughness**: Increase `MAX_REFLECTION_ITERATIONS` to 3

---

## 🎯 Use Cases

### Best for Iteration 2:
- ✅ Detailed diligence where confidence matters
- ✅ Plans with uncertain/incomplete information
- ✅ When you need to justify assessments
- ✅ Research-heavy evaluations

### Best for Iteration 1:
- ✅ Quick screening of many plans
- ✅ When speed > thoroughness
- ✅ High-quality, complete business plans
- ✅ When API costs are a concern

---

## 📚 Next Steps

1. **Test with Real Plans**: Use actual business plans from `bizplans/` folder
2. **Tune Thresholds**: Adjust `REFLECTION_CONFIDENCE_THRESHOLD` based on results
3. **Monitor Costs**: Track Serper API usage (free tier: 2,500/month)
4. **Read Architecture**: See `docs/ITERATION2_ARCHITECTURE.md` for details
5. **Iteration 3**: Check `VIRA_MVP_Architecture_Plan_v0.md` for multi-agent system

---

## ❓ FAQ

**Q: Do I need a Serper API key?**  
A: No, it's optional. System works without it, just skips research.

**Q: How much does it cost?**  
A: OpenAI API: ~$0.05-0.15 per analysis. Serper: Free tier covers 2,500 searches.

**Q: Can I use Iteration 1 and 2 simultaneously?**  
A: Yes! Feature flag controls which analyzer is used per request.

**Q: How accurate is the confidence scoring?**  
A: Calibrated to be conservative. Scores 0.7+ are reliable. Needs validation with your data.

**Q: What if research finds nothing useful?**  
A: That's OK! System gracefully handles empty results and still provides the initial analysis.

---

**Quick Links:**
- Architecture: `docs/ITERATION2_ARCHITECTURE.md`
- Full Summary: `ITERATION2_IMPLEMENTATION_SUMMARY.md`
- Phase Plan: `VIRA-Iteration2-phases.md`
- Original Spec: `VIRA_MVP_Architecture_Plan_v0.md`

