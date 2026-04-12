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

    # Skill toggles
    enable_http_skill: bool = True
    enable_file_read_skill: bool = True
    enable_time_skill: bool = True
    enable_json_skill: bool = True

    # Future client integration contract
    client_auth_shared_secret: str | None = None
    slack_signing_secret: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings object for the process lifetime."""

    return Settings()
