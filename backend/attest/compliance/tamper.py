"""Tamper simulation — re-encode asset bytes for demo beat 2:00–2:35."""

from __future__ import annotations

import hashlib
import io
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx

from attest.config import Settings, get_settings
from attest.storage.b2 import fetch_object, put_object_bytes
from attest.storage.local import public_base
from attest.storage.urls import object_key, parse_storage_proxy_url, storage_proxy_url


@dataclass
class TamperResult:
    original_url: str
    tampered_url: str
    original_sha256: str
    tampered_sha256: str
    method: str


def _local_path_from_url(asset_url: str, settings: Settings | None = None) -> Path | None:
    """Map /assets/{tenant}/{run}/file.ext to demo_assets path."""
    settings = settings or get_settings()
    parsed = urlparse(asset_url)
    path = parsed.path
    prefix = "/assets/"
    if not path.startswith(prefix):
        return None
    rel = path[len(prefix) :]
    root = (Path(__file__).resolve().parents[2] / "demo_assets").resolve()
    candidate = (root / rel).resolve()
    # Containment: URL-supplied path must stay inside demo_assets
    if not candidate.is_relative_to(root):
        return None
    return candidate if candidate.exists() else None


def _reencode_png_pillow(data: bytes) -> bytes:
    from PIL import Image

    img = Image.open(io.BytesIO(data))
    out = io.BytesIO()
    img.save(out, format="PNG", compress_level=9, optimize=True)
    return out.getvalue()


def _reencode_ffmpeg(input_path: Path, output_path: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False
    proc = subprocess.run(
        [ffmpeg, "-y", "-i", str(input_path), "-q:v", "5", str(output_path)],
        capture_output=True,
        timeout=120,
    )
    return proc.returncode == 0 and output_path.exists()


def reencode_bytes(data: bytes, suffix: str) -> tuple[bytes, str]:
    """Return altered bytes and method label."""
    lower = suffix.lower()
    if lower in (".png", ".jpg", ".jpeg", ".webp"):
        try:
            return _reencode_png_pillow(data), "pillow-reencode"
        except Exception:
            mutated = bytearray(data)
            if len(mutated) > 64:
                mutated[50] ^= 0x01
            return bytes(mutated), "byte-mutate"

    with tempfile.TemporaryDirectory() as tmp:
        inp = Path(tmp) / f"input{suffix}"
        out = Path(tmp) / f"output{suffix}"
        inp.write_bytes(data)
        if _reencode_ffmpeg(inp, out):
            return out.read_bytes(), "ffmpeg-reencode"

    return data + b"\x00", "append-byte"


async def fetch_asset_bytes(url: str, settings: Settings | None = None) -> bytes:
    settings = settings or get_settings()
    local = _local_path_from_url(url, settings)
    if local is not None:
        return local.read_bytes()

    proxy = parse_storage_proxy_url(url)
    if proxy and settings.b2_configured:
        tenant_id, run_id, filename = proxy
        key = object_key(tenant_id, run_id, filename)
        data, _ = fetch_object(key, settings)
        return data

    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


async def tamper_asset_url(asset_url: str, settings: Settings | None = None) -> TamperResult:
    """
    Download asset, re-encode, write tampered copy alongside original.
    Supports /assets/… (local) and /api/storage/… (B2 proxy).
    """
    settings = settings or get_settings()
    proxy_target = parse_storage_proxy_url(asset_url)
    if proxy_target and proxy_target[0] != settings.tenant_id:
        raise ValueError("Tamper demo is scoped to the configured workspace.")

    try:
        original = await fetch_asset_bytes(asset_url, settings)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Could not fetch asset: {exc}") from exc
    original_sha = hashlib.sha256(original).hexdigest()

    suffix = Path(urlparse(asset_url).path).suffix or ".png"
    tampered_bytes, method = reencode_bytes(original, suffix)

    local = _local_path_from_url(asset_url, settings)
    if local is not None:
        tampered_name = local.stem + "-tampered" + local.suffix
        tampered_path = local.parent / tampered_name
        tampered_path.write_bytes(tampered_bytes)
        base = public_base(settings)
        rel = tampered_path.relative_to(Path(__file__).resolve().parents[2] / "demo_assets")
        tampered_url = f"{base}/assets/{rel.as_posix()}"
    else:
        proxy = parse_storage_proxy_url(asset_url)
        if proxy and settings.b2_configured:
            tenant_id, run_id, filename = proxy
            if tenant_id != settings.tenant_id:
                raise ValueError("Tamper demo is scoped to the configured workspace.")
            stem = Path(filename).stem
            ext = Path(filename).suffix or ".png"
            tampered_name = f"{stem}-tampered{ext}"
            key = object_key(tenant_id, run_id, tampered_name)
            put_object_bytes(
                key,
                tampered_bytes,
                content_type="image/png" if ext == ".png" else "application/octet-stream",
                settings=settings,
            )
            tampered_url = storage_proxy_url(tenant_id, run_id, tampered_name, settings)
        else:
            raise ValueError(
                "Tamper demo requires a local /assets/… or /api/storage/… URL."
            )

    tampered_sha = hashlib.sha256(tampered_bytes).hexdigest()
    return TamperResult(
        original_url=asset_url,
        tampered_url=tampered_url,
        original_sha256=original_sha,
        tampered_sha256=tampered_sha,
        method=method,
    )
