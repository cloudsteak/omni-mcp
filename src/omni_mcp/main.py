"""Entry point for omni-mcp."""

from __future__ import annotations

import argparse

from omni_mcp.config import get_settings
from omni_mcp.server import create_server
from omni_mcp.storage import initialize_schema


def main() -> None:
    """Run the MCP server with the selected transport."""

    parser = argparse.ArgumentParser(description="Run omni-mcp server")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "streamable-http", "sse"],
        help="MCP transport. Use stdio for local development.",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for network transports.")
    parser.add_argument("--port", type=int, default=8080, help="Port for network transports.")
    parser.add_argument(
        "--init-db-only",
        action="store_true",
        help="Initialize database schema and exit.",
    )
    args = parser.parse_args()

    settings = get_settings()
    if args.init_db_only:
        initialize_schema(settings.database_url)
        return

    server = create_server()

    # Keep compatibility with FastMCP versions that only support `run()` or support
    # extended transport parameters in newer releases.
    try:
        server.run(transport=args.transport, host=args.host, port=args.port)
    except TypeError:
        if args.transport != "stdio":
            raise RuntimeError(
                "Installed FastMCP version supports stdio only. Upgrade mcp package for HTTP/SSE."
            )
        server.run()


if __name__ == "__main__":
    main()
