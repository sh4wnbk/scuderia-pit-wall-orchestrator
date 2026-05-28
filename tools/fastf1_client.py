"""
Tools Layer — FastF1 Live Telemetry Client

Responsibilities:
  - Fetch current lap telemetry, tyre state, sector times, position
  - Called by the Agentic Strategist AFTER RAG retrieval
  - This sequencing is intentional: knowledge context established first,
    live data interpreted within that context

FastF1 is a Python library, not a native REST API.
For IBM Orchestrate deployment, wrap this in a thin FastAPI endpoint
on IBM Cloud Code Engine and expose as an Orchestrate skill.
See the comment at the bottom of this file for the wrapper pattern.

MVP: uses historical session data to simulate live race telemetry.
Production: point to the live timing feed when available.
"""

import os
from dataclasses import dataclass
from typing import Optional

import fastf1
import pandas as pd

from config import config
from models import LiveTelemetry


class FastF1Client:

    def __init__(self):
        os.makedirs(config.fastf1_cache_path, exist_ok=True)
        fastf1.Cache.enable_cache(config.fastf1_cache_path)

    def get_driver_telemetry(
        self,
        year: int,
        race: str,
        session_type: str,
        driver_code: str,
    ) -> Optional[LiveTelemetry]:
        """
        Fetch the most recent lap data for a driver.
        Returns None if the session or driver is not found.

        year: e.g. 2024
        race: e.g. "Bahrain" or "Monaco"
        session_type: "R" (Race), "Q" (Qualifying), "FP1" etc.
        driver_code: "LEC", "HAM", "VER" etc.
        """
        try:
            session = fastf1.get_session(year, race, session_type)
            session.load(telemetry=False, weather=False, messages=False)

            driver_laps = session.laps.pick_driver(driver_code)
            if driver_laps.empty:
                return None

            latest = driver_laps.iloc[-1]
            return self._to_model(latest, driver_laps, session, driver_code)

        except Exception as e:
            print(f"[FastF1Client] Failed to fetch telemetry: {e}")
            return None

    def get_race_snapshot(
        self,
        year: int,
        race: str,
        drivers: list[str],
    ) -> dict[str, Optional[LiveTelemetry]]:
        """
        Fetch latest lap data for multiple drivers simultaneously.
        Used by the Agentic Strategist to assess the competitive picture.
        """
        try:
            session = fastf1.get_session(year, race, "R")
            session.load(telemetry=False, weather=False, messages=False)
            return {
                drv: self._fetch_from_loaded(session, drv)
                for drv in drivers
            }
        except Exception as e:
            print(f"[FastF1Client] Race snapshot failed: {e}")
            return {drv: None for drv in drivers}

    # ── Private ──────────────────────────────────────────────────────────────

    def _fetch_from_loaded(
        self, session, driver_code: str
    ) -> Optional[LiveTelemetry]:
        try:
            laps = session.laps.pick_driver(driver_code)
            if laps.empty:
                return None
            return self._to_model(laps.iloc[-1], laps, session, driver_code)
        except Exception:
            return None

    def _pace_delta(self, laps, latest_lap) -> Optional[float]:
        """Last lap time minus average of prior 3 laps, in seconds. Positive = slower."""
        try:
            timed = laps[laps["LapTime"].notna()]
            idx = timed.index.get_loc(latest_lap.name)
            if idx < 1:
                return None
            last = latest_lap["LapTime"].total_seconds()
            prior = timed.iloc[max(0, idx - 3):idx]["LapTime"].apply(
                lambda t: t.total_seconds()
            )
            if prior.empty:
                return None
            return round(last - prior.mean(), 3)
        except Exception:
            return None

    def _to_model(self, lap, driver_laps, session, driver_code: str) -> LiveTelemetry:
        def safe_str(val, default="N/A") -> str:
            try:
                return str(val) if pd.notna(val) else default
            except Exception:
                return default

        def safe_int(val, default=0) -> int:
            try:
                return int(val) if pd.notna(val) else default
            except Exception:
                return default

        try:
            row = session.results[session.results["Abbreviation"] == driver_code]
            driver_name = row["FullName"].iloc[0] if not row.empty else driver_code
        except Exception:
            driver_name = driver_code

        stint = safe_int(lap.get("Stint"), default=1)

        return LiveTelemetry(
            driver_code=driver_code,
            driver_name=driver_name,
            lap_number=safe_int(lap.get("LapNumber")),
            lap_time_str=safe_str(lap.get("LapTime")),
            tyre_compound=safe_str(lap.get("Compound")),
            tyre_age_laps=safe_int(lap.get("TyreLife")),
            position=safe_int(lap.get("Position")),
            gap_to_leader=safe_str(lap.get("GapToLeader")),
            interval_to_ahead=safe_str(lap.get("IntervalToPositionAhead")),
            pit_stops=max(0, stint - 1),
            pace_delta_seconds=self._pace_delta(driver_laps, lap),
            sector_1=safe_str(lap.get("Sector1Time")),
            sector_2=safe_str(lap.get("Sector2Time")),
            sector_3=safe_str(lap.get("Sector3Time")),
            session_name=session.event["EventName"],
            race_year=session.event["EventDate"].year,
        )


# ── IBM Orchestrate Skill Wrapper (deploy on Cloud Code Engine) ──────────────
#
# from fastapi import FastAPI
# from pydantic import BaseModel
#
# app = FastAPI()
# client = FastF1Client()
#
# class TelemetryRequest(BaseModel):
#     year: int
#     race: str
#     session_type: str = "R"
#     driver_code: str
#
# @app.post("/telemetry")
# def get_telemetry(req: TelemetryRequest):
#     result = client.get_driver_telemetry(
#         req.year, req.race, req.session_type, req.driver_code
#     )
#     if result is None:
#         return {"error": "Driver or session not found"}
#     return result.__dict__
#
# Run: uvicorn tools.fastf1_skill:app --host 0.0.0.0 --port 8080
# Then register the /telemetry endpoint as an Orchestrate skill.
# ─────────────────────────────────────────────────────────────────────────────
