# omni-mcp

Security-focused, general-purpose Python MCP hub.

## Built-in MCP tools

- `core.ping`
- `core.server_info`
- `time.now`
- `json.pretty`
- `http.fetch_text`
- `files.read_text`
- `llm.runtime_info`
- `llm.generate`

## Quick Start (Local)

1. Install dependencies:

```bash
uv sync --extra dev
```

2. Configure environment:

```bash
cp .env.example .env
```

3. Run locally over stdio:

```bash
uv run omni-mcp --transport stdio
```

## LLM Provider Configuration (Local MCP Mode)

`omni-mcp` supports these providers in `llm.generate`:
- OpenAI API
- Anthropic API
- Azure Foundry Deployment
- Google Vertex API
- AWS Bedrock API

Set `OMNI_MCP_LLM_PROVIDER` to one of:
- `openai`
- `anthropic`
- `azure_foundry`
- `vertex`
- `bedrock`

### OpenAI

```env
OMNI_MCP_LLM_PROVIDER=openai
OMNI_MCP_LLM_MODEL=gpt-4.1-mini
OMNI_MCP_LLM_OPENAI_API_KEY=<OPENAI_KEY>
OMNI_MCP_LLM_OPENAI_BASE_URL=https://api.openai.com/v1/responses
```

### Anthropic

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

### Google Vertex

```env
OMNI_MCP_LLM_PROVIDER=vertex
OMNI_MCP_LLM_VERTEX_PROJECT_ID=<GCP_PROJECT_ID>
OMNI_MCP_LLM_VERTEX_LOCATION=us-central1
OMNI_MCP_LLM_VERTEX_MODEL=gemini-1.5-pro
# Option A: service account file
OMNI_MCP_LLM_VERTEX_SERVICE_ACCOUNT_FILE=/abs/path/service-account.json
# Option B: pre-generated bearer token
OMNI_MCP_LLM_VERTEX_BEARER_TOKEN=<TOKEN>
```

### AWS Bedrock

```env
OMNI_MCP_LLM_PROVIDER=bedrock
OMNI_MCP_LLM_BEDROCK_REGION=us-east-1
OMNI_MCP_LLM_BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

Notes:
- Bedrock uses standard AWS credential chain (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.).
- If `OMNI_MCP_ALLOWED_OUTBOUND_HOSTS` is set, include provider hosts for HTTP-based providers.
- `llm.generate` supports optional per-call overrides: `model`, `temperature`, `max_output_tokens`.

## Docker

```bash
docker build -t omni-mcp:local .
docker run --rm -p 8080:8080 --env-file .env omni-mcp:local
```

Default container command uses `streamable-http` on port `8080`.

## Helm Charts

Helm chart is managed in a separate repository.

## Documentation

- English architecture/security/client docs: `docs/`
- LLM setup guide: [docs/LLM_SETUP.md](docs/LLM_SETUP.md)
- Hungarian docs: [docs/README.hu.md](docs/README.hu.md)
