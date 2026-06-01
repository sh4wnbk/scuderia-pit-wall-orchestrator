==================================================
PROJECT      Scuderia Pit-Wall Fan Orchestrator
STATE        Deadline day (2026-05-31). Demo mode + Diagnostics Modal
             redesign in static/index.html (local only, NOT committed).
             Demo video NOT yet recorded. BeMyApp NOT yet submitted.
LAST ACTION  Diagnostics Modal (gear icon) fully redesigned:
             — 6 cards, PERFT as guiding framework (not displayed labels)
             — Natural language throughout — no jargon, no acronyms shown
               to fans, no tool names without context
             — Card 1 (Policy): FIA 2026 rulebook grounding, IBM Docling
               named and explained in context
             — Card 2 (Explainability): Three safety checks, AI Review
               panel reference. Latency hidden until after first query,
               then fades in with real "Nms response time" value.
             — Card 3 (Robustness): Granite 4 safety net, honest fallback
             — Card 4 (Fairness): English + Italian, Miami/Milan framing
             — Card 5 (Transparency): All components named + ElevenLabs
               as tappable Ferrari-red hyperlink
             — Card 6 (Source): "Built in the open" statement + INSPECT
               SOURCE hardware stamp chip — red border, glow on hover,
               links to GitHub repo. In-flow (not absolute) to avoid
               phone frame clipping.
             — diag-stt / diag-tts IDs preserved in Card 4 natural language
             — CSS: .github-chip-wrapper, .github-chip, .diagnostic-card
               added to <style> block
NEXT         1. Verify Diagnostics Modal looks correct (reload localhost:8000,
                tap gear icon, check all 6 cards, INSPECT SOURCE stamp)
             2. Record demo video ≤3 min at http://localhost:8000
                Script in memory: project_demo_script.md
                Demo sequence (45s live demo):
                  — App loads → RACE SNAPSHOT
                  — Tap LEC EN card → CONFIRMED + audio + ambient cars
                  — Toggle IT → tap LEC IT card
                  — SYNC to HAM → tap HAM EN card
                  — Pull up AI REVIEW governance panel
                  — Optionally: tap gear icon to show Diagnostics Modal
             3. After recording: revert demo mode
                git checkout static/index.html
                rm static/pitwall_*.wav static/amb_pitwall_*.wav
             4. Commit any final README/asset changes
             5. Submit on BeMyApp:
                — GitHub: https://github.com/sh4wnbk/scuderia-pit-wall-orchestrator
                — Live app: https://tifosi-muretto.web.app
                — Demo video (upload)
                — Click Publish
NOTE         Demo mode LOCAL ONLY — never commit static/index.html or .wav files.
             ElevenLabs /ambient: 401 in Cloud Run (GCP IP block, free tier).
             Works locally. Not a code failure.
             Watson TTS quota resets June 1 — production voice back tomorrow.
             PERFT = Policy, Explainability, Robustness, Fairness, Transparency.
             It's the guiding framework for the Diagnostics Modal cards —
             not displayed as labels, just the design intent behind each card.
==================================================
