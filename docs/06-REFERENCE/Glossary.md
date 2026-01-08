# VIRA Glossary

**Version:** 1.0

---

## Technical Terms

**RAG (Retrieval-Augmented Generation):** AI technique combining information retrieval with text generation. System retrieves relevant documents, then uses them as context for LLM generation.

**Vector Database:** Database storing high-dimensional embeddings for semantic search. VIRA uses Chroma.

**Embeddings:** Numerical representations of text (1536-dimensional vectors). Capture semantic meaning for similarity search.

**Hybrid Retrieval:** Combining semantic search (vector similarity) with keyword search (BM25) for better recall.

**LLM (Large Language Model):** AI model trained on text (e.g., GPT-4o-mini). Generates analysis from retrieved context.

**Agent:** Autonomous AI system that can reason, act, and use tools. Iteration 2+ uses agents.

**LangGraph:** Framework for building multi-step agent workflows as state machines.

**ReAct Pattern:** Reasoning + Acting. Agent reasons about what to do, acts (uses tools), observes results, repeats.

---

## Business Terms

**VC (Venture Capital):** Investment firms funding early-stage companies in exchange for equity.

**Business Plan:** Document describing company's strategy, market, product, team, and financials.

**Alignment Analysis:** Assessment of how well a business plan matches VC investment criteria.

**Investment Thesis:** VC firm's stated focus areas, stage preferences, and deal criteria.

**TAM/SAM/SOM:** Total/Serviceable/Obtainable Addressable Market size metrics.

**Unit Economics:** Per-customer profitability metrics (CAC, LTV, gross margin).

**PMF (Product-Market Fit):** Degree to which product satisfies strong market demand.

---

## VIRA-Specific Terms

**Iteration 1:** Basic RAG pipeline (explanation only, no research).

**Iteration 2:** Reflective agent with autonomous research capabilities.

**Iteration 3:** Multi-agent investment committee simulation (planned).

**Alignment Point:** Single match or gap identified in analysis.

**Confidence Score:** Agent's self-assessed certainty (0.0-1.0) in a claim.

**Information Gap:** Missing data identified by reflection agent.

**Research Query:** Web search conducted by agent to fill gaps.
