"""Core settings via pydantic-settings."""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=False, extra="ignore",
    )

    APP_NAME: str = "AI Customer Support OpenEnv"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_KEY: str = "changeme-dev-key-only-32chars!!"
    ALLOWED_ORIGINS: List[str] = ["*"]

    GEMINI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 1024
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    DATABASE_URL: str = "sqlite+aiosqlite:///./support_env.db"
    REDIS_URL: Optional[str] = None

    FAISS_INDEX_PATH: str = "./faiss_index"
    FAISS_TOP_K: int = 5

    MAX_STEPS_PER_EPISODE: int = 20
    SESSION_TTL_SECONDS: int = 3600

    REWARD_RESOLUTION: float = 1.0
    REWARD_PARTIAL: float = 0.3
    REWARD_ESCALATION: float = 0.1
    REWARD_FAILURE: float = -0.5
    REWARD_STEP_PENALTY: float = -0.05

    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
