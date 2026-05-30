from __future__ import annotations

import base64
import os
import random
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import config
from main import PitWallOrchestrator


class ProcessRequest(BaseModel):
    text_query: Optional[str] = Field(default=None, description="Fan text question")
    audio_b64: Optional[str] = Field(default=None, description="Base64 encoded wav bytes")
    telemetry_event: Optional[str] = Field(default=None, description="Telemetry event label")
    telemetry_data: Optional[dict] = Field(default=None, description="Telemetry payload")
    language: str = Field(default="en", description="Response language: 'en' or 'it'")
    voice: Optional[str] = Field(default=None, description="EN voice: allison | michael | george | emma | lisa")


class ProcessResponse(BaseModel):
    output_type: str
    text: str
    traceability_link: Optional[str]
    audit_flag: bool
    timestamp: str
    audio_b64: Optional[str]


class RaceContextRequest(BaseModel):
    year: int
    race: str
    driver: str


app = FastAPI(
    title="Scuderia Pit-Wall Orchestrator API",
    version="1.0.0",
    description="IBM Cloud deployable API wrapper for the Pit-Wall Fan Orchestrator",
)

orchestrator = PitWallOrchestrator()
_live_collector = None


@app.on_event("startup")
def configure_initial_race_context() -> None:
    global _live_collector
    year = int(os.getenv("RACE_YEAR", "2026"))
    race = os.getenv("RACE_NAME") or random.choice(list(_FASTF1_RACE_NAME_MAP.keys()))
    driver = os.getenv("RACE_DRIVER", "LEC")
    orchestrator.set_race_context(year=year, race=race, driver=driver)

    if config.use_live_timing:
        from tools.fastf1_client import LiveTimingCollector
        _live_collector = LiveTimingCollector()
        _live_collector.start(year=year, race=race)
        orchestrator._f1.live_collector = _live_collector


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def serve_ui():
    response = FileResponse("static/index.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


@app.get("/service-worker.js", include_in_schema=False)
def serve_sw():
    return FileResponse("static/service-worker.js", media_type="application/javascript")


@app.get("/health")
def healthcheck() -> dict:
    return {
        "status": "ok",
        "service": "pit-wall-orchestrator",
        "time": datetime.utcnow().isoformat(),
    }


@app.post("/race-context")
def set_race_context(payload: RaceContextRequest) -> dict:
    # Normalize race name — SYNC panel sends uppercase display text (e.g. "MIAMI")
    race = payload.race.strip().title()
    orchestrator.set_race_context(
        year=payload.year,
        race=race,
        driver=payload.driver,
    )
    return {
        "status": "updated",
        "year": payload.year,
        "race": race,
        "driver": payload.driver,
    }


@app.post("/process", response_model=ProcessResponse)
def process(payload: ProcessRequest) -> ProcessResponse:
    provided = [
        payload.text_query is not None,
        payload.audio_b64 is not None,
        payload.telemetry_event is not None,
    ]
    if sum(provided) != 1:
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one input type: text_query, audio_b64, or telemetry_event",
        )

    audio_bytes = None
    if payload.audio_b64 is not None:
        try:
            audio_bytes = base64.b64decode(payload.audio_b64)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid audio_b64 payload: {exc}")

    output = orchestrator.process(
        text_query=payload.text_query,
        audio_bytes=audio_bytes,
        telemetry_event=payload.telemetry_event,
        telemetry_data=payload.telemetry_data,
        language=payload.language,
        voice=payload.voice,
    )

    output_audio_b64 = (
        base64.b64encode(output.audio_bytes).decode("utf-8")
        if output.audio_bytes
        else None
    )

    return ProcessResponse(
        output_type=output.output_type,
        text=output.text,
        traceability_link=output.traceability_link,
        audit_flag=output.audit_flag,
        timestamp=output.timestamp.isoformat(),
        audio_b64=output_audio_b64,
    )


@app.get("/audit")
def audit_log() -> list[dict]:
    return orchestrator.get_audit_log()


