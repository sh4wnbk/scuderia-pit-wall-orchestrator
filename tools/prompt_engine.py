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


def _t(en: str, it: str, lang: str) -> str:
    return it if lang == "it" else en


def generate_prompts(
    session, driver_code: str, current_lap: Optional[int] = None, lang: str = "en"
) -> list[dict]:
    """
    Returns up to 6 {text, trigger} dicts ordered by priority.
    Falls back to regulation prompts when no session data is available.
    lang: "en" | "it" — governs prompt text only; trigger labels are always English.
    """
    try:
        try:
            driver_laps = session.laps.pick_drivers([driver_code])
        except AttributeError:
            driver_laps = session.laps[session.laps["Driver"] == driver_code]
    except Exception:
        return _fallback(lang)

    if driver_laps.empty:
        return _fallback(lang)

    driver_laps = driver_laps.sort_values("LapNumber")
    if current_lap:
        driver_laps = driver_laps[driver_laps["LapNumber"] <= current_lap]
        if driver_laps.empty:
            return _fallback(lang)
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
    prompts.extend(_race_control_events(session, lap_num, first, lang))

    # 2. Nearby pit stops
    prompts.extend(_nearby_pit_events(session, driver_code, position, lap_num, first, lang))

    # 3. Tyre cliff
    cliff   = COMPOUND_CLIFF.get(compound, 35)
    life    = COMPOUND_LIFE.get(compound, 40)
    age_pct = round((tyre_age / life) * 100) if life else 0
    if tyre_age >= cliff:
        prompts.append({
            "text": _t(
                f"{first}'s {compound}s are {tyre_age} laps in — is the cliff starting?",
                f"Le {compound} di {first} sono a {tyre_age} giri — il cliff è iniziato?",
                lang,
            ),
            "trigger": f"{L}TYRE AGE",
        })
    elif age_pct >= 65:
        prompts.append({
            "text": _t(
                f"{compound}s at {age_pct}% — what's the box window from here?",
                f"{compound} all'{age_pct}% — qual è la finestra box da adesso?",
                lang,
            ),
            "trigger": f"{L}TYRE AGE",
        })

    # 4. Pace trend
    pace_p = _pace_trend(window, first, L, lang)
    if pace_p:
        prompts.append(pace_p)

    # 5. Position trend
    pos_p = _position_trend(window, first, position, L, lang)
    if pos_p:
        prompts.append(pos_p)

    # 6. One-stop gamble (fill if short on prompts)
    if len(prompts) < 3 and (stint - 1) == 0 and lap_num > 20:
        prompts.append({
            "text": _t(
                f"Still no stop at lap {lap_num} — going for the one-stop?",
                f"Ancora nessun pit stop al giro {lap_num} — si punta alla sosta unica?",
                lang,
            ),
            "trigger": f"{L}NO STOP YET",
        })

    # 7. Fill to 3 with distinct strategy prompts so cards never duplicate
    existing = {p["text"] for p in prompts}
    _fills = [
        {
            "text": _t(
                f"P{position} — what moves are available over the next 5 laps?",
                f"P{position} — che mosse ha {first} nei prossimi 5 giri?",
                lang,
            ),
            "trigger": f"{L}P{position}" if position else None,
        } if position else None,
        {
            "text": _t(
                f"{first} on stint {stint} — any surprise strategy still on the table?",
                f"{first} allo stint {stint} — c'è ancora una strategia a sorpresa sul tavolo?",
                lang,
            ),
            "trigger": f"{L}STINT {stint}",
        } if stint else None,
        {
            "text": _t(
                f"{compound} management — can {first} hold position without a late stop?",
                f"Gestione {compound} — {first} può tenere la posizione senza una sosta tardiva?",
                lang,
            ),
            "trigger": f"{L}TYRE MGMT",
        } if compound else None,
        {
            "text": _t(
                f"What does the pitwall tell {first} at this stage of the race?",
                f"Cosa dice il pitwall a {first} in questa fase della gara?",
                lang,
            ),
            "trigger": f"{L}PIT WALL",
        },
    ]
    for fill in _fills:
        if len(prompts) >= 3:
            break
        if fill and fill["text"] not in existing:
            prompts.append(fill)
            existing.add(fill["text"])

    return prompts[:6]


# ── Detectors ─────────────────────────────────────────────────────────────────

