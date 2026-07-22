"""Endpoint-level guards: traversal, tenant scoping, input validation."""

import pytest
from fastapi.testclient import TestClient

from attest.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_storage_proxy_rejects_wrong_tenant(client):
    resp = client.get("/api/storage/other-tenant/run/output.png")
    assert resp.status_code == 404


def test_storage_proxy_rejects_traversal(client):
    for path in (
        "/api/storage/demo-workspace/run/%2e%2e%2f%2e%2e%2f.env",
        "/api/storage/demo-workspace/run/sub%5c..%5c..%5cx",
        "/api/storage/demo-workspace/run/a//b.png",
    ):
        resp = client.get(path)
        assert resp.status_code == 404, path


def test_tamper_scoped_to_configured_tenant(client):
    resp = client.post(
        "/api/tamper",
        json={"asset_url": "http://localhost:8000/api/storage/other-tenant/x/y.png"},
    )
    assert resp.status_code == 400
    assert "scoped" in resp.json()["detail"]


def test_stream_generate_validates_input(client):
    resp = client.post("/api/assets/generate/stream", json={"brief": "short"})
    assert resp.status_code == 422
