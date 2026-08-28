"""NER-LDI Application Settings. No database configuration required."""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────────────────
    APP_ENV: str = Field(default="development")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")

    # ── API ──────────────────────────────────────────────────────
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_PREFIX: str = Field(default="/api/v1")

    # ── Security ────────────────────────────────────────────────
    JWT_SECRET: str = Field(default="ner_ldi_dev_secret_key_change_in_production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=1440)

    # ── CORS ────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    # ── Groq (LLM) ─────────────────────────────────────────────
    GROQ_API_KEY: str = Field(default="")
    GROQ_LLM_MODEL: str = Field(default="qwen/qwen3.8-27b")

    # ── ML ──────────────────────────────────────────────────────
    ML_MODEL_PATH: str = Field(default="ml/artifacts")
    SIMULATION_MODE: bool = Field(default=True)

    # ── NER Region ──────────────────────────────────────────────
    NER_BBOX_MIN_LON: float = Field(default=88.0)
    NER_BBOX_MIN_LAT: float = Field(default=21.9)
    NER_BBOX_MAX_LON: float = Field(default=97.4)
    NER_BBOX_MAX_LAT: float = Field(default=29.5)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
