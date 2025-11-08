# VIRA Evaluation Metrics Summary

## Iteration 1 (Classification-Enhanced Retrieval)

- **Response Quality**
  - Exact Match / Contains for JSON schema validation, company name, citation URLs.
  - Regex checks enforcing URL domains (`a16z.com`) and required quote syntax (`"VC Criterion:"`, `"Business Plan:"`).
  - BLEU/ROUGE and BERTScore spot checks against curated references to catch drift in alignment/gap explanations.
- **Retrieval Quality**
  - Context Precision: share of retrieved alignment/gap chunks confirmed relevant by reviewers.
  - Context Recall: percentage of mandatory evidence from ground-truth sets present in retrieval outputs.
  - Context Relevancy: cosine similarity between queries and alignment/gap contexts to detect noisy inclusions.
  - Context Entity Recall: coverage of critical entities (company, stage, geography, ARR) in retrieved evidence.
- **Generation Quality**
  - Hallucination Score (LLM judge): ensures explanations cite only provided alignment/gap evidence.
  - Answer Relevance (LLM judge): verifies each bullet addresses VC criteria and plan details directly.
  - Answer Correctness (LLM judge + human QA): checks quotes and interpretations remain factually consistent.
- **Agentic / Workflow Metrics**
  - Task Success Rate: runs producing ≥2 validated alignments and ≥2 validated gaps.
  - Routing Accuracy: agreement between automated alignment/gap classification and human review (confusion matrix, macro F1).
  - Latency: overall response plus stage-level timing (retrieval, classification, generation) against 8–12 s budget.
  - Cost per Query: track classification vs. generation spend staying near $0.012 prototype target.
- **Operational Checks**
  - Schema Validation: automated JSON schema tests for downstream stability.
  - Smoke Test Pass Rate: maintain 5-case regression suite as gate.

## Iteration 2 (Reflection & Research Agents)

- **Initial Analysis (Baseline Continuity)**
  - Exact Match / Schema Validation, Context Precision & Recall, and citation guardrail metrics carried forward from Iteration 1.
- **Reflection Layer**
  - Confidence Calibration: mean absolute error between LLM confidence scores and reviewer rubric (strong/medium/weak/insufficient).
  - Claim Coverage: percentage of alignment/gap claims receiving confidence scores without parsing failures.
  - Gap Detection Precision/Recall: confusion matrix of detected `InformationGap` items vs. reviewer judgements.
  - Reflection Latency & Cost: monitor per-pass runtime and API spend for the temperature-0 reflection model.
- **Research Layer**
  - Baseline Query Success: rate at which the three mandatory queries return ≥1 usable snippet.
  - Gap-Driven Query Yield: fraction of supplemental searches producing evidence tied to originating gaps.
  - Research Coverage: ratio of identified gaps covered by at least one validated research result before budget exhaustion.
  - Budget Compliance: ensure total executed searches respect configured limits (3 baseline + up to 2 gap-driven).
  - Result Precision: reviewer confirmation that collected snippets address the intended gap.
- **Integrated Workflow**
  - Overall Confidence Delta: difference between baseline (Iteration 1) confidence and reported Iteration 2 `overall_confidence`.
  - Iterative Improvement Rate: share of runs where research adds new sources or raises confidence above threshold.
  - End-to-End Latency: full pipeline timing breakdown (analysis, reflection, research, regeneration) vs. UX target.
  - Failure Modes: track frequency of populated `error` fields, missing research artifacts, or empty final explanations.

## Iteration 3 (Multi-Agent Investment Committee)

- **Multi-Agent Coordination**
  - Agent Task Completion Rate: percentage of specialist agents successfully completing their assigned analysis tasks within allocated tool budget.
  - Parallel Execution Efficiency: actual vs. theoretical speedup from parallel agent execution (target: 2.5-3x faster than sequential).
  - Cross-Agent Communication Quality: relevance and utility of inter-agent messages/requests as judged by human reviewers.
  - Shared Memory Utilization: percentage of agent findings that are referenced/used by other agents, indicating effective knowledge sharing.
- **Consensus & Synthesis Quality**
  - Consensus Accuracy: agreement between AI-identified consensus areas (3-4 agents agree) and human expert panels on same cases.
  - Disagreement Detection Precision/Recall: how accurately the synthesis agent identifies genuine expert disagreements vs. false positives.
  - Risk Prioritization Correlation: Spearman correlation between AI-ranked risks and human analyst risk rankings.
  - Synthesis Completeness: coverage of key investment dimensions (market, product, team, financial) in final report; target 100% coverage.
- **Strategic Positioning Quality**
  - Recommendation Actionability: percentage of strategic recommendations that are specific, measurable, and implementable (human review).
  - Recommendation Adoption Rate: percentage of startups/VCs who actually use positioning tactics in real outreach (tracked via user surveys).
  - Benchmark Accuracy: MAE between AI-calculated percentiles and human-verified portfolio rankings across key metrics.
  - Partner Match Precision: accuracy of target partner identification validated against actual portfolio fit patterns.
- **Interactive Dialogue Performance**
  - Query Routing Accuracy: percentage of user questions correctly routed to the most appropriate specialist agent.
  - Answer Completeness: human rating of whether dialogue responses fully address user questions (1-5 scale, target >4.0).
  - Follow-up Reduction: percentage decrease in user follow-up questions compared to Iteration 2 single-perspective output.
  - Agent Perspective Clarity: user rating of how well individual agent viewpoints are differentiated and explained.
- **Committee-Grade Output Quality**
  - Human Committee Agreement: percentage agreement between multi-agent assessment and actual human investment committee decisions (target: 75%+).
  - Perspective Diversity: cosine dissimilarity between agent outputs, ensuring genuinely distinct viewpoints (target: >0.3 pairwise).
  - Decision Support Value: user rating of report's usefulness for investment decisions (1-5 scale, target >4.2).
  - Comparative Analysis Quality: accuracy of comparable company matches and portfolio benchmarks validated by domain experts.
- **Integrated Workflow (Building on Iter 1 & 2)**
  - End-to-End Latency with Parallelization: total pipeline time with agent parallelization vs. budgeted 20-40s; breakdown by orchestration/research/synthesis stages.
  - Tool Call Budget Compliance: adherence to 20-call total budget (5 per agent avg) with variance tracking and overage detection.
  - Cost per Committee Analysis: total API spend for full multi-agent run staying within $0.30-0.80 target range.
  - Confidence Calibration Across Agents: whether per-agent confidence scores remain well-calibrated (MAE vs. human agreement per agent type).
- **Operational & Quality Controls**
  - Schema Validation: automated checks ensuring `InvestmentCommitteeReport`, `AgentAssessment`, and `SynthesisResult` structures are complete and valid.
  - Agent Failure Handling: percentage of runs successfully recovering from individual agent failures without full pipeline abort.
  - Memory Consistency: validation that shared working memory maintains consistency across concurrent agent writes.

