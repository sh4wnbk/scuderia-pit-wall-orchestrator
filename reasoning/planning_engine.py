"""
Reasoning & Planning Layer — Planning Engine

Responsibilities:
  - Classify the incoming StructuredSignal as "regulation" or "strategy"
  - Route to the correct specialist agent
  - Guard against misrouting: a regulation question sent to the
    strategy agent produces a plausible but legally incorrect answer

Uses a lightweight Granite call for intent classification.
The classification prompt is deliberately narrow — two choices only.
"""

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

from config import config
from models import StructuredSignal


_CLASSIFICATION_PROMPT = """You are a routing engine for a Formula 1 AI assistant.

Classify the following input as either "regulation" or "strategy".

regulation: questions about FIA rules, technical regulations, legal limits,
            aerodynamic modes, power unit rules, MGU-K specifications,
            what is or is not permitted under the 2026 regulations.

strategy: questions about race tactics, pit stop timing, tyre management,
          undercuts, overcuts, lap delta, competitor positions,
          "should Ferrari pit now", battery deployment decisions in race context.

Input: {signal_text}

Respond with exactly one word: regulation OR strategy"""


class PlanningEngine:

    def __init__(self):
        credentials = Credentials(
            url=config.watsonx_url,
            api_key=config.watsonx_api_key,
        )
        self._model = ModelInference(
            model_id=config.granite_model_id,
            credentials=credentials,
            project_id=config.watsonx_project_id,
            params={
                "max_new_tokens": 5,    # one word response only
                "temperature": 0.0,     # deterministic classification
                "stop_sequences": ["\n"],
            },
        )

    def classify(self, signal: StructuredSignal) -> str:
        """
        Returns "regulation" or "strategy".
        Falls back to "strategy" if the model returns something unexpected —
        the strategy agent is more general and degrades more gracefully.
        """
        prompt = _CLASSIFICATION_PROMPT.format(signal_text=signal.raw_text)
        raw = self._model.generate_text(prompt).strip().lower()

        if "regulation" in raw:
            return "regulation"
        return "strategy"
