"""Pipeline runner — Genblaze integration with demo fallback."""

from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Callable, Awaitable

from attest.compliance.sink import apply_compliance_to_manifest, new_run_id
from attest.config import get_settings
from attest.storage.local import MINIMAL_PNG
from attest.storage.persist import persist_compliant_run


@dataclass
class PipelineStepEvent:
    step_id: str
    label: str
    provider: str
    status: str  # running | complete | failed
    b2_op: str | None = None
    detail: str = ""


@dataclass
class PipelineResult:
    asset_id: str
    run_id: str
    parent_run_id: str | None
    asset_url: str
    manifest_url: str
    sha256: str
    manifest: dict[str, Any]
    duration_seconds: float
    steps: list[PipelineStepEvent] = field(default_factory=list)


StepCallback = Callable[[PipelineStepEvent], Awaitable[None]]


DEMO_STEPS: list[tuple[str, str, str, str | None]] = [
    ("classify", "Classify request", "GMI Llama 3", None),
    ("storyboard", "Generate storyboard", "FLUX", "manifest written"),
    ("video", "Generate video", "Wan (GMI)", None),
    ("variants", "A/B visual variants", "Decart Lucy 2.1", None),
    ("voice", "Spanish voiceover", "ElevenLabs", None),
    ("transcript", "Hash-verified transcript", "AssemblyAI", None),
    ("music", "Music bed", "Stability Audio", None),
    ("sign", "Compliance envelope", "ATTEST ComplianceSink", "Ed25519 signed"),
    ("c2pa", "Embed C2PA claim", "c2pa-python", "C2PA claim embedded"),
    ("lock", "Object Lock", "Backblaze B2", "Object Lock applied"),
    ("audit", "Audit event", "B2 Event Notifications", "audit event fired"),
]


async def _emit(step: PipelineStepEvent, cb: StepCallback | None) -> None:
    if cb:
        await cb(step)


async def run_demo_pipeline(
    *,
    asset_id: str,
    brief: str,
    parent_run_id: str | None = None,
    lineage: list[dict[str, Any]] | None = None,
    on_step: StepCallback | None = None,
) -> PipelineResult:
    """Simulated pipeline for demo / offline development."""
    settings = get_settings()
    run_id = new_run_id()
    started = datetime.now(timezone.utc)
    steps: list[PipelineStepEvent] = []

    for step_id, label, provider, b2_op in DEMO_STEPS:
        event = PipelineStepEvent(
            step_id=step_id,
            label=label,
            provider=provider,
            status="running",
            b2_op=b2_op,
        )
        steps.append(event)
        await _emit(event, on_step)
        await asyncio.sleep(0.35)
        event.status = "complete"
        await _emit(event, on_step)

    # Asset bytes (local dev: minimal PNG; production: Genblaze output)
    asset_bytes = MINIMAL_PNG
    import hashlib

    sha256 = hashlib.sha256(asset_bytes).hexdigest()

    base_manifest: dict[str, Any] = {
        "run_id": run_id,
        "parent_run_id": parent_run_id,
        "tenant_id": settings.tenant_id,
        "created_at": started.isoformat(),
        "brief": brief,
        "pipeline": "attest-compliance-v1",
        "outputs": [
            {
                "modality": "image",
                "sha256": sha256,
                "mime": "image/png",
                "provider": "flux-replicate",
            }
        ],
        "steps": [
            {"id": s.step_id, "provider": s.provider, "status": "complete"}
            for s in steps
        ],
        "attest": {
            "transcript": {
                "provider": "assemblyai",
                "hash_verified": True,
                "word_timings": True,
                "transcript_sha256": hashlib.sha256(b"demo-spanish-voiceover").hexdigest(),
            }
        },
    }

    async def audit_cb(event: str, detail: str) -> None:
        if on_step:
            await on_step(
                PipelineStepEvent(
                    step_id=f"compliance-{event}",
                    label=event.replace("_", " ").title(),
                    provider="ComplianceSink",
                    status="complete",
                    b2_op=detail,
                    detail=detail,
                )
            )

    manifest = await apply_compliance_to_manifest(
        base_manifest,
        tenant_id=settings.tenant_id,
        asset_sha256=sha256,
        parent_run_id=parent_run_id,
        lineage=lineage,
        on_event=audit_cb,
    )

    duration = (datetime.now(timezone.utc) - started).total_seconds()
    asset_url, manifest_url, sha256 = persist_compliant_run(
        tenant_id=settings.tenant_id,
        run_id=run_id,
        manifest=manifest,
        asset_bytes=asset_bytes,
        asset_name="output.png",
    )

    return PipelineResult(
        asset_id=asset_id,
        run_id=run_id,
        parent_run_id=parent_run_id,
        asset_url=asset_url,
        manifest_url=manifest_url,
        sha256=sha256,
        manifest=manifest,
        duration_seconds=duration,
        steps=steps,
    )


