from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from attest.compliance.tamper import tamper_asset_url
from attest.compliance.verify import verify_asset_url
from attest.db import get_db
from attest.models import AssetRecord, AuditLogEntry, AuditEventType, ComplianceStatus
from attest.pipeline.runner import run_demo_pipeline, run_genblaze_pipeline
from attest.services.audit import record_event
from attest.services.lineage import build_lineage, mark_parent_rejected
from attest.services.webhook_auth import verify_b2_webhook
from attest.config import get_settings
from attest.storage.b2_probe import b2_write_probe
from attest.storage.urls import b2_config_warnings

router = APIRouter(prefix="/api", tags=["api"])


class GenerateRequest(BaseModel):
    brief: str = Field(..., min_length=10, max_length=4000)
    title: str = Field(default="Untitled generation")
    parent_run_id: str | None = None


class AssetOut(BaseModel):
    id: str
    title: str
    brief: str
    status: str
    run_id: str | None
    parent_run_id: str | None
    asset_url: str | None
    manifest_url: str | None
    sha256: str | None
    created_at: str

    @classmethod
    def from_record(cls, r: AssetRecord) -> AssetOut:
        return cls(
            id=r.id,
            title=r.title,
            brief=r.brief,
            status=r.status.value,
            run_id=r.run_id,
            parent_run_id=r.parent_run_id,
            asset_url=r.asset_url,
            manifest_url=r.manifest_url,
            sha256=r.sha256,
            created_at=r.created_at.isoformat(),
        )


class VerifyRequest(BaseModel):
    asset_url: str
    manifest_url: str | None = None
    expected_sha256: str | None = None


class TamperRequest(BaseModel):
    asset_url: str
    asset_id: str | None = None
    run_id: str | None = None


class TamperResponse(BaseModel):
    original_url: str
    tampered_url: str
    original_sha256: str
    tampered_sha256: str
    method: str


@router.get("/health")
async def health() -> dict[str, object]:
    settings = get_settings()
    storage = "b2" if settings.b2_configured else "local"
    b2_ok, b2_detail = b2_write_probe(settings) if settings.b2_configured else (False, "not_configured")
    if settings.gmi_pipeline_ready:
        pipeline = "gmi"
    elif settings.genblaze_image_ready:
        pipeline = "replicate"
    else:
        pipeline = "demo"
    return {
        "status": "ok",
        "service": "attest",
        "storage": storage,
        "storage_proxy": settings.b2_configured and not bool(settings.b2_public_url_base),
        "b2_write_ok": b2_ok,
        "b2_write_detail": b2_detail,
        "b2_api": "native",
        "b2_region": settings.b2_region,
        "warnings": b2_config_warnings(settings),
        "pipeline": pipeline,
        "gmi_configured": settings.gmi_configured,
        "b2_configured": settings.b2_configured,
    }


@router.get("/assets", response_model=list[AssetOut])
async def list_assets(db: AsyncSession = Depends(get_db)) -> list[AssetOut]:
    settings = get_settings()
    result = await db.execute(
        select(AssetRecord)
        .where(AssetRecord.tenant_id == settings.tenant_id)
        .order_by(AssetRecord.created_at.desc())
    )
    return [AssetOut.from_record(r) for r in result.scalars().all()]


