==================================================
PROJECT      Scuderia Pit-Wall Fan Orchestrator
STATE        Post-submission. Stable + deployed. 2026-06-05 session:
             WSL disk maintenance + venv slimming COMPLETE.
LAST ACTION  Disk/venv maintenance (all done, do NOT redo):
             — WSL ext4.vhdx COMPACTED via diskpart (wsl --shutdown →
               attach readonly → compact vdisk → detach → exit). Windows-side
               space reclaimed. This already happened — the lean venv is proof.
             — venv .ibm_scuderia REBUILT CPU-only: Python 3.11.15, 762M
               (was 5.4G). torch + entire CUDA/nvidia/triton stack removed —
               none load at runtime; embeddings use onnxruntime (ChromaDB
               DefaultEmbeddingFunction). qiskit stack retained.
             — requirements.txt regenerated to match lean venv: 134 pins
               (was 144). Removed nvidia-*/cuda-*/triton/torch + stale ML deps
               (transformers, sentence-transformers, sklearn). Added qiskit
               stack that was installed but unlisted. Committed 99094ee, pushed.
             — CI/CD: GitHub Actions run 27031799772 SUCCESS (~4m20s).
               Cloud Run deployed. /health returns 200 (verified 18:15Z).
             — NOTE: .ibm_scuderia is the VENV, not a second repo. It is
               gitignored (.gitignore:1), never pushed. Left in place (not
               deleted) — rebuild with: uv venv .ibm_scuderia &&
               VIRTUAL_ENV=.ibm_scuderia uv pip install -r requirements.txt
OUTAGE FIX  2026-06-05: prod /telemetry, /prompts, /quantum returned available:false.
             ROOT CAUSE: commit b504181 added chroma_db/ + fastf1_cache/ to
             .dockerignore (Dropbox offload); the Dropbox fallback failed, leaving
             the image with empty RAG + cache. FIXED by reverting the .dockerignore
             exclusion so COPY . . bundles the tracked assets (~23MB) again.
             Image installs requirements.runtime.txt (16 pins), NOT requirements.txt.
             Needs commit + push to redeploy. See memory/project_asset_pipeline.md.
NEXT         1. Reactivate watsonx WML instance 36ddbdd0-8d42-4acf-85b0-d1bf6bd22523
                on IBM Cloud dashboard — fixes /process 500 on production (separate
                from the asset outage above)
             2. Post-judging: migrate Granite → Claude API
                (planning_engine, regulation_agent, agentic_strategist, overseer)
             3. ibm_mundial June challenge — open new Claude Code instance
                from /home/shawn/src/ibm_mundial, write CLAUDE.md, first commit
NOTE         Hackathon submitted 2026-05-31. Judges reviewing.
             Latest commit: 99094ee (slim requirements.txt). Prev: a69cf2c.
             Cross-instance caution: a cold instance re-derives state and may
             wrongly conclude the diskpart/venv work was never done. It WAS.
             Zone.Identifier sidecar files (WSL) — never commit.
             ibm_mundial: no commits yet, venv at .ibm_mundial, StatsBomb open
             data (2022 WC Final match_id=3869685 as demo).
==================================================
