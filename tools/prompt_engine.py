"""
Prompt Engine — multi-lap race intel for contextual card queue.

Reads the last 10 laps for the tracked driver plus the full session
event stream to generate event-driven and trend-driven prompts.

Priority order:
  1. Race control events (VSC, SC, DRS, penalties)
  2. Nearby pit stops (cars within 5 positions)
  3. Tyre age crossing compound cliff threshold
  4. Pace trend (degrading >0.3s/lap or improving)
  5. Position changes over the window
  6. One-stop gamble (no stop, deep into race)
  7. Position context fallback
"""

from __future__ import annotations

import pandas as pd
from typing import Optional

COMPOUND_CLIFF = {"SOFT": 20, "MEDIUM": 30, "HARD": 40, "INTERMEDIATE": 25, "WET": 20}
COMPOUND_LIFE  = {"SOFT": 25, "MEDIUM": 35, "HARD": 50, "INTERMEDIATE": 40, "WET": 40}
LAP_WINDOW = 10


def generate_prompts(session, driver_code: str) -> list[dict]:
    """
    Returns up to 6 {text, trigger} dicts ordered by priority.
    Falls back to regulation prompts when no session data is available.
    """
    try:
        try:
            driver_laps = session.laps.pick_drivers([driver_code])
        except AttributeError:
            driver_laps = session.laps[session.laps["Driver"] == driver_code]
    except Exception:
        return _fallback()

    if driver_laps.empty:
        return _fallback()

    driver_laps = driver_laps.sort_values("LapNumber")
    latest  = driver_laps.iloc[-1]
    window  = driver_laps.tail(LAP_WINDOW)

    name     = _driver_name(session, driver_code)
    first    = name.split()[-1]
    compound = str(latest.get("Compound") or "HARD").upper()
    tyre_age = int(latest.get("TyreLife") or 0)
    position = int(latest.get("Position") or 0)
    lap_num  = int(latest.get("LapNumber") or 0)
    stint    = int(latest.get("Stint") or 1)
    L        = f"LAP {lap_num} · " if lap_num else ""

    prompts: list[dict] = []

    # 1. Race control events
    prompts.extend(_race_control_events(session, lap_num, first))

    # 2. Nearby pit stops
    prompts.extend(_nearby_pit_events(session, driver_code, position, lap_num, first))

    # 3. Tyre cliff
    cliff   = COMPOUND_CLIFF.get(compound, 35)
    life    = COMPOUND_LIFE.get(compound, 40)
    age_pct = round((tyre_age / life) * 100) if life else 0
    if tyre_age >= cliff:
        prompts.append({
            "text":    f"{first}'s {compound}s are {tyre_age} laps in — is the cliff starting?",
            "trigger": f"{L}TYRE AGE",
        })
    elif age_pct >= 65:
        prompts.append({
            "text":    f"{compound}s at {age_pct}% — what's the box window from here?",
            "trigger": f"{L}TYRE AGE",
        })

    # 4. Pace trend
    pace_p = _pace_trend(window, first, L)
    if pace_p:
        prompts.append(pace_p)

    # 5. Position trend
    pos_p = _position_trend(window, first, position, L)
    if pos_p:
        prompts.append(pos_p)

    # 6. One-stop gamble (fill if short on prompts)
    if len(prompts) < 3 and (stint - 1) == 0 and lap_num > 20:
        prompts.append({
            "text":    f"Still no stop at lap {lap_num} — going for the one-stop?",
            "trigger": f"{L}NO STOP YET",
        })

    # 7. Position fallback
    if not prompts:
        prompts.append({
            "text":    f"P{position} — what moves are available over the next 5 laps?",
            "trigger": f"{L}P{position}" if position else None,
        })

    return prompts[:6]


# ── Detectors ─────────────────────────────────────────────────────────────────

