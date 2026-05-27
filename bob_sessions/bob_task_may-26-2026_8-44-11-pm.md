# Bob Session: Architectural Analysis and Documentation

**Date:** May 26, 2026, 8:44 PM EDT  
**Task:** Analyze workspace and generate high-level architectural overview  
**Status:** ✅ COMPLETED

---

## Task Summary

Generated comprehensive architectural documentation for the Scuderia Pit-Wall Fan Orchestrator, including:
1. Primary entry points and data flow analysis
2. Core dependencies and routing logic
3. Mermaid.js sequence diagram mapping main user journey
4. State mutation and data contracts
5. Governance architecture (the critical differentiator)

---

## Files Analyzed

### Core Entry Points (3)
- `main.py` — PitWallOrchestrator class (programmatic API)
- `app.py` — FastAPI REST service (production deployment)
- `static/index.html` — Progressive Web App UI

### Configuration & Models (3)
- `config.py` — Environment-based configuration with secret management
- `models.py` — 6 typed dataclasses for inter-component communication
- `README.md` — Project overview and architecture diagrams

### Perception Layer (1)
- `perception/nlp_synthesizer.py` — Watson STT + Hook 1 audit

### Memory Layer (1)
- `memory/rag_store.py` — ChromaDB vector store + Hook 2 audit

### Reasoning Layer (3)
- `reasoning/planning_engine.py` — Intent classification (regulation vs strategy)
- `reasoning/regulation_agent.py` — FIA regulation specialist
- `reasoning/agentic_strategist.py` — Race strategy specialist

### Tools Layer (1)
- `tools/fastf1_client.py` — Live telemetry via FastF1 API

### Governance Layer (1)
- `governance/overseer.py` — Proactive validation + Hook 3 audit + retry orchestration

### Execution Layer (1)
- `execution/execution_module.py` — Watson TTS + three-output-state delivery

**Total:** 15 core component files analyzed

---

## Key Architectural Insights

### 1. Six-Layer Architecture
```
① Perception          → NLP Synthesizer (Watson STT)
② Memory & Knowledge  → RAG Vector Store (FIA regs + strategy history)
③ Reasoning           → Planning Engine → Specialist Agents
④ Tools               → FastF1 Client (live telemetry)
⑤ Governance          → Overseer Agent (watsonx.governance)
⑥ Execution           → Execution Module (Watson TTS)
```

### 2. Three-Hook Governance System
- **Hook 1:** Transcript audit (after perception, before reasoning)
- **Hook 2:** Retrieval audit (after RAG query, before reasoning)
- **Hook 3:** Pre-delivery cross-validation (after reasoning, before delivery)

**Critical Innovation:** Overseer validates narrative against cited source using Granite LLM cross-validation, not just confidence scoring.

### 3. Retrieve-First Architecture
**Anti-pattern:** LLM generates → RAG finds citation → append  
**Correct pattern:** RAG retrieves → LLM reasons within context

**Benefit:** Prevents hallucination by grounding LLM in actual sources before generation.

### 4. Three-Output-State System
- `confirmed` — Citation validated, high confidence
- `retry_corrected` — First pass failed, retry succeeded (audit flag set)
- `uncertainty` — Retry budget exhausted, honest partial answer

**Design principle:** Trust preserved over false confidence.

### 5. Routing Logic
```python
PlanningEngine.classify(signal) → "regulation" | "strategy"
  ↓
"regulation" → RegulationAgent (FIA regs RAG only)
"strategy"   → AgenticStrategist (strategy RAG + live FastF1 telemetry)
```

### 6. Data Flow (Immutable)
```
Input → StructuredSignal → RAGResult → LiveTelemetry → Narrative → OverseerDecision → FinalOutput
```

Each component produces new typed objects; no in-place mutation.

### 7. Stateful Components (3 only)
1. **RAGStore** — Persistent ChromaDB (indexed documents)
2. **OverseerAgent** — In-memory audit log (all governance decisions)
3. **AgenticStrategist** — Race context config (year, race, driver)

**No global state** — thread-safe for concurrent FastAPI requests.

---

## Sequence Diagram Created

**Scenario:** Fan asks "Why did Leclerc lift on the straight?"

**Flow:**
1. Fan → PWA UI → FastAPI `/process` endpoint
2. Perception: NLPSynthesizer structures query → Hook 1 audit
3. Planning: PlanningEngine classifies intent → "strategy"
4. Reasoning: AgenticStrategist executes:
   - Step 3a: RAG query → Hook 2 audit
   - Step 3b: FastF1 telemetry fetch (both Ferrari drivers)
   - Step 3c: Granite generates narrative with citation