@app.get("/timing/status")
def timing_status() -> dict:
    """
    Reports whether the live timing WebSocket is active or historical mode is in use.
    Live mode only connects during active F1 race weekends.
    """
    if not config.use_live_timing:
        return {
            "mode": "historical",
            "connected": False,
            "last_update": None,
            "drivers_tracked": [],
            "note": "Set USE_LIVE_TIMING=true to enable live mode",
        }
    if _live_collector is None:
        return {"mode": "live", "connected": False, "last_update": None, "drivers_tracked": []}
    return _live_collector.get_status()


# ── Schedule + Drivers ────────────────────────────────────────────────────────

@app.get("/schedule")
def get_schedule(year: int = 2026) -> dict:
    """Return the F1 race calendar for a given year, names normalised to app format."""
    if year in _schedule_cache:
        return _schedule_cache[year]
    try:
        import fastf1
        sched = fastf1.get_event_schedule(year, include_testing=False)
        races = []
        for _, ev in sched.iterrows():
            ff1_short = str(ev.get("EventName", "")).replace(" Grand Prix", "").strip()
            races.append(_FF1_TO_APP.get(ff1_short, ff1_short))
        result = {"year": year, "races": races}
    except Exception as e:
        result = {"year": year, "races": [], "error": str(e)}
    _schedule_cache[year] = result
    return result


@app.get("/drivers")
def get_drivers(year: int = 2026) -> dict:
    """Return the driver roster for a given year. Curated for 2023–2026, FastF1 fallback otherwise."""
    if year in _drivers_cache:
        return _drivers_cache[year]
    if year in _DRIVERS_BY_YEAR:
        result = {"year": year, "drivers": _DRIVERS_BY_YEAR[year]}
        _drivers_cache[year] = result
        return result
    # FastF1 fallback — load first available race session to read results
    try:
        import fastf1
        sched = fastf1.get_event_schedule(year, include_testing=False)
        drivers: list[dict] = []
        for _, ev in sched.iterrows():
            try:
                s = fastf1.get_session(year, str(ev.get("EventName", "")), "R")
                s.load(telemetry=False, weather=False, messages=False)
                if not s.results.empty:
                    drivers = [
                        {"name": str(r["Abbreviation"]), "code": str(r["Abbreviation"]),
                         "team": str(r.get("TeamName", ""))}
                        for _, r in s.results.iterrows()
                        if str(r.get("Abbreviation", ""))
                    ]
                    break
            except Exception:
                continue
        result = {"year": year, "drivers": drivers}
    except Exception as e:
        result = {"year": year, "drivers": [], "error": str(e)}
    _drivers_cache[year] = result
    return result


# ── Telemetry ─────────────────────────────────────────────────────────────────

def _fmt_interval(val, sign: str = "+") -> Optional[str]:
    """Convert a FastF1 gap value (timedelta or NaT) to '+1.2s' / '-0.8s'."""
    try:
        import pandas as pd
        if pd.isna(val):
            return None
        secs = val.total_seconds() if hasattr(val, "total_seconds") else float(str(val).strip().lstrip("+"))
        return f"{sign}{abs(secs):.1f}s"
    except Exception:
        return None


_telemetry_cache: dict[str, tuple[datetime, dict]] = {}
_TELEMETRY_TTL_SECONDS = 60
_SESSION_PRIORITY = ["R", "Q", "FP3", "FP2", "FP1"]

