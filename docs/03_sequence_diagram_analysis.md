# Sequence Diagram — Analysis, Misalignments & Corrections

---

## What a Sequence Diagram Does That an Architecture Diagram Cannot

The architecture diagram is a map — it shows what components exist and what connects to what. It is static. It answers: "what is this system made of?"

The sequence diagram is a journey — it shows what actually happens, step by step, when something triggers the system. It is temporal, read top to bottom as time passing. It answers: "what does this system do, in what order, and why?"

Both are necessary. Together they give a complete technical picture. The architecture diagram is required for the IBM Week 4 blueprint. The sequence diagram completes the workflow view that the flowchart on the workflow slide only approximates with numbered boxes.

---

## The Original Sequence Diagram Submitted

```
sequenceDiagram
    participant User as Fan / Telemetry Trigger
    participant Intent as Intent Detection
    participant Plan as Planning & Reasoning
    participant Tool as Tool Invocation (FastF1/STT)
    participant Output as Output & Evaluation
    User->>Intent: Natural Language Query or Data Trigger
    Intent->>Plan: Identify Context (Strategy/Technical)
    Plan->>Tool: Request Data/Simulation
    Tool-->>Plan: Return Raw Data/Insights
    Plan->>Output: Synthesize Narrative + Trust Citation
    Output-->>User: Plain-English Tactical Alert
    Note over Output: Includes Traceability Link to Source
    User-->>Intent: Feedback Loop (Follow-up Query)
```

---

## Overall Verdict

**Architecturally valuable as a communication tool for non-technical reviewers, but with 3 meaningful misalignments that understate the system's most important components.**

Specifically: the three components that distinguish this system from a basic chatbot — the NLP Synthesizer, the RAG Vector DB, and the confidence gate — are all absent. A judge reviewing this against the Week 2 cluster prioritisation would note that Cluster 1 (Synthesis Engine, the highest-priority cluster) has no representation in the sequence at all.

The happy path is clear. The feedback loop is a genuine contribution not present in the workflow slide. The traceability note is the most important line in the diagram. The foundation is right. The problems are in the omissions.

---

## Misalignment 1 — The NLP Synthesizer is missing

**What the diagram shows:**  
The Fan/Telemetry Trigger communicates directly with Intent Detection as the first step.

**Why this is wrong:**  
The very first step in the architecture is the Perception layer. Raw telemetry and noisy pit-wall audio get cleaned and transcribed before Intent Detection ever sees them. In the sequence as submitted, the input arrives at Intent Detection as if it is already structured. This skips the most technically complex part of the entire system — the component that justifies using IBM Watson Speech-to-Text, the component that handles 1.1M data points per second, the component that transforms high-noise pit radio into something a reasoning engine can parse.

**What this misalignment conceals:**  
The NLP Synthesizer is Cluster 1 — the highest-priority cluster in the Week 2 prioritisation. It is described in the IBM prioritisation slide as "mandatory to ingest unstructured audio and complex 2026 telemetry." Leaving it out of the sequence diagram means the highest-priority technical component is invisible in the workflow view.

**The correct flow:**  
`Sofia → NLP Synthesizer → Intent Detection`

The NLP Synthesizer is the first active participant Sofia's input reaches. It structures the raw input before anything else happens.

**Additional inference:**  
The NLP Synthesizer also fires an audit notification to the Overseer as it produces output. This means governance knows what came in before any reasoning starts. This monitoring hook is only possible if the Synthesizer is a visible participant in the sequence.

---

## Misalignment 2 — The RAG Vector DB is invisible

**What the diagram shows:**  
Planning & Reasoning calls Tool Invocation for FastF1 data, then synthesises a narrative. No retrieval from the knowledge store occurs.

**Why this is wrong:**  
The RAG Vector DB is what separates this system from a sophisticated API wrapper. The Agentic Strategist produces its analysis by cross-referencing live data against the FIA 2026 regulation corpus and historical strategy patterns. If the RAG retrieval is not shown in the sequence, the reader has no visibility into where the system's knowledge comes from — and no way to understand the citation mechanism that makes outputs trustworthy.

**The ordering problem:**  
The original diagram implies the agent reasons, then looks things up. The correct sequencing is the opposite: retrieve first, reason second. An agent that reasons first and retrieves second is confirming its own assumptions. An agent that retrieves first is constrained by what the documents actually say. This is not a minor implementation detail — it is the fundamental design decision that determines accuracy.

**The correct sequence:**  
`Plan ->> RAG: Retrieve FIA regs + history` → `RAG -->> Plan: Context + citations` → (then) `Plan ->> Tool: Request live data`

RAG retrieval precedes tool invocation. The knowledge context is established before live data is fetched and interpreted.

**What this misalignment conceals:**  
The RAG retrieval audit — the Overseer's second monitoring hook — is only meaningful if RAG retrieval is a visible, discrete step in the sequence. If retrieval is invisible, the audit is invisible, and the governance layer loses one of its three monitoring points.