5. Governance: Overseer validates → Hook 3 cross-validation
   - If APPROVED → deliver with audio
   - If INVALID → retry with amended context
   - If retry exhausted → uncertainty response
6. Execution: Watson TTS synthesizes audio
7. Output: FinalOutput (text + audio + traceability link) → Fan

**Mermaid diagram:** 60+ sequence steps documented in Section 4.

---

## Technology Stack Documented

| Layer | Component | IBM Technology |
|-------|-----------|----------------|
| LLM | Granite 4 | `ibm-watsonx-ai` |
| Speech-to-Text | Watson STT | `ibm-watson` |
| Text-to-Speech | Watson TTS | `ibm-watson` |
| Vector Store | ChromaDB | `chromadb` (MVP), Watson Discovery (production) |
| Telemetry | FastF1 | `fastf1` |
| API Framework | FastAPI | `fastapi` |
| Governance | Overseer Agent | Custom (watsonx-powered) |

---

## Output Generated

### Primary Document
**File:** `docs/10_architectural_overview.md`  
**Size:** 489 lines  
**Sections:** 10 comprehensive sections

**Contents:**
1. Primary Entry Points and Data Flow
2. Core Dependencies and Routing Logic
3. Governance Architecture — The Critical Differentiator
4. Sequence Diagram — Main User Journey (Mermaid.js)
5. State Mutation and Data Contracts
6. Deployment Architecture (local + IBM Cloud)
7. Key Design Decisions (with rationale)
8. Future Enhancements (production readiness)
9. Testing Strategy (unit, integration, adversarial)
10. Conclusion

### Updated Files
- `.bob/context/reboot_latest.md` — Updated with architectural analysis summary
- `bob_sessions/bob_task_may-26-2026_8-44-11-pm.md` — This session log

---

## Key Design Decisions Documented

### Why Retrieve FIRST, Reason SECOND?
Prevents LLM hallucination by grounding in actual sources before generation.

### Why Three Output States (Not Two)?
Honest uncertainty over false confidence preserves trust.

### Why Proactive Governance (Not Reactive)?
Wrong answers never reach the fan; trust preserved at 250ms latency cost.

### Why Typed Data Contracts?
Strong typing prevents integration bugs; clear component boundaries.

### Why Stateless Design?
Horizontal scalability for production deployment on IBM Cloud Code Engine.

---

## Latency Budget Analysis

| Component | Time |
|-----------|------|
| First pass (inference + RAG) | ~1,000ms |
| Overseer check | ~150ms |
| Retry with amended context | ~950ms |
| Re-check | ~150ms |
| **Total worst case** | **~2,250ms** |

**Design decision:** 250ms overrun acceptable for validated output over confident-wrong speed.

---

## Future Enhancements Identified

### Production Readiness
- Replace ChromaDB with IBM Watson Discovery
- Swap embeddings with `ibm/slate-125m-english-rtrvr`
- Deploy FastF1 as IBM Orchestrate skill
- Add Redis cache for telemetry
- Implement WebSocket streaming

### Governance Enhancements
- Integrate watsonx.governance dashboard
- Add confidence calibration tracking
- Implement A/B testing framework
- Add explainability layer

### Fan Experience
- Multi-language support (IT, ES, DE)
- Push notifications for race events
- Personalized strategy preferences
- Social sharing with traceability

---

## Testing Strategy Outlined

### Unit Tests (per component)
- NLP Synthesizer, Planning Engine, RAG Store, Overseer, Execution Module

### Integration Tests (end-to-end)
- Regulation pipeline, Strategy pipeline, Retry mechanism, Uncertainty output

### Governance Tests (adversarial)
- Confident-wrong detection, Citation-free suppression, Low-confidence RAG

---

## Conclusion

Successfully generated comprehensive architectural documentation that:
- Maps all 15 core components and their interactions
- Documents the three-hook governance system (the critical differentiator)
- Provides Mermaid sequence diagram for main user journey
- Explains key design decisions with rationale
- Identifies future enhancements for production deployment

**No code modifications made** — analysis and documentation only, as requested.

The architectural overview is production-ready for stakeholder review and serves as the definitive reference for the 2026 F1 season deployment.

---

## Session Metadata

**Start Time:** 2026-05-27 00:40:18 UTC  
**End Time:** 2026-05-27 00:44:11 UTC  
**Duration:** ~4 minutes  
**Files Read:** 15 core component files  
**Files Created:** 2 (architectural overview + session log)  
**Files Modified:** 1 (reboot context)  
**Total Output:** 489 lines of documentation  
**Cost:** $0.89 (token budget: 200,000)

**Status:** ✅ TASK COMPLETED SUCCESSFULLY