"""
Reasoning & Planning Layer — Agentic Strategist

Responsibilities:
  - Answer race strategy questions using RAG context + live FastF1 telemetry
  - RAG retrieval ALWAYS precedes live data fetch ALWAYS precedes reasoning
  - The two knowledge sources serve different purposes:
      RAG: what teams typically do in this situation (historical knowledge)
      FastF1: what is actually happening right now (live reality)
  - Cross-referencing both prevents book-smart-but-wrong outputs

This is the agent that makes the "Leclerc is harvesting battery" call.
"""

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

from config import config
from memory.rag_store import RAGStore
from models import LiveTelemetry, Narrative, StructuredSignal
from tools.fastf1_client import FastF1Client


_STRATEGY_PROMPT = """You are a Formula 1 race strategy analyst for Scuderia Ferrari.

You have access to two information sources. Use both.

LIVE RACE TELEMETRY — {primary_driver}:
{telemetry_context}

LIVE RACE TELEMETRY — TEAMMATE {teammate_driver}:
{teammate_context}

HISTORICAL STRATEGY CONTEXT (retrieved patterns):
{strategy_context}

Fan question or race event: {query}

Instructions:
1. Synthesise the live telemetry and historical strategy to explain what is happening.
2. Compare both drivers' situations where relevant to the question.
3. Predict the most likely next strategic move within 2–3 laps.
4. Write for a knowledgeable Ferrari fan. Under 90 words.
5. Do NOT speculate beyond what the data supports.
6. {language_instruction}
7. End with exactly this format on a new line:
   [Citation: {citation}]

Analysis:"""


_NO_TELEMETRY_PROMPT = """You are a Formula 1 race strategy analyst for Scuderia Ferrari.

Live telemetry is unavailable. Use only historical strategy context.

HISTORICAL STRATEGY CONTEXT:
{strategy_context}

Fan question: {query}

Provide a concise, plain-English analysis based on historical patterns only.
Note that live data is currently unavailable.
End with: [Citation: {citation}]

Analysis:"""


class AgenticStrategist:

    def __init__(self, rag_store: RAGStore, fastf1_client: FastF1Client):
        self._rag = rag_store
        self._f1 = fastf1_client
        credentials = Credentials(
            url=config.watsonx_url,
            api_key=config.watsonx_api_key,
        )
        self._model = ModelInference(
            model_id=config.granite_model_id,
            credentials=credentials,
            project_id=config.watsonx_project_id,
            params={
                "max_new_tokens": 250,
                "temperature": 0.2,   # slight creativity for narrative quality
                "top_p": 0.9,
                "stop_sequences": ["\n\n"],
            },
        )
        # Current race context — set before each race session
        self._race_year: int = 2026
        self._race_name: str = "Miami"
        self._driver: str = "LEC"
        self._ferrari_drivers: list[str] = ["LEC", "HAM"]

    def set_race_context(
        self,
        year: int,
        race: str,
        driver: str,
        ferrari_drivers: list[str] | None = None,
    ):
        """Call once at session start to configure the live data target."""
        self._race_year = year
        self._race_name = race
        self._driver = driver
        if ferrari_drivers is not None:
            self._ferrari_drivers = ferrari_drivers

    def answer(
        self,
        signal: StructuredSignal,
        amended_context: str | None = None,
    ) -> Narrative:
        """
        Full strategy pipeline: RAG → FastF1 → Granite → Narrative.
        amended_context is passed on Overseer retry with corrected scope.
        """
        # ── Step 1: RAG retrieval (retrieve first) ─────────────────────────
        query = amended_context or signal.raw_text
        rag_result = self._rag.query_strategy(query)
        citation = rag_result.best_citation()
        cited_chunk = rag_result.best_chunk()
        strategy_context = "\n\n".join(rag_result.chunks) if rag_result.chunks else "No historical context retrieved."

        # ── Step 2: FastF1 live data for both Ferrari drivers ──────────────
        snapshot = self._f1.get_race_snapshot(
            year=self._race_year,
            race=self._race_name,
            drivers=self._ferrari_drivers,
        )
        telemetry: LiveTelemetry | None = snapshot.get(self._driver)
        teammates = [d for d in self._ferrari_drivers if d != self._driver]
        teammate_code = teammates[0] if teammates else None
        teammate_telemetry: LiveTelemetry | None = (
            snapshot.get(teammate_code) if teammate_code else None
        )

        # ── Step 3: Build prompt ─────────────────────────────────────────────
        lang_instruction = (
            "Respond in Italian (Italiano)."
            if signal.language == "it"
            else "Respond in English."
        )
        if telemetry:
            teammate_ctx = (
                teammate_telemetry.to_context_string()
                if teammate_telemetry
                else "Teammate data unavailable."
            )
            primary_name = telemetry.driver_name
            teammate_name = teammate_telemetry.driver_name if teammate_telemetry else (teammate_code or "Teammate")
            prompt = _STRATEGY_PROMPT.format(
                primary_driver=primary_name,
                telemetry_context=telemetry.to_context_string(),
                teammate_driver=teammate_name,
                teammate_context=teammate_ctx,
                strategy_context=strategy_context,
                query=signal.raw_text,
                citation=citation,
                language_instruction=lang_instruction,
            )
        else:
            prompt = _NO_TELEMETRY_PROMPT.format(
                strategy_context=strategy_context,
                query=signal.raw_text,
                citation=citation,
            )

        # ── Step 4: Reason (Granite call) ───────────────────────────────────
        raw_response = self._model.generate_text(prompt).strip()
        text, parsed_citation = self._parse_citation(raw_response, citation)

        rag_confidence = (
            max(rag_result.similarity_scores) if rag_result.similarity_scores else 0.0
        )

        return Narrative(
            text=text,
            citation=parsed_citation,
            cited_chunk=cited_chunk,
            rag_confidence=rag_confidence,
            agent_type="strategy",
        )

    # ── Private ──────────────────────────────────────────────────────────────

    def _parse_citation(
        self, raw: str, fallback: str
    ) -> tuple[str, str]:
        if "[Citation:" in raw:
            parts = raw.split("[Citation:")
            text = parts[0].strip()
            citation = parts[1].replace("]", "").strip()
            return text, citation
        return raw.strip(), fallback