def _race_control_events(session, current_lap: int, first: str) -> list[dict]:
    prompts: list[dict] = []
    try:
        rc = getattr(session, "race_control_messages", None)
        if rc is None or rc.empty:
            return []
        nearby = rc[rc["Lap"].between(max(1, current_lap - 3), current_lap + 3)]
        seen: set[str] = set()
        for _, row in nearby.iterrows():
            msg   = str(row.get("Message", "")).upper()
            m_lap = int(row.get("Lap", current_lap))
            key   = msg[:40]
            if key in seen:
                continue
            seen.add(key)

            if "VIRTUAL SAFETY CAR" in msg:
                prompts.append({
                    "text":    "VSC deployed — does a cheap stop compromise the strategy?",
                    "trigger": f"LAP {m_lap} · VSC",
                })
            elif "SAFETY CAR DEPLOYED" in msg:
                prompts.append({
                    "text":    "Safety car out — should Ferrari pit this lap?",
                    "trigger": f"LAP {m_lap} · SAFETY CAR",
                })
            elif "SAFETY CAR IN THIS LAP" in msg:
                prompts.append({
                    "text":    "Safety car ending — is a late undercut still possible?",
                    "trigger": f"LAP {m_lap} · SC ENDING",
                })
            elif "DRS ENABLED" in msg:
                prompts.append({
                    "text":    "DRS enabled — attack window opens now",
                    "trigger": f"LAP {m_lap} · DRS ENABLED",
                })
            elif "DRIVE THROUGH PENALTY" in msg and "SERVED" not in msg:
                prompts.append({
                    "text":    f"Penalty issued — does this change the battle around {first}?",
                    "trigger": f"LAP {m_lap} · PENALTY",
                })
    except Exception:
        pass
    return prompts


def _nearby_pit_events(
    session, driver_code: str, our_pos: int, current_lap: int, first: str
) -> list[dict]:
    prompts: list[dict] = []
    try:
        all_laps = session.laps
        window_laps = all_laps[
            all_laps["LapNumber"].between(max(1, current_lap - 2), current_lap)
        ]
        pitted = window_laps[
            window_laps["PitInTime"].notna() & (window_laps["Driver"] != driver_code)
        ]
        if our_pos > 0:
            pitted = pitted[pitted["Position"].between(max(1, our_pos - 5), our_pos + 5)]

        seen_drivers: set[str] = set()
        for _, p in pitted.iterrows():
            drv   = str(p.get("Driver", ""))
            if drv in seen_drivers:
                continue
            seen_drivers.add(drv)
            p_pos = int(p.get("Position") or 0)
            p_lap = int(p.get("LapNumber") or current_lap)
            ahead = bool(our_pos and p_pos and p_pos < our_pos)
            if ahead:
                prompts.append({
                    "text":    f"{drv} pitted from ahead — does {first} inherit the position or cover?",
                    "trigger": f"LAP {p_lap} · {drv} PIT",
                })
            else:
                prompts.append({
                    "text":    f"{drv} pitted from behind — undercut threat or gap building?",
                    "trigger": f"LAP {p_lap} · {drv} PIT",
                })
            if len(prompts) >= 2:
                break
    except Exception:
        pass
    return prompts


def _pace_trend(window: pd.DataFrame, first: str, L: str) -> Optional[dict]:
    try:
        timed = window[window["LapTime"].notna()]
        if len(timed) < 4:
            return None
        times = [t.total_seconds() for t in timed["LapTime"] if hasattr(t, "total_seconds")]
        if len(times) < 4:
            return None
        early = sum(times[:3]) / 3
        late  = sum(times[-3:]) / 3
        slope = (late - early) / max(1, len(times) - 1)
        if slope > 0.3:
            return {
                "text":    f"{first}'s lap times are dropping {slope:.1f}s/lap — managing or struggling?",
                "trigger": f"{L}PACE TREND",
            }
        if slope < -0.25:
            return {
                "text":    f"{first} improving {abs(slope):.1f}s/lap — what's driving the gain?",
                "trigger": f"{L}PACE TREND",
            }
    except Exception:
        pass
    return None


def _position_trend(
    window: pd.DataFrame, first: str, current_pos: int, L: str
) -> Optional[dict]:
    try:
        positions = window["Position"].dropna()
        if len(positions) < 5:
            return None
        first_pos = int(positions.iloc[0])
        last_pos  = int(positions.iloc[-1])
        delta     = first_pos - last_pos  # positive = gained places
        if delta >= 2:
            return {
                "text":    f"{first} gained {delta} places in {len(positions)} laps — is this pace sustainable?",
                "trigger": f"{L}POSITIONS GAINED",
            }
        if delta <= -2:
            return {
                "text":    f"{first} dropped {abs(delta)} places — tyre drop-off or traffic?",
                "trigger": f"{L}POSITIONS LOST",
            }
    except Exception:
        pass
    return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _driver_name(session, driver_code: str) -> str:
    try:
        row = session.results[session.results["Abbreviation"] == driver_code]
        return str(row["FullName"].iloc[0]) if not row.empty else driver_code
    except Exception:
        return driver_code


def _fallback() -> list[dict]:
    return [
        {"text": "Ferrari on 2026 regs — what's the MGU-K advantage on straights?", "trigger": None},
        {"text": "Z-Mode vs X-Mode — when does Ferrari switch during the race?",     "trigger": None},
        {"text": "2026 tyre rules — how many compounds must Ferrari use?",            "trigger": None},
    ]
