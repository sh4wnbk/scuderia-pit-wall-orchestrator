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

LIVE RACE TELEMETRY (current lap data):
{telemetry_context}

HISTORICAL STRATEGY CONTEXT (retrieved patterns):
{strategy_context}

Fan question or race event: {query}

Instructions:
1. Synthesise the live telemetry and historical strategy to explain what is happening.
2. Predict the most likely next strategic move within 2–3 laps.
3. Write in plain English for a knowledgeable Ferrari fan. Under 80 words.
4. Do NOT speculate beyond what the data supports.
5. End with exactly this format on a new line:
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
        self._race_year: int = 2024
        self._race_name: str = "Bahrain"
        self._driver: str = "LEC"

    def set_race_context(self, year: int, race: str, driver: str):
        """Call once at session start to configure the live data target."""
        self._race_year = year
        self._race_name = race
        self._driver = driver

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

        # ── Step 2: FastF1 live data (after RAG, before reasoning) ─────────
        telemetry: LiveTelemetry | None = self._f1.get_driver_telemetry(
            year=self._race_year,
            race=self._race_name,
            session_type="R",
            driver_code=self._driver,
        )

        # ── Step 3: Build prompt ─────────────────────────────────────────────
        if telemetry:
            prompt = _STRATEGY_PROMPT.format(
                telemetry_context=telemetry.to_context_string(),
                strategy_context=strategy_context,
                query=signal.raw_text,
                citation=citation,
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
