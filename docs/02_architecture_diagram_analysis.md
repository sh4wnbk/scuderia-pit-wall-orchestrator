# Architecture Diagram — Analysis, Misalignments & Corrections

---

## The Original Diagram

The following Mermaid code was the starting point submitted for review:

```
graph TD
    subgraph "Perception Layer (Input)"
        A[Input Processor] -->|Telemetery/Audio| B(NLP Synthesizer)
    end
    subgraph "Reasoning & Planning"
        C{Planning Engine} -->|Query| D[2026 Regulation Agent]
        C -->|Analyze| E[Agentic Strategist]
    end
    subgraph "Memory & Knowledge Store"
        F[(RAG Database)] ---|2026 FIA Regs| D
        F ---|Strategy History| E
    end
    subgraph "Tools & External Interfaces"
        G[Tool Connectors] ---|FastF1 API| E
        G ---|Speech-to-Text| B
    end
    subgraph "Action & Execution Module"
        H[Execution Module] -->|Output| I[Tactical Narrative]
        H -->|Output| J[Audio Overlay]
    end
    B --> C
    D --> H
    E --> H
    style I fill:#FF0000,stroke:#333,stroke-width:2px,color:#fff
    style J fill:#FF0000,stroke:#333,stroke-width:2px,color:#fff
```

---

## Overall Verdict

**Structurally sound, but with 4 notable misalignments.**

The diagram correctly identifies all five required layers. The dual-agent routing (Regulation Agent + Agentic Strategist) maps accurately to Week 2's Cluster 1 and Cluster 2 prioritisation. The red output nodes correctly represent the dual-state UX from Week 1 and Week 2. The foundation is right. The problems are in the connections and omissions.

---

## Misalignment 1 — Speech-to-Text is in the wrong subgraph

**What the diagram shows:**  
Speech-to-Text lives inside the "Tools & External Interfaces" subgraph, connected to the NLP Synthesizer via the Tool Connectors node.

**Why this is wrong:**  
In the project's architecture, audio ingestion is a Perception layer concern. Speech-to-Text is not a tool that gets invoked on demand — it is an always-on component that feeds the input pipeline continuously during a race. Placing it in Tools implies it is optional, external, and called when needed. It is none of those things.

**The correct placement:**  
Speech-to-Text belongs inside the Perception subgraph, feeding directly into the NLP Synthesizer. This accurately reflects the continuous audio transcription pipeline that runs throughout the race session.

**What this misalignment understates:**  
If Speech-to-Text is in Tools, it appears to be the same category of thing as FastF1 API — an external data source queried on demand. But Speech-to-Text is actually half of the input layer alongside structured telemetry. The difference matters for latency architecture: an always-on stream has fundamentally different requirements from a request-response API call.

---

## Misalignment 2 — The user (Sofia) is absent from the diagram

**What the diagram shows:**  
The diagram has no user node. Information appears to begin at the Input Processor with no origin.

**Why this is wrong:**  
Sofia is not passive. Her natural language queries — the "pull" mechanism — are central to the product's value proposition. The Agentic Strategy Chat (Cluster 2, Rank 2 priority in Week 2) is specifically the mechanism by which fans pull context via natural language queries. If Sofia is not in the diagram, this entire interaction mode is invisible.

More critically, the invisible constraint from Sofia's persona card — *"if the AI hallucinates a strategy call or lags behind the live TV broadcast, trust is destroyed and the tool is permanently abandoned"* — has no meaning if the user is absent. The diagram should make visible who the system is serving and how they enter it.

**The correct addition:**  
Sofia appears as a distinct node (stadium shape, IBM Blue `#0f62fe`) with two incoming arrows: one for her voice/text query, and one representing the 1.1M pts/sec telemetry stream as a separate explicit entry point.

**Inference captured here:**  
The 1.1M telemetry figure is one of the most striking numbers in the entire project. It appears in the Week 1 and Week 2 presentations as a key data point justifying the AI approach. Leaving it out of the architecture diagram loses the visual argument for why a simple app cannot handle this — only an agentic AI system can.

---

## Misalignment 3 — RAG connections are undirected

**What the diagram shows:**  
The RAG Database connects to the Regulation Agent and Agentic Strategist using `---` (undirected lines with labels "2026 FIA Regs" and "Strategy History").

**Why this is wrong:**  
Undirected connections suggest a bidirectional or ambiguous relationship. The actual relationship is directional: the agents query the RAG store, and the RAG store returns retrieved context. This is not a passive association — it is an active retrieval operation that is foundational to the system's accuracy and trustworthiness.

**The correct representation:**  
Directional arrows from the RAG DB to each agent, labeled with what is retrieved (`FIA 2026 regs`, `strategy history`). This makes the retrieval flow explicit and sets up the governance layer's audit function correctly — the Overseer needs to monitor what is retrieved, which implies retrieval is a discrete, observable event.

**Inference captured here:**  
The direction matters architecturally. RAG retrieval happens before reasoning, not after. An agent that reasons first and retrieves second is confirming its own assumptions. An agent that retrieves first is constrained by what the documents actually say. Making the arrows directional makes this sequencing visible.

---

## Misalignment 4 — The 1.1M telemetry source has no representation

