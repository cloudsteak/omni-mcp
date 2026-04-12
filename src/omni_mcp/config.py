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

    # MCP safety limits for built-in generic tools
    max_http_response_bytes: int = Field(default=500_000, ge=1_000, le=5_000_000)
    outbound_http_timeout_seconds: float = Field(default=8.0, ge=0.5, le=30.0)
    allowed_outbound_hosts: list[str] = Field(default_factory=list)

    # General LLM runtime defaults for standalone MCP usage
    llm_provider: str = Field(default="openai")
    llm_model: str = Field(default="gpt-4.1-mini")
    llm_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    llm_max_output_tokens: int = Field(default=800, ge=1, le=32_768)
    llm_timeout_seconds: float = Field(default=30.0, ge=1.0, le=120.0)

    # OpenAI API
    llm_openai_api_key: str | None = None
    llm_openai_base_url: str = Field(default="https://api.openai.com/v1/responses")

    # Anthropic API
    llm_anthropic_api_key: str | None = None
    llm_anthropic_base_url: str = Field(default="https://api.anthropic.com/v1/messages")
    llm_anthropic_version: str = Field(default="2023-06-01")

    # Azure Foundry / Azure OpenAI deployment-style endpoint
    llm_azure_foundry_api_key: str | None = None
    llm_azure_foundry_endpoint: str | None = None
    llm_azure_foundry_deployment: str | None = None
    llm_azure_foundry_api_version: str = Field(default="2024-10-21")

    # Google Vertex AI
    llm_vertex_project_id: str | None = None
    llm_vertex_location: str = Field(default="us-central1")
    llm_vertex_model: str = Field(default="gemini-1.5-pro")
    llm_vertex_service_account_file: str | None = None
    llm_vertex_bearer_token: str | None = None

    # AWS Bedrock
    llm_bedrock_region: str | None = None
    llm_bedrock_model_id: str | None = None

    # Built-in skill toggles
    enable_http_skill: bool = True
    enable_file_read_skill: bool = True
    enable_time_skill: bool = True
    enable_json_skill: bool = True
    enable_llm_skill: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings object for the process lifetime."""

    return Settings()
