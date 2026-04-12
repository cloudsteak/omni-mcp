import pytest

from omni_mcp.rss_digest.utils import (
    build_content_fingerprint,
    normalize_language,
    normalize_url_for_dedupe,
    validate_poll_and_retention,
)


def test_normalize_url_for_dedupe() -> None:
    assert normalize_url_for_dedupe("HTTPS://Example.COM/path/?utm=123") == "https://example.com/path"


def test_build_content_fingerprint_stability() -> None:
    fp1 = build_content_fingerprint(
        link="https://example.com/a?utm=1",
        title="Hello   World",
        published_at_raw="Mon, 01 Jan 2026 10:00:00 GMT",
    )
    fp2 = build_content_fingerprint(
        link="https://example.com/a",
        title="hello world",
        published_at_raw="Mon, 01 Jan 2026 10:00:00 GMT",
    )
    assert fp1 == fp2


def test_validate_poll_and_retention() -> None:
    validate_poll_and_retention(6, 14, 2, 24, 7, 30)

    with pytest.raises(ValueError):
        validate_poll_and_retention(1, 14, 2, 24, 7, 30)

    with pytest.raises(ValueError):
        validate_poll_and_retention(6, 31, 2, 24, 7, 30)


def test_normalize_language() -> None:
    assert normalize_language("hu") == "hu"
    assert normalize_language("EN") == "en"

    with pytest.raises(ValueError):
        normalize_language("de")
