# Reads all environment variables for the backend in one place.
# Import `settings` anywhere in the app — never read os.getenv() directly in routes.
import os
from pathlib import Path
from dotenv import load_dotenv

# Always locate the backend/.env file regardless of current working directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")
load_dotenv()


class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "8"))
    primary_llm_api_key: str = os.getenv("PRIMARY_LLM_API_KEY", "")
    primary_llm_model: str = os.getenv(
        "PRIMARY_LLM_MODEL",
        "gemini-2.5-flash",
    )
    fallback_llm_api_key: str = os.getenv("FALLBACK_LLM_API_KEY", "")
    fallback_llm_model: str = os.getenv(
        "FALLBACK_LLM_MODEL",
        "gemini-2.5-flash-lite",
    )
    llm_timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
    llm_max_attempts: int = int(os.getenv("LLM_MAX_ATTEMPTS", "3"))
    ocr_timeout_seconds: int = int(os.getenv("OCR_TIMEOUT_SECONDS", "20"))
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    llm_daily_call_limit: int = int(os.getenv("LLM_DAILY_CALL_LIMIT", "100"))
    llm_daily_cost_limit_usd: float = float(
        os.getenv("LLM_DAILY_COST_LIMIT_USD", "5")
    )
    llm_estimated_cost_usd: float = float(
        os.getenv("LLM_ESTIMATED_COST_USD", "0.01")
    )
    tts_api_key: str = os.getenv("TTS_API_KEY", "")
    tts_provider: str = (os.getenv("TTS_PROVIDER") or "edge").lower()
    tts_voice: str = os.getenv("TTS_VOICE", "bn-BD-NabanitaNeural")
    explain_with_llm: bool = os.getenv("EXPLAIN_WITH_LLM", "false").lower() in {
        "1",
        "true",
        "yes",
    }

settings = Settings()