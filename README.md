# omni-mcp

Security-focused, general-purpose Python MCP hub.

## Built-in MCP tools

- `core.ping`
- `core.server_info`
- `time.now`
- `json.pretty`
- `http.fetch_text`
- `files.read_text`

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

## Docker

```bash
docker build -t omni-mcp:local .
docker run --rm -p 8080:8080 --env-file .env omni-mcp:local
```

Default container command uses `streamable-http` on port `8080`.

## Helm Charts

Helm chart is managed in a separate repository:
`/Users/sipp/dev/github.com/cloudsteak/helm-charts`

## Documentation

- English architecture/security/client docs: `docs/`
- Hungarian docs: [docs/README.hu.md](docs/README.hu.md)
