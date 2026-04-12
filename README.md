# omni-mcp

Security-focused, general-purpose Python MCP server scaffold.

## Built-in MCP tools

Core:
- `core.ping`
- `core.server_info`
- `time.now`
- `json.pretty`
- `http.fetch_text`
- `files.read_text`

Extended:
- `tenant.upsert_preferences`
- `rss.add_feed`
- `rss.list_feeds`
- `rss.poll`
- `rss.list_recent_items`
- `digest.generate_category_summary`
- `digest.list_history`

## Quick Start (Local)

1. Install dependencies:

```bash
uv sync --extra dev
```

2. Configure environment:

```bash
cp .env.example .env
```

3. Initialize database schema:

```bash
uv run omni-mcp --init-db-only
```

4. Run locally over stdio:

```bash
uv run omni-mcp --transport stdio
```

## Docker

```bash
docker build -t omni-mcp:local .
docker run --rm -p 8080:8080 --env-file .env omni-mcp:local
```

Default container command uses `streamable-http` on port `8080`.

## Kubernetes + Helm

Chart location in this repo:
`deploy/helm/omni-mcp`

Install example:

```bash
helm upgrade --install omni-mcp ./deploy/helm/omni-mcp
```

Target chart repo:
`/Users/sipp/dev/github.com/cloudsteak/helm-charts`

## Repo responsibilities

- `omni-mcp`: MCP server + standard skills/agents
- `omni-studio`: frontend + application backend
- `helm-charts`: Helm charts

## Documentation

- English architecture/security/client docs: `docs/`
- Hungarian docs: [docs/README.hu.md](docs/README.hu.md)
