# Week 4 Blueprint — Design Decisions & Rationale

---

## The IBM Week 4 Template Requirements

The IBM Solution Blueprint (Week 4, pages 17–19) requires three distinct slides:

### Slide 1 — AI Agent Architecture (page 17)
Required sections:
- Agent Overview (one-sentence summary, single vs multiple agents)
- Agent Roles table (agent / responsibility / key decisions)
- Why this architecture? (design decisions, data flow traceability, component necessity)
- Architecture Diagram (5-layer block diagram)

### Slide 2 — AI Agent Workflow (page 18)
Required sections:
- Workflow Diagram (flowchart: user request → interpretation → planning → tool invocation → output → loop)
- Workflow Description
- Decision Points (branching conditions)
- Human-in-the-loop moments
- Failure strategy nodes

### Slide 3 — Tools & Integrations (page 19)
Required columns:
- Tool / Service
- Used For
- Integration Type
- Executables vs autonomy (invoked by agents or workflows, automated vs user-verified)
- Notes on Constraints

---

## Version 1 — Dark Theme (Rejected)

### What it was

A dark-background design using Ferrari Red (`#CC0000`) as the primary accent, white text, and dark card backgrounds. Three slides matching the IBM template structure.

### Why it was rejected

**Problem 1 — Too text-heavy**

The original version filled each slide with dense prose. The IBM template calls for concise bullets and a diagram — not paragraphs. Specifically:

- The "Why this architecture?" section was written as a paragraph rather than four tight bullets
- The workflow description cards contained full sentences where short phrases were sufficient
- The agent overview repeated information that should have been in the diagram itself

**Problem 2 — Dark theme conflicts with IBM design language**

The IBM Carbon design language uses a white background for content slides with IBM Gray 100 (`#161616`) for header bands. A dark background throughout is the opposite of IBM's documented aesthetic. Ferrari's own presentation materials use white backgrounds with red accents — not a dark theme.

**Problem 3 — Architecture "diagram" was actually a legend**

The five-layer architecture diagram in Version 1 was five colored rectangles stacked vertically with text inside them. This is a legend, not a diagram. It shows what the layers are named but not how data moves between components. The Mermaid diagram rendered in the chat was superior precisely because it had nodes with relationships — arrows, subgraphs, directionality.

---

## Version 2 — IBM Carbon Theme (Current)

### Design language applied

IBM Carbon's documented design language was applied via web research:

| Element | IBM Carbon spec | Applied value |
|---|---|---|
| Background | White | `#ffffff` |
| Header band | Gray 100 | `#161616` |
| Primary accent | Blue 60 | `#0f62fe` |
| Body text | Gray 100 | `#161616` |
| Secondary text | Gray 60 | `#6f6f6f` |
| Surface | Gray 10 | `#f4f4f4` |
| Border | Gray 20 | `#e0e0e0` |
| Error / Ferrari accent | Red 60 | `#da1e28` |

**Typography:** Calibri used as a system-safe substitute for IBM Plex Sans, which is not available in PowerPoint without installation.

**Layout:** IBM's 2x grid principle applied — consistent column widths, left-aligned headers, generous whitespace between sections.

### Key design decisions

**Decision 1 — Single IBM Blue as the only accent color**

IBM Blue (`#0f62fe`) is used for section headers, table header rows, and the blue line rule under the header band. No other accent color appears in the slide body. Ferrari Red (`#da1e28`) is reserved for the two output nodes in the architecture diagram only.

**Why:** Using one accent color creates a clean visual hierarchy. IBM Blue for structure and navigation; Ferrari Red for the product's delivered value. This encodes meaning — red means "this is what the fan receives" — rather than decorating.

**Decision 2 — Architecture diagram as image embed (Option B)**

Two options were considered for the architecture and workflow diagrams:

**Option A:** Build a proper node-and-edge diagram using PptxGenJS shape primitives (circles, cylinders, diamonds, directional arrows). Self-contained, editable in PowerPoint.

**Option B:** Generate the diagram as a Mermaid render (SVG quality) and embed it as an image into the slide. Not editable in PowerPoint, but matches the quality and structure of the rendered diagrams.

**Option B was chosen** because:
- The Mermaid diagrams rendered in the conversation already have the correct structure — subgraphs, node types, directional arrows, governance connections
- Embedding as an image preserves the diagram's visual integrity without the coordinate math risk of hand-placing nodes in PptxGenJS
- The slides' primary audience (IBM judges) will see a finished diagram, not an editable construction

**Decision 3 — Text reduction strategy**

The IBM template tip says: "Keep text concise and diagrams labelled. Be ready to explain each component and transition."

The phrase "be ready to explain" is the key inference. The slide does not need to contain the explanation — the presenter (Shawn) does. This means the slide's text should be the minimum required to orient a reader, with all detailed explanation living in the presenter notes and in documents like this one.

