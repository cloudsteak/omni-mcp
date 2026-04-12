"""Database engine, ORM models, and schema initialization."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    """Declarative base for omni-mcp tables."""


class TenantPreference(Base):
    """One tenant per user preference row."""

    __tablename__ = "tenant_preferences"

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    language: Mapped[str] = mapped_column(String(8), default="en")
    poll_interval_hours: Mapped[int] = mapped_column(Integer, default=6)
    retention_days: Mapped[int] = mapped_column(Integer, default=14)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


class Feed(Base):
    """RSS feed source registered by a tenant under a category."""

    __tablename__ = "feeds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    url: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class FeedItem(Base):
    """Ingested article from RSS with deduplicated fingerprint per tenant."""

    __tablename__ = "feed_items"
    __table_args__ = (UniqueConstraint("tenant_id", "content_fingerprint", name="uq_feed_items_tenant_fp"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True)
    feed_id: Mapped[str] = mapped_column(String(36), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(Text)
    link: Mapped[str] = mapped_column(Text)
    summary_text: Mapped[str] = mapped_column(Text, default="")
    published_at_raw: Mapped[str] = mapped_column(String(128), default="")
    content_fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)


class PollState(Base):
    """Stores last poll execution timestamp per tenant."""

    __tablename__ = "poll_states"

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    last_polled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class DigestState(Base):
    """Stores last digest timestamp per tenant/category."""

    __tablename__ = "digest_states"

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    category: Mapped[str] = mapped_column(String(64), primary_key=True)
    last_digested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class Digest(Base):
    """Generated digest history."""

    __tablename__ = "digests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(8), default="en")
    body_markdown: Mapped[str] = mapped_column(Text)
    source_links_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)


def create_session_factory(database_url: str) -> sessionmaker:
    """Return a configured SQLAlchemy session factory."""

    engine = create_engine(database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, expire_on_commit=False)


def initialize_schema(database_url: str) -> None:
    """Create tables if they do not exist."""

    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
