import pytest

from omni_mcp.config import Settings
from omni_mcp.llm_runtime import LlmRuntime
from omni_mcp.security import SecurityPolicy


def test_provider_validation_rejects_unknown() -> None:
    settings = Settings(llm_provider="unknown")
    runtime = LlmRuntime(settings=settings, policy=SecurityPolicy(settings))

    with pytest.raises(ValueError, match="Unsupported provider"):
        runtime.runtime_info()


def test_openai_requires_api_key() -> None:
    settings = Settings(llm_provider="openai", llm_openai_api_key=None)
    runtime = LlmRuntime(settings=settings, policy=SecurityPolicy(settings))

    with pytest.raises(ValueError, match="OMNI_MCP_LLM_OPENAI_API_KEY"):
        runtime.generate(prompt="Hello")


def test_anthropic_requires_api_key() -> None:
    settings = Settings(llm_provider="anthropic", llm_anthropic_api_key=None)
    runtime = LlmRuntime(settings=settings, policy=SecurityPolicy(settings))

    with pytest.raises(ValueError, match="OMNI_MCP_LLM_ANTHROPIC_API_KEY"):
        runtime.generate(prompt="Hello")


def test_azure_requires_endpoint_and_deployment() -> None:
    settings = Settings(
        llm_provider="azure_foundry",
        llm_azure_foundry_api_key="x",
        llm_azure_foundry_endpoint=None,
        llm_azure_foundry_deployment=None,
    )
    runtime = LlmRuntime(settings=settings, policy=SecurityPolicy(settings))

    with pytest.raises(ValueError, match="OMNI_MCP_LLM_AZURE_FOUNDRY_ENDPOINT"):
        runtime.generate(prompt="Hello")


def test_vertex_requires_project() -> None:
    settings = Settings(
        llm_provider="vertex",
        llm_vertex_project_id=None,
        llm_vertex_bearer_token="token",
    )
    runtime = LlmRuntime(settings=settings, policy=SecurityPolicy(settings))

    with pytest.raises(ValueError, match="OMNI_MCP_LLM_VERTEX_PROJECT_ID"):
        runtime.generate(prompt="Hello")


def test_bedrock_requires_region() -> None:
    settings = Settings(llm_provider="bedrock", llm_bedrock_region=None, llm_bedrock_model_id="m")
    runtime = LlmRuntime(settings=settings, policy=SecurityPolicy(settings))

    with pytest.raises(ValueError, match="OMNI_MCP_LLM_BEDROCK_REGION"):
        runtime.generate(prompt="Hello")


def test_extract_openai_output_text_prefers_output_text_field() -> None:
    payload = {"output_text": "  result text  "}
    assert LlmRuntime._extract_openai_output_text(payload) == "result text"


def test_extract_openai_output_text_fallback_parsing() -> None:
    payload = {
        "output": [
            {
                "content": [
                    {"text": "First line"},
                    {"text": "Second line"},
                ]
            }
        ]
    }
    assert LlmRuntime._extract_openai_output_text(payload) == "First line\nSecond line"