**What the diagram shows:**  
The Input Processor exists but has no labeled input. The telemetry stream — the primary continuous data source — is implied but invisible.

**Why this is wrong:**  
The entire justification for an agentic AI system (rather than a smarter app) is the scale and velocity of the data. 1.1 million data points per second is not a number that can be handled by a traditional request-response architecture. Making this visible in the architecture diagram is the primary argument for the technical approach chosen. Leaving it out loses that argument.

**The correct addition:**  
An explicit `Telem[1.1M pts/sec]` node with a labeled arrow (`raw telemetry`) into the Input Processor. This appears alongside Sofia's query entry point — two distinct input streams, both explicit.

---

## The Fifth Issue Added During Governance Review — Missing Governance Layer

This was identified during Week 4 reasoning, not the initial review.

**What the original diagram lacks:**  
No governance, oversight, or trust enforcement mechanism. The system is designed to produce outputs with no component responsible for validating those outputs before delivery.

**Why this is critical:**  
The invisible constraint from Sofia's persona card is not solved by the confidence gate alone. The confidence gate addresses retrieval uncertainty. It does not address confident-wrong output — where the RAG retrieval returns a plausible but incorrect chunk, the model generates a fluent narrative, the citation looks real, and the confidence score is high. The system is certain. It is also wrong.

**The correct addition:**  
A full Governance subgraph containing the Overseer Agent and Audit Log. Full rationale documented in `04_governance_guardrails.md`.

---

## The Corrected Architecture Diagram

```
graph TD
    Sofia([Sofia · Tifosi]) -->|voice / text query| A
    Telem[1.1M pts/sec] -->|raw telemetry| A

    subgraph percep["① Perception"]
        A[Input processor] --> B(NLP Synthesizer)
        STT[Speech-to-Text] --> B
    end

    subgraph reason["② Reasoning & planning"]
        C{Planning engine} -->|regulation query| D[Regulation agent]
        C -->|strategy analysis| E[Agentic Strategist]
    end

    subgraph memory["③ Memory & knowledge"]
        F[(RAG Vector DB)]
    end

    subgraph tools["④ Tools"]
        G[FastF1 API]
    end

    subgraph govern["⑤ Governance · watsonx.governance"]
        OV[Overseer agent] --> AL[(Audit log)]
        OV -->|retry — amended context| C
    end

    subgraph action["⑥ Action & execution"]
        H[Execution module]
        H --> I[Tactical narrative]
        H --> J[Audio overlay]
        H --> K[Uncertainty response]
    end

    B --> C
    F -->|FIA 2026 regs| D
    F -->|strategy history| E
    G -->|live data| E
    D --> H
    E --> H
    H -.->|pre-delivery check| OV
    B -.->|transcript audit| OV
    F -.->|retrieval audit| OV

    I --> Sofia
    J --> Sofia
    K --> Sofia

    style Sofia fill:#0f62fe,stroke:#0043ce,color:#ffffff
    style Telem fill:#525252,stroke:#393939,color:#ffffff
    style I fill:#da1e28,stroke:#a11e2b,color:#ffffff
    style J fill:#da1e28,stroke:#a11e2b,color:#ffffff
    style K fill:#f1c21b,stroke:#b28600,color:#161616
    style OV fill:#6929c4,stroke:#491d8b,color:#ffffff
    style AL fill:#491d8b,stroke:#31135e,color:#ffffff
```

---

## Color Encoding Rationale

| Color | Hex | Used for | Why |
|---|---|---|---|
| IBM Blue | `#0f62fe` | Sofia node | She is the user — the reason the system exists. IBM Blue aligns with the IBM Carbon design language used throughout the project. |
| IBM Gray | `#525252` | Telemetry source | Structural input — not a person, not a system component, just raw data. Should recede visually. |
| Ferrari Red | `#da1e28` | Tactical Narrative, Audio Overlay | These are the confirmed, validated outputs — the product's delivered value. Ferrari Red encodes success-state delivery. |
| IBM Yellow | `#f1c21b` | Uncertainty Response | Warning state — not failure, not success. A deliberate honest fallback that preserves trust. |
| IBM Purple | `#6929c4` | Overseer Agent | Governance has a distinct visual identity — it is the one component with authority over all others. Should be immediately recognisable as different in kind from the processing agents. |
| Dark Purple | `#491d8b` | Audit Log | Same family as Overseer — governance infrastructure. Darker to signal it is a store, not a processor. |

---

## Architecture Alignment Against Week 2 Cluster Priorities

| Week 2 Cluster | Priority | Representation in corrected diagram |
|---|---|---|
| Cluster 1: Synthesis Engine | Rank 1 | NLP Synthesizer + Speech-to-Text in Perception layer |
| Cluster 2: Agentic Strategist | Rank 2 | Planning Engine + Agentic Strategist + RAG retrieval |
| Cluster 3: Adaptive Interface | Rank 3 | Tactical Narrative + Audio Overlay in Action/Execution |
| Governance (added Week 4) | Critical | Overseer Agent + Audit Log in dedicated Governance subgraph |

The corrected diagram now represents all three week 2 clusters plus the governance addition that was identified as architecturally necessary in Week 4 reasoning.
