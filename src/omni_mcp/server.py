"""Server assembly and logging setup."""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP
from pythonjsonlogger.json import JsonFormatter

from omni_mcp.config import get_settings
from omni_mcp.rss_digest import RssDigestService
from omni_mcp.security import SecurityPolicy
from omni_mcp.skills import register_builtin_skills, register_rss_digest_skills
from omni_mcp.storage import initialize_schema


def _configure_logging(level: str) -> None:
    """Configure structured JSON logs suitable for containers and SIEM ingestion."""

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


def create_server() -> FastMCP:
    """Create and return a fully configured FastMCP server instance."""

    settings = get_settings()
    _configure_logging(settings.log_level)

    if settings.auto_create_schema:
        initialize_schema(settings.database_url)

    policy = SecurityPolicy(settings)
    rss_digest_service = RssDigestService(settings=settings, policy=policy)

    server = FastMCP(
        name="omni-mcp",
        instructions=(
            "General-purpose MCP server with secure-by-default built-in skills. "
            "This instance is pre-configured for RSS polling and category digest workflows."
        ),
    )
    register_builtin_skills(server=server, settings=settings, policy=policy)
    register_rss_digest_skills(server=server, settings=settings, service=rss_digest_service)
    return server
