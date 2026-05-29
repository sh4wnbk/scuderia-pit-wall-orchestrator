"""
Tools Layer — FastF1 Telemetry Client

Two operating modes, selected by config.use_live_timing:

  False (default): loads completed session data from FastF1 cache.
      get_race_snapshot() reads historical lap DataFrames.

  True: LiveTimingCollector opens a FastF1 SignalR WebSocket to the
      F1 live timing feed in a daemon thread. State is accumulated
      in memory as incremental messages arrive. Falls back to historical
      if no active session is connected.

The LiveTelemetry model is identical in both modes — only the source
changes. Consumers (AgenticStrategist, /telemetry endpoint) are unaware
of which mode is active.
"""

import os
import re
import threading
import tempfile
from collections import defaultdict, deque
from datetime import datetime
from typing import Optional

import fastf1
import pandas as pd

from config import config
from models import LiveTelemetry


# ── Helpers ───────────────────────────────────────────────────────────────────

def _deep_merge(base: dict, update: dict) -> None:
    """In-place deep merge of update into base. Dicts recurse; scalars overwrite."""
    for key, val in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        else:
            base[key] = val


def _parse_laptime_seconds(s: str) -> Optional[float]:
    """Convert 'M:SS.mmm' or bare float string to seconds. Returns None on failure."""
    try:
        m = re.match(r"(\d+):(\d+\.\d+)", str(s))
        if m:
            return int(m.group(1)) * 60 + float(m.group(2))
        return float(s)
    except Exception:
        return None


# ── Live Timing Collector ─────────────────────────────────────────────────────

