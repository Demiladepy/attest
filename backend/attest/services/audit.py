"""Audit log service — tamper-evident event trail."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from attest.models import AuditEventType, AuditLogEntry


async def record_event(
    session: AsyncSession,
    *,
    tenant_id: str,
    event_type: AuditEventType,
    detail: str = "",
    asset_id: str | None = None,
    run_id: str | None = None,
    b2_object_key: str | None = None,
) -> AuditLogEntry:
    entry = AuditLogEntry(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        asset_id=asset_id,
        run_id=run_id,
        event_type=event_type,
        detail=detail,
        b2_object_key=b2_object_key,
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry
