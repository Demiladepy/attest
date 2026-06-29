"""SQLAlchemy models — audit trail and asset registry."""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ComplianceStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    SIGNED = "signed"
    COMPLIANT = "compliant"
    REJECTED = "rejected"
    TAMPERED = "tampered"


class AuditEventType(str, enum.Enum):
    GENERATED = "generated"
    MANIFEST_WRITTEN = "manifest_written"
    SIGNED = "signed"
    WATERMARKED = "watermarked"
    C2PA_EMBEDDED = "c2pa_embedded"
    OBJECT_LOCK_APPLIED = "object_lock_applied"
    VERIFIED = "verified"
    TAMPER_DETECTED = "tamper_detected"
    REJECTED = "rejected"


class AssetRecord(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(512))
    brief: Mapped[str] = mapped_column(Text)
    status: Mapped[ComplianceStatus] = mapped_column(Enum(ComplianceStatus), default=ComplianceStatus.PENDING)
    run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parent_run_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    asset_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    manifest_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AuditLogEntry(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    asset_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    run_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    event_type: Mapped[AuditEventType] = mapped_column(Enum(AuditEventType))
    detail: Mapped[str] = mapped_column(Text, default="")
    b2_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
