from contextlib import asynccontextmanager
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from attest.api.routes import router
from attest.api.storage import router as storage_router
from attest.config import get_settings
from attest.db import get_session_factory, init_db
from attest.models import AuditEventType, AssetRecord, ComplianceStatus
from attest.pipeline.runner import stream_pipeline
from attest.services.audit import record_event
from attest.services.audit_events import record_pipeline_step
from attest.services.lineage import build_lineage, mark_parent_rejected
from attest.storage.local import assets_root
import uuid


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    assets_root()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ATTEST API",
        description="Compliance-grade AI media gateway for Article 50",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    app.include_router(storage_router)

    demo_assets = assets_root(settings)
    app.mount("/assets", StaticFiles(directory=str(demo_assets)), name="assets")

    @app.post("/api/assets/generate/stream")
    async def generate_stream(body: dict):
        from pydantic import BaseModel, Field

        class Req(BaseModel):
            brief: str = Field(..., min_length=10)
            title: str = "Untitled generation"
            parent_run_id: str | None = None

        req = Req(**body)
        asset_id = str(uuid.uuid4())
        factory = get_session_factory()
        run_id_holder: list[str | None] = [None]

        async def event_gen():
            lineage: list = []
            async with factory() as db:
                if req.parent_run_id:
                    await mark_parent_rejected(db, req.parent_run_id)
                lineage = await build_lineage(db, req.parent_run_id)
                record = AssetRecord(
                    id=asset_id,
                    tenant_id=settings.tenant_id,
                    title=req.title,
                    brief=req.brief,
                    status=ComplianceStatus.GENERATING,
                    parent_run_id=req.parent_run_id,
                )
                db.add(record)
                await db.commit()
                await record_event(
                    db,
                    tenant_id=settings.tenant_id,
                    event_type=AuditEventType.GENERATED,
                    asset_id=asset_id,
                    detail=req.brief[:200],
                )

            yield f"data: {json.dumps({'type': 'started', 'asset_id': asset_id})}\n\n"

            try:
                async for event in stream_pipeline(
                    asset_id=asset_id,
                    brief=req.brief,
                    parent_run_id=req.parent_run_id,
                    lineage=lineage,
                ):
                    yield f"data: {json.dumps(event)}\n\n"

                    if event.get("type") == "error":
                        async with factory() as db:
                            record = await db.get(AssetRecord, asset_id)
                            if record:
                                record.status = ComplianceStatus.REJECTED
                                await db.commit()
                        return

                    if event.get("type") == "step" and event.get("step"):
                        step = event["step"]
                        if step.get("status") == "complete":
                            async with factory() as db:
                                await record_pipeline_step(
                                    db,
                                    tenant_id=settings.tenant_id,
                                    asset_id=asset_id,
                                    run_id=run_id_holder[0],
                                    step_id=step.get("id", ""),
                                    status="complete",
                                    detail=step.get("b2_op") or step.get("detail") or "",
                                )

                    if event.get("type") == "complete":
                        r = event["result"]
                        run_id_holder[0] = r["run_id"]
                        async with factory() as db:
                            record = await db.get(AssetRecord, asset_id)
                            if record:
                                record.run_id = r["run_id"]
                                record.asset_url = r["asset_url"]
                                record.manifest_url = r["manifest_url"]
                                record.sha256 = r["sha256"]
                                record.status = ComplianceStatus.COMPLIANT
                                await db.commit()
                            await record_event(
                                db,
                                tenant_id=settings.tenant_id,
                                event_type=AuditEventType.SIGNED,
                                asset_id=asset_id,
                                run_id=r["run_id"],
                                detail=f"sha256={r['sha256'][:16]} manifest={r['manifest_url']}",
                            )
            except Exception as exc:
                yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

        return StreamingResponse(event_gen(), media_type="text/event-stream")

    return app


app = create_app()
