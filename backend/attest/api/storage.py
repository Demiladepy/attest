"""Serve private B2 objects via authenticated API proxy."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from attest.config import get_settings
from attest.storage.b2 import fetch_object
from attest.storage.local import assets_root
from attest.storage.urls import object_key, safe_object_segments

router = APIRouter(prefix="/api/storage", tags=["storage"])

_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".json": "application/json",
    ".mp4": "video/mp4",
}


def _guess_content_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return _CONTENT_TYPES.get(suffix, "application/octet-stream")


@router.get("/{tenant_id}/{run_id}/{filename:path}")
async def serve_storage_object(tenant_id: str, run_id: str, filename: str) -> Response:
    settings = get_settings()
    if tenant_id != settings.tenant_id:
        raise HTTPException(status_code=404, detail="Not found")
    if not safe_object_segments(tenant_id, run_id, filename):
        raise HTTPException(status_code=404, detail="Not found")

    key = object_key(tenant_id, run_id, filename)

    if settings.b2_configured:
        try:
            data, content_type = fetch_object(key, settings)
            return Response(content=data, media_type=content_type)
        except Exception:
            pass

    root = assets_root(settings).resolve()
    local_path = (root / tenant_id / run_id / filename).resolve()
    if not local_path.is_relative_to(root):
        raise HTTPException(status_code=404, detail="Not found")
    if local_path.is_file():
        return Response(
            content=local_path.read_bytes(),
            media_type=_guess_content_type(filename),
        )

    raise HTTPException(status_code=404, detail="Object not found")
