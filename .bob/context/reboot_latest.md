==================================================
PROJECT      Scuderia Pit-Wall Fan Orchestrator
STATE        Demo mode wired in index.html (local only, NOT committed).
             Watson TTS quota exhausted — resets June 1. Deadline May 31.
             Judges won't review same day — TTS will be live when checked.
             Demo video not yet recorded. Submission not yet made.
LAST ACTION  Full demo mode implementation in static/index.html:
             — _DEMO_CARDS keyed by (driver:lang) — 4 entries:
               LEC:en, HAM:en, LEC:it, HAM:it
             — Each entry: card text, trigger label, voice .wav,
               ambient .wav, canned response text (exact transcription)
             — submitQuery() intercepts demo cards — skips Granite
               entirely, shows canned text after 820ms PROCESSING delay,
               output_type: 'confirmed', CONFIRMED badge + green hooks
             — setupAudioUrl({ wav, amb }) plays voice + ambient
               simultaneously; both stop together on voice end
             — fetchPrompts(true) in submitSync() — forces card reseed
               on driver switch so HAM demo card appears immediately
             — _getDemoCard() injects scripted card at index 0 in both
               fetchPrompts() and updateSpotter() paths
             — 8 .wav files in static/ (untracked, local only):
               pitwall_LEC/HAM/LEC_it/HAM_it.wav (voice)
               amb_pitwall_LEC/HAM/LEC_it/HAM_it.wav (ambient F1 cars)
             — Competition landscape reviewed: ~15 F1 strategy entries.
               Differentiators: voice in/out, bilingual EN/IT, governance
               panel as UI feature, Tifosi fan identity, FastF1 telemetry
               driving prompt cards.
NEXT         1. Hard refresh browser (Ctrl+Shift+R) at http://localhost:8000
             2. Test all 4 demo cards: LEC EN, HAM EN, toggle IT, LEC IT
             3. Record demo video ≤2 min:
                — App loads → RACE SNAPSHOT visible
                — Tap LEC EN card → PROCESSING → CONFIRMED + voice + cars
                — Toggle IT → tap LEC IT card
                — SYNC to HAM → tap HAM EN card
                — Pull up AI REVIEW governance panel
             4. After recording: revert demo mode
                git checkout static/index.html
                rm static/pitwall_*.wav static/amb_pitwall_*.wav
             5. Submit on BeMyApp: repo URL + tifosi-muretto.web.app + video
NOTE         Demo mode is LOCAL ONLY — never commit static/index.html
             changes or the .wav files. Revert immediately after recording.
             Watson TTS resets June 1 — production app will have audio again.
             ElevenLabs Sound Effects API noted as post-hackathon feature:
             generative ambient audio keyed to race context (free tier 10k
             credits/month).
             Spoken Race Engineer concept still reserved as IP.
==================================================