# UI race names → FastF1 event names (FastF1 uses its own naming convention)
_FASTF1_RACE_NAME_MAP: dict[str, str] = {
    "Imola":         "Emilia Romagna",
    "Great Britain": "British",
    "United States": "United States",
    "Las Vegas":     "Las Vegas",
    "Saudi Arabia":  "Saudi Arabian",
    "Abu Dhabi":     "Abu Dhabi",
    "Bahrain":       "Bahrain",
    "Australia":     "Australian",
    "Japan":         "Japanese",
    "China":         "Chinese",
    "Miami":         "Miami",
    "Monaco":        "Monaco",
    "Spain":         "Spanish",
    "Canada":        "Canadian",
    "Austria":       "Austrian",
    "Belgium":       "Belgian",
    "Hungary":       "Hungarian",
    "Netherlands":   "Dutch",
    "Italy":         "Italian",
    "Azerbaijan":    "Azerbaijan",
    "Singapore":     "Singapore",
    "Mexico":        "Mexico City",
    "Brazil":        "São Paulo",
    "Qatar":         "Qatar",
}

# Reverse map: FastF1 short name → app name (for schedule parsing)
_FF1_TO_APP: dict[str, str] = {v: k for k, v in _FASTF1_RACE_NAME_MAP.items()}

# Ferrari driver roster by year — instant lookup for demo years
_DRIVERS_BY_YEAR: dict[int, list[dict]] = {
    2026: [{"name": "LECLERC", "code": "LEC", "team": "Ferrari"},
           {"name": "HAMILTON", "code": "HAM", "team": "Ferrari"}],
    2025: [{"name": "LECLERC", "code": "LEC", "team": "Ferrari"},
           {"name": "SAINZ",   "code": "SAI", "team": "Ferrari"}],
    2024: [{"name": "LECLERC", "code": "LEC", "team": "Ferrari"},
           {"name": "HAMILTON", "code": "HAM", "team": "Mercedes"},
           {"name": "SAINZ",   "code": "SAI", "team": "Ferrari"}],
    2023: [{"name": "LECLERC", "code": "LEC", "team": "Ferrari"},
           {"name": "SAINZ",   "code": "SAI", "team": "Ferrari"}],
}

_schedule_cache: dict[int, dict] = {}
_drivers_cache:  dict[int, dict] = {}


@app.get("/telemetry")
def get_telemetry() -> dict:
    """
    Fetch driver telemetry from FastF1 for the current race context.
    Tries Race → Qualifying → Practice sessions in order.
    Cached for 60 seconds to avoid redundant session loads.
    """
    strat = orchestrator._strat_agent
    year, race, driver = strat._race_year, strat._race_name, strat._driver

    cache_key = f"{year}:{race}:{driver}"
    now = datetime.utcnow()

    if cache_key in _telemetry_cache:
        cached_at, cached_data = _telemetry_cache[cache_key]
        if (now - cached_at) < timedelta(seconds=_TELEMETRY_TTL_SECONDS):
            return cached_data

    f1_race = _FASTF1_RACE_NAME_MAP.get(race, race)

    telemetry = None
    session_type_used = None
    for st in _SESSION_PRIORITY:
        t = orchestrator._f1.get_driver_telemetry(year, f1_race, st, driver)
        if t is not None:
            telemetry = t
            session_type_used = st
            break

    if telemetry is None:
        return {
            "available": False,
            "driver": driver,
            "race": race,
            "year": year,
            "message": "No session data available yet",
        }

    result = {
        "available": True,
        "driver_code": telemetry.driver_code,
        "driver_name": telemetry.driver_name,
        "session_type": session_type_used,
        "lap_number": telemetry.lap_number,
        "tyre_compound": telemetry.tyre_compound,
        "tyre_age_laps": telemetry.tyre_age_laps,
        "position": telemetry.position,
        "gap_to_leader": telemetry.gap_to_leader,
        "interval_to_ahead": telemetry.interval_to_ahead,
        "pit_stops": telemetry.pit_stops,
        "pace_delta_seconds": telemetry.pace_delta_seconds,
        "lap_time": telemetry.lap_time_str,
        "sector_1": telemetry.sector_1,
        "sector_2": telemetry.sector_2,
        "sector_3": telemetry.sector_3,
        "session_name": telemetry.session_name,
        "race_year": telemetry.race_year,
        "fetched_at": now.isoformat(),
    }

    # Rivals — P-1 ahead and P+1 behind, from FastF1 disk cache (no network call)
    rivals: dict = {}
    try:
        import fastf1 as _ff1
        rv_session = _ff1.get_session(year, f1_race, session_type_used)
        rv_session.load(telemetry=False, weather=False, messages=False)
        all_laps = rv_session.laps
        latest_per = (
            all_laps.sort_values("LapNumber")
            .groupby("Driver", sort=False)
            .last()
            .reset_index()
        )
        our_pos = telemetry.position or 0
        if our_pos > 0:
            our_row    = latest_per[latest_per["Driver"] == driver]
            our_t      = our_row.iloc[0].get("Time") if not our_row.empty else None
            our_lap_n  = our_row.iloc[0].get("LapNumber") if not our_row.empty else None
            # Filter to same-lap only — retired drivers keep their last recorded position,
            # which collides with finishers at the same position number.
            same_lap   = latest_per[latest_per["LapNumber"] == our_lap_n] if our_lap_n is not None else latest_per
            ahead_row  = same_lap[same_lap["Position"] == our_pos - 1]
            behind_row = same_lap[same_lap["Position"] == our_pos + 1]
            if not ahead_row.empty and our_pos > 1:
                a = ahead_row.iloc[0]
                gap = _fmt_interval(a.get("Time") - our_t if our_t is not None else None, "+")
                rivals["ahead"] = {
                    "driver": str(a["Driver"]),
                    "gap": gap or "N/A",
                    "tyre": str(a.get("Compound", "N/A")).upper(),
                }
            if not behind_row.empty:
                b = behind_row.iloc[0]
                gap = _fmt_interval(b.get("Time") - our_t if our_t is not None else None, "-")
                rivals["behind"] = {
                    "driver": str(b["Driver"]),
                    "gap": gap or "N/A",
                }
    except Exception:
        pass
    result["rivals"] = rivals

    _telemetry_cache[cache_key] = (now, result)
    return result


