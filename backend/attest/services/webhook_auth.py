"""B2 Event Notifications webhook verification."""

from __future__ import annotations

import hashlib
import hmac

from fastapi import HTTPException, Request


async def verify_b2_webhook(request: Request, secret: str) -> bytes:
    """
    Verify inbound webhook when B2_WEBHOOK_SECRET is configured.
    Expects X-Attest-Signature: sha256=<hex hmac of raw body>.
    """
    body = await request.body()
    if not secret:
        return body

    header = request.headers.get("X-Attest-Signature", "")
    if not header.startswith("sha256="):
        raise HTTPException(status_code=401, detail="Missing or invalid webhook signature")

    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    provided = header.removeprefix("sha256=")
    if not hmac.compare_digest(expected, provided):
        raise HTTPException(status_code=401, detail="Webhook signature mismatch")
    return body
