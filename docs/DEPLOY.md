# ATTEST — Deploy (finish-first)

## Architecture

| Service | Platform | Target URL |
|---------|----------|------------|
| Frontend | Vercel | `app.attest.io`, `verify.attest.io` |
| Backend | Railway or Render | `api.attest.io` |

Fallback if DNS missing: use platform URLs and put them in Devpost.

## Backend env (Railway / Render)

Root directory: `backend/`  
Start: `uvicorn attest.main:app --host 0.0.0.0 --port $PORT`  
Or use `backend/Dockerfile`.

| Variable | Required | Notes |
|----------|----------|-------|
| `ATTEST_SIGNING_KEY_HEX` | yes | Same as local — **do not rotate** |
| `ATTEST_VERIFY_KEY_HEX` | yes | Match `frontend/public/attest-pubkey.pem` |
| `API_PUBLIC_BASE_URL` | yes | Public API origin (used for `/api/storage/…` URLs) |
| `CORS_ORIGINS` | yes | Console + verifier origins |
| `DEMO_MODE` | yes | `true` keeps SSE visualizer speed; GMI still runs when keys ready |
| `B2_KEY_ID` / `B2_APPLICATION_KEY` / `B2_BUCKET` | yes | Native B2 API (`b2sdk`) — Master Key OK |
| `B2_REGION` | yes | Match bucket endpoint (e.g. `us-east-005`) |
| `B2_PUBLIC_URL_BASE` | no | **Leave empty** for private buckets (proxy URLs) |
| `GMI_API_KEY` | for real image | Devpost credits |
| `B2_WEBHOOK_SECRET` | no | Only when Event Notifications wired |

## Frontend env (Vercel)

Root: `frontend/`  
`NEXT_PUBLIC_API_URL=https://api.attest.io` (or Railway URL)

## DNS (optional but ideal)

```
app.attest.io     → CNAME Vercel
verify.attest.io  → CNAME Vercel
api.attest.io     → CNAME Railway/Render
```

## Smoke after deploy

```bash
curl https://api…/api/health
# expect: status ok, b2_write_ok true, pipeline gmi|demo
```

Then Console → Generate (or pin existing B2 asset) → Verifier deep link → Tamper red.

## Genblaze PR (operator only)

```bash
cd genblaze-pr/genblaze
git push -u origin feat/mode2-ed25519-signer
# Open PR with genblaze-pr/PR_BODY.md
```

## Local compose

```bash
docker compose up --build
```
