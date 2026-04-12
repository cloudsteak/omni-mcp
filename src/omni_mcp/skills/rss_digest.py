"""RSS and digest related MCP tools."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from omni_mcp.config import Settings
from omni_mcp.rss_digest import RssDigestService


def register_rss_digest_skills(server: FastMCP, settings: Settings, service: RssDigestService) -> None:
    """Register tools for the RSS polling and digest use case."""

    if not settings.enable_rss_digest_skills:
        return

    @server.tool(
        name="tenant.upsert_preferences",
        description=(
            "Create or update tenant preferences. "
            "Enforces poll interval (2-24h), retention (7-30 days), and language (en/hu)."
        ),
    )
    def tenant_upsert_preferences(
        tenant_id: str,
        language: str,
        poll_interval_hours: int,
        retention_days: int,
    ) -> dict[str, object]:
        return service.upsert_tenant_preferences(
            tenant_id=tenant_id,
            language=language,
            poll_interval_hours=poll_interval_hours,
            retention_days=retention_days,
        )

    @server.tool(
        name="rss.add_feed",
        description="Register one RSS feed URL under a tenant and category.",
    )
    def rss_add_feed(tenant_id: str, category: str, feed_url: str) -> dict[str, str]:
        return service.add_feed(tenant_id=tenant_id, category=category, feed_url=feed_url)

    @server.tool(
        name="rss.list_feeds",
        description="List feeds for a tenant.",
    )
    def rss_list_feeds(tenant_id: str, active_only: bool = True) -> list[dict[str, object]]:
        return service.list_feeds(tenant_id=tenant_id, active_only=active_only)

    @server.tool(
        name="rss.poll",
        description="Poll all active feeds for a tenant and ingest only new deduplicated items.",
    )
    def rss_poll(tenant_id: str) -> dict[str, object]:
        return service.poll_feeds(tenant_id=tenant_id)

    @server.tool(
        name="rss.list_recent_items",
        description="List recent ingested articles for one category.",
    )
    def rss_list_recent_items(tenant_id: str, category: str, limit: int = 20) -> list[dict[str, str]]:
        return service.list_recent_items(tenant_id=tenant_id, category=category, limit=limit)

    @server.tool(
        name="digest.generate_category_summary",
        description=(
            "Generate a 3-5 minute article-style digest for one category from new items since last digest. "
            "Language can be en or hu."
        ),
    )
    def digest_generate_category_summary(
        tenant_id: str,
        category: str,
        language: str | None = None,
    ) -> dict[str, object]:
        return service.generate_digest(tenant_id=tenant_id, category=category, language=language)

    @server.tool(
        name="digest.list_history",
        description="List historical digests for one tenant/category.",
    )
    def digest_list_history(tenant_id: str, category: str, limit: int = 10) -> list[dict[str, object]]:
        return service.list_digests(tenant_id=tenant_id, category=category, limit=limit)
