from omni_mcp.config import Settings
from omni_mcp.security import SecurityError, SecurityPolicy


def test_https_required() -> None:
    settings = Settings(allowed_outbound_hosts=[])
    policy = SecurityPolicy(settings)

    policy.validate_outbound_url("https://example.com/path")

    try:
        policy.validate_outbound_url("http://example.com")
        assert False, "Expected SecurityError for non-HTTPS URL"
    except SecurityError:
        pass


def test_allowlist_blocks_unknown_host() -> None:
    settings = Settings(allowed_outbound_hosts=["example.com"])
    policy = SecurityPolicy(settings)

    policy.validate_outbound_url("https://example.com/ok")

    try:
        policy.validate_outbound_url("https://not-allowed.example.org")
        assert False, "Expected SecurityError for blocked host"
    except SecurityError:
        pass
