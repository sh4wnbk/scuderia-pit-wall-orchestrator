"""
Quantum Strategy Layer — Multi-Car QUBO Pit Window Optimizer

Multi-car formulation: models the joint pit decision for up to 5 cars
simultaneously. Variables: pit[car][lap] ∈ {0,1} for each car and each
candidate lap in the window. Up to 4 cars × 5 laps = 20 binary variables.

QUBO structure:
  Linear terms    — per-car tyre degradation cost vs fresh-tyre benefit
  Quadratic terms — cross-car coupling:
                    • Same lap:                          +8.0 double-stack penalty
                    • Rival pits 1 lap before primary:   +4.0 primary gets undercut
                    • Primary pits 1 lap before rival:   −2.0 primary undercuts rival
                    • Rival–rival adjacent laps:          +2.0 traffic interaction
  Penalty terms   — per-car exactly-one-stop constraint (λ=15 per car)

Solver: numpy vectorised brute-force enumeration over all 2^n bitstrings.
Exact for n ≤ 20 (2^20 = 1M evaluations, < 1s). No Qiskit runtime dependency
for the optimisation step — the QUBO is formulated and solved in pure numpy.
QAOA circuit execution is a future path when a Qiskit 2.x-compatible
qiskit-algorithms release is available; the QUBO formulation is unchanged.

Output feeds directly into Granite for plain-English explanation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import numpy as np

from models import LiveTelemetry


# ── Tyre degradation model ────────────────────────────────────────────────────
_DEGRADATION_RATE = {
    "SOFT":         0.12,   # fast cliff
    "MEDIUM":       0.07,
    "HARD":         0.04,   # slow burn
    "INTERMEDIATE": 0.09,
    "WET":          0.06,
}
_CLIFF_LAP = {
    "SOFT": 18, "MEDIUM": 28, "HARD": 42, "INTERMEDIATE": 22, "WET": 18,
}
_PIT_STOP_LOSS = 22.0   # seconds lost in the pit lane (stationary + in/out lap)
_MAX_VARS      = 20     # brute-force ceiling: 2^20 = 1M evaluations, < 1s


@dataclass
class QuantumStrategyResult:
    recommended_lap: int
    confidence: float               # energy gap clarity score (0–1); not a quantum probability
    candidate_laps: list[int]
    energy_landscape: dict[int, float]   # primary driver: lap → QUBO cost (lower = better)
    strategy_type: str              # "multi-car-one-stop" | "one-stop"
    explanation_context: str        # pre-built context string for Granite
    car_recommendations: list[dict] = field(default_factory=list)   # per-car results


def solve_pit_window(
    telemetry: LiveTelemetry,
    total_laps: int,
    window_size: int = 5,
    teammate_telem: Optional[LiveTelemetry] = None,
    rival_telems: Optional[list[LiveTelemetry]] = None,
    p: int = 2,
) -> Optional[QuantumStrategyResult]:
    """
    Main entry point. Optimises pit stop timing for up to 5 cars jointly.

    telemetry:     primary driver (car 0 — the recommendation surfaced to the fan)
    rival_telems:  up to 4 rivals by position proximity.
                   teammate_telem folded in as first rival when rival_telems is None.
    window_size:   candidate laps per car. Total variables = n_cars × n_laps ≤ 20.
    p:             reserved for future QAOA circuit depth parameter.
    """
    current_lap = telemetry.lap_number
    remaining   = max(1, total_laps - current_lap)

    # ── Build car list (primary first, then rivals) ───────────────────────────
    all_cars: list[LiveTelemetry] = [telemetry]
    if rival_telems:
        all_cars.extend(rival_telems[:4])
    elif teammate_telem:
        all_cars.append(teammate_telem)

    # Candidate laps: next window_size laps, capped at race end
    candidate_laps = list(range(
        current_lap + 1,
        min(current_lap + window_size + 1, total_laps - 2)
    ))
    if len(candidate_laps) < 2:
        return None

    n_laps = len(candidate_laps)

    # Trim n_cars so total variables stay within brute-force ceiling
    max_cars = _MAX_VARS // n_laps
    all_cars = all_cars[:max(1, max_cars)]
    n_cars   = len(all_cars)
    n        = n_cars * n_laps

    # ── Build QUBO coefficient dicts ──────────────────────────────────────────
    var_names: list[str] = [
        f"pit_c{c}_l{l}" for c in range(n_cars) for l in range(n_laps)
    ]

    linear:    dict[str, float]             = {}
    quadratic: dict[tuple[str, str], float] = {}

    # Linear terms — per-car projected tyre cost vs fresh-tyre benefit
    for c, car in enumerate(all_cars):
        compound = (car.tyre_compound or "HARD").upper()
        tyre_age = car.tyre_age_laps or 0
        car_lap  = car.lap_number or current_lap
        for l, lap in enumerate(candidate_laps):
            age_at_pit      = max(0, tyre_age + (lap - car_lap))
            laps_left_after = remaining - (lap - current_lap)
            degrad  = _tyre_cost(compound, age_at_pit, laps_left_after)
            benefit = _fresh_tyre_benefit(compound, laps_left_after)
            linear[f"pit_c{c}_l{l}"] = degrad - benefit

    # Cross-car quadratic coupling — double-stack, undercut/overcut, traffic
    for ca in range(n_cars):
        for cb in range(ca + 1, n_cars):
            for la, lap_a in enumerate(candidate_laps):
                for lb, lap_b in enumerate(candidate_laps):
                    key = (f"pit_c{ca}_l{la}", f"pit_c{cb}_l{lb}")
                    if lap_a == lap_b:
                        quadratic[key] = quadratic.get(key, 0.0) + 8.0
                    elif ca == 0 and lap_b == lap_a - 1:
                        quadratic[key] = quadratic.get(key, 0.0) + 4.0
                    elif ca == 0 and lap_a == lap_b - 1:
                        quadratic[key] = quadratic.get(key, 0.0) - 2.0
                    elif abs(lap_a - lap_b) == 1:
                        quadratic[key] = quadratic.get(key, 0.0) + 2.0

    # Per-car one-hot penalty: λ * (Σ_l pit_c_l − 1)² for each car
    lam = 15.0
    for c in range(n_cars):
        for l in range(n_laps):
            key = f"pit_c{c}_l{l}"
            linear[key] = linear.get(key, 0.0) + lam * (1 - 2)
        for l in range(n_laps):
            for l2 in range(l + 1, n_laps):
                key = (f"pit_c{c}_l{l}", f"pit_c{c}_l{l2}")
                quadratic[key] = quadratic.get(key, 0.0) + 2 * lam

    # ── Solve via numpy brute-force enumeration ───────────────────────────────
    try:
        x = _solve_qubo(linear, quadratic, var_names)
    except Exception as e:
        print(f"[Quantum] Solver failed: {e}")
        return _classical_fallback(all_cars, candidate_laps, current_lap, remaining)

    # ── Parse per-car results ─────────────────────────────────────────────────
    car_recommendations: list[dict] = []
    for c, car in enumerate(all_cars):
        car_slice = x[c * n_laps : (c + 1) * n_laps]
        chosen_l  = int(np.argmax(car_slice))
        car_recommendations.append({
            "driver":          car.driver_code,
            "recommended_lap": candidate_laps[chosen_l],
            "compound":        (car.tyre_compound or "HARD").upper(),
            "tyre_age":        car.tyre_age_laps or 0,
            "position":        car.position or 0,
        })

    recommended_lap = car_recommendations[0]["recommended_lap"]

    # Primary driver energy landscape — single-car cost (c=0, no cross-car terms)
    energy_landscape: dict[int, float] = {}
    idx = {name: i for i, name in enumerate(var_names)}
    lin = np.array([linear.get(v, 0.0) for v in var_names])
    Q   = np.zeros((n, n))
    for (a, b), coeff in quadratic.items():
        i, j = idx[a], idx[b]
        if i <= j:
            Q[i, j] += coeff
        else:
            Q[j, i] += coeff
    for l in range(n_laps):
        vec       = np.zeros(n)
        vec[l]    = 1.0   # pit_c0_l{l}
        energy_landscape[candidate_laps[l]] = float(vec @ lin + vec @ Q @ vec)

    # Strategy clarity — QUBO energy gap between best and next-best lap.
    sorted_energies = sorted(energy_landscape.values())
    if len(sorted_energies) >= 2 and sorted_energies[1] != sorted_energies[0]:
        gap        = abs(sorted_energies[1] - sorted_energies[0])
        confidence = min(0.97, 0.60 + gap / (abs(sorted_energies[0]) + 1e-6) * 0.3)
    else:
        confidence = 0.65

    context = _build_context(
        recommended_lap, confidence, candidate_laps,
        (telemetry.tyre_compound or "HARD").upper(),
        telemetry.tyre_age_laps or 0,
        current_lap, total_laps, energy_landscape,
        car_recommendations,
    )

    return QuantumStrategyResult(
        recommended_lap=recommended_lap,
        confidence=round(confidence, 3),
        candidate_laps=candidate_laps,
        energy_landscape=energy_landscape,
        strategy_type="multi-car-one-stop" if n_cars > 1 else "one-stop",
        explanation_context=context,
        car_recommendations=car_recommendations,
    )


# ── QUBO solver ───────────────────────────────────────────────────────────────

def _solve_qubo(
    linear: dict[str, float],
    quadratic: dict[tuple[str, str], float],
    var_names: list[str],
) -> np.ndarray:
    """
    Numpy vectorised brute-force QUBO solver. Exact for n ≤ 20.
    Enumerates all 2^n bitstrings, evaluates x·L + x·Q·x for each,
    returns the binary vector minimising the objective.
    """
    n   = len(var_names)
    idx = {name: i for i, name in enumerate(var_names)}

    lin = np.array([linear.get(v, 0.0) for v in var_names])
    Q   = np.zeros((n, n))
    for (a, b), coeff in quadratic.items():
        i, j = idx[a], idx[b]
        if i <= j:
            Q[i, j] += coeff
        else:
            Q[j, i] += coeff

    # Enumerate all 2^n bitstrings as rows of X
    all_bits = np.arange(1 << n, dtype=np.int64)
    X = ((all_bits[:, None] >> np.arange(n, dtype=np.int64)) & 1).astype(np.float64)

    costs = X @ lin + np.einsum('bi,ij,bj->b', X, Q, X)
    return X[int(np.argmin(costs))]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tyre_cost(compound: str, age_at_pit: int, laps_remaining: int) -> float:
    """Time lost to degradation if we stay out until age_at_pit laps."""
    cliff = _CLIFF_LAP.get(compound, 30)
    rate  = _DEGRADATION_RATE.get(compound, 0.07)
    laps_over_cliff = max(0, age_at_pit - cliff)
    return laps_over_cliff * rate * min(laps_remaining, age_at_pit)


def _fresh_tyre_benefit(compound: str, laps_on_fresh: int) -> float:
    """Time gained by running fresh tyres for laps_on_fresh laps."""
    rate = _DEGRADATION_RATE.get(compound, 0.07)
    return laps_on_fresh * rate * 0.4


def _classical_fallback(
    all_cars: list[LiveTelemetry],
    candidate_laps: list[int],
    current_lap: int,
    remaining: int,
) -> QuantumStrategyResult:
    """Greedy fallback when solver fails — picks lap minimising primary driver's degradation cost."""
    primary  = all_cars[0]
    compound = (primary.tyre_compound or "HARD").upper()
    tyre_age = primary.tyre_age_laps or 0
    costs    = {}
    for lap in candidate_laps:
        age = tyre_age + (lap - current_lap)
        costs[lap] = _tyre_cost(compound, age, remaining - (lap - current_lap))
    best = min(costs, key=costs.get)
    car_recs = [
        {"driver": car.driver_code, "recommended_lap": best,
         "compound": (car.tyre_compound or "HARD").upper(),
         "tyre_age": car.tyre_age_laps or 0, "position": car.position or 0}
        for car in all_cars
    ]
    return QuantumStrategyResult(
        recommended_lap=best,
        confidence=0.55,
        candidate_laps=candidate_laps,
        energy_landscape=costs,
        strategy_type="one-stop",
        explanation_context=f"Classical fallback: box lap {best} minimises tyre cost.",
        car_recommendations=car_recs,
    )


def _build_context(
    lap, confidence, candidates, compound, tyre_age,
    current_lap, total_laps, landscape, car_recommendations,
) -> str:
    best_alt    = min((l for l in landscape if l != lap), key=lambda l: landscape[l], default=None)
    n_cars      = len(car_recommendations)
    n_vars      = n_cars * len(candidates)
    car_summary = " | ".join(
        f"{r['driver']} lap {r['recommended_lap']}" for r in car_recommendations
    )
    return (
        f"QUBO optimizer evaluated {len(candidates)} candidate laps "
        f"({candidates[0]}–{candidates[-1]}) across {n_cars} car{'s' if n_cars > 1 else ''}. "
        f"Primary recommendation: lap {lap} (strategy clarity {confidence:.0%}). "
        f"Current compound: {compound}, age {tyre_age} laps, lap {current_lap}/{total_laps}. "
        f"Best alternative: lap {best_alt} "
        f"(QUBO cost {landscape.get(best_alt, 0):.2f} vs {landscape.get(lap, 0):.2f}). "
        f"Joint recommendations: {car_summary}. "
        f"QUBO: {n_vars} binary variables, exact numpy enumeration of all 2^{n_vars} states."
    )
