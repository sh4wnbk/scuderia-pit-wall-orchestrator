# Scuderia Pit-Wall

![Scuderia Pit-Wall Fan Orchestrator](assets/Pit-Wall_Fan_Orchestrator.png)

A voice-first AI companion for Formula 1 fans. Ask a question mid-race, get a cited, governed response in plain English — spoken back in your language while you keep your eyes on the screen.

**Live:** [tifosi-muretto.web.app](https://tifosi-muretto.web.app)

> **Quantum strategy layer — QAOA optimizer (Qiskit Aer) formulates pit stop timing as a QUBO problem and recommends the optimal box lap with confidence** *(post-submission)*
> The quantum layer (HAMILTONIAN) reflects the project's continued evolution beyond the original submission.

---

## The Problem

![The Synthesis Gap](assets/synthesis_gap.png)

When Leclerc's engineer says *"Charles, X-Mode hold. Override zero. Harvest phase active. Two laps to window"* — 396 million Ferrari fans hear words they cannot decode.

Three information channels exist: TV broadcast (visuals, no context), live timing app (raw data, no explanation), social media (delayed, unverified). Fans are forced to abandon the broadcast and act as their own data engineers. They miss the race while looking for answers.

This is the **Synthesis Gap**.

---

## What It Does

- **Voice input** — speak a question, Watson STT transcribes it in English or Italian
- **RAG reasoning** — IBM Granite 4 cross-references your query against 777 chunks of FIA 2026 regulations and strategy history
- **Proactive governance** — every response is validated against its citation before delivery; confident-wrong answers are suppressed, not delivered
- **Voice output** — Watson TTS speaks the response while you watch the race
- **Contextual prompt cards** — three telemetry-driven questions update every 30 seconds based on the current lap situation
- **Quantum strategy layer** — QAOA optimizer (Qiskit Aer) formulates pit stop timing as a QUBO problem and recommends the optimal box lap with confidence

---

## Architecture

```
① Perception      NLP Synthesizer · Watson STT (EN + IT)
② Knowledge       RAG — 777 chunks · FIA 2026 Regs + Strategy History
③ Reasoning       Planning Engine → Regulation Agent | Agentic Strategist
④ Telemetry       FastF1 lap-summary data · LiveTimingCollector (USE_LIVE_TIMING)
⑤ Quantum         QAOA pit window optimizer · Qiskit Aer · HAMILTONIAN
⑥ Governance      Proactive Overseer · 3-hook audit · retry loop
⑦ Execution       Execution Module · Watson TTS · three-output delivery
```

### Governance — Why It Exists

![Governance Loop](assets/governance_loop.png)

A confident wrong answer is more damaging than acknowledged uncertainty. A fan who receives *"I cannot confirm this right now"* stays engaged. A fan who gets a wrong answer, feels something about it, shares it, and later discovers the truth — loses trust permanently.

The Overseer intercepts every output at three points before delivery:

| Hook | Trigger | Checks |
|---|---|---|
| 1 | After transcription | Confidence threshold, anomaly flag |
| 2 | After RAG retrieval | Similarity scores, citation chain |
| 3 | Pre-delivery | Narrative vs cited source (Granite cross-validation) |

**Three possible outputs. No others.**

| Output | Condition |
|---|---|
| `confirmed` | Citation validated, Overseer approved |
| `retry_corrected` | First pass failed, retry with amended context passed |
| `uncertainty` | Retry budget exhausted — honest partial answer |

![HAMILTONIAN — QAOA pit window optimizer](assets/quantum_gates1.png)

### HAMILTONIAN — Quantum Strategy Layer

The pit stop timing problem is a QUBO (Quadratic Unconstrained Binary Optimization):

- **Variables** — `pit[i] ∈ {0,1}` for each candidate lap in the window
- **Objective** — minimize projected race time accounting for tyre degradation and pit stop time loss
- **Quadratic terms** — teammate interaction penalties (double-stack cost), traffic coupling
- **Penalty constraint** — exactly one pit stop in the evaluation window

QAOA (Quantum Approximate Optimization Algorithm) solves this on the Qiskit Aer statevector simulator (p=2 layers, COBYLA optimizer). The ground state — minimum energy — is the optimal pit lap. Granite explains the result in plain English.

```
FastF1 telemetry → QUBO formulation → QAOA → recommended lap + energy landscape → Granite explanation
```

Access via the `⚗` center button in the app (HAMILTONIAN screen).

---

## Technology Stack

| Layer | Technology |
|---|---|
| LLM / Reasoning | IBM Granite 4 (`ibm/granite-4-h-small`) via watsonx.ai |
| Speech-to-Text | IBM Watson STT — EN-US + IT-IT Broadband models |
| Text-to-Speech | IBM Watson TTS — Allison / Michael / George / Emma (EN), Francesca (IT) |
| Ambient audio | ElevenLabs Sound Generation + Watson Orchestrate |
| Vector store | ChromaDB — 777 chunks, FIA 2026 Regs + Strategy History (Docling-indexed) |
| Telemetry | FastF1 3.8 — lap-summary data; live timing via SignalR WebSocket (flag-gated) |
| Quantum | Qiskit 2.4 + Qiskit Aer + QAOA optimizer |
| Asset storage | Dropbox API — chroma_db + fastf1_cache pulled at container startup |
| API | FastAPI — Cloud Run `us-central1` |
| Frontend | Vanilla JS PWA — Firebase Hosting |
| CI/CD | GitHub Actions → GCP Artifact Registry → Cloud Run (Workload Identity Federation) |
| Coding | IBM Bob IDE |

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | PWA shell |
| `POST` | `/process` | Main pipeline — text, audio, or telemetry event input |
| `GET` | `/telemetry` | FastF1 lap data for current race context (60s cache) |
| `GET` | `/prompts` | Contextual prompt cards (30s cache, bilingual) |
| `GET` | `/quantum/strategy` | QAOA pit window optimization |
| `GET` | `/timing/status` | Live vs historical timing mode |
| `POST` | `/race-context` | Set year / race / driver |
| `GET` | `/schedule` | Race calendar by year |
| `GET` | `/drivers` | Driver roster by year |
| `POST` | `/ambient` | ElevenLabs ambient race audio via Watson Orchestrate |
| `GET` | `/audit` | Full watsonx.governance audit log |
| `GET` | `/health` | Liveness check |

---

## Setup

**Requirements:** Python 3.12+, [uv](https://astral.sh/uv)

```bash
git clone https://github.com/sh4wnbk/scuderia-pit-wall-orchestrator.git
cd scuderia-pit-wall-orchestrator
uv venv .ibm_scuderia
source .ibm_scuderia/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```
WATSONX_API_KEY=
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=
WATSON_STT_API_KEY=
WATSON_STT_URL=
WATSON_TTS_API_KEY=
WATSON_TTS_URL=
ELEVENLABS_API_KEY=
ORCHESTRATE_API_KEY=
DROPBOX_TOKEN=
```

Run locally:

```bash
uvicorn app:app --host 0.0.0.0 --port 8080
```

---

## Deployment

Push to `main` → GitHub Actions builds and deploys to Cloud Run (~5 min).

```
push → GCP Artifact Registry → Cloud Run (us-central1) → tifosi-muretto.web.app
```

`chroma_db/` and `fastf1_cache/` are stored in Dropbox and pulled at container startup by `scripts/download_assets.py`. The Docker image contains no bundled data — assets are always fresh from the source of truth.

To pre-bundle a new race for instant cold-start response:

```python
import fastf1
fastf1.Cache.enable_cache('./fastf1_cache')
fastf1.get_session(2024, 'Monaco', 'R').load(telemetry=False, weather=False, messages=True)
```

Then commit the pkl files, run `python scripts/upload_assets.py` to push to Dropbox, and push to `main`.

**Pre-bundled races (immediate response):** Miami 2026 · Canada 2026 · Australian 2026 · Monza 2024 · Azerbaijan 2024 · Bahrain 2022/2024

---

## What's Next

- **Landscape visualization** — energy landscape bar chart in landscape mode (Chart.js)
- **Push notifications** — pit stop alerts, safety car, position changes via Web Push
- **Silence detection** — auto-submit voice query after 1.5s of silence
- **Live timing** — `USE_LIVE_TIMING=true` during race weekends activates the SignalR collector
- **Multi-team** — extend beyond Ferrari to any driver on the grid
- **Hamiltonian** — deeper quantum layer post-Qiskit Global Summer School 2026

---

## License

MIT. Formula 1 and related trademarks are the property of their respective owners. Telemetry data sourced from FastF1 for educational and non-commercial purposes.
