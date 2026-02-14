"""Application configuration via Pydantic Settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from environment / .env file."""

    # ── Database ──────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://ecoplanta:ecoplanta@localhost:5432/ecoplanta"

    # ── Redis ─────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Auth / JWT ────────────────────────────────────────────────────
    AUTH_SECRET_KEY: str = "ecoplanta-dev-secret-change-in-production"
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Deterministic seed ────────────────────────────────────────────
    SEED: int = 42

    # ── Server ────────────────────────────────────────────────────────
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    # ── Observability ─────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ── Dev mode (auto-auth, seed data on startup) ────────────────────
    DEV_MODE: bool = True

    # ── App meta ──────────────────────────────────────────────────────
    APP_VERSION: str = "0.1.0"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
