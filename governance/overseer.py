"""
Governance Layer — Proactive Overseer Agent (watsonx.governance)

This is the most architecturally important component.

Responsibilities:
  Hook 1: Receive transcript audits from NLP Synthesizer
  Hook 2: Receive retrieval audits from RAG Store
  Hook 3: Pre-delivery cross-validation of every narrative before delivery

Cross-validation logic (Hook 3):
  - Takes the narrative + its claimed citation + the actual cited chunk
  - Asks Granite: does this narrative accurately represent what the chunk says?
  - This is NOT confidence scoring — it is claim verification
  - A confident wrong narrative passes confidence scoring; it fails here

The retry mechanism:
  - On failure, sends a SPECIFIC failure reason + amended context back to Planning
  - Not "wrong, try again" — "wrong because X, re-query with scope Y"
  - Max retries enforced by config.max_retries

Three possible verdicts:
  APPROVED → deliver with traceability link
  RETRY    → re-enter pipeline with amended context (up to max_retries)
  SUPPRESS → deliver uncertainty response (retry budget exhausted)

Audit log:
  Every decision recorded with full traceability.
  This is the watsonx.governance artifact — explainability at decision level.
"""

from datetime import datetime
from typing import Optional

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

from config import config
from models import Narrative, OverseerDecision


_CROSS_VALIDATION_PROMPT = """You are a governance overseer for an AI assistant used by Ferrari fans.
Your job: verify that a narrative accurately represents its cited source.

NARRATIVE (what the AI told the fan):
{narrative}

CLAIMED CITATION:
{citation}

ACTUAL CITED SOURCE TEXT:
{cited_chunk}

Does the narrative accurately represent what the cited source says?
Be strict. Flag any claim not directly supported by the source text.

Respond with EXACTLY one of these two formats:
VALIDATED: <one sentence explaining why it is accurate>
INVALID: <specific failure reason> | AMENDED_SCOPE: <corrected query scope for retry>

Response:"""


