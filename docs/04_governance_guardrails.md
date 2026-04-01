# Governance Guardrails — Design Rationale & Architecture

---

## Why Governance Was Added

Governance was not in the original architecture. It was identified during Week 4 reasoning as architecturally load-bearing — not a feature addition, but a structural necessity.

Three reasons made it non-negotiable:

**1. The invisible constraint from the persona card is not solved by the confidence gate alone.**  
The confidence gate handles retrieval uncertainty — cases where the RAG store doesn't return a strongly matching chunk and the model signals it isn't sure. But the confidence gate does not address a different and more dangerous failure mode: confident-wrong output. This is when the RAG retrieval returns a plausible-sounding but incorrect chunk, the model generates a fluent narrative, the citation looks real, and the confidence score is high. The system is certain. It is also wrong. The confidence gate passes this through. The Overseer catches it.

**2. IBM watsonx.governance is a real product in the stack.**  
Leaving it out of the architecture when it is the primary IBM offering for AI risk management, explainability, and audit traceability is a missed opportunity in the context of the IBM Build Challenge specifically. The challenge is evaluated in part on appropriate use of IBM tools. Governance is not an afterthought — it is a first-class IBM product.

**3. The output layer makes real-time strategy assertions to users in emotionally charged moments.**  
The FIA governs the sport with a rulebook. The Pit-Wall Fan Orchestrator needs its own governance layer governing the AI's assertions about that sport. A system that makes confident real-time claims about race strategy — claims that fans act on emotionally — without any oversight mechanism is not a trustworthy product. It is a liability.

---

## The Trust Failure Scenario — Why This Matters

The following scenario was explicitly identified as the product's existential risk:

> The app returns a confident wrong output. The fan, in the moment, believes it — either ecstasy or disappointment, depending on the race context. Later, they check social media or official F1 outlets and discover the opposite was true. Trust is gone. The app is abandoned until updates are pushed. The app begins to accumulate user distrust and garner bad reviews.

This is not a hypothetical edge case. It is the most likely failure mode of a real-time AI system operating on high-velocity, high-noise inputs during emotionally charged live events. It has a specific name: **confident-wrong output**.

### Why confident-wrong is more damaging than acknowledged uncertainty

| Output type | Fan experience | Trust outcome |
|---|---|---|
| Correct answer | Feels informed, engaged | Trust built |
| Acknowledged uncertainty | Momentarily frustrated, still informed | Trust maintained |
| Confident-wrong answer | Feels certain, acts on it, later discovers the truth | Trust destroyed — unrecoverably |

A fan who receives "I can't fully confirm this right now — here's what I know with confidence" may be momentarily frustrated. That fan stays engaged and returns.

A fan who receives a confident wrong narrative, feels an emotion about it, potentially shares it on social media, and then discovers via X or the official F1 broadcast that the opposite was true has been actively misled by the product. That fan leaves a bad review. That fan does not return until there is visible evidence the problem was fixed. If enough fans have the same experience, the app accumulates a reputation for unreliability during exactly the moments it is supposed to be most valuable.

**The business inference:** The cost of a confident-wrong output is not one lost fan. It is one lost fan plus their social network reach plus the review they leave plus the pattern of abandonment that accumulates across the user base. The governance layer's budget — the latency cost of the retry loop — pays for itself many times over against this cost.

---

## Reactive vs. Proactive — The Design Decision

### What reactive governance looks like

A reactive Overseer monitors outputs and logs failures after they occur. It can suppress future outputs matching the same failure pattern. It builds a record of what went wrong.

**Why reactive was rejected:**  
Reactive governance does not prevent the confident-wrong output from reaching Sofia. It prevents the *next* confident-wrong output of the same type from reaching Sofia. The first fan who receives the wrong answer has already been misled. The trust damage has already occurred. Logging the failure after delivery is an audit function, not a protection function.

In a real-time sports context, there is no "undo." A wrong confident narrative delivered during a dramatic race moment cannot be retracted. The fan has already had the experience.

### What proactive governance looks like

A proactive Overseer intercepts every output before delivery, validates it against its cited source, and either approves, retries with amended context, or suppresses in favour of an honest uncertainty response.

**Why proactive was chosen:**  
User trust is paramount. The product's entire value proposition depends on Sofia trusting the output she receives. A single confident-wrong output during a high-emotion race moment can destroy that trust permanently. The proactive Overseer's job is specifically to prevent confident-wrong output — not to log it after the fact.

---

## The Overseer Agent — What It Does

The Overseer Agent is not a simple filter. It is a cross-validation engine with three monitoring hooks and one intervention mechanism.

### Three monitoring hooks

**Hook 1 — NLP Transcript Audit (earliest possible point)**  
As the NLP Synthesizer produces a structured transcript from raw audio and telemetry, it fires an audit signal to the Overseer. The Overseer receives the raw transcript alongside the structured output and checks for obvious transcription anomalies — garbled terms, impossible telemetry values, truncated radio phrases that might have been misheard. This is the earliest possible intervention point. If the transcript is flagged here, the Overseer can signal the Planning Engine before reasoning begins, rather than catching the problem at delivery.

