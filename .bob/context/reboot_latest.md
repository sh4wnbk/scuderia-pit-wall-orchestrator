==================================================
PROJECT      Scuderia Pit-Wall Fan Orchestrator
STATE        Telemetry dashboard expanded, all nav/UI bugs fixed,
             deadline in 4 days (2026-05-31), clean git tree
LAST ACTION  Added interval-to-ahead, pit stops, pace trend delta to
             LiveTelemetry model + FastF1 client + /telemetry API +
             frontend. Wear bar now green→yellow→red gradient.
             Also: DATA→AUDIT rename, FastF1 race name mapping (all 24
             races), active nav tab indicator, FRANCESCA IT voice display
NEXT         Record demo video (≤3 min) and submit on BeMyApp:
             repo URL + tifosi-muretto.web.app + video → Publish
NOTE         FastF1 returns available:false for races not yet in cache.
             Miami 2026 works (Race session confirmed). Imola fails
             because FastF1 event name is "Emilia Romagna" — mapping
             is now in app.py _FASTF1_RACE_NAME_MAP. SYNC back to
             Miami to restore telemetry during demo.
==================================================
