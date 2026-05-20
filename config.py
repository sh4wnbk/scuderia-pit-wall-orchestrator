import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _read_secret_from_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def _get_secret(name: str, default: str = "") -> str:
    """
    Prefer env var value, then fall back to file-mounted secret.
    Supports Code Engine secret mounts with <NAME>_FILE paths.
    """
    direct = os.getenv(name)
    if direct:
        return direct

    file_path = os.getenv(f"{name}_FILE", "")
    if file_path:
        value = _read_secret_from_file(file_path)
        if value:
            return value

    return default


@dataclass
class Config:
    # ── IBM watsonx.ai ────────────────────────────────────────────────────────
    watsonx_api_key: str = _get_secret("WATSONX_API_KEY")
    watsonx_url: str = os.getenv(
        "WATSONX_URL", "https://us-south.ml.cloud.ibm.com"
    )
    watsonx_project_id: str = _get_secret("WATSONX_PROJECT_ID")
    granite_model_id: str = "ibm/granite-4-h-small"

    # ── IBM Watson Speech-to-Text ─────────────────────────────────────────────
    stt_api_key: str = _get_secret("WATSON_STT_API_KEY")
    stt_url: str = os.getenv("WATSON_STT_URL", "")
    stt_model: str = "en-US_BroadbandModel"
    stt_model_it: str = "it-IT_BroadbandModel"

    # ── IBM Watson Text-to-Speech ─────────────────────────────────────────────
    tts_api_key: str = _get_secret("WATSON_TTS_API_KEY")
    tts_url: str = os.getenv("WATSON_TTS_URL", "")
    tts_voice: str = "en-US_AllisonExpressive"      # EN default
    tts_voice_it: str = "it-IT_FrancescaV3Voice"    # IT only option
    tts_voices: dict = field(default_factory=lambda: {
        "allison": "en-US_AllisonExpressive",
        "michael": "en-US_MichaelExpressive",
        "george":  "en-GB_GeorgeExpressive",
        "emma":    "en-US_EmmaExpressive",
        "lisa":    "en-US_LisaExpressive",
    })

    # ── Governance thresholds ─────────────────────────────────────────────────
    confidence_threshold: float = 0.55  # RAG similarity floor; FIA legal text embeds lower than plain English
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
