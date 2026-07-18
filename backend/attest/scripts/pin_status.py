"""CLI: report health + recent assets without spending GMI credits."""

from __future__ import annotations

import asyncio
import json

from sqlalchemy import select

from attest.config import get_settings
from attest.db import get_session_factory, init_db
from attest.models import AssetRecord
from attest.storage.b2_probe import b2_write_probe
from attest.storage.urls import b2_config_warnings, use_storage_proxy


async def _main() -> None:
    settings = get_settings()
    await init_db()

    b2_ok, b2_detail = b2_write_probe(settings) if settings.b2_configured else (False, "not_configured")
    if settings.gmi_pipeline_ready:
        pipeline = "gmi"
    elif settings.genblaze_image_ready:
        pipeline = "replicate"
    else:
        pipeline = "demo"

    factory = get_session_factory()
    assets: list[dict] = []
    async with factory() as db:
        result = await db.execute(
            select(AssetRecord)
            .where(AssetRecord.tenant_id == settings.tenant_id)
            .order_by(AssetRecord.created_at.desc())
            .limit(5)
        )
        for r in result.scalars().all():
            assets.append(
                {
                    "id": r.id,
                    "title": r.title,
                    "status": r.status.value,
                    "run_id": r.run_id,
                    "asset_url": r.asset_url,
                    "manifest_url": r.manifest_url,
                    "sha256": (r.sha256 or "")[:16] or None,
                }
            )

    warnings = b2_config_warnings(settings)
    report = {
        "pipeline": pipeline,
        "b2_configured": settings.b2_configured,
        "b2_write_ok": b2_ok,
        "b2_write_detail": b2_detail,
        "storage_proxy": use_storage_proxy(settings),
        "gmi_configured": settings.gmi_configured,
        "signing_configured": bool(settings.attest_signing_key_hex),
        "region": settings.b2_region,
        "public_url_base": settings.b2_public_url_base or None,
        "warnings": warnings,
        "recent_assets": assets,
        "hint": (
            "Clear B2_PUBLIC_URL_BASE for private-bucket proxy URLs. "
            "Set allow_gmi_burn: true in docs/LOOP_STATE.md before a hero GMI run."
        ),
    }
    print(json.dumps(report, indent=2))


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
