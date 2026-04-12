"""Service layer for feed management, polling, deduplication, and digest generation."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import feedparser
import httpx
from sqlalchemy import and_, desc, select

from omni_mcp.config import Settings
from omni_mcp.security import SecurityPolicy
from omni_mcp.storage import Digest, DigestState, Feed, FeedItem, PollState, TenantPreference, create_session_factory
from omni_mcp.rss_digest.utils import (
    build_content_fingerprint,
    normalize_language,
    validate_poll_and_retention,
)


class RssDigestService:
    """Coordinates all RSS and digest operations for one MCP server instance."""

    def __init__(self, settings: Settings, policy: SecurityPolicy) -> None:
        self._settings = settings
        self._policy = policy
        self._session_factory = create_session_factory(settings.database_url)

    def upsert_tenant_preferences(
        self,
        tenant_id: str,
        language: str,
        poll_interval_hours: int,
        retention_days: int,
    ) -> dict[str, object]:
        """Create or update preferences for one tenant."""

        self._policy.validate_tenant_id(tenant_id)
        language = normalize_language(language)
        validate_poll_and_retention(
            poll_interval_hours=poll_interval_hours,
            retention_days=retention_days,
            min_poll_interval_hours=self._settings.min_poll_interval_hours,
            max_poll_interval_hours=self._settings.max_poll_interval_hours,
            min_retention_days=self._settings.min_retention_days,
            max_retention_days=self._settings.max_retention_days,
        )

        with self._session_factory() as session:
            existing = session.get(TenantPreference, tenant_id)
            if existing is None:
                existing = TenantPreference(
                    tenant_id=tenant_id,
                    language=language,
                    poll_interval_hours=poll_interval_hours,
                    retention_days=retention_days,
                )
                session.add(existing)
            else:
                existing.language = language
                existing.poll_interval_hours = poll_interval_hours
                existing.retention_days = retention_days
                existing.updated_at = datetime.now(UTC)

            session.commit()

        return {
            "tenant_id": tenant_id,
            "language": language,
            "poll_interval_hours": poll_interval_hours,
            "retention_days": retention_days,
        }

    def add_feed(self, tenant_id: str, category: str, feed_url: str) -> dict[str, str]:
        """Register a new active feed for a tenant and category."""

        self._policy.validate_tenant_id(tenant_id)
        self._policy.validate_outbound_url(feed_url)

        feed = Feed(id=str(uuid4()), tenant_id=tenant_id, category=category.strip(), url=feed_url.strip())
        with self._session_factory() as session:
            session.add(feed)
            session.commit()

        return {
            "feed_id": feed.id,
            "tenant_id": tenant_id,
            "category": feed.category,
            "url": feed.url,
            "status": "added",
        }

    def list_feeds(self, tenant_id: str, active_only: bool = True) -> list[dict[str, object]]:
        """List feeds registered for a tenant."""

        self._policy.validate_tenant_id(tenant_id)
        with self._session_factory() as session:
            stmt = select(Feed).where(Feed.tenant_id == tenant_id)
            if active_only:
                stmt = stmt.where(Feed.active.is_(True))
            stmt = stmt.order_by(Feed.category.asc(), Feed.created_at.desc())
            rows = session.execute(stmt).scalars().all()

        return [
            {
                "id": row.id,
                "category": row.category,
                "url": row.url,
                "active": row.active,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]

    def poll_feeds(self, tenant_id: str) -> dict[str, object]:
        """Poll all active feeds and ingest only newly discovered deduplicated items."""

        self._policy.validate_tenant_id(tenant_id)
        timeout = self._settings.outbound_http_timeout_seconds

        inserted_count = 0
        processed_feeds = 0

        with self._session_factory() as session:
            feeds = session.execute(
                select(Feed).where(and_(Feed.tenant_id == tenant_id, Feed.active.is_(True)))
            ).scalars().all()

            for feed in feeds:
                processed_feeds += 1
                self._policy.validate_outbound_url(feed.url)

                with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                    response = client.get(feed.url)
                    response.raise_for_status()
                    parsed = feedparser.parse(response.content)

                for entry in parsed.entries[:100]:
                    link = str(getattr(entry, "link", "")).strip()
                    title = str(getattr(entry, "title", "Untitled")).strip()
                    summary_text = str(getattr(entry, "summary", "")).strip()
                    published_at_raw = str(getattr(entry, "published", "")).strip()

                    if not link:
                        continue

                    fingerprint = build_content_fingerprint(
                        link=link, title=title, published_at_raw=published_at_raw
                    )

                    exists = session.execute(
                        select(FeedItem.id).where(
                            and_(
                                FeedItem.tenant_id == tenant_id,
                                FeedItem.content_fingerprint == fingerprint,
                            )
                        )
                    ).scalar_one_or_none()
                    if exists:
                        continue

                    session.add(
                        FeedItem(
                            id=str(uuid4()),
                            tenant_id=tenant_id,
                            feed_id=feed.id,
                            category=feed.category,
                            title=title,
                            link=link,
                            summary_text=summary_text,
                            published_at_raw=published_at_raw,
                            content_fingerprint=fingerprint,
                        )
                    )
                    inserted_count += 1

            state = session.get(PollState, tenant_id)
            if state is None:
                state = PollState(tenant_id=tenant_id, last_polled_at=datetime.now(UTC))
                session.add(state)
            else:
                state.last_polled_at = datetime.now(UTC)

            session.commit()

        return {
            "tenant_id": tenant_id,
            "processed_feeds": processed_feeds,
            "new_items": inserted_count,
        }

    def list_recent_items(self, tenant_id: str, category: str, limit: int = 20) -> list[dict[str, str]]:
        """Return recent ingested items for one category."""

        self._policy.validate_tenant_id(tenant_id)
        safe_limit = min(max(limit, 1), 100)

        with self._session_factory() as session:
            rows = session.execute(
                select(FeedItem)
                .where(and_(FeedItem.tenant_id == tenant_id, FeedItem.category == category))
                .order_by(desc(FeedItem.ingested_at))
                .limit(safe_limit)
            ).scalars().all()

        return [
            {
                "title": row.title,
                "link": row.link,
                "published_at": row.published_at_raw,
                "ingested_at": row.ingested_at.isoformat(),
            }
            for row in rows
        ]

    def generate_digest(self, tenant_id: str, category: str, language: str | None = None) -> dict[str, object]:
        """Generate and persist one category digest from items since the previous digest."""

        self._policy.validate_tenant_id(tenant_id)

        with self._session_factory() as session:
            pref = session.get(TenantPreference, tenant_id)
            chosen_language = normalize_language(language) if language else (pref.language if pref else "en")

            state_key = {"tenant_id": tenant_id, "category": category}
            digest_state = session.get(DigestState, state_key)

            if digest_state is None:
                window_start = datetime.now(UTC) - timedelta(hours=24)
            else:
                window_start = digest_state.last_digested_at

            rows = session.execute(
                select(FeedItem)
                .where(
                    and_(
                        FeedItem.tenant_id == tenant_id,
                        FeedItem.category == category,
                        FeedItem.ingested_at > window_start,
                    )
                )
                .order_by(FeedItem.ingested_at.asc())
                .limit(120)
            ).scalars().all()

            if not rows:
                return {
                    "tenant_id": tenant_id,
                    "category": category,
                    "language": chosen_language,
                    "status": "no_new_items",
                }

            digest_markdown = self._generate_markdown_digest(rows=rows, language=chosen_language)
            sources = [row.link for row in rows]

            digest = Digest(
                id=str(uuid4()),
                tenant_id=tenant_id,
                category=category,
                language=chosen_language,
                body_markdown=digest_markdown,
                source_links_json=json.dumps(sources),
            )
            session.add(digest)

            if digest_state is None:
                digest_state = DigestState(
                    tenant_id=tenant_id,
                    category=category,
                    last_digested_at=datetime.now(UTC),
                )
                session.add(digest_state)
            else:
                digest_state.last_digested_at = datetime.now(UTC)

            self._apply_retention(session=session, tenant_id=tenant_id)
            session.commit()

        return {
            "tenant_id": tenant_id,
            "category": category,
            "language": chosen_language,
            "status": "created",
            "source_count": len(sources),
            "digest_markdown": digest_markdown,
            "sources": sources,
        }

    def list_digests(self, tenant_id: str, category: str, limit: int = 10) -> list[dict[str, object]]:
        """Return digest history for one tenant and category."""

        self._policy.validate_tenant_id(tenant_id)
        safe_limit = min(max(limit, 1), 100)

        with self._session_factory() as session:
            rows = session.execute(
                select(Digest)
                .where(and_(Digest.tenant_id == tenant_id, Digest.category == category))
                .order_by(desc(Digest.created_at))
                .limit(safe_limit)
            ).scalars().all()

        return [
            {
                "id": row.id,
                "created_at": row.created_at.isoformat(),
                "language": row.language,
                "body_markdown": row.body_markdown,
                "sources": json.loads(row.source_links_json),
            }
            for row in rows
        ]

    def _generate_markdown_digest(self, rows: list[FeedItem], language: str) -> str:
        """Generate an article-style digest with source links."""

        if not self._settings.openai_api_key:
            raise ValueError("OMNI_MCP_OPENAI_API_KEY is required for digest generation.")

        language_hint = "Hungarian" if language == "hu" else "English"
        bullets = "\n".join(
            [f"- Title: {row.title}\n  Link: {row.link}\n  Context: {row.summary_text[:600]}" for row in rows]
        )

        prompt = (
            f"Write a {language_hint} category digest that takes roughly 3-5 minutes to read. "
            "Output markdown with:\n"
            "1) A concise title\n"
            "2) A flowing article-style summary body\n"
            "3) Key developments section\n"
            "4) Source links section listing all unique links\n"
            "Do not invent facts. Use only the provided articles.\n\n"
            f"Articles:\n{bullets}"
        )

        with httpx.Client(timeout=self._settings.outbound_http_timeout_seconds) as client:
            response = client.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {self._settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._settings.openai_model,
                    "input": prompt,
                },
            )
            response.raise_for_status()
            payload = response.json()

        output_text = payload.get("output_text", "").strip()
        if output_text:
            return output_text

        # Fallback parser for structured output payloads.
        parts: list[str] = []
        for output in payload.get("output", []):
            for content in output.get("content", []):
                text = content.get("text")
                if text:
                    parts.append(text)

        if not parts:
            raise ValueError("OpenAI response did not include textual output.")

        return "\n".join(parts)

    def _apply_retention(self, session, tenant_id: str) -> None:
        """Delete old feed items and digests based on tenant retention policy."""

        pref = session.get(TenantPreference, tenant_id)
        retention_days = pref.retention_days if pref else self._settings.max_retention_days
        cutoff = datetime.now(UTC) - timedelta(days=retention_days)

        old_items = session.execute(
            select(FeedItem).where(and_(FeedItem.tenant_id == tenant_id, FeedItem.ingested_at < cutoff))
        ).scalars().all()
        for row in old_items:
            session.delete(row)

        old_digests = session.execute(
            select(Digest).where(and_(Digest.tenant_id == tenant_id, Digest.created_at < cutoff))
        ).scalars().all()
        for row in old_digests:
            session.delete(row)
