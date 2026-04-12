# omni-mcp

Security-focused, general-purpose Python MCP server scaffold.

This repository currently implements **Phase 1** (local server), and includes deployment-ready assets for **Phase 3** (Docker) and **Phase 4** (Kubernetes/Helm).  
Phase 2 client integration is prepared via an interface contract and will be implemented in:
`/Users/sipp/dev/github.com/cloudsteak/omni-studio`

## Features

- MCP server with tools, resources, and prompts
- Built-in skills (toggleable by environment variables):
  - `core.ping`
  - `core.server_info`
  - `time.now`
  - `json.pretty`
  - `http.fetch_text` (HTTPS + allowlist + response limits)
  - `files.read_text` (safe relative-path reads only)
- Structured JSON logging
- Secure defaults:
  - HTTPS-only outbound fetches
  - Optional host allowlist
  - Size/time limits for network responses
  - Non-root container user
  - Read-only root filesystem in Helm defaults

## Quick Start (Phase 1: Local)

1. Install dependencies:

```bash
pip install -e .
```

2. Optional config:

```bash
cp .env.example .env
```

3. Run locally over stdio:

```bash
omni-mcp --transport stdio
```

## Docker (Phase 3)

```bash
docker build -t omni-mcp:local .
docker run --rm -p 8080:8080 omni-mcp:local
```

Default container command uses `streamable-http` on port `8080`.

## Kubernetes + Helm (Phase 4)

Chart location in this repo:
`deploy/helm/omni-mcp`

Install example:

```bash
helm upgrade --install omni-mcp ./deploy/helm/omni-mcp
```

Target chart repo for later migration:
`/Users/sipp/dev/github.com/cloudsteak/helm-charts`

## Environment Variables

See `.env.example`.

Key variables:
- `OMNI_MCP_ALLOWED_OUTBOUND_HOSTS` (JSON list)
- `OMNI_MCP_CLIENT_AUTH_SHARED_SECRET`
- `OMNI_MCP_SLACK_SIGNING_SECRET`
- `OMNI_MCP_ENABLE_*` skill toggles

## Documentation

- English architecture/security/client docs: `docs/`
- Hungarian docs: [docs/README.hu.md](docs/README.hu.md)
