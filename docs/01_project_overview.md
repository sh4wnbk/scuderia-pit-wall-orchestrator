# Scuderia Pit-Wall Fan Orchestrator — Project Overview & Context

**Author:** Shawn Blackman, B.S. Environmental Science, Lehman College (CUNY)  
**Track:** Track 3 — Fan-Centric Sports & Entertainment  
**Challenge:** IBM Build Challenge  
**Contact:** mr.shawn.blackman@gmail.com

---

## One-Sentence Summary

An agentic AI companion powered by IBM watsonx that ingests 1.1 million live F1 telemetry data points per second alongside unstructured pit-wall radio, translating complex 2026 Formula 1 technical regulations and real-time race events into plain-English tactical narratives for Ferrari fans — without requiring them to break visual focus from the TV broadcast.

---

## The Problem: The Synthesis Gap

### The 2026 Landscape

Formula 1's 2026 technical regulations introduce two unprecedented complexities running simultaneously:

- **Power Unit complexity:** ICE/ERS integration with active MGU-K (Motor Generator Unit–Kinetic) management, recharge phases, and 350kW battery deployment decisions happening lap by lap.
- **Active Aerodynamics:** Z-Mode (high-downforce cornering state) and X-Mode (low-drag straight-line state) shifting dynamically, visible in car behaviour but invisible in meaning to most fans.

At the same time, F1 cars generate **1.1 million telemetry data points per second** — RPM, tyre temperatures, fuel flow, G-forces, sector deltas, MGU-K status, aero mode states — all simultaneously.

### The Fan Reality

There are 396 million Scuderia Ferrari fans globally. 71% define the sport by high performance and precision. But the current digital ecosystem leaves them entirely outside the strategic conversation.

**What fans hear:** "Override 350kW. Z-Mode active. Box box, push now."  
**What fans think:** "Is the MGU-K failing or harvesting? I have no idea."

### The Three-Fragmentation Problem

The current information landscape has three isolated, incompatible channels:

| Channel | What it provides | What it fails to provide |
|---|---|---|
| TV Broadcast (Visual) | Race visuals, commentary | Real-time technical context |
| Live Timing App (Data) | Raw lap times, positions | Explanation of what the data means |
| Social Media / Commentary (Context) | Fan reactions, delayed analysis | Real-time accuracy, synthesis |

The failure between these channels is called the **Synthesis Gap**: raw data exists, but no mechanism translates it into strategic understanding in real time. Fans are forced to act as their own data engineers — scrambling between Reddit, X, and the F1 app — and they miss the race while doing it.

**The insight gap:** Missing the strategic chess match happening in front of them.

---

## Primary Persona: The Passionate Tifosi (Sofia)

Sofia is the primary user. She is a passionate Ferrari fan with solid basic F1 knowledge but no engineering background.

| Dimension | Detail |
|---|---|
| **Says** | "I know the basics, but the 2026 aero rules are impossible to track live." |
| **Thinks** | "Why did Leclerc just lift? Is the MGU-K failing or harvesting?" |
| **Does** | Scrambles between Reddit (r/scuderiaferrari), X, and F1 TV to find answers. |
| **Feels** | High anticipation degrading into frustration and FOMO. |

### Sofia's Persona Card (formal)

| Field | Detail |
|---|---|
| **Primary Goal** | To understand the real-time strategic chess match of a live F1 race without breaking visual focus from the TV broadcast. |
| **Systemic Friction** | Trapped in the Synthesis Gap. The official app only pushes raw data. Sofia is forced to act as a human data bridge, abandoning the live broadcast to hunt for strategic context on Reddit or X, causing severe cognitive overload. |
| **Agentic Need** | An entity that can reason through unstructured audio and live telemetry to tell her exactly why a strategic decision is happening — in plain English. |
| **Invisible Constraint** | Trust and latency. If the AI hallucinates a strategy call or lags behind the live TV broadcast, trust is destroyed and the tool is permanently abandoned. |

> **Key inference:** The invisible constraint is not a feature requirement — it is an existential product requirement. It directly shaped the governance architecture.

---

## The As-Is Journey: Five Phases of Failure

| Phase | Sofia does | Sofia thinks | Sofia feels |
|---|---|---|---|
| 1. Pre-Race Setup | Opens Ferrari App | "App looks great, but I need real data" | Anticipation |
| 2. Lights Out | Matches TV to timing app | "Did Charles get a good launch?" | Sensory overload |
| 3. Strategic Pit Window | Decodes fragmented radio | "Why did we pit Lewis now?" | Confusion |
| 4. Technical Battles (2026 Regs) | Searches social media for MGU-K status | "Why did Leclerc lift? Harvesting?" | Cognitive overload |
| 5. Post-Race Debrief | Waits for podcasts | "Missed the strategic chess match" | Partial satisfaction / FOMO |

**The result:** Cognitive overload and app abandonment — specifically during peak-value moments.

---

## Why Current Platforms Fail