---

## Misalignment 3 — The confidence gate is missing

**What the diagram shows:**  
`Plan → Output` is a straight arrow. The output is generated and delivered without any decision point.

**Why this is wrong:**  
The workflow slide correctly identified a confidence gate: if RAG retrieval score is below 0.7, the output is text-only (no audio) and flagged as low confidence. But the sequence diagram — which is the more precise temporal view of the system — shows no such gate. A sequence diagram with no decision points is not a complete technical workflow; it is the happy path only.

**The deeper problem:**  
A confidence score gate and a governance pre-delivery check are two different things serving two different purposes. The confidence gate handles retrieval uncertainty (the model isn't sure). The governance check handles confident-wrong output (the model is sure but incorrect). Both need to be visible in the sequence. The original diagram has neither.

**The correct addition:**  
An `alt` block showing two branches:  
- Confidence ≥ 0.7 + citation validated → deliver with traceability link  
- Below threshold or citation mismatch → flag, suppress, or retry

After the governance layer was added, this became a three-branch `alt` block. See below.

---

## The Additional Correction Applied During Governance Design

**The feedback loop re-entry point**

The original diagram shows: `User -->> Intent: Feedback Loop (Follow-up Query)`

This re-enters at Intent Detection. The corrected diagram re-enters at the NLP Synthesizer.

**Why this matters:**  
A follow-up query is still raw human input that requires structuring before it can be reasoned about. Re-entering at Intent Detection implies follow-up queries are already structured — that the system trusts them more because they are continuations of a prior conversation. This creates a potential fast path that bypasses the Perception layer's cleaning and auditing functions.

Re-entering at the NLP Synthesizer ensures every query, regardless of context, receives the same structuring and transcript auditing treatment on the way in. There are no shortcuts for follow-up queries. This closes a potential vulnerability in which an unusual or adversarial follow-up query could exploit the assumed trust of being a continuation.

---

## The Corrected Sequence Diagram (pre-governance)

This is the corrected version before the Governance Overseer was added — three misalignments fixed:

```
sequenceDiagram
    participant Sofia as Tifosi (Sofia)
    participant NLP as NLP Synthesizer
    participant Intent as Intent Detection
    participant Plan as Planning & Reasoning
    participant RAG as RAG Vector DB
    participant Tool as FastF1 / STT
    participant Output as Output & Evaluation
    Sofia->>NLP: Raw audio + telemetry stream
    NLP->>Intent: Structured signal + transcript
    Intent->>Plan: Context identified
    Plan->>RAG: Retrieve FIA regs + strategy history
    RAG-->>Plan: Context + citations
    Plan->>Tool: Request live data
    Tool-->>Plan: Raw data + insights
    alt Confidence >= 0.7
        Plan->>Output: Synthesize narrative + citation
        Output-->>Sofia: Plain-English tactical alert
        Note over Output: Traceability link to source
    else Confidence < 0.7
        Plan->>Output: Flag uncertain
        Output-->>Sofia: Partial context + uncertainty flag
    end
    Sofia-->>NLP: Follow-up query
```

---

## The Final Corrected Sequence Diagram (with Governance)

After the Governance Overseer Agent was added, the sequence was extended. See `04_governance_guardrails.md` for full rationale and `06_final_mermaid_code.md` for the complete pasteable code.

### Summary of additional changes from governance addition:

1. **Overseer Agent added as a participant** — sits between Execution Module and Sofia at the delivery stage
2. **NLP transcript audit added** — NLP Synthesizer fires an audit to the Overseer as it produces output, before reasoning begins
3. **RAG retrieval audit added** — Overseer receives parallel notification of what was retrieved and how well it matched
4. **Pre-delivery check formalised** — Execution Module asks Overseer for permission before delivering to Sofia
5. **Retry loop added** — Overseer sends failure reason back to Planning with amended context, not just a block signal
6. **Three-branch alt block** — Approved / Retry passes / Retry budget exhausted (uncertainty response)

---

## Alignment Against IBM Week 4 Template Requirements

The IBM Week 4 Solution Blueprint (page 18) requires the workflow diagram to show:

| Required element | Present in corrected sequence |
|---|---|
| User request received | Sofia → NLP Synthesizer |
| Interpretation / intent detection | NLP Synthesizer → Planning |
| Planning / Reasoning | Planning Engine (full participant) |
| Tool invocation or action execution | FastF1 / STT participant |
| Output & evaluation | Execution Module + Overseer pre-delivery check |
| Loop / feedback if needed | Sofia -->> NLP: Follow-up query |

All six required elements are present. The corrected sequence exceeds the template requirements by also showing RAG retrieval, the Overseer audit chain, and the retry loop — all of which are necessary for a complete technical audit trail.
