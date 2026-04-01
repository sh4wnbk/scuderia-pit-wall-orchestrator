# Final Mermaid Code — Both Diagrams

Paste these directly into diagrams.net (Draw.io) via **Extras → Edit Diagram**, then select **Mermaid** from the format dropdown.

---

## Architecture Diagram

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

## Sequence Diagram

```
sequenceDiagram
    participant Sofia as Sofia (Tifosi)
    participant NLP as NLP Synthesizer
    participant Plan as Planning & Reasoning
    participant RAG as RAG Vector DB
    participant Tool as FastF1 / STT
    participant OV as Overseer Agent
    participant Out as Execution Module

    Sofia->>NLP: Raw audio + telemetry
    NLP->>OV: Transcript audit
    NLP->>Plan: Structured signal
    Plan->>RAG: Retrieve FIA regs + history
    OV-->>Plan: RAG retrieval audit
    RAG-->>Plan: Context + citations
    Plan->>Tool: Request live data
    Tool-->>Plan: Raw data
    Plan->>Out: Synthesize narrative + citation

    Out->>OV: Pre-delivery check

    alt Citation validated · confidence >= 0.7
        OV-->>Out: Approved
        Out-->>Sofia: Tactical narrative + audio overlay
        Note over Out,Sofia: Traceability link included
    else Citation mismatch or confidence < 0.7
        OV->>Plan: Retry — amended context + failure reason
        Plan->>RAG: Re-query with corrected scope
        RAG-->>Plan: Refined context
        Plan->>Out: Revised narrative
        Out->>OV: Pre-delivery check 2
        alt Retry passes
            OV-->>Out: Approved on retry
            Out-->>Sofia: Tactical narrative + audit flag
        else Retry budget exhausted
            OV-->>Out: Suppress confident output
            Out-->>Sofia: Uncertainty response — partial context
            Note over Out,Sofia: Trust preserved over false confidence
        end
    end

    Sofia-->>NLP: Follow-up query
```

---

## Node Shape Reference

In Mermaid, node shapes encode meaning. This diagram uses shapes deliberately:

| Shape syntax | Renders as | Used for | Why |
|---|---|---|---|
| `([text])` | Stadium / pill | Sofia | Distinguishes the human user from system components |
| `[text]` | Rectangle | Processing components | Standard system node |
| `(text)` | Rounded rectangle | NLP Synthesizer | Soft process — indicates transformation |
| `{text}` | Diamond | Planning Engine | Decision node — routes to one of two agents |
| `[(text)]` | Cylinder | RAG Vector DB, Audit Log | Database / store — universally recognised convention |

---

## Color Encoding Reference

| Color | Hex | Applied to | Meaning |
|---|---|---|---|
| IBM Blue | `#0f62fe` | Sofia node | The user — reason the system exists. IBM Carbon primary. |
| IBM Gray | `#525252` | Telemetry source | Structural raw input. Should visually recede. |
| Ferrari Red | `#da1e28` | Tactical Narrative, Audio Overlay | Confirmed delivery — the product's primary value. |
| IBM Warning Yellow | `#f1c21b` | Uncertainty Response | Warning state. Not failure. Honest partial delivery. |
| IBM Purple | `#6929c4` | Overseer Agent | Governance — authority over all other components. |
| Dark Purple | `#491d8b` | Audit Log | Governance infrastructure. Darker = store, not processor. |

---

## Draw.io Import Notes

**Architecture Diagram:**
- Import via Extras → Edit Diagram → select Mermaid format
- `style` lines are standard Mermaid and render correctly on import
- Draw.io converts all elements to its own shape/edge format on import — you can then restyle individual nodes using the Draw.io panel rather than being locked to the hex values above
- Dashed lines (`-.->`) render as dashed edges in Draw.io
- Subgraph labels render as container group labels

**Sequence Diagram:**
- Imports cleanly as-is
- Nested `alt` blocks are supported in Draw.io's Mermaid importer
- The `Note over` annotations may need minor manual repositioning after import depending on the Draw.io version
- `-->>` renders as dashed return arrows (responses); `->>` renders as solid request arrows

**General note:**
Draw.io's auto-layout may reposition nodes on import. The logical relationships are preserved; visual positions may need adjustment to match the intended reading flow.

---

## Rendering Environments

These diagrams were developed and rendered in:

- **Claude.ai Visualizer** (primary rendering — IBM Carbon color theme applied via Mermaid themeVariables)
- **Draw.io / diagrams.net** (target export environment)
- **Mermaid Live Editor** (mermaid.live) — paste code directly, renders without theming

For the IBM Carbon theme to render in Draw.io, apply colors manually using the Draw.io style panel after import, using the hex values in the color reference table above.
