"""Environment-driven configuration. Never hardcode secrets."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    # App
    environment: Literal["development", "staging", "production"] = "development"
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    # AI provider
    ai_provider: Literal["claude", "openai", "mock"] = "mock"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    model_strong: str = "claude-sonnet-5"
    model_cheap: str = "claude-haiku-4-5-20251001"
    embedding_model: str = "text-embedding-3-small"

    # Data
    database_url: str = ""  # postgres; empty => in-memory dev store
    redis_url: str = ""     # empty => run pipeline inline (dev)

    # Jobs
    jobs_inline: bool = False  # True => run pipeline jobs synchronously (tests)

    # Supabase (auth + storage)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""

    # Stripe (billing)
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    frontend_url: str = "http://localhost:3000"

    # Limits / cost control
    max_video_duration_seconds: int = 3600
    max_upload_mb: int = 500
    free_plan_credits: int = 5
    default_transcript_language: str = "en"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def use_mock_ai(self) -> bool:
        if self.ai_provider == "mock":
            return True
        if self.ai_provider == "claude" and not self.anthropic_api_key:
            return True
        if self.ai_provider == "openai" and not self.openai_api_key:
            return True
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()
