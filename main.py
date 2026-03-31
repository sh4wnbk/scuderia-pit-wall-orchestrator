"""
Scuderia Pit-Wall Fan Orchestrator — Main Pipeline

Entry point. Wires all components in the correct dependency order
and exposes the single public method: process()

Pipeline execution order (matches the sequence diagram exactly):
  1. NLP Synthesizer structures input + fires Hook 1 to Overseer
  2. Planning Engine classifies intent → routes to specialist agent
  3. RAG Store retrieves knowledge context + fires Hook 2 to Overseer
     (happens inside the specialist agent's answer() call)
  4. FastF1 client fetches live data (strategy agent only)
  5. Specialist agent synthesises narrative with citation
  6. Execution Module sends to Overseer for Hook 3 pre-delivery check
  7. Overseer approves / triggers retry / suppresses
  8. FinalOutput delivered as text + audio

Usage:
    orchestrator = PitWallOrchestrator()
    orchestrator.set_race_context(year=2024, race="Bahrain", driver="LEC")

    # Text query from Sofia
    result = orchestrator.process(text_query="Why did Leclerc just lift?")

    # Audio from pit radio
    result = orchestrator.process(audio_bytes=raw_audio_bytes)

    # Telemetry-triggered push
    result = orchestrator.process(
        telemetry_event="MGU-K mode change detected",
        telemetry_data={"mode": "harvest", "battery_pct": 42}
    )
"""

from typing import Optional

from config import config
from execution.execution_module import ExecutionModule
from governance.overseer import OverseerAgent
from memory.rag_store import RAGStore
from models import FinalOutput, StructuredSignal
from perception.nlp_synthesizer import NLPSynthesizer
from reasoning.agentic_strategist import AgenticStrategist
from reasoning.planning_engine import PlanningEngine
from reasoning.regulation_agent import RegulationAgent
from tools.fastf1_client import FastF1Client