Applied reductions:
- Agent overview: one sentence + type declaration (not a paragraph)
- "Why this architecture?" four tight bullets (not a paragraph)
- Workflow cards: label + 2–3 short lines maximum
- Tools table: single-clause entries in "Used For" column (not full sentences)

**Decision 4 — Three constraint cards, not a bulleted list**

The constraints section uses four equal-width cards with IBM Blue top-accent bars. This is a visual structure borrowed from IBM Carbon's "feature tiles" pattern — equal-weight items displayed in a grid rather than a ranked list.

**Why:** The four constraints (latency, hallucination guard, API quotas, data availability) are not ranked — they are all active simultaneously. A bulleted list implies sequence or priority. Cards imply parallel concerns at equal weight.

---

## The Diagram Type Decision — Block vs Node-Edge

The initial PPTX versions used block diagrams (colored rectangles with text). The conversation identified this as the wrong choice.

### Why block diagrams fail for this architecture

A block diagram shows what exists. A node-edge diagram shows what connects and how. For an agentic AI system where the relationships between components — particularly the governance monitoring hooks and retry loops — are the architecturally interesting parts, a block diagram hides the most important information.

Specifically:
- A block labeled "Governance · watsonx.governance" tells the reader it exists
- A node connected by dashed monitoring lines to three upstream components and a retry arrow back into Planning tells the reader *how it works*

The second version carries the architectural argument. The first does not.

### The tool recommendation analysis

The following tools were assessed for diagram creation:

**Lucidchart / diagrams.net (Draw.io)**  
Best for the Architecture Diagram. Built-in libraries for Blocks, Nodes, and Database icons that match the IBM Carbon technical aesthetic. Node-edge diagramming with proper shape semantics (cylinders for databases, diamonds for decisions, etc.).

**Figma**  
Best for UI wireframes and the Workflow Diagram where precise visual control of the Ferrari Rosso accents and whitespace is needed. Allows pixel-level control of the IBM Carbon aesthetic.

**Excalidraw / Miro**  
Appropriate for ideation sprints and whiteboarding initial agent handoffs, but the hand-drawn aesthetic is too informal for a final professional presentation.

**Decision made:** Use Mermaid renders (via Claude Visualizer) exported to the PPTX as embedded images. The Mermaid code is also provided for direct import into Draw.io, where colors and layouts can be refined using the Draw.io style panel.

---

## The PPTX Slide-by-Slide Breakdown

### Slide 1 — AI Agent Architecture

Left column contains: Agent Overview (one sentence + type), Agent Roles table (three-row, three-column), Why this architecture (four bullets).

Right column contains: The five-layer architecture block diagram with numbered layers, IBM Blue-to-dark-navy-to-charcoal-to-Ferrari-Red color graduation encoding data flow direction.

**Color graduation inference:** The layers graduate from IBM Blue (Perception) through darker blues/navies (Reasoning, Memory) to charcoal (Tools) to Ferrari Red (Action/Execution). This encodes the data flow direction visually — the eye follows the color gradient from input to output — without needing a separate legend.

### Slide 2 — AI Agent Workflow

Left column contains: Four compact cards — Workflow Description, Decision Points, Human-in-the-loop, Failure Nodes. Each card uses IBM Blue top-accent bar + Gray 10 background.

Right column contains: Six-step numbered flowchart with the same color graduation as the architecture diagram. Step numbers appear as white rectangles inside each colored step block.

Footer contains: Feedback loop note in italic gray — "↺ Loop — fan feedback or new telemetry re-enters at step 1."

### Slide 3 — Tools & Integrations

Full-width tools table with seven rows and four columns. Alternating Gray 10 / White row backgrounds for readability.

Below the table: Four constraint cards (Latency, Hallucination guard, API quotas, Data availability) using the same IBM Blue top-accent card pattern.

---

## Outstanding Design Questions

These were identified during the conversation but not yet resolved:

1. **Full-bleed diagram vs split layout:** Should the architecture and workflow diagrams occupy the full slide (with just a title and caption as text), or share the slide with the text sections as in the current template layout? The full-bleed option allows more diagram detail but loses the template structure IBM expects.

2. **Diagram embed resolution:** Mermaid SVG renders at screen resolution. For a professional presentation, the embed should be at minimum 300 DPI equivalent. The optimal approach is to render the Mermaid diagram at high resolution (via mermaid.live or Draw.io) and save as a high-resolution PNG before embedding in the PPTX.

3. **Draw.io refinement:** The Mermaid code provided in `06_final_mermaid_code.md` imports cleanly into Draw.io. After import, IBM Carbon colors should be applied manually using the style panel. The Draw.io version can then be exported as a high-resolution PNG and embedded into the PPTX as Option B.
