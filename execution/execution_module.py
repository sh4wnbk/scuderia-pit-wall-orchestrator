"""
Action & Execution Layer — Execution Module

Responsibilities:
  - Receive narrative from specialist agents
  - Send to Overseer for pre-delivery check (Hook 3)
  - Execute the retry loop with amended context if Overseer rejects
  - Deliver one of three output states — never a fourth
  - Convert confirmed output to audio via Watson Text-to-Speech

Three output states (no others exist):
  "confirmed"       → citation validated, Overseer approved
  "retry_corrected" → first pass failed, retry passed
  "uncertainty"     → retry budget exhausted, honest partial context

Watson TTS is the IBM-native Audio Overlay implementation.
The fan never reads the narrative — they hear it. Eyes stay on the TV.
"""

import io
from typing import Callable, Optional

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from config import config
from governance.overseer import OverseerAgent
from models import FinalOutput, Narrative, StructuredSignal


_UNCERTAINTY_TEMPLATE = (
    "I cannot fully confirm a strategy call for this situation right now. "
    "Here is what I can tell you with confidence: {partial_context} "
    "I will update you as more information becomes available."
)


class ExecutionModule:

    def __init__(self, overseer: OverseerAgent):
        self._overseer = overseer
        authenticator = IAMAuthenticator(config.tts_api_key)
        self._tts = TextToSpeechV1(authenticator=authenticator)
        self._tts.set_service_url(config.tts_url)

    def deliver(
        self,
        narrative: Narrative,
        signal: StructuredSignal,
        agent_callable: Callable[[StructuredSignal, Optional[str]], Narrative],
    ) -> FinalOutput:
        """
        Main delivery pipeline with retry loop.

        agent_callable: the specialist agent's answer() method, passed in
        so the Execution Module can trigger retries without circular imports.
        """
        retry_count = 0
        current_narrative = narrative

        while True:
            # ── Hook 3: Pre-delivery check ─────────────────────────────────
            decision = self._overseer.validate(current_narrative, retry_count)

            if decision.approved:
                # ── APPROVED ────────────────────────────────────────────────
                output_type = "retry_corrected" if retry_count > 0 else "confirmed"
                return self._build_output(
                    current_narrative, output_type, retry_count > 0
                )

            if decision.amended_context is None:
                # ── SUPPRESS (retry budget exhausted or no citation) ─────────
                return self._uncertainty_output(current_narrative)

            # ── RETRY with amended context ───────────────────────────────────
            retry_count += 1
            current_narrative = agent_callable(
                signal, decision.amended_context
            )

    # ── Private ──────────────────────────────────────────────────────────────

    def _build_output(
        self, narrative: Narrative, output_type: str, audit_flag: bool
    ) -> FinalOutput:
        """
        Build a confirmed or retry_corrected FinalOutput.
        Synthesises audio via Watson TTS.
        """
        audio = self._synthesise_audio(narrative.text)
        traceability = f"Source: {narrative.citation}"

        return FinalOutput(
            text=narrative.text,
            audio_bytes=audio,
            output_type=output_type,
            audit_flag=audit_flag,
            traceability_link=traceability,
        )

    def _uncertainty_output(self, narrative: Narrative) -> FinalOutput:
        """
        Build the uncertainty response.
        Delivers partial, honest context — never confident wrong output.
        Trust preserved over false confidence.
        """
        # Use what we can verify — the citation reference at minimum
        partial = narrative.citation if narrative.has_citation() else "data is still loading"
        text = _UNCERTAINTY_TEMPLATE.format(partial_context=partial)
        audio = self._synthesise_audio(text)

        return FinalOutput(
            text=text,
            audio_bytes=audio,
            output_type="uncertainty",
            audit_flag=False,
            traceability_link=None,
        )

    def _synthesise_audio(self, text: str) -> Optional[bytes]:
        """
        Watson Text-to-Speech — the Audio Overlay implementation.
        Returns None gracefully if TTS credentials are not configured.
        """
        if not config.tts_api_key or not config.tts_url:
            return None
        try:
            response = self._tts.synthesize(
                text,
                voice=config.tts_voice,
                accept="audio/wav",
            ).get_result()
            return response.content
        except Exception as e:
            print(f"[ExecutionModule] TTS failed: {e}")
            return None
