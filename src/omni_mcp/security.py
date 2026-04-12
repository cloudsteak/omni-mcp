"""Security helpers used by tools and transports."""

from __future__ import annotations

from urllib.parse import urlparse

from omni_mcp.config import Settings


class SecurityError(ValueError):
    """Raised when a request violates a local security policy."""


class SecurityPolicy:
    """Enforces local policy rules for sensitive operations."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def validate_outbound_url(self, url: str) -> None:
        """Allow only HTTPS and optionally host allowlists for outbound fetches."""

        parsed = urlparse(url)
        if parsed.scheme.lower() != "https":
            raise SecurityError("Only HTTPS outbound URLs are allowed.")

        if not parsed.hostname:
            raise SecurityError("Outbound URL must include a valid hostname.")

        allowed = {host.lower().strip() for host in self._settings.allowed_outbound_hosts if host.strip()}
        if allowed and parsed.hostname.lower() not in allowed:
            raise SecurityError(
                f"Host '{parsed.hostname}' is not in OMNI_MCP_ALLOWED_OUTBOUND_HOSTS."
            )
