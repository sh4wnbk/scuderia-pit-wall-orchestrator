"""
Reasoning & Planning Layer — Regulation Agent

Responsibilities:
  - Answer questions grounded ONLY in the FIA 2026 Technical Regulations
  - RETRIEVE first via RAG, then REASON
  - Every output MUST carry a citation — no citation = suppressed by Overseer
  - Translate technical regulation language into plain English for Sofia

The "retrieve first, reason second" ordering is enforced structurally:
RAG query happens before the Granite call is made.
"""

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

from config import config
from memory.rag_store import RAGStore
from models import Narrative, RAGResult, StructuredSignal


# Fan-facing terms → 2026 regulation language.
# The 2026 regs retired several common F1 abbreviations.
_TERM_SYNONYMS: dict[str, str] = {
    "drs": "movable rear wing flap rear wing adjuster system",
    "drag reduction system": "movable rear wing flap rear wing adjuster system",
    "ers": "energy recovery system MGU-K MGU-H energy store",
    "mgu-h": "Motor Generator Unit Heat energy recovery",
    "mgu-k": "Motor Generator Unit Kinetic energy recovery",
    "kers": "energy recovery system kinetic energy store",
    "floor": "floor body underfloor ground effect",
    "porpoising": "aerodynamic oscillation plank ride height",
    "parc ferme": "parc ferme impound",
    "power unit": "power unit internal combustion engine PU",
}


def _expand_query(query: str) -> str:
    """Append regulation synonyms for known fan shorthand terms."""
    q_lower = query.lower()
    extras = []
    for fan_term, reg_terms in _TERM_SYNONYMS.items():
        if fan_term in q_lower:
            extras.append(reg_terms)
    return f"{query} {' '.join(extras)}".strip() if extras else query


_REGULATION_PROMPT = """You are a Formula 1 technical regulation expert for Scuderia Ferrari fans.

Your ONLY source of knowledge is the regulation context provided below.
Do not use any outside knowledge. Do not guess. Do not extrapolate.

If the context does not contain enough information to answer the question,
state clearly: "I cannot confirm this from the available regulation text."

Question: {query}

Regulation context:
{context}

Instructions:
1. Answer in plain English that a knowledgeable Ferrari fan can understand.
2. Keep the answer under 60 words.
3. {language_instruction}
4. End with exactly this format on a new line:
   [Citation: {citation}]

Answer:"""


class RegulationAgent:

    def __init__(self, rag_store: RAGStore):
        self._rag = rag_store
        credentials = Credentials(
            url=config.watsonx_url,
            api_key=config.watsonx_api_key,
        )
        self._model = ModelInference(
            model_id=config.granite_model_id,
            credentials=credentials,
            project_id=config.watsonx_project_id,
            params={
                "max_new_tokens": 200,
                "temperature": 0.1,   # low temperature — factual, not creative
                "top_p": 0.9,
                "stop_sequences": ["\n\n"],
            },
        )

    def answer(
        self,
        signal: StructuredSignal,
        amended_context: str | None = None,
    ) -> Narrative:
        """
        Full regulation answer pipeline.
        amended_context is passed on retry — the Overseer's corrected scope.
        """
        # ── Step 1: Retrieve (ALWAYS before reasoning) ─────────────────────
        query = _expand_query(amended_context or signal.raw_text)
        rag_result: RAGResult = self._rag.query_regulations(query)

        if not rag_result.meets_threshold(config.confidence_threshold):
            return self._low_confidence_narrative(signal.raw_text, rag_result)

        # ── Step 2: Build context string ────────────────────────────────────
        context = "\n\n".join(rag_result.chunks)
        citation = rag_result.best_citation()
        cited_chunk = rag_result.best_chunk()

        # ── Step 3: Reason (Granite call) ───────────────────────────────────
        lang_instruction = (
            "Respond in Italian (Italiano)."
            if signal.language == "it"
            else "Respond in English."
        )
        prompt = _REGULATION_PROMPT.format(
            query=signal.raw_text,
            context=context,
            citation=citation,
            language_instruction=lang_instruction,
        )
        raw_response = self._model.generate_text(prompt).strip()

        # ── Step 4: Parse citation from response ────────────────────────────
        text, parsed_citation = self._parse_citation(raw_response, citation)

        return Narrative(
            text=text,
            citation=parsed_citation,
            cited_chunk=cited_chunk,
            rag_confidence=max(rag_result.similarity_scores),
            agent_type="regulation",
        )

    # ── Private ──────────────────────────────────────────────────────────────

    def _low_confidence_narrative(
        self, query: str, rag_result: RAGResult
    ) -> Narrative:
        """
        RAG did not return a sufficiently similar chunk.
        Return a structured low-confidence signal rather than guessing.
        """
        return Narrative(
            text=(
                f"I cannot find a specific 2026 regulation that directly "
                f"addresses: '{query}'. The regulation corpus may not yet "
                f"cover this scenario."
            ),
            citation="No citation available",
            cited_chunk="",
            rag_confidence=max(rag_result.similarity_scores, default=0.0),
            agent_type="regulation",
        )

    def _parse_citation(
        self, raw: str, fallback_citation: str
    ) -> tuple[str, str]:
        """
        Extract [Citation: ...] from the model's response.
        If parsing fails, use the RAG citation as fallback.
        """
        if "[Citation:" in raw:
            parts = raw.split("[Citation:")
            text = parts[0].strip()
            citation = parts[1].replace("]", "").strip()
            return text, citation
        return raw.strip(), fallback_citation
