import pytest

from omni_mcp.config import Settings
from omni_mcp.security import SecurityError, SecurityPolicy


def test_https_required() -> None:
    settings = Settings(allowed_outbound_hosts=[])
    policy = SecurityPolicy(settings)

    policy.validate_outbound_url("https://example.com/path")

    with pytest.raises(SecurityError):
        policy.validate_outbound_url("http://example.com")


def test_allowlist_blocks_unknown_host() -> None:
    settings = Settings(allowed_outbound_hosts=["example.com"])
    policy = SecurityPolicy(settings)

    policy.validate_outbound_url("https://example.com/ok")

    with pytest.raises(SecurityError):
        policy.validate_outbound_url("https://not-allowed.example.org")


def test_validate_tenant_id() -> None:
    policy = SecurityPolicy(Settings())
    policy.validate_tenant_id("user_123@example.com")

    with pytest.raises(SecurityError):
        policy.validate_tenant_id("bad tenant id with spaces")
