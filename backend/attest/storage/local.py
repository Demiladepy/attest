"""Local asset persistence — real fetchable URLs without B2 keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from attest.config import Settings, get_settings

# 1×1 PNG (valid image bytes for verifier SHA-256 checks)
MINIMAL_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000a49444154789c63000100000500010d0a2db400000000"
    "49454e44ae426082"
)


def assets_root(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    root = Path(__file__).resolve().parents[2] / "demo_assets"
    root.mkdir(parents=True, exist_ok=True)
    return root


def run_dir(tenant_id: str, run_id: str, settings: Settings | None = None) -> Path:
    path = assets_root(settings) / tenant_id / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def public_base(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    return settings.api_public_base_url.rstrip("/")


def persist_run(
    *,
    tenant_id: str,
    run_id: str,
    manifest: dict[str, Any],
    asset_bytes: bytes | None = None,
    asset_name: str = "output.png",
    settings: Settings | None = None,
) -> tuple[str, str, str]:
    """
    Write manifest + asset to disk. Returns (asset_url, manifest_url, sha256).
    URLs are served by FastAPI static mount at /assets/.
    """
    settings = settings or get_settings()
    data = asset_bytes if asset_bytes is not None else MINIMAL_PNG
    import hashlib

    sha256 = hashlib.sha256(data).hexdigest()
    directory = run_dir(tenant_id, run_id, settings)

    asset_path = directory / asset_name
    asset_path.write_bytes(data)

    manifest_path = directory / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    base = public_base(settings)
    prefix = f"{base}/assets/{tenant_id}/{run_id}"
    return f"{prefix}/{asset_name}", f"{prefix}/manifest.json", sha256
