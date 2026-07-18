"""Optional B2 credential probe for health checks."""

from __future__ import annotations

from attest.config import Settings, get_settings


def b2_write_probe(settings: Settings | None = None) -> tuple[bool, str]:
    """Try a tiny native B2 upload. Returns (ok, detail)."""
    settings = settings or get_settings()
    if not settings.b2_configured:
        return False, "not_configured"

    try:
        from attest.storage.b2 import put_object_bytes

        key = f".attest-probe/{settings.tenant_id}/ping.txt"
        put_object_bytes(key, b"ok", content_type="text/plain", settings=settings)
        return True, "ok_native"
    except Exception as exc:
        return False, str(exc).split("\n")[0][:120]
