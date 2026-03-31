import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # ── IBM watsonx.ai ────────────────────────────────────────────────────────
    watsonx_api_key: str = os.getenv("WATSONX_API_KEY", "")
    watsonx_url: str = os.getenv(
        "WATSONX_URL", "https://us-south.ml.cloud.ibm.com"
    )
    watsonx_project_id: str = os.getenv("WATSONX_PROJECT_ID", "")
    granite_model_id: str = "ibm/granite-13b-chat-v2"

    # ── IBM Watson Speech-to-Text ─────────────────────────────────────────────
    stt_api_key: str = os.getenv("WATSON_STT_API_KEY", "")
    stt_url: str = os.getenv("WATSON_STT_URL", "")
    stt_model: str = "en-US_BroadbandModel"   # handles heavy accents + noise

    # ── IBM Watson Text-to-Speech ─────────────────────────────────────────────
    tts_api_key: str = os.getenv("WATSON_TTS_API_KEY", "")
    tts_url: str = os.getenv("WATSON_TTS_URL", "")
    tts_voice: str = "en-US_AllisonV3Voice"

    # ── Governance thresholds ─────────────────────────────────────────────────
    confidence_threshold: float = 0.7   # RAG similarity floor
    max_retries: int = 2                # Overseer retry budget

    # ── Latency budget (milliseconds) ─────────────────────────────────────────
    # First pass ~1000ms + Overseer ~150ms + Retry ~950ms + Recheck ~150ms
    target_latency_ms: int = 2000
    max_latency_ms: int = 2250

    # ── Vector store ──────────────────────────────────────────────────────────
    chroma_path: str = "./chroma_db"
    fia_collection: str = "fia_2026_regulations"
    strategy_collection: str = "strategy_history"

    # ── FastF1 cache ──────────────────────────────────────────────────────────
    fastf1_cache_path: str = "./fastf1_cache"


# Module-level singleton — imported everywhere
config = Config()
