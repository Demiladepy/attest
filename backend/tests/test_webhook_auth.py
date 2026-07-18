import hashlib
import hmac

import pytest
from starlette.requests import Request

from attest.services.webhook_auth import verify_b2_webhook


async def _make_request(body: bytes, headers: dict | None = None) -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/webhooks/b2",
        "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
    }

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(scope, receive)


@pytest.mark.asyncio
async def test_webhook_no_secret_allows():
    req = await _make_request(b"{}")
    assert await verify_b2_webhook(req, "") == b"{}"


@pytest.mark.asyncio
async def test_webhook_valid_signature():
    secret = "test-secret"
    body = b'{"event":"upload"}'
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    req = await _make_request(body, {"X-Attest-Signature": f"sha256={sig}"})
    assert await verify_b2_webhook(req, secret) == body
