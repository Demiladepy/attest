# CLAUDE_HANDOFF.md

> **Purpose:** This file is the source of truth for any AI assistant (Cursor, Claude, Copilot) working on ATTEST when the human operator's session limits are exhausted, the operator is away, or context has been lost. Read this file completely before touching code.

## What ATTEST is

A compliance-grade AI media gateway demonstrating EU AI Act Article 50 readiness. Every AI-generated asset ships with embedded provenance (Ed25519 signature, C2PA-candidate manifest, invisible watermark, tamper-evident B2 storage). Built on Backblaze Genblaze + B2 for the Backblaze Generative AI Media Hackathon. Submission deadline: **August 3, 2026.**

## Operator

Demilade Ayeku. Working solo. Stack preferences: Next.js + TypeScript frontend, FastAPI + Python backend. Communication style: direct, no filler, technical depth preferred. Pushes back on sycophancy — disagree when you have grounds.

## PM

**Claude** owns product scope, demo script, and rubric alignment. See `docs/PM.md`. If this file disagrees with the PM brief on product scope, ask the operator. Rubric grading follows Backblaze criteria (B2 + Genblaze are non-negotiable; full C2PA library is deferrable).

## Current state (update this section at end of every session)

**Last updated:** 2026-06-29
**Current block:** Block 1 — Make one end-to-end path real
**Last completed:** CLAUDE_HANDOFF.md added; stable Ed25519 keypair generated (Block 1 item 1)
**Next item:** Wire ObjectStorageSink into one real Genblaze Pipeline (image, FLUX via Replicate)
**Blockers:** B2 credentials not yet configured in `.env`
**Known broken:** Demo URLs are still string-concatenated (runner.py L147–149); verifier 404s on generated URLs until B2 upload is wired

## Non-negotiables — never violate these without operator approval

1. **Do not delete the SSE visualizer in `pipeline/runner.py` and `PipelineVisualizer.tsx`.** It is the strongest demo asset.
2. **Do not regenerate the Ed25519 signing key.** It lives in `.env` as `ATTEST_SIGNING_KEY_HEX`. The public key in `frontend/public/attest-pubkey.pem` must match.
3. **Do not commit any `.env`, `.env.local`, or API keys.** Check `.gitignore` before every commit.
4. **Do not change the manifest schema** without bumping a version field and updating `verify.py`.
5. **Do not introduce blockchain, on-chain attestation, or smart contracts.** Object Lock + Ed25519 + B2 audit log is sufficient.
6. **Do not add C2PA full library (c2pa-python) integration** unless explicitly instructed. Intentionally deferred to roadmap.
7. **Do not migrate SQLite → Postgres** during the hackathon.
8. **Do not refactor working code** that isn't on the critical path.

## Architecture — read before changing anything

- **Frontend:** Next.js (App Router) + Tailwind. Compliance Console at `/`, public verifier at `/verify`.
- **Backend:** FastAPI in `backend/attest/`. Pipeline in `pipeline/runner.py`. Compliance in `compliance/` (signing.py, verify.py, sink.py).
- **Storage:** SQLite for audit log + asset metadata. B2 for binary assets + signed manifests. Object Lock on signed manifests.
- **Pipeline:** Genblaze Pipeline + ComplianceSink. Multi-provider with fallback chains.
- **Providers in scope:** GMI Cloud (classifier), FLUX via Replicate (image), ElevenLabs (voice), AssemblyAI (transcript), Wan/Seedance via GMI (video — hero asset only).

## Demo script — the contract

`docs/DEMO_SCRIPT.md` is the acceptance spec for demo beats. Rubric grading follows Backblaze criteria — see PM brief. Three judge-pasteable URLs:

1. `app.attest.io` — Compliance Console
2. `verify.attest.io/?asset=<demo_asset_url>` — real verified asset
3. GitHub PR URL — Mode 2 signer in `backblaze-labs/genblaze`

## Roadmap

### Block 1: Make one end-to-end path real (June 30 – July 4)
- [x] Stable Ed25519 keypair in `.env` + public key in `frontend/public/attest-pubkey.pem`
- [ ] Replace `base_url + tenant_id + run_id` string concat with real durable URL from sink
- [ ] Wire `ObjectStorageSink` into one real Genblaze Pipeline (image only, FLUX via Replicate)
- [ ] Apply Object Lock programmatically on signed manifest upload
- [ ] Generate one demo asset end-to-end, save B2 URL in `docs/DEMO_ASSETS.md`
- [ ] Call `record_event()` from SSE path in `main.py` at every state transition

### Block 2: Multi-step pipeline + tamper beat (July 5 – 11)
- [ ] 4-step real pipeline: GMI classifier → FLUX → ElevenLabs → AssemblyAI
- [ ] `tamper.py`: download → ffmpeg re-encode → re-upload
- [ ] Verifier red state for tampered URL
- [ ] Audit log UI panel on Console
- [ ] TrustMark on image outputs

### Block 3: Upstream PR + deploy (July 12 – 18)
- [ ] Fork genblaze, branch `feat/mode2-ed25519-signer`
- [ ] Port signing.py into genblaze core
- [ ] Open PR
- [ ] Deploy backend + frontend
- [ ] DNS for app.attest.io and verify.attest.io
- [ ] B2 webhook signature validation

### Block 4: Lineage + second asset + content (July 19 – 25)
- [ ] parent_run_id end-to-end in Console
- [ ] Lineage tree in verifier
- [ ] One video demo asset
- [ ] dev.to + LinkedIn posts published

### Block 5: Polish + submit (July 26 – Aug 2)
- [ ] Record 3-minute demo
- [ ] Devpost copy
- [ ] Submit Mon/Tue before deadline

## When the operator is unavailable

1. Open current block in roadmap.
2. Identify next unchecked item.
3. Write one-paragraph plan before coding.
4. Smallest change that completes the item.
5. Update "Current state" in this file.
6. Commit: `[Block N] short description — session [DATE]`.
7. Stop unless roadmap explicitly chains items.

## Forbidden without operator approval

- `git push --force`
- Deleting `.env` or rotating keys
- Opening upstream PR to backblaze-labs/genblaze (operator opens personally)
- Modifying `docs/DEMO_SCRIPT.md`
- Submitting Devpost
- C2PA full library integration

## Approved package additions

- `trustmark` (Block 2)
- `boto3`, `httpx`, `pytest`, `pytest-asyncio`
- Standard FastAPI / Next.js ecosystem packages

## Useful commands

```bash
cd backend && .\.venv\Scripts\uvicorn attest.main:app --reload --port 8000
cd frontend && npm run dev
cd backend && .\.venv\Scripts\pytest
```

## Open questions for the operator

- Should tamper demo use ffmpeg re-encode or byte flip? (Plan says re-encode.)

---

**This file is the source of truth for session handoff. If it disagrees with the audit, PM brief, or demo script on *scope*, ask the operator before acting.**
