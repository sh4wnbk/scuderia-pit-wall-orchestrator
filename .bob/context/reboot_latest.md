==================================================
PROJECT      Scuderia Pit-Wall Fan Orchestrator
STATE        Race Intel card queue + /prompts endpoint shipped. UI shows
             3 rotating cards with trigger labels (LAP N · EVENT TYPE).
             Queue shifts every 30s: new card enters bottom, top exits.
             Deadline 2026-05-31. Demo video + BeMyApp submit remaining.
LAST ACTION  Multi-session UI + backend build:
             — Spotter Agent → 3-card queue fed by server /prompts endpoint
             — /prompts (GET): reads last 10 laps + race_control_messages
               for the tracked driver. Priority: RC events → nearby pits →
               tyre cliff → pace trend → position trend → one-stop gamble.
             — tools/prompt_engine.py (new): generate_prompts(session, driver)
             — Real Miami 2026 events wired: LAP 6 SC, LAP 11 SC ending,
               LAP 21 RUS pit, LAP 27 HAM pit, pace trend, tyre cliff
             — messages=True in FastF1 session.load(); disk-cached after 1st load
             — Queue rotation: _shiftQueue() all-cards-nudge-up animation,
               30s fixed timer, holds if no new event available
             — Trigger label per card: "LAP 36 · TYRE AGE" in 9px JetBrains Mono
             — Telemetry grid moved to top; RACE INTEL zone below
             — Yellow equalizer waveform restored
             — Pace delta capped at ±10s (in-lap outlier guard)
             — Card text = punchy reactive phrase, submitted directly to Granite
NEXT         1. Verify /prompts at tifosi-muretto.web.app (CI ~5 min from 3cc64f4)
             2. Verify queue rotation and trigger labels render correctly
             3. Update CLAUDE.md with prompts endpoint state
             4. Record demo video ≤3 min:
                voice/card tap → PROCESSING → CONFIRMED + audio → governance panel
             5. Submit on BeMyApp: GitHub URL + tifosi-muretto.web.app + video → Publish
NOTE         Open question: current_lap is hardcoded to session end (latest lap).
             For historical replay to feel live, /prompts should accept
             ?lap=N so LAP 6 SC surfaces at the right moment, not at race end.
             — USE_LIVE_TIMING=false is correct for demo (Miami 2026 historical)
             — signal_type NOT in /prompts response schema (text + trigger only)
             — Deadline: 2026-05-31 11:59pm ET
==================================================