class PitWallOrchestrator:

    def __init__(self):
        # ── Instantiate all components ────────────────────────────────────
        self._overseer = OverseerAgent()
        self._rag = RAGStore()
        self._f1 = FastF1Client()
        self._nlp = NLPSynthesizer()
        self._planner = PlanningEngine()
        self._reg_agent = RegulationAgent(self._rag)
        self._strat_agent = AgenticStrategist(self._rag, self._f1)
        self._execution = ExecutionModule(self._overseer)

        # ── Wire governance audit hooks ───────────────────────────────────
        # Hook 1: NLP Synthesizer → Overseer
        self._nlp.register_audit_callback(self._overseer.receive_audit)
        # Hook 2: RAG Store → Overseer
        self._rag.register_audit_callback(self._overseer.receive_audit)
        # Hook 3: Execution Module → Overseer (wired inside ExecutionModule)

    def set_race_context(self, year: int, race: str, driver: str):
        """
        Configure the live race session.
        Call once at the start of each race session.
        """
        self._strat_agent.set_race_context(year, race, driver)
        print(f"[Orchestrator] Race context set: {year} {race} — tracking {driver}")

    def index_documents(
        self,
        fia_documents: Optional[list[dict]] = None,
        strategy_documents: Optional[list[dict]] = None,
    ) -> dict:
        """
        Load knowledge base documents into the RAG vector store.
        Call once before the race session begins.

        fia_documents: [{"text": str, "section": str, "title": str}, ...]
        strategy_documents: [{"text": str, "race": str, "year": int, "outcome": str}, ...]
        """
        results = {}
        if fia_documents:
            n = self._rag.index_fia_regulations(fia_documents)
            results["fia_chunks_indexed"] = n
            print(f"[Orchestrator] Indexed {n} FIA regulation chunks")
        if strategy_documents:
            n = self._rag.index_strategy_history(strategy_documents)
            results["strategy_chunks_indexed"] = n
            print(f"[Orchestrator] Indexed {n} strategy history chunks")
        return results

    # ── Main entry point ──────────────────────────────────────────────────────

    def process(
        self,
        text_query: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        telemetry_event: Optional[str] = None,
        telemetry_data: Optional[dict] = None,
    ) -> FinalOutput:
        """
        Single public method. Exactly one input type should be provided.
        Returns a FinalOutput with output_type in:
          "confirmed" | "retry_corrected" | "uncertainty"
        """
        # ── Step 1: Perception ────────────────────────────────────────────
        signal: StructuredSignal = self._perceive(
            text_query, audio_bytes, telemetry_event, telemetry_data
        )

        # ── Step 2: Planning — intent classification and routing ──────────
        intent = self._planner.classify(signal)
        print(f"[Orchestrator] Intent classified: {intent}")

        # ── Steps 3–5: RAG retrieval + tool invocation + synthesis ────────
        # (all happen inside the agent's answer() method in the correct order)
        if intent == "regulation":
            narrative = self._reg_agent.answer(signal)
            agent_callable = self._reg_agent.answer
        else:
            narrative = self._strat_agent.answer(signal)
            agent_callable = self._strat_agent.answer

        # ── Steps 6–8: Governance gate + retry loop + delivery ────────────
        output = self._execution.deliver(narrative, signal, agent_callable)

        print(f"[Orchestrator] Output delivered — type: {output.output_type}")
        return output

    def get_audit_log(self) -> list[dict]:
        """
        Full watsonx.governance audit log.
        Every hook receipt, every Overseer decision, with timestamps.
        """
        return self._overseer.get_audit_log()

    # ── Private ───────────────────────────────────────────────────────────────

    def _perceive(
        self,
        text_query: Optional[str],
        audio_bytes: Optional[bytes],
        telemetry_event: Optional[str],
        telemetry_data: Optional[dict],
    ) -> StructuredSignal:
        if audio_bytes is not None:
            return self._nlp.process_audio(audio_bytes)
        if text_query is not None:
            return self._nlp.process_text_query(text_query)
        if telemetry_event is not None:
            return self._nlp.process_telemetry_event(
                telemetry_event, telemetry_data or {}
            )
        raise ValueError(
            "process() requires text_query, audio_bytes, or telemetry_event"
        )


# ── Quick MVP demo ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    orchestrator = PitWallOrchestrator()

    # Load a minimal FIA regulation document for the demo
    sample_fia_doc = {
        "text": (
            "Article 5.4.2 — MGU-K Deployment\n\n"
            "The MGU-K may deploy a maximum of 120kW continuously during "
            "the race. Teams may store recovered energy in the Energy Store "
            "up to a maximum capacity of 4MJ per lap. The Recharge Phase "
            "refers to any period where the MGU-K is configured to recover "
            "kinetic energy rather than deploy it. During the Recharge Phase, "
            "the driver will experience reduced acceleration on straights as "
            "the electrical system prioritises energy recovery over deployment.\n\n"
            "Z-Mode refers to the high-downforce active aerodynamic configuration "
            "used in cornering zones. X-Mode refers to the low-drag configuration "
            "deployed on straights to minimise energy consumption at high speed."
        ),
        "section": "Article 5.4.2",
        "title": "MGU-K Deployment and Aerodynamic Modes",
    }

    orchestrator.index_documents(fia_documents=[sample_fia_doc])
    orchestrator.set_race_context(year=2024, race="Bahrain", driver="LEC")

    # Simulate Sofia's query
    print("\n── Processing fan query ──")
    result = orchestrator.process(
        text_query="Why did Leclerc just lift on the straight? Is the MGU-K failing?"
    )

    print(f"\nOutput type: {result.output_type}")
    print(f"Narrative: {result.text}")
    print(f"Traceability: {result.traceability_link}")
    print(f"Audio generated: {result.audio_bytes is not None}")
    print(f"Audit flag: {result.audit_flag}")
    print(f"\nAudit log entries: {len(orchestrator.get_audit_log())}")
