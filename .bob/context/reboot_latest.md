==================================================
PROJECT      Scuderia Pit-Wall Fan Orchestrator
STATE        RACE SNAPSHOT live + year-aware SYNC + all session bugs fixed.
             Deadline 2026-05-31. Demo video + BeMyApp submit remaining.
LAST ACTION  Session-long bug-fix + feature sprint (10 commits to main):
             — RACE SNAPSHOT: renamed LAST LAP → two-column widget.
               Left: tyre compound+age+bar, lap time, pace delta (▲▼ 0.1s).
               Right: ▲ AHEAD (driver, gap, tyre) + ▼ BEHIND (driver, gap).
             — /telemetry returns rivals{ahead,behind} from FastF1 Time-col
               diff (IntervalToPositionAhead absent in FastF1 v3.8).
               Miami: VER +0.3s ahead, HAM -9.5s behind.
             — /prompts?current_lap=N anchors lap window for replay.
               current_lap ≤ 0 normalized to None. Cache key includes lap.
             — SYNC bug fixed: fetches telemetry+prompts immediately on
               confirm (was waiting up to 60s on stale poll timer).
             — Year-aware roster: GET /schedule?year=N (FastF1 calendar),
               GET /drivers?year=N (curated 2023–2026 + FastF1 fallback).
               2024 → HAM=Mercedes; 2025 → SAI; 2026 → LEC+HAM Ferrari.
               2026 schedule no longer pre-seeded — fetches from FastF1
               (22 races actual 2026 calendar, not old 24-race hardcoded).
             — SYNC case bug fixed: selectRace() stored uppercase display
               text ("MIAMI") → FastF1 lookup failed silently (available:
               false for every race after first SYNC). Fixed: backend
               .strip().title() normalization + frontend syncRaceName var.
             — Duplicate card fix: prompt engine pads to 3 distinct prompts
               with fill templates (position moves, stint strategy, tyre
               mgmt, pitwall Q) — cards never triple/double on thin pools.
             — Random startup race: RACE_NAME env var overrides; if unset,
               random.choice(_FASTF1_RACE_NAME_MAP). Cloud Run pins
               RACE_NAME=Miami via workflow (already in deploy-cloudrun.yml).
NEXT         1. Verify tifosi-muretto.web.app after CI (~5 min from 233e2d6):
                — RACE SNAPSHOT shows rivals with real gap values (+0.3s etc)
                — SYNC China · Hamilton → 3 distinct cards, no duplicates
                — Year −1 to 2024 → HAM shows as Mercedes in driver sheet
             2. Record demo video ≤3 min:
                voice/card tap → PROCESSING → CONFIRMED + audio → governance
                Show RACE SNAPSHOT with rivals. Show SYNC year change.
             3. Submit on BeMyApp: GitHub URL + tifosi-muretto.web.app + video
NOTE         FastF1 v3.8 laps DataFrame has no GapToLeader or
             IntervalToPositionAhead — rivals gaps use Time-col diff instead.
             pace_delta_seconds outlier guard: Math.abs(d) > 10 → "--".
             USE_LIVE_TIMING=false correct for demo (historical data).
             Deadline: 2026-05-31 11:59pm ET.
==================================================