class OverseerAgent:

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
                "max_new_tokens": 100,
                "temperature": 0.0,    # deterministic validation
                "stop_sequences": ["\n\n"],
            },
        )
        self._audit_log: list[dict] = []
        self._pending_retrieval: dict = {}  # Hook 2 data, keyed by query

    # ── Audit hooks (called by NLP Synthesizer and RAG Store) ────────────────

    def receive_audit(self, hook_type: str, data: dict) -> None:
        """
        Unified audit receiver for Hook 1 (transcript) and Hook 2 (retrieval).
        Stores data for use in the Hook 3 pre-delivery check.
        """
        entry = {
            "hook": hook_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        self._audit_log.append(entry)

        if hook_type == "retrieval_audit":
            # Store indexed by query for cross-validation lookup at Hook 3
            query = data.get("query", "")
            self._pending_retrieval[query] = data

        # Flag anomalies immediately — transcript confidence below threshold
        if hook_type == "transcript_audit" and data.get("anomaly_flag"):
            self._log_anomaly("low_transcript_confidence", data)

    # ── Hook 3: Pre-delivery cross-validation ─────────────────────────────────

    def validate(
        self, narrative: Narrative, retry_count: int = 0
    ) -> OverseerDecision:
        """
        Pre-delivery check. Called by the Execution Module before
        any output reaches Sofia.

        Returns an OverseerDecision with:
          approved=True  → deliver
          approved=False → retry or suppress based on retry_count
        """
        # Guard: no citation = automatic suppression
        if not narrative.has_citation():
            return self._suppress(
                narrative,
                reason="No citation present — output suppressed to prevent ungrounded delivery.",
                retry_count=retry_count,
            )

        # Retrieve the cited chunk from Hook 2 audit log
        cited_chunk = self._resolve_cited_chunk(narrative)
        if not cited_chunk:
            # We have a citation string but no stored chunk — soft fail
            return self._suppress(
                narrative,
                reason="Cited chunk not found in retrieval audit log — cannot cross-validate.",
                retry_count=retry_count,
            )

        # Cross-validation via Granite
        prompt = _CROSS_VALIDATION_PROMPT.format(
            narrative=narrative.text,
            citation=narrative.citation,
            cited_chunk=cited_chunk,
        )
        raw = self._model.generate_text(prompt).strip()

        if raw.upper().startswith("VALIDATED"):
            return self._approve(narrative, raw, retry_count)
        else:
            return self._handle_failure(narrative, raw, retry_count)

    # ── Audit log access ──────────────────────────────────────────────────────

    def get_audit_log(self) -> list[dict]:
        """Full audit log — every hook receipt and every decision."""
        return self._audit_log.copy()

    def get_last_decision(self) -> Optional[dict]:
        decisions = [e for e in self._audit_log if e.get("hook") == "overseer_decision"]
        return decisions[-1] if decisions else None

    # ── Private ───────────────────────────────────────────────────────────────

    def _approve(
        self, narrative: Narrative, validation_reason: str, retry_count: int
    ) -> OverseerDecision:
        entry = {
            "hook": "overseer_decision",
            "verdict": "APPROVED",
            "retry_count": retry_count,
            "citation": narrative.citation,
            "agent_type": narrative.agent_type,
            "validation_reason": validation_reason,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._audit_log.append(entry)
        return OverseerDecision(
            approved=True,
            retry_count=retry_count,
            audit_entry=entry,
        )

    def _handle_failure(
        self, narrative: Narrative, raw_response: str, retry_count: int
    ) -> OverseerDecision:
        """
        Parse the failure reason and amended scope from the Overseer's response.
        If retry budget is exhausted, suppress. Otherwise, return retry signal.
        """
        failure_reason, amended_scope = self._parse_failure(raw_response)

        if retry_count >= config.max_retries:
            return self._suppress(narrative, failure_reason, retry_count)

        entry = {
            "hook": "overseer_decision",
            "verdict": "RETRY",
            "retry_count": retry_count,
            "failure_reason": failure_reason,
            "amended_scope": amended_scope,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._audit_log.append(entry)

        return OverseerDecision(
            approved=False,
            failure_reason=failure_reason,
            amended_context=amended_scope,
            retry_count=retry_count,
            audit_entry=entry,
        )

    def _suppress(
        self, narrative: Narrative, reason: str, retry_count: int
    ) -> OverseerDecision:
        entry = {
            "hook": "overseer_decision",
            "verdict": "SUPPRESS",
            "retry_count": retry_count,
            "failure_reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._audit_log.append(entry)
        return OverseerDecision(
            approved=False,
            failure_reason=reason,
            amended_context=None,
            retry_count=retry_count,
            audit_entry=entry,
        )

    def _resolve_cited_chunk(self, narrative: Narrative) -> Optional[str]:
        """
        Look up the actual cited chunk from the Hook 2 retrieval audit log.
        The Overseer needs the raw source text to cross-validate the narrative.
        """
        for entry in reversed(self._audit_log):
            if entry.get("hook") == "retrieval_audit":
                chunks = entry["data"].get("chunks", [])
                if chunks:
                    return chunks[0]   # best chunk is always first
        return None

    def _parse_failure(self, raw: str) -> tuple[str, str]:
        """
        Extract failure reason and amended scope from:
        INVALID: <reason> | AMENDED_SCOPE: <scope>
        """
        try:
            without_prefix = raw.replace("INVALID:", "").strip()
            if "| AMENDED_SCOPE:" in without_prefix:
                parts = without_prefix.split("| AMENDED_SCOPE:")
                return parts[0].strip(), parts[1].strip()
            return without_prefix.strip(), ""
        except Exception:
            return "Validation failed — unable to parse failure reason.", ""

    def _log_anomaly(self, anomaly_type: str, data: dict) -> None:
        self._audit_log.append({
            "hook": "anomaly_flag",
            "anomaly_type": anomaly_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })
