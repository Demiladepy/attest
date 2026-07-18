"""Public URL helpers for local, B2 direct, and API-proxied private B2."""

from __future__ import annotations

import re

from attest.config import Settings, get_settings
from attest.storage.local import public_base

_REGION_IN_URL = re.compile(r"\.s3\.([a-z0-9-]+)\.backblazeb2\.com", re.IGNORECASE)


def use_storage_proxy(settings: Settings | None = None) -> bool:
    """Private B2 buckets need judge-pasteable URLs via the API."""
    settings = settings or get_settings()
    return settings.b2_configured and not settings.b2_public_url_base


def b2_config_warnings(settings: Settings | None = None) -> list[str]:
    """
    Soft config checks for deploy/demo readiness.
    Prefer empty B2_PUBLIC_URL_BASE for private buckets + /api/storage proxy.
    """
    settings = settings or get_settings()
    warnings: list[str] = []
    if not settings.b2_configured:
        return warnings

    base = (settings.b2_public_url_base or "").strip()
    region = (settings.b2_region or "").strip()

    if base:
        warnings.append(
            "B2_PUBLIC_URL_BASE is set — private buckets may not be fetchable by the "
            "public verifier. Clear it to use /api/storage/… proxy URLs."
        )
        match = _REGION_IN_URL.search(base)
        if match and region and match.group(1) != region:
            warnings.append(
                f"B2_REGION={region} does not match region in B2_PUBLIC_URL_BASE "
                f"({match.group(1)}). Set B2_REGION to the bucket endpoint region."
            )
    elif not region:
        warnings.append("B2_REGION is empty — set it to the bucket S3 endpoint region (e.g. us-east-005).")

    return warnings


def object_key(tenant_id: str, run_id: str, filename: str) -> str:
    return f"{tenant_id}/{run_id}/{filename}"


def storage_proxy_url(
    tenant_id: str,
    run_id: str,
    filename: str,
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    base = public_base(settings)
    return f"{base}/api/storage/{tenant_id}/{run_id}/{filename}"


def parse_storage_proxy_url(url: str) -> tuple[str, str, str] | None:
    """Return (tenant_id, run_id, filename) for /api/storage/… URLs."""
    from urllib.parse import urlparse

    path = urlparse(url).path
    prefix = "/api/storage/"
    if not path.startswith(prefix):
        return None
    parts = path[len(prefix) :].split("/")
    if len(parts) < 3:
        return None
    tenant_id, run_id = parts[0], parts[1]
    filename = "/".join(parts[2:])
    return tenant_id, run_id, filename