1. **The Unidirectional Push:** Existing platforms (official F1 and Ferrari apps) broadcast isolated raw data — lap times, time deficits, positions — with no contextual translation.
2. **The Missing Context:** No translation of highly complex technical regulations into fan-readable language.
3. **The Pull Failure:** No mechanism for fans to query the data. Forced into cognitive overload.
4. **The Business Reality:** Non-subscribers and casual fans migrate to third-party streaming platforms, social media, or delayed broadcast. The app loses its audience during the moments it matters most.

---

## The Solution: The Scuderia Pit-Wall Fan Orchestrator

### Core Concept

An agentic AI companion powered by IBM watsonx (Granite LLMs) that:

- Ingests **1.1M live telemetry data points per second**
- Transcribes and translates **unstructured pit-wall radio** in real time
- Cross-references both against the **FIA 2026 Technical Regulations**
- Delivers **predictive, human-readable tactical narratives** via text and audio overlay
- Allows fans to **query the system in natural language** without looking away from the TV

### The Agentic Shift: The Synthesis Gap Eliminated

| As-Is (Cognitive Overload) | To-Be (Frictionless Flow) |
|---|---|
| Fan hears fragmented radio ("Z-mode"). Timing app shows raw data, no context. | Watsonx ingests 1.1M telemetry points + live radio feed continuously. |
| Fan searches social media for explanations. Misses on-track action. | Agent cross-references telemetry (harvesting data) with unstructured audio. |
| Fan abandons app. | Agent synthesises tactical insight using RAG against 2026 FIA rulebook. Delivers instant audio overlay: "Leclerc is harvesting battery for a push lap." |

### The Needs Statement

**The User:** The passionate Ferrari fan (Tifosi).  
**The Need:** Instantly synthesise live telemetry and team radio via voice and chat.  
**The Outcome:** Understand the real-time strategic narrative without breaking visual focus from the TV broadcast.

---

## Point of View (POV) Statement

> "The passionate Scuderia Ferrari fan needs a way to instantly translate complex 2026 telemetry and technical pit wall jargon into plain English, because current digital platforms force them to abandon the live broadcast to act as their own data engineers."

---

## Technical Glossary

| Term | Definition |
|---|---|
| **MGU-K** | Motor Generator Unit–Kinetic. Recovers braking energy and redeploys it as electrical power to boost acceleration and improve efficiency. |
| **Recharge Phase** | The critical tactical period where a driver must aggressively harvest kinetic energy to refill the 350kW battery. |
| **Z-Mode** | The high-downforce active aero state used for cornering grip. |
| **X-Mode** | The low-drag active aero state deployed on straights to compensate for battery depletion. |
| **RAG** | Retrieval-Augmented Generation. A technique where AI outputs are grounded in retrieved documents rather than generated from training data alone. |
| **Synthesis Gap** | The missing interactive layer between raw data and fan comprehension. The failure of current platforms to translate data into strategic context. |

---

## Three-Week Project Arc

### Week 1 — Opportunity Framing & Solution Definition
- Identified the synthesis gap
- Established Sofia as the primary persona
- Documented the five-phase as-is journey
- Defined the needs statement and POV

### Week 2 — Solution Design & Agentic Ideation
- Seven "How Might We" statements generated
- Three idea clusters identified:
  - **Cluster 1 (Synthesis Engine):** Data Translation — NLP radio transcription, aero shift explanation, personalised focus, fan-specific narrative
  - **Cluster 2 (Agentic Strategist):** Interaction — Natural language telemetry query, predictive alerts
  - **Cluster 3 (Adaptive Interface):** UI/UX — Audio overlay, MGU-K visualisation
- Prioritisation by AI justification:
  - Rank 1: Synthesis Engine (NLP mandatory for unstructured audio ingestion)
  - Rank 2: Agentic Strategist (RAG required for live cross-reference)
  - Rank 3: Adaptive Interface (UI triggers, critical for cognitive overload)
- Three top solution directions identified:
  - Direction 1: Real-Time NLP Synthesiser
  - Direction 2: Agentic Strategy Chat
  - Direction 3: Context-Aware Audio Overlay

### Week 3 — Convergence & RAG Architecture
- Full system design converged on watsonx + Granite LLMs
- RAG architecture formalised
- Persona card finalised with invisible constraint defined
- Agentic shift documented: as-is chaos vs to-be frictionless flow
- Three value propositions locked:
  - Translation Brain (NLP Synthesiser)
  - Pull Mechanism (Agentic Strategy Interface)
  - Frictionless UI (Context-Aware Audio Overlay)

### Week 4 — Solution Blueprint
- AI agent architecture formalised across five layers
- Governance Guardrails added via IBM watsonx.governance
- Proactive Overseer Agent designed with retry loop
- Sequence diagram corrected and extended
- Full plain-English justification documented

---

## Reference Architecture Sources

| Category | Source |
|---|---|
| **Regulatory** | FIA 2026 Formula 1 Technical Regulations; 2025 Global Fan Survey (Motivators, Passions, Cultural Identity) |
| **Ecosystem** | Scuderia Ferrari Digital App & Live Timing Infrastructure |
| **Technology** | IBM watsonx AI & Agentic Knowledge Synthesiser models |
