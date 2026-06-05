# Scuderia Pit-Wall

![Scuderia Pit-Wall Fan Orchestrator](assets/Pit-Wall_Fan_Orchestrator.png)

A voice-first AI companion for Formula 1 fans. Ask a question mid-race, get a cited, governed response in plain English — spoken back in your language while you keep your eyes on the screen.

**Live:** [tifosi-muretto.web.app](https://tifosi-muretto.web.app)

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
- **Ambient audio** — Watson Orchestrate crafts a contextual F1 soundscape prompt; ElevenLabs Sound Generation renders it as race atmosphere audio
- **Quantum strategy layer** — a multi-car QUBO optimizer formulates pit stop timing as a binary optimization problem and recommends the optimal box lap with confidence

---

## Architecture

```
① Perception      NLP Synthesizer · Watson STT (EN + IT)
② Knowledge       RAG — 777 chunks · FIA 2026 Regs + Strategy History
③ Reasoning       Planning Engine → Regulation Agent | Agentic Strategist
④ Telemetry       FastF1 lap-summary data · LiveTimingCollector (USE_LIVE_TIMING)
⑤ Quantum         Multi-car QUBO pit optimizer · numpy exact solver · HAMILTONIAN
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

![HAMILTONIAN — multi-car QUBO pit window optimizer](assets/quantum_gates1.png)

### HAMILTONIAN — Quantum Strategy Layer

The pit stop timing problem is a multi-car QUBO (Quadratic Unconstrained Binary Optimization):

- **Variables** — `pit[car][i] ∈ {0,1}` for each car and each candidate lap — up to 4 cars × 5 laps = 20 binary variables (brute-force ceiling: 2²⁰ ≈ 1M evaluations, < 1s)
- **Objective** — minimise joint projected race time across all cars, accounting for per-car tyre degradation and pit stop time loss
- **Quadratic terms** — cross-car coupling: double-stack penalty (same lap), undercut/overcut interactions (adjacent laps, asymmetric for primary driver), rival–rival traffic
- **Penalty constraint** — exactly one pit stop per car in the evaluation window (one constraint per car, λ=15)

A numpy vectorised brute-force solver enumerates all 2ⁿ bitstrings and returns the ground state — the minimum-energy assignment of the QUBO. This is exact for n ≤ 20 and runs in under a second, with no Qiskit runtime dependency (an earlier Qiskit `MinimumEigenOptimizer` path caused out-of-memory crashes on Cloud Run). The QUBO formulation and Hamiltonian encoding are unchanged; a QAOA circuit implementation is a future path pending a Qiskit 2.x-compatible `qiskit-algorithms` release. The primary driver's recommendation surfaces to the fan; all car recommendations are returned in the API response. Granite explains the result in plain English.

```
FastF1 telemetry (up to 5 cars) → multi-car QUBO (≤20 variables) → numpy exact enumeration → joint pit recommendations + energy landscape → Granite explanation
```

Access via the `|ψ⟩` center button in the app (HAMILTONIAN screen).

*The HAMILTONIAN screen reflects the project's continued evolution beyond the original hackathon submission.*

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
| Quantum | numpy exact QUBO solver (Qiskit 2.4 retained for future QAOA circuit path) |
| Asset storage | chroma_db + fastf1_cache bundled in image via `COPY . .` (Dropbox = optional startup fallback) |
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
| `GET` | `/quantum/strategy` | Multi-car QUBO pit window optimization |
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

`chroma_db/` and `fastf1_cache/` are git-tracked (~23 MB) and bundled into the Docker image via `COPY . .`, so cold starts are deterministic with no runtime network dependency. `scripts/download_assets.py` runs at startup as an optional Dropbox fallback (`scripts/upload_assets.py` pushes the zips) — it no-ops when the assets are already present.

To pre-bundle a new race for instant cold-start response:

```python
import fastf1
fastf1.Cache.enable_cache('./fastf1_cache')
fastf1.get_session(2024, 'Monaco', 'R').load(telemetry=False, weather=False, messages=True)
```

Then commit the pkl files and push to `main`.

**Pre-bundled races (immediate response):** 2026 — Australian · Miami · Canada · Belgian · Azerbaijan · United States · São Paulo · Abu Dhabi. 2024 — Monza · Azerbaijan · Bahrain. 2022 — Bahrain.

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
