# Evaluation Framework

**Version:** 1.0

---

## Evaluation Metrics

### Iteration 1 Metrics
- **Retrieval Precision:** % relevant docs retrieved
- **Retrieval Recall:** % relevant docs found
- **Alignment Accuracy:** % agreement with human analysts
- **Source Citation Accuracy:** % sources correctly attributed
- **Response Time:** Latency (p50, p95)

**Targets:** 80% precision, 70% recall, 70% accuracy

### Iteration 2 Metrics
- **Confidence Calibration:** Correlation with human confidence
- **Gap Filling Accuracy:** % gaps correctly filled by research
- **Research Relevance:** % research results relevant to gaps
- **Follow-up Reduction:** % decrease in user follow-up questions

**Targets:** r>0.65 calibration, 40% gap filling, 30% follow-up reduction

---

## Evaluation Process

### 1. Create Test Set
```bash
# Collect 50 business plans with ground truth assessments
# Store in: tests/evaluation/test_cases/
```

### 2. Run Batch Evaluation
```bash
python tests/evaluation/run_batch_eval.py --test-set test_cases.json
```

### 3. Analyze Results
```bash
python tests/evaluation/analyze_results.py --output evaluation_report.pdf
```

---

## Manual Review

### Sample 10 Random Cases
1. Run analysis
2. Expert reviewer assesses quality
3. Compare AI vs human
4. Document discrepancies

**Review Template:** `tests/evaluation/review_template.md`

---

## Continuous Monitoring

- Track metrics weekly
- A/B test prompt variations
- Monitor user feedback
- Iterate on poor-performing cases
