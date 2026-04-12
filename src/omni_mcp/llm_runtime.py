"""General LLM runtime for omni-mcp built-in skills."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import boto3
import httpx
from botocore.exceptions import BotoCoreError, ClientError

from omni_mcp.config import Settings
from omni_mcp.security import SecurityPolicy


class LlmRuntime:
    """Provider-agnostic runtime wrapper for text generation tools."""

    def __init__(self, settings: Settings, policy: SecurityPolicy) -> None:
        self._settings = settings
        self._policy = policy

    def runtime_info(self) -> dict[str, object]:
        """Return non-sensitive runtime metadata."""

        provider = self._provider()
        info: dict[str, object] = {
            "provider": provider,
            "default_temperature": self._settings.llm_temperature,
            "default_max_output_tokens": self._settings.llm_max_output_tokens,
        }

        if provider == "openai":
            info.update(
                {
                    "default_model": self._settings.llm_model,
                    "base_url": self._settings.llm_openai_base_url,
                    "has_credentials": bool(self._settings.llm_openai_api_key),
                }
            )
        elif provider == "anthropic":
            info.update(
                {
                    "default_model": self._settings.llm_model,
                    "base_url": self._settings.llm_anthropic_base_url,
                    "anthropic_version": self._settings.llm_anthropic_version,
                    "has_credentials": bool(self._settings.llm_anthropic_api_key),
                }
            )
        elif provider == "azure_foundry":
            info.update(
                {
                    "deployment": self._settings.llm_azure_foundry_deployment,
                    "endpoint": self._settings.llm_azure_foundry_endpoint,
                    "api_version": self._settings.llm_azure_foundry_api_version,
                    "has_credentials": bool(self._settings.llm_azure_foundry_api_key),
                }
            )
        elif provider == "vertex":
            info.update(
                {
                    "project_id": self._settings.llm_vertex_project_id,
                    "location": self._settings.llm_vertex_location,
                    "default_model": self._settings.llm_vertex_model,
                    "has_bearer_token": bool(self._settings.llm_vertex_bearer_token),
                    "has_service_account_file": bool(self._settings.llm_vertex_service_account_file),
                }
            )
        elif provider == "bedrock":
            info.update(
                {
                    "region": self._settings.llm_bedrock_region,
                    "model_id": self._settings.llm_bedrock_model_id,
                    "credentials_mode": "aws-default-credential-chain",
                }
            )

        return info

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, object]:
        """Generate text using configured LLM provider and runtime defaults."""

        provider = self._provider()
        resolved_temperature = (
            temperature if temperature is not None else self._settings.llm_temperature
        )
        resolved_max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else self._settings.llm_max_output_tokens
        )

        if resolved_temperature < 0 or resolved_temperature > 2:
            raise ValueError("temperature must be between 0 and 2.")
        if resolved_max_output_tokens < 1:
            raise ValueError("max_output_tokens must be greater than 0.")

        if provider == "openai":
            resolved_model = (model or self._settings.llm_model).strip()
            output = self._generate_openai(
                prompt=prompt,
                system_prompt=system_prompt,
                model=resolved_model,
                temperature=resolved_temperature,
                max_output_tokens=resolved_max_output_tokens,
            )
        elif provider == "anthropic":
            resolved_model = (model or self._settings.llm_model).strip()
            output = self._generate_anthropic(
                prompt=prompt,
                system_prompt=system_prompt,
                model=resolved_model,
                temperature=resolved_temperature,
                max_output_tokens=resolved_max_output_tokens,
            )
        elif provider == "azure_foundry":
            output = self._generate_azure_foundry(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=resolved_temperature,
                max_output_tokens=resolved_max_output_tokens,
            )
            resolved_model = self._settings.llm_azure_foundry_deployment or ""
        elif provider == "vertex":
            resolved_model = (model or self._settings.llm_vertex_model).strip()
            output = self._generate_vertex(
                prompt=prompt,
                system_prompt=system_prompt,
                model=resolved_model,
                temperature=resolved_temperature,
                max_output_tokens=resolved_max_output_tokens,
            )
        elif provider == "bedrock":
            resolved_model = (model or self._settings.llm_bedrock_model_id or "").strip()
            output = self._generate_bedrock(
                prompt=prompt,
                system_prompt=system_prompt,
                model_id=resolved_model,
                temperature=resolved_temperature,
                max_output_tokens=resolved_max_output_tokens,
            )
        else:
            raise ValueError(
                "Unsupported provider. Supported providers: openai, anthropic, "
                "azure_foundry, vertex, bedrock."
            )

        return {
            "provider": provider,
            "model": resolved_model,
            "output_text": output["output_text"],
            "usage": output.get("usage", {}),
        }

    def _provider(self) -> str:
        provider = self._settings.llm_provider.strip().lower()
        allowed = {"openai", "anthropic", "azure_foundry", "vertex", "bedrock"}
        if provider not in allowed:
            raise ValueError(
                "Unsupported provider. Supported providers: openai, anthropic, "
                "azure_foundry, vertex, bedrock."
            )
        return provider

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: str | None,
        model: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict[str, object]:
        api_key = (self._settings.llm_openai_api_key or "").strip()
        if not api_key:
            raise ValueError("OMNI_MCP_LLM_OPENAI_API_KEY is required for provider=openai.")
        if not model:
            raise ValueError("llm_model cannot be empty for provider=openai.")

        self._policy.validate_outbound_url(self._settings.llm_openai_base_url)

        input_messages: list[dict[str, Any]] = []
        if system_prompt and system_prompt.strip():
            input_messages.append({"role": "system", "content": system_prompt.strip()})
        input_messages.append({"role": "user", "content": prompt})

        with httpx.Client(timeout=self._settings.llm_timeout_seconds) as client:
            response = client.post(
                self._settings.llm_openai_base_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "input": input_messages,
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                },
            )
            response.raise_for_status()
            payload = response.json()

        return {
            "output_text": self._extract_openai_output_text(payload),
            "usage": payload.get("usage", {}),
        }

    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: str | None,
        model: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict[str, object]:
        api_key = (self._settings.llm_anthropic_api_key or "").strip()
        if not api_key:
            raise ValueError("OMNI_MCP_LLM_ANTHROPIC_API_KEY is required for provider=anthropic.")
        if not model:
            raise ValueError("llm_model cannot be empty for provider=anthropic.")

        self._policy.validate_outbound_url(self._settings.llm_anthropic_base_url)

        body: dict[str, Any] = {
            "model": model,
            "max_tokens": max_output_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt and system_prompt.strip():
            body["system"] = system_prompt.strip()

        with httpx.Client(timeout=self._settings.llm_timeout_seconds) as client:
            response = client.post(
                self._settings.llm_anthropic_base_url,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": self._settings.llm_anthropic_version,
                    "content-type": "application/json",
                },
                json=body,
            )
            response.raise_for_status()
            payload = response.json()

        chunks: list[str] = []
        for item in payload.get("content", []):
            if item.get("type") == "text" and item.get("text"):
                chunks.append(str(item["text"]))
        output_text = "\n".join(chunks).strip()
        if not output_text:
            raise ValueError("Anthropic response did not include textual output.")

        return {"output_text": output_text, "usage": payload.get("usage", {})}

    def _generate_azure_foundry(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_output_tokens: int,
    ) -> dict[str, object]:
        endpoint = (self._settings.llm_azure_foundry_endpoint or "").strip().rstrip("/")
        deployment = (self._settings.llm_azure_foundry_deployment or "").strip()
        api_key = (self._settings.llm_azure_foundry_api_key or "").strip()

        if not endpoint or not deployment:
            raise ValueError(
                "OMNI_MCP_LLM_AZURE_FOUNDRY_ENDPOINT and OMNI_MCP_LLM_AZURE_FOUNDRY_DEPLOYMENT are required."
            )
        if not api_key:
            raise ValueError("OMNI_MCP_LLM_AZURE_FOUNDRY_API_KEY is required for provider=azure_foundry.")

        url = (
            f"{endpoint}/openai/deployments/{deployment}/chat/completions"
            f"?api-version={self._settings.llm_azure_foundry_api_version}"
        )
        self._policy.validate_outbound_url(url)

        messages: list[dict[str, str]] = []
        if system_prompt and system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt.strip()})
        messages.append({"role": "user", "content": prompt})

        with httpx.Client(timeout=self._settings.llm_timeout_seconds) as client:
            response = client.post(
                url,
                headers={"api-key": api_key, "Content-Type": "application/json"},
                json={
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_output_tokens,
                },
            )
            response.raise_for_status()
            payload = response.json()

        try:
            output_text = str(payload["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("Azure Foundry response did not include textual output.") from exc

        usage = payload.get("usage", {})
        return {"output_text": output_text, "usage": usage}

    def _generate_vertex(
        self,
        prompt: str,
        system_prompt: str | None,
        model: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict[str, object]:
        project_id = (self._settings.llm_vertex_project_id or "").strip()
        location = self._settings.llm_vertex_location.strip()
        if not project_id:
            raise ValueError("OMNI_MCP_LLM_VERTEX_PROJECT_ID is required for provider=vertex.")
        if not model:
            raise ValueError("Vertex model cannot be empty.")

        token = self._get_vertex_bearer_token()

        url = (
            f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}"
            f"/locations/{location}/publishers/google/models/{model}:generateContent"
        )
        self._policy.validate_outbound_url(url)

        parts: list[dict[str, str]] = []
        if system_prompt and system_prompt.strip():
            parts.append({"text": f"System instruction: {system_prompt.strip()}"})
        parts.append({"text": prompt})

        with httpx.Client(timeout=self._settings.llm_timeout_seconds) as client:
            response = client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "contents": [{"role": "user", "parts": parts}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_output_tokens,
                    },
                },
            )
            response.raise_for_status()
            payload = response.json()

        candidates = payload.get("candidates", [])
        if not candidates:
            raise ValueError("Vertex response did not include candidates.")

        content_parts = candidates[0].get("content", {}).get("parts", [])
        chunks = [str(part.get("text", "")).strip() for part in content_parts if part.get("text")]
        output_text = "\n".join([chunk for chunk in chunks if chunk]).strip()
        if not output_text:
            raise ValueError("Vertex response did not include textual output.")

        usage = payload.get("usageMetadata", {})
        return {"output_text": output_text, "usage": usage}

    def _generate_bedrock(
        self,
        prompt: str,
        system_prompt: str | None,
        model_id: str,
        temperature: float,
        max_output_tokens: int,
    ) -> dict[str, object]:
        region = (self._settings.llm_bedrock_region or "").strip()
        if not region:
            raise ValueError("OMNI_MCP_LLM_BEDROCK_REGION is required for provider=bedrock.")
        if not model_id:
            raise ValueError("OMNI_MCP_LLM_BEDROCK_MODEL_ID is required for provider=bedrock.")

        client = boto3.client("bedrock-runtime", region_name=region)

        request_body: dict[str, Any] = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {
                "temperature": temperature,
                "maxTokens": max_output_tokens,
            },
        }
        if system_prompt and system_prompt.strip():
            request_body["system"] = [{"text": system_prompt.strip()}]

        try:
            response = client.converse(modelId=model_id, **request_body)
        except (BotoCoreError, ClientError) as exc:
            raise ValueError(f"Bedrock request failed: {exc}") from exc

        content = response.get("output", {}).get("message", {}).get("content", [])
        chunks = [str(item.get("text", "")).strip() for item in content if item.get("text")]
        output_text = "\n".join([chunk for chunk in chunks if chunk]).strip()
        if not output_text:
            raise ValueError("Bedrock response did not include textual output.")

        usage = response.get("usage", {})
        return {"output_text": output_text, "usage": usage}

    def _get_vertex_bearer_token(self) -> str:
        """Get Vertex bearer token from explicit token or service account file."""

        explicit = (self._settings.llm_vertex_bearer_token or "").strip()
        if explicit:
            return explicit

        service_account_file = (self._settings.llm_vertex_service_account_file or "").strip()
        if not service_account_file:
            raise ValueError(
                "Set OMNI_MCP_LLM_VERTEX_BEARER_TOKEN or OMNI_MCP_LLM_VERTEX_SERVICE_ACCOUNT_FILE for provider=vertex."
            )

        path = Path(service_account_file)
        if not path.exists():
            raise ValueError(f"Vertex service account file does not exist: {service_account_file}")

        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
        except ImportError as exc:
            raise ValueError(
                "Vertex authentication dependencies are missing. Install google-auth and requests."
            ) from exc

        credentials = service_account.Credentials.from_service_account_file(
            str(path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        credentials.refresh(Request())
        if not credentials.token:
            raise ValueError("Failed to obtain Vertex bearer token from service account.")
        return credentials.token

    @staticmethod
    def _extract_openai_output_text(payload: dict[str, Any]) -> str:
        """Extract normalized output text from OpenAI responses payload."""

        output_text = str(payload.get("output_text", "")).strip()
        if output_text:
            return output_text

        chunks: list[str] = []
        for output in payload.get("output", []):
            for content in output.get("content", []):
                text = content.get("text")
                if text:
                    chunks.append(str(text))

        merged = "\n".join(chunks).strip()
        if not merged:
            raise ValueError("OpenAI response did not include textual output.")
        return merged