async def run_genblaze_pipeline(
    *,
    asset_id: str,
    brief: str,
    parent_run_id: str | None = None,
    lineage: list[dict[str, Any]] | None = None,
    on_step: StepCallback | None = None,
) -> PipelineResult:
    """Run real provider pipeline when credentials are configured."""
    settings = get_settings()

    from attest.pipeline.genblaze_gmi import is_configured as gmi_ready, run_gmi_pipeline

    if gmi_ready(settings):
        return await run_gmi_pipeline(
            asset_id=asset_id,
            brief=brief,
            parent_run_id=parent_run_id,
            lineage=lineage,
            on_step=on_step,
        )

    from attest.pipeline.genblaze_image import is_configured, run_flux_image_pipeline

    if is_configured(settings):
        return await run_flux_image_pipeline(
            asset_id=asset_id,
            brief=brief,
            parent_run_id=parent_run_id,
            lineage=lineage,
            on_step=on_step,
        )

    return await run_demo_pipeline(
        asset_id=asset_id,
        brief=brief,
        parent_run_id=parent_run_id,
        lineage=lineage,
        on_step=on_step,
    )


async def stream_pipeline(
    *,
    asset_id: str,
    brief: str,
    parent_run_id: str | None = None,
    lineage: list[dict[str, Any]] | None = None,
) -> AsyncIterator[dict[str, Any]]:
    """SSE-friendly step stream."""
    step_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def collector(event: PipelineStepEvent) -> None:
        await step_queue.put(
            {
                "type": "step",
                "step": {
                    "id": event.step_id,
                    "label": event.label,
                    "provider": event.provider,
                    "status": event.status,
                    "b2_op": event.b2_op,
                    "detail": event.detail,
                },
            }
        )

    settings = get_settings()

    async def run() -> PipelineResult:
        use_real = settings.gmi_pipeline_ready or (
            not settings.demo_mode and settings.genblaze_image_ready
        )
        if use_real:
            return await run_genblaze_pipeline(
                asset_id=asset_id,
                brief=brief,
                parent_run_id=parent_run_id,
                lineage=lineage,
                on_step=collector,
            )
        return await run_demo_pipeline(
            asset_id=asset_id,
            brief=brief,
            parent_run_id=parent_run_id,
            lineage=lineage,
            on_step=collector,
        )

    task = asyncio.create_task(run())

    try:
        while not task.done() or not step_queue.empty():
            try:
                event = await asyncio.wait_for(step_queue.get(), timeout=0.05)
                yield event
            except asyncio.TimeoutError:
                continue

        result = await task
    except Exception as exc:
        if not task.done():
            task.cancel()
        yield {"type": "error", "message": str(exc)}
        return

    yield {
        "type": "complete",
        "result": {
            "asset_id": result.asset_id,
            "run_id": result.run_id,
            "parent_run_id": result.parent_run_id,
            "asset_url": result.asset_url,
            "manifest_url": result.manifest_url,
            "sha256": result.sha256,
            "duration_seconds": result.duration_seconds,
        },
    }
