"""Security helpers used by tools and transports."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from omni_mcp.config import Settings


class SecurityError(ValueError):
    """Raised when a request violates a local security policy."""


class SecurityPolicy:
    """Enforces local policy rules for sensitive operations."""

    _TENANT_ID_RE = re.compile(r"^[a-zA-Z0-9._@:-]{3,128}$")

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

    def validate_tenant_id(self, tenant_id: str) -> None:
        """Validate tenant identifier format for user-is-tenant model."""

        if not self._TENANT_ID_RE.fullmatch(tenant_id.strip()):
            raise SecurityError(
                "Invalid tenant_id. Allowed charset: letters, digits, dot, underscore, at, colon, hyphen."
            )

    def enforce_shared_secret(self, provided_secret: str | None) -> None:
        """Validate shared secret for integrations that use simple symmetric auth."""

        configured = self._settings.client_auth_shared_secret
        if configured is None:
            return
        if not provided_secret or provided_secret != configured:
            raise SecurityError("Invalid shared secret.")
