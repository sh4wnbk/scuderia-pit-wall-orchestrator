from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class StructuredSignal:
    """
    Output of the NLP Synthesizer (Perception layer).
    Everything downstream works from this — never from raw input.
    """
    raw_text: str
    signal_type: str          # "query" | "telemetry_event" | "radio"
    transcript_confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    telemetry: Optional[dict] = None   # populated for telemetry_event signals
    language: str = "en"               # "en" | "it" — governs STT model, TTS voice, prompt language

    def is_high_confidence(self, threshold: float = 0.75) -> bool:
        return self.transcript_confidence >= threshold


@dataclass
class RAGResult:
    """
    Output of a RAG Vector DB query.
    Carries the retrieved chunks and their provenance — the citation chain.
    """
    chunks: list[str]
    citations: list[str]         # document section references
    similarity_scores: list[float]
    query: str
    collection_name: str

    def best_citation(self) -> str:
        if not self.citations:
            return "No citation available"
        best_idx = self.similarity_scores.index(max(self.similarity_scores))
        return self.citations[best_idx]

    def best_chunk(self) -> str:
        if not self.chunks:
            return ""
        best_idx = self.similarity_scores.index(max(self.similarity_scores))
        return self.chunks[best_idx]

    def meets_threshold(self, threshold: float = 0.7) -> bool:
        return bool(self.similarity_scores) and max(self.similarity_scores) >= threshold


@dataclass
class LiveTelemetry:
    """
    Output of the FastF1 tool invocation (Tools layer).
    """
    driver_code: str
    driver_name: str
    lap_number: int
    lap_time_str: str
    tyre_compound: str
    tyre_age_laps: int
    position: int
    gap_to_leader: str
    interval_to_ahead: str          # gap to car immediately ahead
    pit_stops: int                  # stops completed (stint - 1)
    pace_delta_seconds: Optional[float]   # last lap vs avg of prior 3 laps (positive = slower)
    sector_1: str
    sector_2: str
    sector_3: str
    session_name: str
    race_year: int

    def to_context_string(self) -> str:
        pace = f"{self.pace_delta_seconds:+.2f}s" if self.pace_delta_seconds is not None else "N/A"
        return (
            f"Driver: {self.driver_name} | Lap: {self.lap_number} | "
            f"Lap Time: {self.lap_time_str} | Tyre: {self.tyre_compound} "
            f"({self.tyre_age_laps} laps old) | Position: P{self.position} | "
            f"Interval to ahead: {self.interval_to_ahead} | "
            f"Pit stops: {self.pit_stops} | Pace delta: {pace} | "
            f"Sectors: {self.sector_1} / {self.sector_2} / {self.sector_3}"
        )


@dataclass
class Narrative:
    """
    The synthesised output from a specialist agent before governance review.
    Must carry a citation — citation-free narratives are suppressed by the Overseer.
    """
    text: str
    citation: str
    cited_chunk: str             # the actual source text — Overseer uses this
    rag_confidence: float
    agent_type: str              # "regulation" | "strategy"

    def has_citation(self) -> bool:
        return bool(self.citation) and self.citation != "No citation available"


@dataclass
class OverseerDecision:
    """
    The Overseer Agent's verdict after pre-delivery cross-validation.
    Carries enough information for the retry to be genuinely better informed.
    """
    approved: bool
    failure_reason: Optional[str] = None
    amended_context: Optional[str] = None  # corrected RAG scope for retry
    retry_count: int = 0
    audit_entry: Optional[dict] = None


@dataclass
class FinalOutput:
    """
    What actually reaches Sofia — one of three possible output states.
    output_type encodes the system's epistemic state at delivery time.
    """
    text: str
    audio_bytes: Optional[bytes]
    output_type: str              # "confirmed" | "retry_corrected" | "uncertainty"
    audit_flag: bool = False      # True when output passed on retry
    traceability_link: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_trustworthy(self) -> bool:
        """Confirmed and retry_corrected are both trustworthy. Uncertainty is honest."""
        return self.output_type in ("confirmed", "retry_corrected", "uncertainty")
