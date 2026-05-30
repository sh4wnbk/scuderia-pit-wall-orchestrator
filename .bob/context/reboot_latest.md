==================================================
PROJECT      Scuderia Pit-Wall Fan Orchestrator
STATE        Contextual prompt cards live + live timing infrastructure
             built. Deadline 2026-05-31. Demo video + BeMyApp submit next.
LAST ACTION  Two-task build shipped in commit 14c3501:
             Task 1 — Removed redundant center mic button; replaced with
             3 tappable prompt cards driven by FastF1 telemetry triggers
             (tyre age %, gap to car ahead, pace delta). Cards 0+1 stable,
             card 2 rotates every 20-30s from a pool. Tap → 900ms preview
             → auto-submit. Source indicator dot (green=live, amber=session).
             Center nav repurposed to refreshPrompts() (auto_awesome icon).
             VOICE nav button is now the sole voice entry point.
             Task 2 — LiveTimingCollector class in tools/fastf1_client.py:
             daemon thread, FastF1 SignalRClient subclass, deep-merge of
             TimingData + TimingAppData + DriverList. USE_LIVE_TIMING env
             flag in config.py (default false). FastF1Client.live_collector
             injection point. GET /timing/status endpoint.
NEXT         1. Verify deploy at tifosi-muretto.web.app (CI ~5 min)
             2. Record demo video ≤3 min:
                voice query → Granite reasoning → governance panel → audio
                Show prompt cards rotating. Show CONFIRMED badge.
             3. Submit on BeMyApp: GitHub URL + deployed URL + video → Publish
NOTE         USE_LIVE_TIMING=false is correct for demo — 2026 Miami historical
             data is real race data. README telemetry claim fixed (no longer
             claims 1.1M pts/sec). Orchestrate YAML removed from critical path
             (not a hackathon requirement). Deadline: 2026-05-31 11:59pm ET.
==================================================
