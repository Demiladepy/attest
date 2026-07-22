"""Register script-generated pipeline results in the Console DB.

CLI runs (generate_demo_asset, gmi_smoke --full) bypass the API, so without
this the pinned hero asset never appears in the assets grid, can't be revised,
and leaves no audit trail.
"""

from __future__ import annotations

from attest.config import get_settings
from attest.db import get_session_factory, init_db
from attest.models import AssetRecord, AuditEventType, ComplianceStatus
from attest.pipeline.runner import PipelineResult
from attest.services.audit import record_event


async def register_pipeline_result(
    result: PipelineResult,
    *,
    brief: str,
    title: str = "Scripted generation",
) -> None:
    await init_db()
    settings = get_settings()
    factory = get_session_factory()
    async with factory() as db:
        record = AssetRecord(
            id=result.asset_id,
            tenant_id=settings.tenant_id,
            title=title,
            brief=brief,
            status=ComplianceStatus.COMPLIANT,
            run_id=result.run_id,
            parent_run_id=result.parent_run_id,
            asset_url=result.asset_url,
            manifest_url=result.manifest_url,
            sha256=result.sha256,
        )
        db.add(record)
        await db.commit()
        await record_event(
            db,
            tenant_id=settings.tenant_id,
            event_type=AuditEventType.GENERATED,
            asset_id=result.asset_id,
            run_id=result.run_id,
            detail=brief[:200],
        )
        await record_event(
            db,
            tenant_id=settings.tenant_id,
            event_type=AuditEventType.SIGNED,
            asset_id=result.asset_id,
            run_id=result.run_id,
            detail=f"sha256={result.sha256[:16]}",
        )
