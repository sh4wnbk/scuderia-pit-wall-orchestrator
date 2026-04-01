# Both Diagrams Explained in Plain English

This document explains every step of both the Architecture Diagram and the Sequence Diagram — what each step does, why it exists, and what it guards against.

---

## The Architecture Diagram

Think of this diagram as a map of the whole system at rest. It shows all the components, how they are grouped, and what connects to what. It answers the question: "what does this thing consist of?"

---

### Sofia and the telemetry stream — two doors into the same system

There are two ways information enters the system. Sofia types or says something — a question, a reaction, a "why did Leclerc just back off?" — and that enters as unstructured human language. Simultaneously, 1.1 million data points per second are streaming in from the car's sensors. These are completely different kinds of input arriving at the same moment, and the system has to handle both at once.

This is why there is an explicit entry point for each. Without making both visible, you would have an architecture that handles queries but ignores the live race, or vice versa.

**What it guards against:** An architecture that serves either the passive viewer or the active querier, but not both simultaneously. The Pit-Wall Fan Orchestrator needs to handle live telemetry continuously while also responding to Sofia's questions on demand. Two entry points make both modes architecturally explicit.

---

### The Perception Layer — cleaning the noise before anything else happens

Before any reasoning occurs, the raw inputs have to become something the system can actually work with. The NLP Synthesizer takes Sofia's voice or text and the telemetry stream and structures them. The Speech-to-Text component handles the pit-wall radio specifically — which is high-noise, heavily accented, full of jargon, and often clipped mid-sentence.

This layer exists because every component downstream depends on clean, structured input. If you skip this step and feed raw audio directly into reasoning, you get garbage in, confident garbage out.

**What it guards against:** The first line of defence against the core failure scenario — the app returning something wrong that feels right. If the transcript of a pit radio message is garbled before it reaches the reasoning layer, every downstream output based on that transcript is potentially wrong. Cleaning the input is non-negotiable.

**Why Speech-to-Text belongs here and not in Tools:** Speech-to-Text is not invoked on demand like an API call. It runs continuously throughout the race session, transcribing audio as it arrives. It is infrastructure, not a tool. Classifying it as a tool implies it is optional and called when needed. It is neither.

---

### The Reasoning and Planning Layer — the brain that decides what to do

Once the input is clean, the Planning Engine looks at what is being asked and makes a routing decision. It asks: is this a regulation question or a strategy question?

These are fundamentally different problems that require different knowledge and different tools. A question about whether Z-Mode is legal under 2026 FIA rules needs the Regulation Agent, which is trained specifically on that regulatory corpus. A question about whether Ferrari should pit now needs the Agentic Strategist, which understands race context, tyre degradation history, undercut windows, and competitor positioning.

Keeping these two agents separate means neither is doing a job it is not equipped for.

**What it guards against:** Misrouting — sending a regulation question to the strategy agent and getting a plausible but legally incorrect answer, or sending a strategy question to the regulation agent and getting a technically correct but contextually irrelevant response. The Planning Engine enforces specialisation.

---

### The Memory and Knowledge Layer — the only source of truth

The RAG Vector Database is what separates this system from a chatbot that makes things up. Every answer the agents produce has to be grounded in something real that lives here.

The FIA 2026 regulations are stored here as a searchable corpus. Ferrari's historical strategy patterns are here. Fan query history is here. When the Regulation Agent says "Z-Mode is the high-downforce active aero state," it is not generating that from pattern-matching on training data — it is retrieving it from an actual document.

This is the citation mechanism. It is what makes outputs auditable and traceable.

**What it guards against:** Hallucination at the knowledge level. Without the RAG store, the system can produce fluent, confident answers that have no basis in any official document. With the RAG store, every output can be traced to a specific chunk in a specific document. The citation is not decoration — it is the evidence.

---

### The Tools Layer — live data that the knowledge store cannot have

The RAG store contains what was known before the race. The FastF1 API contains what is happening right now — current lap times, sector splits, tyre age, live gaps between cars. These are two completely different things.

Historical strategy patterns tell you what teams tend to do in a given situation. Live telemetry tells you what is actually happening in this lap of this race. The Agentic Strategist needs both.