class LiveTimingCollector:
    """
    Background collector for the FastF1 SignalR live timing WebSocket.
    Maintains per-driver timing state as incremental messages arrive.
    Call start() once at app startup; stop() on shutdown.

    Only meaningful during active F1 race weekends. Outside those windows
    _connected stays False and get_telemetry() returns None, causing
    FastF1Client to fall back to historical data.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._timing: dict[str, dict] = {}           # driver number → TimingData state
        self._tyre: dict[str, dict] = {}             # driver number → TimingAppData state
        self._tla_map: dict[str, str] = {}           # TLA (LEC) → driver number (16)
        self._names: dict[str, str] = {}             # driver number → full name
        self._lap_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=5))
        self._session_name: str = "Live Session"
        self._race_year: int = datetime.utcnow().year
        self._connected: bool = False
        self._last_update: Optional[datetime] = None
        self._thread: Optional[threading.Thread] = None
        self._client = None

    # ── Public ────────────────────────────────────────────────────────────────

    def start(self, year: int, race: str) -> None:
        """Start the live timing daemon thread. Safe to call multiple times."""
        self._race_year = year
        self._session_name = f"{race} Grand Prix"
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="live-timing"
        )
        self._thread.start()
        print(f"[LiveTiming] Collector started for {year} {race}")

    def stop(self) -> None:
        if self._client:
            try:
                self._client.stop()
            except Exception:
                pass
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def get_status(self) -> dict:
        return {
            "mode": "live",
            "connected": self._connected,
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "drivers_tracked": sorted(self._tla_map.keys()),
        }

    def get_telemetry(self, driver_code: str) -> Optional[LiveTelemetry]:
        """Build LiveTelemetry from accumulated state. Returns None if no data yet."""
        with self._lock:
            number = self._tla_map.get(driver_code.upper())
            if not number:
                return None
            t = self._timing.get(number, {})
            ty = self._tyre.get(number, {})
            if not t:
                return None
            return self._build_model(number, driver_code, t, ty)

    # ── Background thread ─────────────────────────────────────────────────────

    def _run(self) -> None:
        try:
            from fastf1.livetiming.client import SignalRClient
        except ImportError:
            print("[LiveTiming] fastf1.livetiming not available — staying in historical mode")
            return

        collector = self

        class _InMemoryClient(SignalRClient):
            """Subclass that routes messages to in-memory handler alongside file write."""
            def __init__(self):
                self._tmp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".livetiming", mode="w"
                )
                super().__init__(filename=self._tmp.name)

            def _on_message(self, msg_type, data, timestamp):
                super()._on_message(msg_type, data, timestamp)
                try:
                    collector._handle_message(msg_type, data, timestamp)
                except Exception:
                    pass

        self._client = _InMemoryClient()
        try:
            self._connected = True
            self._client.start()
        except Exception as e:
            print(f"[LiveTiming] Connection ended: {e}")
        finally:
            self._connected = False

    # ── Message handlers ──────────────────────────────────────────────────────

    def _handle_message(self, msg_type: str, data, timestamp: str) -> None:
        with self._lock:
            self._last_update = datetime.utcnow()
            if msg_type == "DriverList":
                self._process_driver_list(data)
            elif msg_type == "TimingData":
                self._process_timing(data)
            elif msg_type == "TimingAppData":
                self._process_tyre(data)
            elif msg_type == "SessionInfo":
                self._process_session(data)

    def _process_driver_list(self, data: dict) -> None:
        for number, info in data.items():
            if not isinstance(info, dict):
                continue
            tla = info.get("Tla") or info.get("Abbreviation", "")
            full = info.get("FullName", "")
            if tla:
                self._tla_map[tla.upper()] = str(number)
                self._names[str(number)] = full.title() if full else tla.upper()

    def _process_timing(self, data: dict) -> None:
        lines = data.get("Lines") if isinstance(data, dict) else None
        if not lines:
            return
        for number, update in lines.items():
            if not isinstance(update, dict):
                continue
            number = str(number)
            if number not in self._timing:
                self._timing[number] = {}
            _deep_merge(self._timing[number], update)
            lap_t = self._timing[number].get("LastLapTime", {})
            val = lap_t.get("Value") if isinstance(lap_t, dict) else None
            if val and val != "":
                self._lap_history[number].append(val)

    def _process_tyre(self, data: dict) -> None:
        lines = data.get("Lines") if isinstance(data, dict) else None
        if not lines:
            return
        for number, update in lines.items():
            if not isinstance(update, dict):
                continue
            number = str(number)
            if number not in self._tyre:
                self._tyre[number] = {}
            _deep_merge(self._tyre[number], update)

    def _process_session(self, data: dict) -> None:
        if not isinstance(data, dict):
            return
        meeting = data.get("Meeting", {})
        if isinstance(meeting, dict):
            name = meeting.get("Name")
            if name:
                self._session_name = name
        start = data.get("StartDate", "")
        if isinstance(start, str) and len(start) >= 4 and start[:4].isdigit():
            self._race_year = int(start[:4])

    # ── Model builder ─────────────────────────────────────────────────────────

    def _build_model(
        self, number: str, driver_code: str, t: dict, ty: dict
    ) -> LiveTelemetry:
        def safe_str(val, default="N/A") -> str:
            return str(val) if val not in (None, "", {}) else default

        def safe_int(val, default=0) -> int:
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        # Position and lap number
        position = safe_int(t.get("Position"), 0)
        lap_number = safe_int(t.get("NumberOfLaps"), 0)

        # Lap time
        lap_t = t.get("LastLapTime", {})
        lap_time_str = (
            lap_t.get("Value", "N/A") if isinstance(lap_t, dict) else safe_str(lap_t)
        )

        # Sector times
        sectors = t.get("Sectors", {})
        def _sector(n: int) -> str:
            if not isinstance(sectors, dict):
                return "N/A"
            s = sectors.get(str(n), {})
            return s.get("Value", "N/A") if isinstance(s, dict) else "N/A"

        # Gaps
        gap_raw = t.get("GapToLeader", "N/A")
        gap = gap_raw if isinstance(gap_raw, str) else safe_str(gap_raw)
        int_raw = t.get("IntervalToPositionAhead", {})
        interval = (
            int_raw.get("Value", "N/A") if isinstance(int_raw, dict) else safe_str(int_raw)
        )

        # Tyre and pit stops from stint data
        compound, tyre_age, pit_stops = "UNKNOWN", 0, 0
        stints = ty.get("Stints", {}) or {}
        stint_list = list(stints.values()) if isinstance(stints, dict) else (
            stints if isinstance(stints, list) else []
        )
        if stint_list:
            last = stint_list[-1]
            if isinstance(last, dict):
                compound = last.get("Compound", "UNKNOWN")
                tyre_age = safe_int(last.get("TotalLaps"), 0)
            pit_stops = max(0, len(stint_list) - 1)

        return LiveTelemetry(
            driver_code=driver_code,
            driver_name=self._names.get(number, driver_code),
            lap_number=lap_number,
            lap_time_str=lap_time_str,
            tyre_compound=compound,
            tyre_age_laps=tyre_age,
            position=position,
            gap_to_leader=gap,
            interval_to_ahead=interval,
            pit_stops=pit_stops,
            pace_delta_seconds=self._pace_delta(number),
            sector_1=_sector(0),
            sector_2=_sector(1),
            sector_3=_sector(2),
            session_name=self._session_name,
            race_year=self._race_year,
        )

    def _pace_delta(self, number: str) -> Optional[float]:
        """Last lap minus mean of prior laps (seconds). Positive = slower."""
        history = self._lap_history.get(number)
        if not history or len(history) < 2:
            return None
        times = [_parse_laptime_seconds(lt) for lt in history]
        times = [t for t in times if t is not None]
        if len(times) < 2:
            return None
        return round(times[-1] - sum(times[:-1]) / len(times[:-1]), 3)


# ── FastF1 Historical Client ──────────────────────────────────────────────────

class FastF1Client:
    """
    Fetches driver telemetry from FastF1.

    When config.use_live_timing is True and a LiveTimingCollector with an
    active connection is injected via self.live_collector, live data takes
    priority. Falls back to historical session data in all other cases.
    """

    def __init__(self):
        os.makedirs(config.fastf1_cache_path, exist_ok=True)
        fastf1.Cache.enable_cache(config.fastf1_cache_path)
        self.live_collector: Optional[LiveTimingCollector] = None

    def get_driver_telemetry(
        self,
        year: int,
        race: str,
        session_type: str,
        driver_code: str,
    ) -> Optional[LiveTelemetry]:
        """
        Fetch the most recent lap data for a driver.
        Live mode is tried first when configured; historical is the fallback.
        """
        if (
            config.use_live_timing
            and self.live_collector
            and self.live_collector.is_connected()
        ):
            t = self.live_collector.get_telemetry(driver_code)
            if t is not None:
                return t

        # Historical path
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
        """
        if (
            config.use_live_timing
            and self.live_collector
            and self.live_collector.is_connected()
        ):
            result = {drv: self.live_collector.get_telemetry(drv) for drv in drivers}
            if any(v is not None for v in result.values()):
                return result

        # Historical path
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

    # ── Private ───────────────────────────────────────────────────────────────

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
