"""Configuration and validated runtime settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="OMNI_MCP_", case_sensitive=False)

    environment: str = Field(default="development", description="Runtime environment name.")
    log_level: str = Field(default="INFO", description="Python log level.")

    # MCP capabilities and safety limits
    max_http_response_bytes: int = Field(default=500_000, ge=1_000, le=5_000_000)
    outbound_http_timeout_seconds: float = Field(default=8.0, ge=0.5, le=30.0)
    allowed_outbound_hosts: list[str] = Field(default_factory=list)

    # Core service dependencies
    database_url: str = Field(
        default="postgresql+psycopg://omni_mcp:omni_mcp@localhost:5432/omni_mcp",
        description="SQLAlchemy database URL. PostgreSQL is recommended.",
    )
    auto_create_schema: bool = True

    # OpenAI integration (Phase 1 target provider for summaries)
    openai_api_key: str | None = None
    openai_model: str = Field(default="gpt-4.1-mini")

    # Tenant policy bounds from your use case
    min_poll_interval_hours: int = Field(default=2, ge=1, le=24)
    max_poll_interval_hours: int = Field(default=24, ge=2, le=168)
    min_retention_days: int = Field(default=7, ge=1, le=365)
    max_retention_days: int = Field(default=30, ge=1, le=365)

    # Skill toggles
    enable_http_skill: bool = True
    enable_file_read_skill: bool = True
    enable_time_skill: bool = True
    enable_json_skill: bool = True
    enable_rss_digest_skills: bool = True

    # Client/server integration contract
    client_auth_shared_secret: str | None = None
    slack_signing_secret: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings object for the process lifetime."""

    return Settings()
