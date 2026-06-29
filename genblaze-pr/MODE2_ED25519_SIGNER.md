# Mode 2: Ed25519 Manifest Signing for Genblaze

**ATTEST upstream contribution** — reference implementation of Genblaze trust Mode 2.

## Summary

Adds optional Ed25519 signing to `Manifest` persistence so downstream verifiers can
cryptographically attest that a manifest has not been altered since the pipeline run.

Aligns with [trust-modes.md](https://github.com/backblaze-labs/genblaze/blob/main/docs/features/trust-modes.md) Mode 2.

## Proposed API

```python
from genblaze_core import ManifestSigner, Ed25519Signer

signer = Ed25519Signer.from_env("GENBLAZE_SIGNING_KEY_HEX")
signed = signer.sign_manifest(manifest.to_dict())
manifest.attest = {"signature": signed.to_dict()}
```

## Verification

```python
Manifest.verify(manifest_dict)  # existing sha256 checks
Ed25519Signer.verify(manifest_dict, manifest_dict["attest"]["signature"])
```

## Design notes

- Canonical JSON: `sort_keys=True`, `separators=(",", ":")`
- Sign the manifest **without** the `attest` block; store signature inside `attest`
- Public key embedded in signature bundle for verifier-only deployments
- Optional: integrate with `ObjectStorageSink` via `manifest_lock` for storage-layer immutability

## Tags

@ppatterson @jdeleon — per Backblaze Genblaze trust roadmap.

## Status

Draft PR — opened during ATTEST hackathon build.

- **Upstream clone:** `genblaze-pr/genblaze/` (local fork workspace)
- **Reference implementation:** `backend/attest/compliance/signing.py`
- **Trust modes doc (local):** `genblaze-pr/genblaze/docs/features/trust-modes.md`
