"""Unified persistence — local dev or B2 when configured."""

from __future__ import annotations

from typing import Any

from attest.config import Settings, get_settings
from attest.storage.local import MINIMAL_PNG, persist_run


def persist_compliant_run(
    *,
    tenant_id: str,
    run_id: str,
    manifest: dict[str, Any],
    asset_bytes: bytes | None = None,
    asset_name: str = "output.png",
    settings: Settings | None = None,
) -> tuple[str, str, str]:
    settings = settings or get_settings()
    data = asset_bytes if asset_bytes is not None else MINIMAL_PNG

    if settings.b2_configured:
        from attest.storage.b2 import upload_compliant_run

        try:
            return upload_compliant_run(
                tenant_id=tenant_id,
                run_id=run_id,
                asset_bytes=data,
                manifest=manifest,
                asset_name=asset_name,
                settings=settings,
            )
        except Exception:
            # Keep real provider output reachable while B2 credentials are fixed
            return persist_run(
                tenant_id=tenant_id,
                run_id=run_id,
                manifest=manifest,
                asset_bytes=data,
                asset_name=asset_name,
                settings=settings,
            )

    return persist_run(
        tenant_id=tenant_id,
        run_id=run_id,
        manifest=manifest,
        asset_bytes=data,
        asset_name=asset_name,
        settings=settings,
    )
