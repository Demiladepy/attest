"""Optional B2 credential probe for health checks."""

from __future__ import annotations

import time

from attest.config import Settings, get_settings

# The console pings /api/health on every page load and platform healthchecks
# poll it too — don't pay a real B2 upload each time.
_PROBE_TTL_SECONDS = 300
_probe_cache: tuple[float, bool, str] | None = None


def b2_write_probe(settings: Settings | None = None, *, force: bool = False) -> tuple[bool, str]:
    """Try a tiny native B2 upload. Returns (ok, detail). Cached for 5 minutes."""
    global _probe_cache
    settings = settings or get_settings()
    if not settings.b2_configured:
        return False, "not_configured"

    now = time.monotonic()
    if not force and _probe_cache and now - _probe_cache[0] < _PROBE_TTL_SECONDS:
        return _probe_cache[1], _probe_cache[2]

    try:
        from attest.storage.b2 import put_object_bytes

        key = f".attest-probe/{settings.tenant_id}/ping.txt"
        put_object_bytes(key, b"ok", content_type="text/plain", settings=settings)
        result = (True, "ok_native")
    except Exception as exc:
        result = (False, str(exc).split("\n")[0][:120])

    _probe_cache = (now, result[0], result[1])
    return result
