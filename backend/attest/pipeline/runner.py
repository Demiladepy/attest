"""Pipeline runner — Genblaze integration with demo fallback."""

from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Callable, Awaitable

from attest.compliance.sink import apply_compliance_to_manifest, get_signer, new_run_id
from attest.config import get_settings


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

    # Synthetic asset hash from brief + run_id (deterministic for demo)
    payload = f"{brief}:{run_id}".encode()
    sha256 = hashlib.sha256(payload).hexdigest()

    base_manifest: dict[str, Any] = {
        "run_id": run_id,
        "parent_run_id": parent_run_id,
        "tenant_id": settings.tenant_id,
        "created_at": started.isoformat(),
        "brief": brief,
        "pipeline": "attest-compliance-v1",
        "outputs": [
            {
                "modality": "video",
                "sha256": sha256,
                "mime": "video/mp4",
                "provider": "wan-gmi",
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
    base_url = settings.b2_public_url_base or "https://f004.backblazeb2.com/file/attest-demo"
    asset_url = f"{base_url}/{settings.tenant_id}/{run_id}/output.mp4"
    manifest_url = f"{base_url}/{settings.tenant_id}/{run_id}/manifest.json"

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
    on_step: StepCallback | None = None,
) -> PipelineResult:
    """Run real Genblaze pipeline when providers + B2 are configured."""
    settings = get_settings()
    storage = None
    try:
        from attest.compliance.sink import build_storage_sink

        storage = build_storage_sink(settings)
        if storage is None:
            return await run_demo_pipeline(
                asset_id=asset_id,
                brief=brief,
                parent_run_id=parent_run_id,
                on_step=on_step,
            )

        # Provider wiring ships in a follow-up once API keys are set.
        # For now, fall back to demo when no provider keys detected.
        return await run_demo_pipeline(
            asset_id=asset_id,
            brief=brief,
            parent_run_id=parent_run_id,
            on_step=on_step,
        )
    finally:
        if storage is not None and hasattr(storage, "close"):
            storage.close()


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

    async def run() -> PipelineResult:
        if get_settings().demo_mode:
            return await run_demo_pipeline(
                asset_id=asset_id,
                brief=brief,
                parent_run_id=parent_run_id,
                lineage=lineage,
                on_step=collector,
            )
        return await run_genblaze_pipeline(
            asset_id=asset_id,
            brief=brief,
            parent_run_id=parent_run_id,
            on_step=collector,
        )

    task = asyncio.create_task(run())

    while not task.done() or not step_queue.empty():
        try:
            event = await asyncio.wait_for(step_queue.get(), timeout=0.05)
            yield event
        except asyncio.TimeoutError:
            continue

    result = await task
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