def _race_control_events(session, current_lap: int, first: str, lang: str = "en") -> list[dict]:
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
                    "text": _t(
                        "VSC deployed — does a cheap stop compromise the strategy?",
                        "Virtual Safety Car in pista — uno stop economico compromette la strategia?",
                        lang,
                    ),
                    "trigger": f"LAP {m_lap} · VSC",
                })
            elif "SAFETY CAR DEPLOYED" in msg:
                prompts.append({
                    "text": _t(
                        "Safety car out — should Ferrari pit this lap?",
                        "Safety car in pista — Ferrari chiama ai box questo giro?",
                        lang,
                    ),
                    "trigger": f"LAP {m_lap} · SAFETY CAR",
                })
            elif "SAFETY CAR IN THIS LAP" in msg:
                prompts.append({
                    "text": _t(
                        "Safety car ending — is a late undercut still possible?",
                        "Safety car rientra — è ancora possibile un undercut tardivo?",
                        lang,
                    ),
                    "trigger": f"LAP {m_lap} · SC ENDING",
                })
            elif "DRS ENABLED" in msg:
                prompts.append({
                    "text": _t(
                        "DRS enabled — attack window opens now",
                        "DRS aperto — la finestra d'attacco si apre adesso",
                        lang,
                    ),
                    "trigger": f"LAP {m_lap} · DRS ENABLED",
                })
            elif "DRIVE THROUGH PENALTY" in msg and "SERVED" not in msg:
                prompts.append({
                    "text": _t(
                        f"Penalty issued — does this change the battle around {first}?",
                        f"Penalità comminata — cambia qualcosa nella battaglia intorno a {first}?",
                        lang,
                    ),
                    "trigger": f"LAP {m_lap} · PENALTY",
                })
    except Exception:
        pass
    return prompts


def _nearby_pit_events(
    session, driver_code: str, our_pos: int, current_lap: int, first: str, lang: str = "en"
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
                    "text": _t(
                        f"{drv} pitted from ahead — does {first} inherit the position or cover?",
                        f"{drv} rientra da davanti — {first} eredita la posizione o copre?",
                        lang,
                    ),
                    "trigger": f"LAP {p_lap} · {drv} PIT",
                })
            else:
                prompts.append({
                    "text": _t(
                        f"{drv} pitted from behind — undercut threat or gap building?",
                        f"{drv} rientra da dietro — minaccia undercut o gap in crescita?",
                        lang,
                    ),
                    "trigger": f"LAP {p_lap} · {drv} PIT",
                })
            if len(prompts) >= 2:
                break
    except Exception:
        pass
    return prompts


def _pace_trend(window: pd.DataFrame, first: str, L: str, lang: str = "en") -> Optional[dict]:
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
                "text": _t(
                    f"{first}'s lap times are dropping {slope:.1f}s/lap — managing or struggling?",
                    f"I tempi di {first} calano di {slope:.1f}s/giro — gestione o problema reale?",
                    lang,
                ),
                "trigger": f"{L}PACE TREND",
            }
        if slope < -0.25:
            return {
                "text": _t(
                    f"{first} improving {abs(slope):.1f}s/lap — what's driving the gain?",
                    f"{first} migliora di {abs(slope):.1f}s/giro — cosa sta guidando il recupero?",
                    lang,
                ),
                "trigger": f"{L}PACE TREND",
            }
    except Exception:
        pass
    return None


def _position_trend(
    window: pd.DataFrame, first: str, current_pos: int, L: str, lang: str = "en"
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
                "text": _t(
                    f"{first} gained {delta} places in {len(positions)} laps — is this pace sustainable?",
                    f"{first} ha guadagnato {delta} posizioni in {len(positions)} giri — il ritmo regge?",
                    lang,
                ),
                "trigger": f"{L}POSITIONS GAINED",
            }
        if delta <= -2:
            return {
                "text": _t(
                    f"{first} dropped {abs(delta)} places — tyre drop-off or traffic?",
                    f"{first} ha perso {abs(delta)} posizioni — degrado gomme o traffico?",
                    lang,
                ),
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


def _fallback(lang: str = "en") -> list[dict]:
    if lang == "it":
        return [
            {"text": "Ferrari sulle reg 2026 — qual è il vantaggio dell'MGU-K sui rettilinei?", "trigger": None},
            {"text": "Z-Mode vs X-Mode — quando cambia la Ferrari durante la gara?",             "trigger": None},
            {"text": "Reg gomme 2026 — quante mescole deve usare la Ferrari?",                  "trigger": None},
        ]
    return [
        {"text": "Ferrari on 2026 regs — what's the MGU-K advantage on straights?", "trigger": None},
        {"text": "Z-Mode vs X-Mode — when does Ferrari switch during the race?",     "trigger": None},
        {"text": "2026 tyre rules — how many compounds must Ferrari use?",            "trigger": None},
    ]
