# CLAUDE_HANDOFF.md

> **Purpose:** This file is the source of truth for any AI assistant (Cursor, Claude, Copilot) working on ATTEST when the human operator's session limits are exhausted, the operator is away, or context has been lost. Read this file completely before touching code.

## What ATTEST is

A compliance-grade AI media gateway demonstrating EU AI Act Article 50 readiness. Every AI-generated asset ships with embedded provenance (Ed25519 signature, C2PA-candidate manifest, invisible watermark, tamper-evident B2 storage). Built on Backblaze Genblaze + B2 for the Backblaze Generative AI Media Hackathon. Submission deadline: **August 3, 2026.**

## Operator

Demilade Ayeku. Working solo. Stack preferences: Next.js + TypeScript frontend, FastAPI + Python backend. Communication style: direct, no filler, technical depth preferred. Pushes back on sycophancy — disagree when you have grounds.

## PM

**Claude** owns product scope, demo script, and rubric alignment. See `docs/PM.md`. If this file disagrees with the PM brief on product scope, ask the operator. Rubric grading follows Backblaze criteria (B2 + Genblaze are non-negotiable; full C2PA library is deferrable).

## Current state (update this section at end of every session)

**Last updated:** 2026-07-18
**Current block:** Finish-first Tier 0 (deploy + pin + PR + video + Devpost)
**Daily loop:** `docs/LOOP_STATE.md` — 24h wake `AGENT_LOOP_WAKE_attest_finish`. Operator exams; agent does A-queue only unless `allow_gmi_burn`.
**Last completed:**
- **A-queue complete (A1–A13).** `.env` fixed live: `B2_REGION=us-east-005`, `B2_PUBLIC_URL_BASE` cleared (had dup-key paste typo) → `pin_status` **zero warnings**, `storage_proxy: true`, `b2_write_ok: true` native, pytest 14 passed (2026-07-18)
- `docs/DEPLOY_ENV_CHECKLIST.md` — paste-and-go env table for Railway + Vercel incl. `API_PUBLIC_BASE_URL` (not in local `.env`, defaults localhost — required in prod)
- GMI live (`DeepSeek-V4-Pro` classify + seedream image); B2 native `b2sdk`; `/api/storage/…` proxy; lineage tree; tamper; deploy configs; all finish-first docs
**Next item (agent):** none — all remaining work is B-queue (operator)
**Next item (operator):** B3 deploy via `docs/DEPLOY_ENV_CHECKLIST.md` → then B2 hero pin on production → B4 PR → B5 video → B6 Devpost. Target: submit by Aug 1
**Known broken / weak:** Object Lock disabled on bucket; no live domains; VERIFY_URL not production-pinned; SQLite is ephemeral on Railway redeploys (accepted — B2 holds assets/manifests)

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
- [x] Local dev: real fetchable URLs via `/assets/` static mount
- [x] Call `record_event()` from SSE path in `main.py`
- [x] Audit log UI on Console
- [x] B2 durable URLs via `persist_compliant_run()` + API proxy for private buckets
- [ ] Pin production VERIFY_URL in `docs/DEMO_ASSETS.md` (hero GMI + B2 after allow_gmi_burn)

### Block 2: Multi-step pipeline + tamper beat (July 5 – 11)
- [x] GMI classifier + image path when `GMI_API_KEY` configured (`genblaze_gmi.py`)
- [ ] ElevenLabs + AssemblyAI steps (stubs — deferred)
- [x] Tamper simulation (local re-encode + API + verifier UI)
- [x] Verifier red state for tampered URL
- [x] Audit log UI panel on Console
- [x] parent_run_id revise flow in Console
- [x] Lineage tree in verifier UI
- [ ] TrustMark on image outputs (deferred)

### Block 3: Upstream PR + deploy (July 12 – 18)
- [x] Branch `feat/mode2-ed25519-signer` + signing module in genblaze clone
- [x] PR body draft (`genblaze-pr/PR_BODY.md`)
- [ ] Operator opens PR on GitHub
- [x] Deploy configs (Docker/Railway/Render/Vercel) — see `docs/DEPLOY.md`
- [ ] Live deploy at app.attest.io / verify.attest.io
- [x] B2 webhook signature validation

### Block 4: Lineage + second asset + content (July 19 – 25)
- [x] parent_run_id wired in Console UI (revise flow)
- [x] Lineage tree visualization in verifier
- [ ] One video demo asset (deferred — burn credits carefully)
- [ ] dev.to + LinkedIn posts (optional)

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
- `boto3`, `b2sdk`, `httpx`, `pytest`, `pytest-asyncio`, `genblaze-gmicloud`, `Pillow`
- Standard FastAPI / Next.js ecosystem packages

## Useful commands

```bash
cd backend && .\.venv\Scripts\uvicorn attest.main:app --reload --port 8000
cd frontend && npm run dev
cd backend && .\.venv\Scripts\pytest
docker compose up --build
python -m attest.scripts.verify_url <url>
python -m attest.scripts.tamper_cli <url>
# Genblaze PR branch: cd genblaze-pr/genblaze && git log feat/mode2-ed25519-signer -1
```

## Open questions for the operator

- Should tamper demo use ffmpeg re-encode or byte flip? (Plan says re-encode.)

---

**This file is the source of truth for session handoff. If it disagrees with the audit, PM brief, or demo script on *scope*, ask the operator before acting.**
