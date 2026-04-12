"""Server assembly and logging setup."""

from __future__ import annotations

import logging
from pythonjsonlogger.json import JsonFormatter
from mcp.server.fastmcp import FastMCP

from omni_mcp.config import get_settings
from omni_mcp.security import SecurityPolicy
from omni_mcp.skills import register_builtin_skills


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

    server = FastMCP(
        name="omni-mcp",
        instructions=(
            "General-purpose MCP server with secure-by-default built-in skills. "
            "Designed for local execution first, then container and Kubernetes deployment."
        ),
    )
    register_builtin_skills(server=server, settings=settings, policy=SecurityPolicy(settings))
    return server
