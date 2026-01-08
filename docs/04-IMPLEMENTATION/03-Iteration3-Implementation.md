# Iteration 3: Multi-Agent Implementation

**Version:** 1.0  
**Status:** 📋 Specification Only

---

## Implementation Plan

Iteration 3 will implement a multi-agent investment committee:
- Coordinator Agent (orchestration)
- Market Agent (TAM, competition, timing)
- Product Agent (tech moat, PMF)
- Team Agent (founder backgrounds)
- Financial Agent (unit economics)
- Synthesis Agent (consensus/disagreement)
- Strategy Agent (positioning recommendations)

### Planned Architecture
```python
from vira.agents.committee import CoordinatorAgent
from vira.agents.committee.specialists import (
    MarketAgent, ProductAgent, TeamAgent, FinancialAgent
)

coordinator = CoordinatorAgent()
results = await coordinator.analyze_parallel(plan, criteria)
synthesis = SynthesisAgent().synthesize(results)
strategy = StrategyAgent().generate_positioning(synthesis)
```

### Implementation Phases
1. Phase 1: Coordinator + 2 agents (Weeks 7-9)
2. Phase 2: All 4 specialists (Weeks 10-11)
3. Phase 3: Synthesis + Strategy (Weeks 12-13)
4. Phase 4: Dialogue interface (Week 14)

---

**See:** `../02-ARCHITECTURE/04-Multi-Agent-Architecture.md` for full specification
