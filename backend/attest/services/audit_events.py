"""Map pipeline SSE steps to audit log events."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from attest.models import AuditEventType
from attest.services.audit import record_event

STEP_TO_AUDIT: dict[str, AuditEventType] = {
    "compliance-manifest_written": AuditEventType.MANIFEST_WRITTEN,
    "compliance-signed": AuditEventType.SIGNED,
    "compliance-watermarked": AuditEventType.WATERMARKED,
    "compliance-c2pa_embedded": AuditEventType.C2PA_EMBEDDED,
    "compliance-object_lock_applied": AuditEventType.OBJECT_LOCK_APPLIED,
    "audit": AuditEventType.VERIFIED,
}


async def record_pipeline_step(
    db: AsyncSession,
    *,
    tenant_id: str,
    asset_id: str,
    run_id: str | None,
    step_id: str,
    status: str,
    detail: str = "",
) -> None:
    if status != "complete":
        return
    event_type = STEP_TO_AUDIT.get(step_id)
    if event_type is None:
        if step_id == "storyboard":
            event_type = AuditEventType.MANIFEST_WRITTEN
        elif step_id == "sign":
            event_type = AuditEventType.SIGNED
        elif step_id == "lock":
            event_type = AuditEventType.OBJECT_LOCK_APPLIED
        else:
            return
    await record_event(
        db,
        tenant_id=tenant_id,
        event_type=event_type,
        asset_id=asset_id,
        run_id=run_id,
        detail=detail or step_id,
    )
