# ATTEST

**Compliance-grade AI media gateway for the EU AI Act era.**

Every AI-generated asset that leaves an enterprise pipeline ships with embedded C2PA provenance, cryptographic signature, invisible watermark, and a tamper-evident audit trail in Backblaze B2 — turning Article 50 from a €15M legal risk into a 3-second pipeline step.

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
