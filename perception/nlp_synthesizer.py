"""
Perception Layer — NLP Synthesizer

Responsibilities:
  1. Transcribe raw audio via Watson Speech-to-Text (Hook 1 source)
  2. Structure the signal into a typed StructuredSignal
  3. Fire transcript audit to the Overseer before reasoning begins

Watson STT is the correct IBM-native choice here:
  - Handles high-noise, heavily-accented pit-wall radio
  - en-US_BroadbandModel performs well on technical jargon
  - Streaming WebSocket available for always-on race session use
"""

import io
import re
from datetime import datetime
from typing import Optional

from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from config import config
from models import StructuredSignal


class NLPSynthesizer:

    # Keywords that flag a telemetry event rather than a fan query
    _TELEMETRY_KEYWORDS = {
        "x-mode", "z-mode", "harvest", "deploy", "override",
        "box box", "push now", "recharge", "mgu-k", "ers",
        "delta", "sector", "undercut", "overcut"
    }

    def __init__(self):
        authenticator = IAMAuthenticator(config.stt_api_key)
        self._stt = SpeechToTextV1(authenticator=authenticator)
        self._stt.set_service_url(config.stt_url)
        self._audit_callback = None   # set by main pipeline after Overseer is built

    def register_audit_callback(self, callback):
        """
        The Overseer registers itself here so the NLP Synthesizer
        can fire Hook 1 (transcript audit) without a circular import.
        """
        self._audit_callback = callback

    # ── Public API ──────────────────────────────────────────────────────────

    def process_audio(self, audio_bytes: bytes) -> StructuredSignal:
        """
        Full pipeline: raw audio → Watson STT → structured signal → audit.
        Used for pit-wall radio transcription.
        """
        transcript, confidence = self._transcribe(audio_bytes)
        signal = self._structure(transcript, confidence)
        self._fire_audit(signal)
        return signal

    def process_text_query(self, text: str) -> StructuredSignal:
        """
        Direct text path: Sofia's typed query → structured signal → audit.
        Confidence is 1.0 — no transcription uncertainty.
        """
        signal = self._structure(text, confidence=1.0)
        self._fire_audit(signal)
        return signal

    def process_telemetry_event(
        self, event_description: str, telemetry: dict
    ) -> StructuredSignal:
        """
        Triggered by the FastF1 polling loop when a significant
        telemetry delta is detected (e.g. MGU-K mode change).
        """
        signal = StructuredSignal(
            raw_text=event_description,
            signal_type="telemetry_event",
            transcript_confidence=1.0,
            timestamp=datetime.utcnow(),
            telemetry=telemetry,
        )
        self._fire_audit(signal)
        return signal

    # ── Private methods ─────────────────────────────────────────────────────

    def _transcribe(self, audio_bytes: bytes) -> tuple[str, float]:
        """
        Watson STT call. Returns (transcript, confidence).
        smart_formatting=True handles numbers and technical notation.
        """
        result = (
            self._stt.recognize(
                audio=io.BytesIO(audio_bytes),
                content_type="audio/wav",
                model=config.stt_model,
                smart_formatting=True,
            )
            .get_result()
        )

        if not result.get("results"):
            return "", 0.0

        best = result["results"][0]["alternatives"][0]
        return best["transcript"].strip(), best.get("confidence", 0.0)

    def _structure(self, text: str, confidence: float) -> StructuredSignal:
        """
        Classify the signal type based on content.
        Radio/telemetry language is distinguishable from fan queries.
        """
        lowered = text.lower()
        is_radio = any(kw in lowered for kw in self._TELEMETRY_KEYWORDS)
        signal_type = "radio" if is_radio else "query"

        return StructuredSignal(
            raw_text=text,
            signal_type=signal_type,
            transcript_confidence=confidence,
            timestamp=datetime.utcnow(),
        )

    def _fire_audit(self, signal: StructuredSignal) -> None:
        """
        Governance Hook 1 — fires to the Overseer immediately after
        transcription, before any reasoning begins.
        If the Overseer is not yet registered, the audit is a no-op.
        """
        if self._audit_callback:
            self._audit_callback("transcript_audit", {
                "signal_type": signal.signal_type,
                "raw_text": signal.raw_text,
                "confidence": signal.transcript_confidence,
                "timestamp": signal.timestamp.isoformat(),
                "anomaly_flag": not signal.is_high_confidence(),
            })