**What it guards against:** Reasoning from stale data — making a pit strategy call based on historical patterns without knowing that the safety car just came out and changed everything. The Tools layer ensures the system is always grounded in current race reality, not just historical probability.

---

### The Governance Layer — the proactive trust enforcer

This is the component that exists specifically because of the trust failure scenario. The Overseer Agent sits alongside the entire pipeline with three monitoring hooks: it audits the NLP transcript as it is produced, audits the RAG retrieval as it happens, and runs a pre-delivery check on every output before it reaches Sofia.

If the Overseer detects a problem — a citation that does not support the claim, a transcript that was likely misheard, a confidence score that is high but the underlying sources are contradictory — it does not just block the output. It sends a retry signal back to the Planning Engine with a specific reason and amended context, so the second attempt is genuinely better informed.

**What it guards against:** Confident-wrong output — the most damaging failure mode in the system. This is distinct from low-confidence output (which the confidence gate handles) and is more dangerous precisely because the system does not know it is wrong. The Overseer's cross-validation catches what the confidence gate cannot.

**Why it is purple in the diagram:** Governance has a distinct visual identity because it is the one component with authority over all others. It should be immediately recognisable as different in kind from the processing agents.

---

### The Action and Execution Layer — three possible outcomes, not one

Most systems have one output: the answer. This system has three.

**Tactical Narrative + Audio Overlay (red):** The confirmed, validated, approved happy path. A cited, checked insight delivered as text and spoken aloud so Sofia never has to look away from the TV. The audio overlay is the product's primary differentiator — it solves the visual focus problem entirely.

**Uncertainty Response (yellow):** The honest fallback. Partial, validated context delivered transparently when the Overseer cannot validate a confident answer after retry. This is not failure — it is the system choosing trust over the appearance of knowledge.

**Audit Log (silent):** Every decision recorded with full traceability. The development team can review exactly what was said, why, and what the Overseer did about it.

**What the three-output design guards against:** The false binary of "answer or silence." During a live race, silence is nearly as bad as a wrong answer. An honest partial answer — "here is what I can confirm right now" — keeps Sofia informed and her trust intact. The three-output design acknowledges that different confidence states warrant different responses, and encodes that explicitly into the architecture.

---

## The Sequence Diagram

Where the architecture diagram shows the map, the sequence diagram shows the journey. It answers: "what actually happens, step by step, when Sofia asks something during a race?" Read it top to bottom as time passing.

---

### Sofia to NLP Synthesizer — structuring the raw input

The moment Sofia speaks or types, the NLP Synthesizer is the first thing that receives it — not the Planning Engine, not the reasoning layer. The Synthesizer's job is translation: turning "why did he just back off is the MGU-K failing?" into a structured signal that the rest of the system can parse.

It does this simultaneously for the live telemetry stream.

It also immediately fires an audit notification to the Overseer, so governance knows what came in before any reasoning starts.

**What it guards against:** A problem entering the system undetected. If the transcript is garbled or the telemetry signal is anomalous, the Overseer knows at the earliest possible moment — before reasoning based on that corrupted input has begun. Early detection means the correction is cheapest here.

---

### NLP Synthesizer transcript audit to Overseer

As the NLP Synthesizer produces its output, a copy goes to the Overseer simultaneously. The Overseer checks for transcription anomalies — garbled technical terms, telemetry values that are physically impossible, radio phrases that appear truncated or misheard.

**What it guards against:** Garbage entering the reasoning layer undetected. This is the system's earliest intervention point. Catching a bad transcript here is far cheaper than catching a wrong output at delivery — it avoids an entire reasoning cycle based on corrupt input.

---

### Planning Engine to RAG — grounding before reasoning

Before the Planning Engine does any reasoning, it queries the RAG Vector DB for relevant FIA regulations and strategy history. This sequencing is deliberate.

The agent does not reason first and then look things up to support its reasoning. It retrieves first and reasons second. That ordering matters enormously. An agent that reasons first and retrieves second is confirming its own assumptions. An agent that retrieves first is constrained by what the documents actually say.

**What it guards against:** The model using its training data priors instead of the actual 2026 FIA rulebook. Training data has a cutoff date. The FIA regulations in the RAG store are current and authoritative. Grounding before reasoning ensures the output is based on what the rules actually say, not what the model was trained to believe they might say.

