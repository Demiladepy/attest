"""Demo failsafe: GMI outage must complete via the simulated pipeline."""

import asyncio as _asyncio

_real_sleep = _asyncio.sleep


async def _fast_sleep(_seconds: float) -> None:
    await _real_sleep(0)

import hashlib

import pytest

import attest.compliance.sink as sink_mod
import attest.pipeline.genblaze_gmi as gmi_mod
import attest.pipeline.runner as runner_mod
from attest.compliance.signing import Ed25519Signer
from attest.pipeline.runner import PipelineStepEvent, run_genblaze_pipeline


@pytest.mark.asyncio
async def test_gmi_failure_falls_back_to_demo(monkeypatch):
    async def _boom(**kwargs):
        raise RuntimeError("GMI 503 upstream")

    def _fake_persist(*, tenant_id, run_id, manifest, asset_bytes, asset_name="output.png"):
        sha = hashlib.sha256(asset_bytes).hexdigest()
        base = f"http://test/{tenant_id}/{run_id}"
        return f"{base}/{asset_name}", f"{base}/manifest.json", sha

    monkeypatch.setattr(gmi_mod, "run_gmi_pipeline", _boom)
    monkeypatch.setattr(gmi_mod, "is_configured", lambda settings=None: True)
    monkeypatch.setattr(runner_mod, "persist_compliant_run", _fake_persist)
    # CI has no ATTEST_SIGNING_KEY_HEX — sign with an ephemeral test key
    _test_signer = Ed25519Signer.generate()
    monkeypatch.setattr(sink_mod, "get_signer", lambda settings=None: _test_signer)
    # Keep the fallback demo run fast
    monkeypatch.setattr(runner_mod.asyncio, "sleep", _fast_sleep)

    seen: list[PipelineStepEvent] = []

    async def collector(event: PipelineStepEvent) -> None:
        seen.append(event)

    result = await run_genblaze_pipeline(
        asset_id="test-fallback",
        brief="fallback brief for provider outage",
        on_step=collector,
    )

    assert result.run_id
    assert result.sha256
    fallback_events = [e for e in seen if e.step_id == "provider-fallback"]
    assert len(fallback_events) == 1
    assert "GMI unavailable" in fallback_events[0].label