@router.post("/assets/generate", response_model=AssetOut)
async def generate_asset(body: GenerateRequest, db: AsyncSession = Depends(get_db)) -> AssetOut:
    settings = get_settings()
    asset_id = str(uuid.uuid4())

    record = AssetRecord(
        id=asset_id,
        tenant_id=settings.tenant_id,
        title=body.title,
        brief=body.brief,
        status=ComplianceStatus.GENERATING,
        parent_run_id=body.parent_run_id,
    )
    db.add(record)
    await db.commit()

    if body.parent_run_id:
        await mark_parent_rejected(db, body.parent_run_id)
    lineage = await build_lineage(db, body.parent_run_id)

    runner = run_demo_pipeline if settings.demo_mode else run_genblaze_pipeline
    result = await runner(
        asset_id=asset_id,
        brief=body.brief,
        parent_run_id=body.parent_run_id,
        lineage=lineage,
    )

    record.run_id = result.run_id
    record.asset_url = result.asset_url
    record.manifest_url = result.manifest_url
    record.sha256 = result.sha256
    record.status = ComplianceStatus.COMPLIANT
    await db.commit()
    await db.refresh(record)

    await record_event(
        db,
        tenant_id=settings.tenant_id,
        event_type=AuditEventType.GENERATED,
        asset_id=asset_id,
        run_id=result.run_id,
        detail=body.brief[:200],
    )
    await record_event(
        db,
        tenant_id=settings.tenant_id,
        event_type=AuditEventType.SIGNED,
        asset_id=asset_id,
        run_id=result.run_id,
        detail=f"sha256={result.sha256[:16]}",
    )

    return AssetOut.from_record(record)


@router.post("/verify")
async def verify(body: VerifyRequest) -> dict[str, Any]:
    result = await verify_asset_url(
        body.asset_url,
        manifest_url=body.manifest_url,
        expected_sha256=body.expected_sha256,
    )
    return result.to_dict()


@router.post("/tamper", response_model=TamperResponse)
async def tamper(body: TamperRequest, db: AsyncSession = Depends(get_db)) -> TamperResponse:
    """Re-encode asset bytes — demo beat for verifier failure + audit event."""
    settings = get_settings()
    try:
        result = await tamper_asset_url(body.asset_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    await record_event(
        db,
        tenant_id=settings.tenant_id,
        event_type=AuditEventType.TAMPER_DETECTED,
        asset_id=body.asset_id,
        run_id=body.run_id,
        detail=f"method={result.method} tampered_sha={result.tampered_sha256[:16]}",
    )

    if body.asset_id:
        record = await db.get(AssetRecord, body.asset_id)
        if record:
            record.status = ComplianceStatus.TAMPERED
    elif body.run_id:
        rows = await db.execute(
            select(AssetRecord).where(AssetRecord.run_id == body.run_id)
        )
        for record in rows.scalars().all():
            record.status = ComplianceStatus.TAMPERED
    await db.commit()

    return TamperResponse(**result.__dict__)


@router.get("/audit")
async def audit_log(db: AsyncSession = Depends(get_db), limit: int = 50) -> list[dict[str, Any]]:
    settings = get_settings()
    result = await db.execute(
        select(AuditLogEntry)
        .where(AuditLogEntry.tenant_id == settings.tenant_id)
        .order_by(AuditLogEntry.created_at.desc())
        .limit(min(limit, 200))
    )
    return [
        {
            "id": e.id,
            "event_type": e.event_type.value,
            "asset_id": e.asset_id,
            "run_id": e.run_id,
            "detail": e.detail,
            "b2_object_key": e.b2_object_key,
            "created_at": e.created_at.isoformat(),
        }
        for e in result.scalars().all()
    ]


@router.post("/webhooks/b2")
async def b2_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """B2 Event Notifications → audit log row."""
    settings = get_settings()
    body_bytes = await verify_b2_webhook(request, settings.b2_webhook_secret)
    try:
        payload = json.loads(body_bytes.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {"raw": body_bytes.decode("utf-8", errors="replace")[:500]}

    event_name = payload.get("eventType") or payload.get("event_type") or "unknown"
    object_key = payload.get("objectKey") or payload.get("object_key") or ""

    await record_event(
        db,
        tenant_id=settings.tenant_id,
        event_type=AuditEventType.TAMPER_DETECTED if "tamper" in event_name.lower() else AuditEventType.VERIFIED,
        detail=json.dumps(payload)[:2000],
        b2_object_key=object_key,
    )
    return {"status": "recorded"}