---

### RAG retrieval audit to Overseer — the second monitoring hook

As the RAG retrieval happens, the Overseer receives a parallel notification of what was retrieved and how well it matched the query. The Overseer is looking for retrieval failures — cases where the returned chunks are plausible-sounding but from the wrong regulation section, or where the similarity score is high but the content is tangentially related.

The Overseer does not block retrieval. It records what was retrieved. That record is what makes the pre-delivery cross-validation possible later.

**What it guards against:** The RAG store being used as a false authority — where a document is cited but does not actually support the claim made. The retrieval audit gives the Overseer the evidence it needs to check citation accuracy at the pre-delivery stage.

---

### Planning to FastF1 — getting live race reality

Only after the knowledge context is established does the system reach out for live data. This sequencing ensures the agent is reasoning about current lap times and tyre states in the context of regulatory and historical knowledge, not in isolation.

A pit stop recommendation without regulation context might be strategically sound but technically illegal under 2026 rules. A regulation interpretation without live race context might be accurate but irrelevant to what is actually happening on track.

**What it guards against:** The system being either book-smart or street-smart but not both simultaneously. Knowledge context first, live context second — then synthesis.

---

### Output to Overseer — the pre-delivery gate

The Planning Engine synthesises its narrative and passes it to the Execution Module, which then stops and asks the Overseer for permission to deliver. The Overseer takes the generated narrative, finds the citation it claims to be based on, reads the cited source, and checks whether the narrative is actually supported by what the citation says.

This is cross-validation, not confidence scoring. A high confidence score means the model is sure about its answer. Cross-validation checks whether the answer is consistent with the source it is citing. These are completely different tests.

**What it guards against:** Confident-wrong output. This is the primary guard — the pre-delivery check is the last line of defence before the output reaches Sofia. If it passes here, it can be delivered with confidence. If it does not, the retry mechanism activates.

---

### The three-branch alt block — the system's moral architecture

Three things can happen after the pre-delivery check. All three are intentional design decisions.

**Branch 1 — Citation validated, confidence ≥ 0.7: Approved**

The output is delivered with the traceability link intact. Sofia gets her answer with a source she can verify. Trust is built because the system is showing its work. The traceability link is not decorative — it is an invitation to verify, which is itself a trust signal.

**Branch 2 — Citation mismatch or confidence < 0.7: Retry with amended context**

The Overseer sends a specific failure reason back to the Planning Engine — not just "wrong, try again" but "the cited regulation refers to 2025 rules, not 2026" or "the narrative claims harvesting but the telemetry shows deploying." Planning re-queries the RAG store with that corrected scope. The second attempt is genuinely better informed because it knows specifically what was wrong with the first one.

If this retry passes, it delivers with an audit flag — a small visible marker that this answer went through a correction cycle. The audit flag is itself a trust signal: the system checked itself.

**Branch 3 — Retry budget exhausted: Uncertainty response**

The system suppresses the confident output entirely and delivers honest partial context. This is the design decision that protects against the trust failure scenario. The fan who gets "I cannot fully confirm this right now — here is what I know with confidence" may be momentarily frustrated. That fan stays engaged. That fan returns.

The fan who gets a confident wrong narrative, feels an emotion about it, shares it, discovers the truth, and leaves a one-star review is gone permanently. The system accepts the smaller cost — momentary uncertainty — to avoid the catastrophic cost of demonstrated unreliability.

**What this block guards against:** The false binary between "confident answer" and "silence." The three branches acknowledge that reality exists on a spectrum of certainty, and that honest representation of that spectrum is more valuable than the appearance of omniscience.

---

### The feedback loop — Sofia re-entering at the right point

The diagram closes with Sofia's follow-up query going back to the NLP Synthesizer, not to Intent Detection or Planning. Every query, regardless of context, gets the same cleaning and auditing treatment on the way in. There are no shortcuts for follow-up queries.

**What it guards against:** A potential fast path that bypasses the Perception layer's structuring and auditing for queries the system treats as "trusted" because they continue a prior conversation. An unusual or adversarial follow-up query should not receive less scrutiny than an initial query. Re-entering at the NLP Synthesizer enforces this.
