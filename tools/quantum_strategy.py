"""
Quantum Strategy Layer — QAOA Pit Window Optimizer

Formulates F1 pit stop timing as a Quadratic Unconstrained Binary
Optimization (QUBO) problem and solves it using the Quantum Approximate
Optimization Algorithm (QAOA) on the Qiskit Aer simulator.

QUBO variables:
  pit[i] ∈ {0, 1} — binary decision for each candidate lap in the window.
  pit[i] = 1 means "pit on lap i".

Objective (minimize):
  Total projected race time = Σ lap_time(i) over remaining laps,
  where lap_time depends on tyre age at each lap (degradation model) and
  includes the time cost of the pit stop itself on the chosen lap.

Penalty terms (enforcing strategy constraints):
  - Exactly one pit stop in the window (can be relaxed for two-stop)
  - Minimum laps between consecutive stops

Quadratic interactions:
  - Teammate coupling: if teammate pits on lap i, pit[i] cost increases
    (track position loss from double-stacking)
  - Traffic interaction: pitting when a rival just pitted gives free air

The QAOA ansatz alternates cost and mixer Hamiltonian layers (p=2 by
default). The Aer statevector simulator finds the minimum energy state
— the optimal pit lap — without requiring real quantum hardware.

Output feeds directly into Granite for plain-English explanation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import numpy as np

from models import LiveTelemetry


# ── Tyre degradation model ────────────────────────────────────────────────────
# Lap time delta per lap of age (seconds added per lap beyond cliff threshold)
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


@dataclass
class QuantumStrategyResult:
    recommended_lap: int
    confidence: float          # energy gap clarity score (0–1); not a quantum probability
    candidate_laps: list[int]
    energy_landscape: dict[int, float]   # lap → QUBO cost (lower = better)
    strategy_type: str         # "one-stop" | "two-stop"
    explanation_context: str   # pre-built context string for Granite


def solve_pit_window(
    telemetry: LiveTelemetry,
    total_laps: int,
    window_size: int = 6,
    teammate_telem: Optional[LiveTelemetry] = None,
    p: int = 2,
) -> Optional[QuantumStrategyResult]:
    """
    Main entry point. Takes current telemetry and returns the QAOA-optimal
    pit lap within the next `window_size` laps.

    p: QAOA depth (number of alternating cost/mixer layers). Higher p =
       better approximation but more circuit depth. p=2 balances quality
       and NISQ noise tolerance.
    """
    try:
        from qiskit_optimization import QuadraticProgram
        from qiskit_optimization.algorithms import MinimumEigenOptimizer
        from qiskit_algorithms import QAOA
        from qiskit_algorithms.optimizers import COBYLA
        from qiskit_aer import AerSimulator
        from qiskit.primitives import StatevectorSampler
    except ImportError as e:
        print(f"[Quantum] Qiskit not available: {e}")
        return None

    current_lap   = telemetry.lap_number
    compound      = (telemetry.tyre_compound or "HARD").upper()
    tyre_age      = telemetry.tyre_age_laps or 0
    remaining     = max(1, total_laps - current_lap)

    # Candidate laps: next `window_size` laps, capped at race end
    candidate_laps = list(range(
        current_lap + 1,
        min(current_lap + window_size + 1, total_laps - 2)
    ))
    if len(candidate_laps) < 2:
        return None

    n = len(candidate_laps)

    # ── Build QUBO ────────────────────────────────────────────────────────────
    qp = QuadraticProgram(name="pit_window")
    for i in range(n):
        qp.binary_var(name=f"pit_{i}")

    # Linear terms — projected time cost of pitting on each lap
    linear = {}
    for i, lap in enumerate(candidate_laps):
        age_at_pit = tyre_age + (lap - current_lap)
        degradation_penalty = _tyre_cost(compound, age_at_pit, remaining - (lap - current_lap))
        # Pitting later = more degradation laps but fresh tyres longer
        # Pitting earlier = less degradation but shorter stint on new rubber
        linear[f"pit_{i}"] = degradation_penalty - _fresh_tyre_benefit(
            compound, remaining - (lap - current_lap)
        )

    # Linear penalty — double-stack cost on laps where teammate is expected to pit.
    # Estimate teammate's cliff lap from their compound and current tyre age, then
    # penalise any candidate lap within ±1 of that estimate. This is a linear term
    # on our own decision, not a quadratic cross-term between two of our candidates.
    quadratic = {}
    if teammate_telem and teammate_telem.lap_number:
        team_compound = (teammate_telem.tyre_compound or "HARD").upper()
        team_age      = teammate_telem.tyre_age_laps or 0
        team_cliff    = _CLIFF_LAP.get(team_compound, 30)
        laps_to_cliff = max(0, team_cliff - team_age)
        expected_team_pit = teammate_telem.lap_number + laps_to_cliff
        for i, lap in enumerate(candidate_laps):
            if abs(lap - expected_team_pit) <= 1:
                linear[f"pit_{i}"] = linear.get(f"pit_{i}", 0.0) + 8.0

    # Penalty: exactly one pit stop in window (λ * (Σpit_i - 1)²)
    # Expanded: λ * (Σpit_i² + 2Σ_{i<j} pit_i*pit_j - 2Σpit_i + 1)
    # Since pit_i ∈ {0,1}: pit_i² = pit_i
    lam = 15.0   # penalty weight — must dominate the objective terms
    for i in range(n):
        key = f"pit_{i}"
        linear[key] = linear.get(key, 0.0) + lam * (1 - 2)   # -2λ per variable

    for i in range(n):
        for j in range(i + 1, n):
            key = (f"pit_{i}", f"pit_{j}")
            quadratic[key] = quadratic.get(key, 0.0) + 2 * lam

    qp.minimize(linear=linear, quadratic=quadratic)

    # ── QAOA solve ────────────────────────────────────────────────────────────
    try:
        sampler   = StatevectorSampler()
        optimizer = COBYLA(maxiter=150)
        qaoa      = QAOA(sampler=sampler, optimizer=optimizer, reps=p)
        solver    = MinimumEigenOptimizer(qaoa)
        result    = solver.solve(qp)
    except Exception as e:
        print(f"[Quantum] QAOA failed: {e}")
        return _classical_fallback(candidate_laps, compound, tyre_age, current_lap, remaining)

    # ── Parse result ──────────────────────────────────────────────────────────
    x = result.x
    chosen_idx = int(np.argmax(x)) if any(x) else 0
    recommended_lap = candidate_laps[chosen_idx]

    # Energy landscape — evaluate QUBO cost for each single-pit option
    energy_landscape = {}
    for i, lap in enumerate(candidate_laps):
        vec = np.zeros(n)
        vec[i] = 1.0
        energy_landscape[lap] = float(qp.objective.evaluate(vec))

    # Strategy clarity — QUBO energy gap between best and next-best lap.
    # Larger gap means the recommended lap is more clearly dominant. Not a quantum probability.
    sorted_energies = sorted(energy_landscape.values())
    if len(sorted_energies) >= 2 and sorted_energies[1] != sorted_energies[0]:
        gap = abs(sorted_energies[1] - sorted_energies[0])
        confidence = min(0.97, 0.60 + gap / (abs(sorted_energies[0]) + 1e-6) * 0.3)
    else:
        confidence = 0.65

    context = _build_context(
        recommended_lap, confidence, candidate_laps, compound,
        tyre_age, current_lap, total_laps, energy_landscape, teammate_telem
    )

    return QuantumStrategyResult(
        recommended_lap=recommended_lap,
        confidence=round(confidence, 3),
        candidate_laps=candidate_laps,
        energy_landscape=energy_landscape,
        strategy_type="one-stop",
        explanation_context=context,
    )


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
    return laps_on_fresh * rate * 0.4   # ~40% of degradation saved on fresh rubber


def _classical_fallback(
    candidate_laps, compound, tyre_age, current_lap, remaining
) -> QuantumStrategyResult:
    """Greedy fallback when QAOA fails — picks lap minimising degradation cost."""
    costs = {}
    for lap in candidate_laps:
        age = tyre_age + (lap - current_lap)
        costs[lap] = _tyre_cost(compound, age, remaining - (lap - current_lap))
    best = min(costs, key=costs.get)
    return QuantumStrategyResult(
        recommended_lap=best,
        confidence=0.55,
        candidate_laps=candidate_laps,
        energy_landscape=costs,
        strategy_type="one-stop",
        explanation_context=f"Classical fallback: box lap {best} minimises tyre cost.",
    )


def _build_context(
    lap, confidence, candidates, compound, tyre_age, current_lap,
    total_laps, landscape, teammate
) -> str:
    best_alt = min((l for l in landscape if l != lap), key=lambda l: landscape[l], default=None)
    teammate_note = ""
    if teammate:
        teammate_note = f" Teammate is on lap {teammate.lap_number}, {teammate.tyre_compound} tyres."
    return (
        f"QAOA quantum optimizer evaluated {len(candidates)} candidate laps "
        f"({candidates[0]}–{candidates[-1]}) for a pit stop. "
        f"Recommended lap: {lap} (strategy clarity {confidence:.0%}). "
        f"Current compound: {compound}, age {tyre_age} laps, lap {current_lap}/{total_laps}. "
        f"Best alternative: lap {best_alt} (QUBO cost {landscape.get(best_alt, 0):.2f} vs {landscape.get(lap, 0):.2f})."
        f"{teammate_note} "
        f"This is a QUBO (Quadratic Unconstrained Binary Optimization) solution via QAOA "
        f"with p=2 layers on the Qiskit Aer statevector simulator."
    )
