"""
NER-SAGE Application Settings
Loaded from environment variables via pydantic-settings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────────────────
    APP_ENV: str = Field(default="development", description="Environment name")
    APP_NAME: str = Field(default="ner-sage", description="Application name")
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Log level")

    # ── API ──────────────────────────────────────────────────────
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_PREFIX: str = Field(default="/api/v1")

    # ── Security ────────────────────────────────────────────────
    JWT_SECRET: str = Field(default="CHANGE_ME_insecure_default", min_length=16)
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=1440)

    # ── CORS ────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    # ── MongoDB ─────────────────────────────────────────────────
    MONGODB_URI: str = Field(
        default="mongodb://nersage:nersage_pass@localhost:27017/ner_sage?authSource=ner_sage"
    )
    MONGODB_DATABASE: str = Field(default="ner_sage")

    # ── Neo4j ───────────────────────────────────────────────────
    NEO4J_URI: str = Field(default="bolt://localhost:7687")
    NEO4J_USERNAME: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(default="nersage_neo4j_pass")
    NEO4J_DATABASE: str = Field(default="neo4j")

    # ── Redis ───────────────────────────────────────────────────
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_DEFAULT_TTL: int = Field(default=3600, description="Default cache TTL in seconds")

    # ── Qdrant ──────────────────────────────────────────────────
    QDRANT_LOCATION: str = Field(default=":memory:")
    QDRANT_API_KEY: str = Field(default="")
    QDRANT_COLLECTION_DOCUMENTS: str = Field(default="ner_sage_documents")
    QDRANT_COLLECTION_EVIDENCE: str = Field(default="ner_sage_evidence")

    # ── Groq (LLM / RAG) ────────────────────────────────────────
    GROQ_API_KEY: str = Field(default="")
    GROQ_LLM_MODEL: str = Field(default="llama-3.3-70b-versatile")
    GROQ_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")

    # ── ML Configuration ────────────────────────────────────────
    ML_MODEL_PATH: str = Field(default="ml/artifacts")
    ML_DEFAULT_MODEL: str = Field(default="xgb_v1")
    ML_CONFIDENCE_THRESHOLD: float = Field(default=0.70)
    ML_HIGH_RISK_THRESHOLD: float = Field(default=0.75)
    ML_MEDIUM_RISK_THRESHOLD: float = Field(default=0.50)

    # ── Simulation ──────────────────────────────────────────────
    SIMULATION_MODE: bool = Field(default=True)

    # ── NER Region Bounding Box ──────────────────────────────────
    NER_BBOX_MIN_LON: float = Field(default=88.0)
    NER_BBOX_MIN_LAT: float = Field(default=21.9)
    NER_BBOX_MAX_LON: float = Field(default=97.4)
    NER_BBOX_MAX_LAT: float = Field(default=29.5)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
