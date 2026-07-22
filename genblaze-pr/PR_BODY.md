# Mode 2: Ed25519 Manifest Signing

## Summary

Implements **Trust Mode 2 — Authenticated integrity** from [`docs/features/trust-modes.md`](docs/features/trust-modes.md).

Adds optional Ed25519 signing via `genblaze_core.signing`, behind the `signing` extra (`cryptography`).

Reference consumer: [ATTEST](https://github.com/Demiladepy/attest) — EU AI Act Article 50 compliance gateway built on Genblaze + B2.

## Motivation

Mode 1 proves integrity but not authorship. Article 50 and enterprise compliance buyers need manifests only a trusted pipeline key could produce. The `Manifest.signature` field was reserved for this; this PR fills it.

## Complements v0.6.0 `verify --fetch`

v0.6.0 added byte-level output verification (`genblaze verify --fetch` re-hashes each asset against the manifest's committed `sha256`). That proves an asset's **bytes are unmodified**; Mode 2 proves the manifest was **authored by a trusted key**. Together they close the full chain — *this pipeline produced it* **and** *nothing changed since* — which is exactly the provenance guarantee Article 50 transparency obligations call for. Rebases cleanly onto `main` at the 0.6.0 wave (`ce65121`); the `signing/` module is purely additive.

## API

```python
from genblaze_core.signing import Ed25519Signer, verify_signature_bundle

signer = Ed25519Signer.from_env("GENBLAZE_SIGNING_KEY_HEX")
bundle = signer.sign_manifest(manifest_dict, signed_at="2026-06-29T12:00:00Z")
manifest.signature = bundle.to_json()
assert verify_signature_bundle(manifest_dict, bundle)
```

## Design

- Canonical payload excludes `signature`, `manifest_uri`, `encryption_scheme` (transport metadata)
- Signs SHA-256 hex digest of canonical JSON (same pattern as ATTEST `backend/attest/compliance/signing.py`)
- Optional extra keeps core dependency-light
- Tests in `libs/core/tests/unit/test_ed25519_signing.py`

## Checklist

- [x] `Ed25519Signer`, `SignatureBundle`, `verify_signature_bundle`
- [x] Optional `[signing]` extra
- [x] Lazy exports on `genblaze_core`
- [x] trust-modes.md updated
- [ ] CLI `genblaze sign` / `genblaze verify-signature` (follow-up)

## Reviewers

@ppatterson @jdeleon — per trust-modes roadmap and hackathon collaboration.

**Do not merge from this fork** — open from operator's fork of `backblaze-labs/genblaze`. Copy this branch to your fork and submit.
