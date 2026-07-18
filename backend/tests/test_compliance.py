from attest.compliance.signing import Ed25519Signer
from attest.compliance.tamper import reencode_bytes
from attest.storage.local import MINIMAL_PNG, persist_run


def test_ed25519_sign_and_verify():
    signer = Ed25519Signer.generate()
    manifest = {"run_id": "test", "outputs": [{"sha256": "abc"}]}
    bundle = signer.sign_manifest(manifest, signed_at="2026-01-01T00:00:00Z")
    assert signer.verify(manifest, bundle)


def test_reencode_changes_hash():
    tampered, method = reencode_bytes(MINIMAL_PNG, ".png")
    assert tampered != MINIMAL_PNG
    assert method in ("pillow-reencode", "byte-mutate")


def test_persist_run_creates_files(tmp_path, monkeypatch):
    import attest.storage.local as local_mod

    monkeypatch.setattr(local_mod, "assets_root", lambda settings=None: tmp_path)
    asset_url, manifest_url, sha = persist_run(
        tenant_id="t",
        run_id="r1",
        manifest={"run_id": "r1"},
        asset_bytes=MINIMAL_PNG,
    )
    assert "/assets/t/r1/output.png" in asset_url
    assert (tmp_path / "t" / "r1" / "output.png").exists()
    assert len(sha) == 64
