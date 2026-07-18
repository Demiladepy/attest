"""Storage URL helper tests."""

from attest.storage.urls import (
    b2_config_warnings,
    parse_storage_proxy_url,
    storage_proxy_url,
    use_storage_proxy,
)


class _Settings:
    b2_configured = True
    b2_public_url_base = ""
    b2_region = "us-east-005"
    api_public_base_url = "http://localhost:8000"


def test_storage_proxy_url():
    url = storage_proxy_url("demo-workspace", "run-abc", "output.png", _Settings())
    assert url == "http://localhost:8000/api/storage/demo-workspace/run-abc/output.png"


def test_parse_storage_proxy_url():
    parsed = parse_storage_proxy_url(
        "http://localhost:8000/api/storage/demo-workspace/run-abc/manifest.json"
    )
    assert parsed == ("demo-workspace", "run-abc", "manifest.json")


def test_use_storage_proxy_when_private_b2():
    assert use_storage_proxy(_Settings()) is True


def test_no_proxy_when_public_base_set():
    class _Pub(_Settings):
        b2_public_url_base = "https://cdn.example.com"

    assert use_storage_proxy(_Pub()) is False


def test_b2_config_warnings_prefer_empty_public_base():
    class _Pub(_Settings):
        b2_public_url_base = "https://attest-dma-2026.s3.us-east-005.backblazeb2.com"
        b2_region = "us-west-004"

    warnings = b2_config_warnings(_Pub())
    assert any("B2_PUBLIC_URL_BASE is set" in w for w in warnings)
    assert any("does not match region" in w for w in warnings)


def test_b2_config_warnings_clean_when_proxy():
    assert b2_config_warnings(_Settings()) == []
