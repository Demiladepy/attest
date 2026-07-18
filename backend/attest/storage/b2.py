"""Backblaze B2 storage — native B2 API (works with Master Application Key)."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from attest.config import Settings, get_settings
from attest.storage.urls import storage_proxy_url, use_storage_proxy


@lru_cache(maxsize=1)
def _authorized_api(key_id: str, app_key: str):
    """Cache B2 session per process (key rotation requires restart)."""
    from b2sdk.v2 import B2Api, InMemoryAccountInfo

    api = B2Api(InMemoryAccountInfo())
    api.authorize_account("production", key_id, app_key)
    return api


def _bucket(settings: Settings):
    api = _authorized_api(settings.b2_key_id.strip(), settings.b2_application_key.strip())
    return api.get_bucket_by_name(settings.b2_bucket)


def _object_url(settings: Settings, key: str) -> str:
    base = settings.b2_public_url_base.rstrip("/")
    if base:
        return f"{base}/{key}"
    return f"https://{settings.b2_bucket}.s3.{settings.b2_region}.backblazeb2.com/{key}"


def fetch_object(key: str, settings: Settings | None = None) -> tuple[bytes, str]:
    """Download object from B2. Returns (bytes, content_type)."""
    settings = settings or get_settings()
    if not settings.b2_configured:
        raise RuntimeError("B2 credentials not configured")
    bucket = _bucket(settings)
    downloaded = bucket.download_file_by_name(key)
    content_type = downloaded.response.headers.get("content-type", "application/octet-stream")
    return downloaded.response.content, content_type


def put_object_bytes(
    key: str,
    data: bytes,
    *,
    content_type: str = "application/octet-stream",
    object_lock: bool = False,
    settings: Settings | None = None,
) -> None:
    del object_lock  # native upload; retention depends on bucket Object Lock config
    settings = settings or get_settings()
    bucket = _bucket(settings)
    bucket.upload_bytes(data, key, file_infos={"contentType": content_type})


def public_urls_for_run(
    *,
    tenant_id: str,
    run_id: str,
    asset_name: str,
    settings: Settings | None = None,
) -> tuple[str, str]:
    """Return (asset_url, manifest_url) using proxy or direct B2 base."""
    settings = settings or get_settings()
    if use_storage_proxy(settings):
        return (
            storage_proxy_url(tenant_id, run_id, asset_name, settings),
            storage_proxy_url(tenant_id, run_id, "manifest.json", settings),
        )
    return (
        _object_url(settings, f"{tenant_id}/{run_id}/{asset_name}"),
        _object_url(settings, f"{tenant_id}/{run_id}/manifest.json"),
    )


def upload_compliant_run(
    *,
    tenant_id: str,
    run_id: str,
    asset_bytes: bytes,
    manifest: dict[str, Any],
    asset_name: str = "output.png",
    settings: Settings | None = None,
) -> tuple[str, str, str]:
    """
    Upload asset + signed manifest to B2 via native API.
    Returns (asset_url, manifest_url, sha256).
    """
    import hashlib

    settings = settings or get_settings()
    if not settings.b2_configured:
        raise RuntimeError("B2 credentials not configured")

    sha256 = hashlib.sha256(asset_bytes).hexdigest()
    asset_key = f"{tenant_id}/{run_id}/{asset_name}"
    manifest_key = f"{tenant_id}/{run_id}/manifest.json"

    content_type = "image/png" if asset_name.endswith(".png") else "application/octet-stream"
    put_object_bytes(asset_key, asset_bytes, content_type=content_type, settings=settings)
    put_object_bytes(
        manifest_key,
        json.dumps(manifest, indent=2).encode("utf-8"),
        content_type="application/json",
        settings=settings,
    )

    asset_url, manifest_url = public_urls_for_run(
        tenant_id=tenant_id,
        run_id=run_id,
        asset_name=asset_name,
        settings=settings,
    )
    return asset_url, manifest_url, sha256
