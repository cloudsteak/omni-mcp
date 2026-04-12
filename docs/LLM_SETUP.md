# LLM Setup

This document explains how to configure the built-in `llm.generate` tool in `omni-mcp`.

## Supported providers

- OpenAI API
- Anthropic API
- Azure Foundry Deployment
- Google Vertex API
- AWS Bedrock API

Set the active provider with:

```env
OMNI_MCP_LLM_PROVIDER=<openai|anthropic|azure_foundry|vertex|bedrock>
```

## Common runtime settings

These are shared across providers:

```env
OMNI_MCP_LLM_MODEL=
OMNI_MCP_LLM_TEMPERATURE=0.2
OMNI_MCP_LLM_MAX_OUTPUT_TOKENS=800
OMNI_MCP_LLM_TIMEOUT_SECONDS=30
OMNI_MCP_ENABLE_LLM_SKILL=true
```

## Provider-specific configuration

### OpenAI API

```env
OMNI_MCP_LLM_PROVIDER=openai
OMNI_MCP_LLM_MODEL=gpt-4.1-mini
OMNI_MCP_LLM_OPENAI_API_KEY=<OPENAI_KEY>
OMNI_MCP_LLM_OPENAI_BASE_URL=https://api.openai.com/v1/responses
```

### Anthropic API

```env
OMNI_MCP_LLM_PROVIDER=anthropic
OMNI_MCP_LLM_MODEL=claude-3-7-sonnet-latest
OMNI_MCP_LLM_ANTHROPIC_API_KEY=<ANTHROPIC_KEY>
OMNI_MCP_LLM_ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/messages
OMNI_MCP_LLM_ANTHROPIC_VERSION=2023-06-01
```

### Azure Foundry Deployment

```env
OMNI_MCP_LLM_PROVIDER=azure_foundry
OMNI_MCP_LLM_AZURE_FOUNDRY_API_KEY=<AZURE_KEY>
OMNI_MCP_LLM_AZURE_FOUNDRY_ENDPOINT=https://<resource>.openai.azure.com
OMNI_MCP_LLM_AZURE_FOUNDRY_DEPLOYMENT=<deployment_name>
OMNI_MCP_LLM_AZURE_FOUNDRY_API_VERSION=2024-10-21
```

### Google Vertex API

```env
OMNI_MCP_LLM_PROVIDER=vertex
OMNI_MCP_LLM_VERTEX_PROJECT_ID=<GCP_PROJECT_ID>
OMNI_MCP_LLM_VERTEX_LOCATION=us-central1
OMNI_MCP_LLM_VERTEX_MODEL=gemini-1.5-pro
# Option A:
OMNI_MCP_LLM_VERTEX_SERVICE_ACCOUNT_FILE=/abs/path/service-account.json
# Option B:
OMNI_MCP_LLM_VERTEX_BEARER_TOKEN=<TOKEN>
```

### AWS Bedrock API

```env
OMNI_MCP_LLM_PROVIDER=bedrock
OMNI_MCP_LLM_BEDROCK_REGION=us-east-1
OMNI_MCP_LLM_BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

AWS credentials are resolved via the default AWS credential chain.

## Outbound host allowlist

If you use `OMNI_MCP_ALLOWED_OUTBOUND_HOSTS`, include the selected provider host.

Examples:
- `api.openai.com`
- `api.anthropic.com`
- `<region>-aiplatform.googleapis.com`
- `<resource>.openai.azure.com`

## Run locally

```bash
uv sync --extra dev
cp .env.example .env
uv run omni-mcp --transport stdio
```