**Hook 2 — RAG Retrieval Audit (knowledge source monitoring)**  
As the RAG Vector DB returns retrieved chunks to the Planning Engine, a parallel audit signal goes to the Overseer. The Overseer receives: what was queried, what was returned, and the similarity/confidence scores for each chunk. It is checking for retrieval failures — cases where the returned chunks are plausible-sounding but from the wrong regulation section, where the similarity score is high but the content is tangentially related, or where retrieved chunks directly contradict each other. The Overseer does not block retrieval; it records what was retrieved. This record is what makes the pre-delivery cross-validation possible.

**Hook 3 — Pre-Delivery Check (final gate)**  
Before the Execution Module delivers any output to Sofia, it sends the complete generated narrative to the Overseer. The Overseer takes the narrative, identifies the citation it claims to be grounded in, retrieves that citation from its audit log (recorded in Hook 2), reads the cited source, and checks whether the narrative's key claim is actually supported by the citation. This is cross-validation — not confidence scoring. A high confidence score means the model is certain. Cross-validation checks whether the certain answer is consistent with what the cited document actually says. These are completely different tests.

### The intervention mechanism — retry with amended context

When the Overseer detects a problem at the pre-delivery check, it does not simply block the output and deliver silence. It sends a retry signal to the Planning Engine with two pieces of information:

1. **What failed:** The specific failure reason — citation mismatch, retrieved regulation from wrong year, claim not supported by cited document, etc.
2. **Amended context:** Corrected scope for re-querying the RAG store — narrowed regulation section, different historical strategy period, explicit exclusion of the conflicting chunk.

This is the critical distinction between a watchdog and an overseer. A watchdog says "wrong, try again." An Overseer says "wrong, here's specifically what was wrong, here's a corrected approach for the next attempt." The second attempt is genuinely better informed, not a coin-flip retry.

---

## The Retry Loop Budget

The latency constraint is a 2-second end-to-end target. The retry loop adds real cost. The budget:

| Step | Time estimate |
|---|---|
| First pass: inference + RAG retrieval | ~800ms + ~200ms = 1,000ms |
| Overseer pre-delivery check | ~150ms |
| Retry: inference with amended context + re-query | ~800ms + ~150ms = 950ms |
| Overseer re-check | ~150ms |
| **Total worst case (one retry)** | **~2,250ms** |

This slightly exceeds the 2-second target. The design decision is explicit: the 250ms overrun is acceptable given the alternative. The trust arithmetic strongly favors the additional latency. A 2.25-second response that is validated is preferable to a 1.8-second response that is confidently wrong.

**Hard cap:** Maximum 2 retries. If both retries fail the Overseer check, the system delivers an uncertainty response rather than continuing to retry indefinitely. This caps the maximum latency at approximately 3.4 seconds — still within a window that feels live during a race, where events unfold over 90-second laps.

---

## The Three Output States — Design Philosophy

The system has three possible outputs from the Execution Module, not one:

### Output 1 — Tactical Narrative + Audio Overlay (confirmed delivery)

Delivered when: Citation validated, confidence ≥ 0.7, Overseer approves.

This is the product's primary value delivery. Tactile narrative as text, simultaneously spoken as audio overlay so Sofia never has to look away from the TV. Includes a traceability link — visible evidence that the output is grounded in a specific source document. The traceability link is not decorative; it is a trust signal. It shows Sofia's work was done rigorously.

### Output 2 — Tactical Narrative + Audit Flag (retry-corrected delivery)

Delivered when: First pass failed, retry passed, Overseer approves on second check.

A small visible indicator that this answer went through a correction cycle. This is itself a trust signal. A system that shows it checked itself and corrected itself is more trustworthy than one that never acknowledges uncertainty. The audit flag is not a warning — it is transparency.

### Output 3 — Uncertainty Response (honest fallback)

Delivered when: Both retries failed, retry budget exhausted.

Partial, honest context rather than fluent fiction. The explicit design decision behind this output: *trust preserved over false confidence.* This output acknowledges the limit of what the system can confirm in this moment and provides whatever partial context it can validate. Sofia receives less than a full answer. She does not receive a wrong one. She remains engaged and trusting.

**The inference:** The design of Output 3 is the most important single decision in the governance architecture. Most AI systems have one output — the answer. This system has three, and the existence of Output 3 is what makes Outputs 1 and 2 trustworthy. If the system could not say "I don't know" when warranted, the times it does say "I know" would carry less weight.

---

## Audit Log — What It Records

Every decision the Overseer makes is recorded in the Audit Log with:

- Timestamp
- Input received (structured NLP output)
- RAG chunks retrieved (with similarity scores)
- Generated narrative (pre-delivery)
- Overseer decision (approve / retry / suppress)
- Failure reason (if retry or suppress)
- Amended context sent to Planning (if retry)
- Final output delivered to Sofia
- Output type (confirmed / retry-corrected / uncertainty)

This log serves two purposes: real-time governance (the Overseer uses it for cross-validation at Hook 3) and retrospective audit (the development team can review exactly what the system said, why it said it, and what the Overseer did about it). The retrospective audit capability is what IBM watsonx.governance specifically provides — explainability at the decision level, not just the model level.

---

## Governance in the Agent Roles Table

| Agent | Responsibility | Key Decision |
|---|---|---|
| NLP Synthesizer | Transcribes & translates pit radio + telemetry | Which signals trigger a push |
| Agentic Strategist | RAG-driven reasoning across FIA regs + history | Pull vs push; confidence threshold for output |
| Governance Overseer | Monitors pipeline integrity, enforces citation requirements, logs all decisions, triggers retries with amended context | Suppress vs pass; retry vs uncertainty response |
