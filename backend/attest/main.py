from contextlib import asynccontextmanager
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from attest.api.routes import router
from attest.config import get_settings
from attest.db import init_db
from attest.pipeline.runner import stream_pipeline
import uuid

from attest.db import get_session_factory
from attest.models import AssetRecord, ComplianceStatus


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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

        async def event_gen():
            async with factory() as db:
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

            yield f"data: {json.dumps({'type': 'started', 'asset_id': asset_id})}\n\n"

            async for event in stream_pipeline(
                asset_id=asset_id,
                brief=req.brief,
                parent_run_id=req.parent_run_id,
            ):
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") == "complete":
                    async with factory() as db:
                        record = await db.get(AssetRecord, asset_id)
                        if record:
                            r = event["result"]
                            record.run_id = r["run_id"]
                            record.asset_url = r["asset_url"]
                            record.manifest_url = r["manifest_url"]
                            record.sha256 = r["sha256"]
                            record.status = ComplianceStatus.COMPLIANT
                            await db.commit()

        return StreamingResponse(event_gen(), media_type="text/event-stream")

    return app


app = create_app()
