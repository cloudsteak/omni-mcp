"""Built-in skills for the omni-mcp server."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

from omni_mcp.config import Settings
from omni_mcp.security import SecurityPolicy


def register_builtin_skills(server: FastMCP, settings: Settings, policy: SecurityPolicy) -> None:
    """Register all default MCP tools, resources, and prompts."""

    @server.tool(
        name="core.ping",
        description="Liveness test tool. Returns pong with UTC timestamp.",
    )
    def ping() -> dict[str, str]:
        return {
            "status": "pong",
            "server": "omni-mcp",
            "timestamp_utc": datetime.now(UTC).isoformat(),
        }

    @server.tool(
        name="core.server_info",
        description="Returns non-sensitive runtime metadata and enabled skills.",
    )
    def server_info() -> dict[str, object]:
        return {
            "name": "omni-mcp",
            "environment": settings.environment,
            "enabled_skills": {
                "http": settings.enable_http_skill,
                "file_read": settings.enable_file_read_skill,
                "time": settings.enable_time_skill,
                "json": settings.enable_json_skill,
                "rss_digest": settings.enable_rss_digest_skills,
            },
            "use_case_profiles": ["rss_digest_automation"],
        }

    if settings.enable_time_skill:

        @server.tool(
            name="time.now",
            description="Returns current UTC timestamp and UNIX epoch seconds.",
        )
        def time_now() -> dict[str, object]:
            now = datetime.now(UTC)
            return {
                "utc_iso": now.isoformat(),
                "epoch_seconds": int(now.timestamp()),
            }

    if settings.enable_json_skill:

        @server.tool(
            name="json.pretty",
            description="Validates JSON and returns a normalized pretty-printed version.",
        )
        def json_pretty(raw_json: str) -> dict[str, str]:
            parsed = json.loads(raw_json)
            return {"pretty": json.dumps(parsed, indent=2, sort_keys=True)}

    if settings.enable_http_skill:

        @server.tool(
            name="http.fetch_text",
            description=(
                "Fetches UTF-8 text from an HTTPS URL with strict timeout, optional host allowlist, "
                "and maximum response size limits."
            ),
        )
        def http_fetch_text(url: str) -> dict[str, object]:
            policy.validate_outbound_url(url)
            timeout = settings.outbound_http_timeout_seconds
            with httpx.Client(timeout=timeout, follow_redirects=False) as client:
                response = client.get(url)
                response.raise_for_status()
                content = response.content[: settings.max_http_response_bytes]
                return {
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "body": content.decode("utf-8", errors="replace"),
                    "truncated": len(response.content) > settings.max_http_response_bytes,
                }

    if settings.enable_file_read_skill:

        @server.tool(
            name="files.read_text",
            description=(
                "Reads UTF-8 text from a relative path under the current working directory. "
                "Absolute paths and path traversal are blocked."
            ),
        )
        def files_read_text(path: str) -> dict[str, str]:
            requested = Path(path)
            if requested.is_absolute() or ".." in requested.parts:
                raise ValueError("Only safe relative paths are allowed.")

            resolved = (Path.cwd() / requested).resolve()
            cwd = Path.cwd().resolve()
            if cwd not in resolved.parents and resolved != cwd:
                raise ValueError("Path escapes the current working directory.")

            return {"path": str(requested), "content": resolved.read_text(encoding="utf-8")}

    @server.resource(
        uri="omni://server/capabilities",
        name="Server Capabilities",
        description="Lists currently enabled features exposed by this MCP server.",
        mime_type="application/json",
    )
    def capabilities_resource() -> str:
        return json.dumps(
            {
                "name": "omni-mcp",
                "features": {
                    "tools": True,
                    "resources": True,
                    "prompts": True,
                    "rss_digest_automation": True,
                    "google_oauth_frontend": "planned_in_omni_studio",
                    "slack_client_ingress": "planned_in_omni_studio",
                },
            },
            indent=2,
            sort_keys=True,
        )

    @server.prompt(
        name="prompts.task_breakdown",
        description="Prompt template for turning a goal into an actionable task breakdown.",
    )
    def task_breakdown_prompt(goal: str) -> str:
        return (
            "Break down the following goal into a concise implementation plan with risks, "
            f"test strategy, and delivery steps:\n\nGoal: {goal}"
        )