# ── Prompts ───────────────────────────────────────────────────────────────────

_prompts_cache: dict[str, tuple[datetime, dict]] = {}
_PROMPTS_TTL_SECONDS = 30


@app.get("/prompts")
def get_prompts(current_lap: Optional[int] = None, lang: str = "en") -> dict:
    """
    Generate contextual race intel prompts from multi-lap analysis.
    Analyzes pace trends, tyre age, race control events, and nearby pit stops
    over a 10-lap window. Cached for 30 seconds per (lap, lang) pair.
    ?current_lap=N  — anchor window for replay
    ?lang=it        — return Italian prompt text (trigger labels always English)
    """
    import fastf1
    from tools.prompt_engine import generate_prompts

    if current_lap is not None and current_lap <= 0:
        current_lap = None
    lang = lang if lang in ("en", "it") else "en"

    strat = orchestrator._strat_agent
    year, race, driver = strat._race_year, strat._race_name, strat._driver

    cache_key = f"{year}:{race}:{driver}:{current_lap or 'latest'}:{lang}:prompts"
    now = datetime.utcnow()

    if cache_key in _prompts_cache:
        cached_at, cached_data = _prompts_cache[cache_key]
        if (now - cached_at) < timedelta(seconds=_PROMPTS_TTL_SECONDS):
            return cached_data

    f1_race = _FASTF1_RACE_NAME_MAP.get(race, race)

    session = None
    for st in _SESSION_PRIORITY:
        try:
            s = fastf1.get_session(year, f1_race, st)
            s.load(telemetry=False, weather=False, messages=True)
            if not s.laps.empty:
                session = s
                break
        except Exception:
            continue

    if session is None:
        return {"available": False, "prompts": [], "source": "none", "driver": driver}

    prompts = generate_prompts(session, driver, current_lap=current_lap, lang=lang)

    result = {
        "available": True,
        "prompts":   prompts,
        "source":    "historical",
        "driver":    driver,
        "race":      race,
        "year":      year,
    }
    _prompts_cache[cache_key] = (now, result)
    return result
