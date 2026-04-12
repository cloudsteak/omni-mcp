"""Utility functions for RSS ingestion and digest generation."""

from __future__ import annotations

import hashlib
from urllib.parse import urlsplit, urlunsplit


def normalize_url_for_dedupe(url: str) -> str:
    """Normalize a URL to improve deduplication stability."""

    parts = urlsplit(url.strip())
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))


def build_content_fingerprint(link: str, title: str, published_at_raw: str) -> str:
    """Build a stable SHA-256 fingerprint for duplicate detection."""

    payload = "|".join(
        [
            normalize_url_for_dedupe(link),
            " ".join(title.lower().split()),
            published_at_raw.strip().lower(),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_poll_and_retention(
    poll_interval_hours: int,
    retention_days: int,
    min_poll_interval_hours: int,
    max_poll_interval_hours: int,
    min_retention_days: int,
    max_retention_days: int,
) -> None:
    """Validate tenant-specific interval and retention ranges."""

    if poll_interval_hours < min_poll_interval_hours or poll_interval_hours > max_poll_interval_hours:
        raise ValueError(
            f"poll_interval_hours must be between {min_poll_interval_hours} and {max_poll_interval_hours}."
        )

    if retention_days < min_retention_days or retention_days > max_retention_days:
        raise ValueError(f"retention_days must be between {min_retention_days} and {max_retention_days}.")


def normalize_language(language: str) -> str:
    """Allow only English and Hungarian for now."""

    normalized = language.strip().lower()
    if normalized not in {"en", "hu"}:
        raise ValueError("language must be 'en' or 'hu'.")
    return normalized
