"""
Real Genblaze image pipeline (FLUX via Replicate → B2 ObjectStorageSink).

Activates when B2 + REPLICATE_API_TOKEN are configured. Until then, runner.py
uses the simulated step visualizer + local asset persistence.
"""

from __future__ import annotations

import asyncio
from typing import Any

from attest.compliance.sink import apply_compliance_to_manifest, build_storage_sink
from attest.config import Settings, get_settings
from attest.pipeline.runner import PipelineResult, PipelineStepEvent, StepCallback


def is_configured(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    return bool(
        settings.b2_bucket
        and settings.b2_key_id
        and settings.b2_application_key
        and settings.replicate_api_token
    )


def _run_flux_sync(*, brief: str, tenant_id: str) -> dict[str, Any]:
    """Blocking Genblaze pipeline — run in executor."""
    from datetime import datetime, timedelta, timezone

    from genblaze_core import KeyStrategy, Modality, ObjectLockConfig, ObjectStorageSink, Pipeline
    from genblaze_replicate import ReplicateProvider

    settings = get_settings()
    storage = build_storage_sink(settings)
    if storage is None:
        raise RuntimeError("B2 storage sink could not be constructed")

    provider = ReplicateProvider()
    result = (
        Pipeline("attest-flux", project_id=tenant_id)
        .step(
            provider,
            model="black-forest-labs/flux-schnell",
            prompt=brief,
            modality=Modality.IMAGE,
            num_outputs=1,
            aspect_ratio="16:9",
            fallback_models=["google/imagen-3"],
        )
        .run(sink=storage, timeout=120, tenant_id=tenant_id)
    )

    manifest_dict = result.manifest.to_dict() if hasattr(result.manifest, "to_dict") else dict(result.manifest)
    asset = result.run.steps[0].assets[0] if result.run.steps and result.run.steps[0].assets else None
    asset_url = asset.url if asset else ""
    sha256 = asset.sha256 if asset else ""

    # Durable manifest URL via sink helper when available
    manifest_url = ""
    if hasattr(storage, "manifest_url_for"):
        manifest_url = storage.manifest_url_for(result.run)

    return {
        "run_id": result.run.run_id,
        "manifest": manifest_dict,
        "asset_url": asset_url,
        "manifest_url": manifest_url,
        "sha256": sha256,
    }


async def run_flux_image_pipeline(
    *,
    asset_id: str,
    brief: str,
    parent_run_id: str | None = None,
    lineage: list[dict[str, Any]] | None = None,
    on_step: StepCallback | None = None,
) -> PipelineResult:
    """Run FLUX → B2 when credentials are present."""
    settings = get_settings()

    if on_step:
        await on_step(
            PipelineStepEvent(
                step_id="flux",
                label="Generate image",
                provider="FLUX (Replicate)",
                status="running",
            )
        )

    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, lambda: _run_flux_sync(brief=brief, tenant_id=settings.tenant_id))

    if on_step:
        await on_step(
            PipelineStepEvent(
                step_id="flux",
                label="Generate image",
                provider="FLUX (Replicate)",
                status="complete",
                b2_op="manifest written",
            )
        )

    manifest = await apply_compliance_to_manifest(
        raw["manifest"],
        tenant_id=settings.tenant_id,
        asset_sha256=raw["sha256"],
        parent_run_id=parent_run_id,
        lineage=lineage,
    )

    return PipelineResult(
        asset_id=asset_id,
        run_id=raw["run_id"],
        parent_run_id=parent_run_id,
        asset_url=raw["asset_url"],
        manifest_url=raw["manifest_url"],
        sha256=raw["sha256"],
        manifest=manifest,
        duration_seconds=0.0,
    )
