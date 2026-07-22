# ATTEST

[![CI](https://github.com/Demiladepy/attest/actions/workflows/ci.yml/badge.svg)](https://github.com/Demiladepy/attest/actions/workflows/ci.yml)

**Compliance-grade AI media gateway for the EU AI Act era.**

Every AI-generated asset that leaves an enterprise pipeline ships with embedded C2PA provenance, cryptographic signature, invisible watermark, and a tamper-evident audit trail in Backblaze B2 — turning Article 50 from a €15M legal risk into a 3-second pipeline step.

## 60-second proof (judges)

1. Open the **Verifier** with a pinned asset URL (see `docs/DEMO_ASSETS.md`) — every check goes green: SHA-256, Ed25519 signature, C2PA claim, watermark, lineage.
2. Click **Simulate tamper** — the asset is re-encoded, re-verified, and the verdict flips to a red **Tamper detected**: hash mismatch against the signed manifest, byte-for-byte.
3. Every event (generate, sign, tamper) lands in the **audit log**, and every binary + manifest is durably stored in **Backblaze B2** behind a traversal-guarded proxy.

## Engineering highlights

- **Ed25519 canonical manifest signing** (Genblaze Mode 2 candidate — upstream PR in `genblaze-pr/`), verified independently by a public verifier that re-hashes the canonical manifest.
- **Native B2 storage** (`b2sdk`) with private-bucket API proxy, tenant scoping, and path-traversal guards (tested at the endpoint level).
- **Revision lineage**: reject-and-retry flow links runs via `parent_run_id`; the verifier renders the full ancestry tree.
- **Provider failsafe**: a GMI Cloud outage mid-generation falls back to the simulated pipeline with a visible pipeline step — a live demo can never die.
- **CI on every push**: 23 backend tests + frontend lint + production build.

## Finish-first (hackathon)

**Deadline Aug 3.** Daily autonomous build loop: [`docs/LOOP_STATE.md`](docs/LOOP_STATE.md).  
Exams mode — operator actions only in [`docs/OPERATOR_15MIN.md`](docs/OPERATOR_15MIN.md).

Winning bar: live Console + Verifier (pinned asset) + Genblaze Mode 2 PR + 3-min video + Devpost.

## PM

**Claude** owns product scope, demo script, and rubric alignment. See [`docs/PM.md`](docs/PM.md).

Engineering implements against the PM brief. The [3-minute demo script](docs/DEMO_SCRIPT.md) is the acceptance spec.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Compliance      │     │ FastAPI +        │     │ Backblaze B2    │
│ Console         │────▶│ ComplianceSink   │────▶│ Object Lock     │
│ app.attest.io   │     │ (Genblaze)       │     │ Event Notifs    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                        │
         │               ┌────────┴────────┐
         │               │ Genblaze Pipeline│
         │               │ classify→generate│
         │               │ →sign→watermark  │
         │               └─────────────────┘
         ▼
┌─────────────────┐
│ Public Verifier │
│ verify.attest.io│
└─────────────────┘
```

## Repo layout

| Path | Purpose |
|------|---------|
| `backend/` | FastAPI, ComplianceSink, Genblaze pipeline, audit API |
| `frontend/` | Next.js — Compliance Console + Verifier |
| `genblaze-pr/` | Mode 2 Ed25519 upstream PR — includes cloned `genblaze/` repo |
| `docs/` | PM, demo script, `LOOP_STATE`, deploy, Devpost draft |

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn attest.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

- Console: http://localhost:3000
- Verifier: http://localhost:3000/verify

## Demo mode

Set `DEMO_MODE=true` (default) to run the full pipeline visualizer without provider API keys. Wire B2 + Genblaze providers by filling `.env`.

## Regulatory citations

- EU AI Act **Article 50** — transparency obligations for AI-generated content
- **Code of Practice on Transparency** (June 10, 2026)
- Genblaze [trust modes](https://github.com/backblaze-labs/genblaze/blob/main/docs/features/trust-modes.md)

## License

MIT
