# DEPLOY_ENV_CHECKLIST.md — paste-and-go (A13)

> Generated from live `pin_status` on 2026-07-18: `b2_write_ok: true` (native), `pipeline: gmi`,
> `storage_proxy: true`, `region: us-east-005`, **zero warnings**. Local `.env` is the source of
> truth for secret values — copy from it, never from this file.

## Order of operations

1. Deploy backend (Railway) → note its public URL
2. Deploy frontend (Vercel) → note its public URL
3. Circular deps: `API_PUBLIC_BASE_URL` needs the backend URL, `CORS_ORIGINS` needs the frontend
   URL, `NEXT_PUBLIC_API_URL` needs the backend URL — set placeholders on first deploy, then update
   both services once real URLs exist and redeploy.
4. Smoke: `curl <backend-url>/api/health` → expect `b2_write_ok: true`, `pipeline: "gmi"`, empty `warnings`.

## Backend — Railway (root `backend/`, uses `backend/Dockerfile` or `railway.toml`)

Copy each value from local `backend/.env` unless noted.

| # | Variable | Value | Done |
|---|----------|-------|------|
| 1 | `DEMO_MODE` | `true` | ☐ |
| 2 | `DEBUG` | `false` (do NOT copy local) | ☐ |
| 3 | `TENANT_ID` | `demo-workspace` | ☐ |
| 4 | `CORS_ORIGINS` | `https://<vercel-app-url>` — add `https://app.attest.io,https://verify.attest.io` if DNS lands | ☐ |
| 5 | `DATABASE_URL` | leave unset (SQLite default) — DB is ephemeral on redeploy, acceptable: manifests + assets live in B2 | ☐ |
| 6 | `B2_KEY_ID` | copy | ☐ |
| 7 | `B2_APPLICATION_KEY` | copy | ☐ |
| 8 | `B2_BUCKET` | copy (`attest-dma-2026`) | ☐ |
| 9 | `B2_REGION` | `us-east-005` | ☐ |
| 10 | `B2_PUBLIC_URL_BASE` | **leave unset/empty** — private bucket, proxy URLs | ☐ |
| 11 | `ATTEST_SIGNING_KEY_HEX` | copy — **never rotate**; must match `frontend/public/attest-pubkey.pem` | ☐ |
| 12 | `ATTEST_VERIFY_KEY_HEX` | copy | ☐ |
| 13 | `API_PUBLIC_BASE_URL` | `https://<railway-backend-url>` (no trailing slash) — required, defaults to localhost | ☐ |
| 14 | `GMI_API_KEY` | copy | ☐ |
| 15 | `B2_WEBHOOK_SECRET` | copy only if Event Notifications get wired to the live URL | ☐ |

## Frontend — Vercel (root `frontend/`)

| # | Variable | Value | Done |
|---|----------|-------|------|
| 1 | `NEXT_PUBLIC_API_URL` | `https://<railway-backend-url>` | ☐ |

## Post-deploy smoke (5 min)

```bash
curl https://<backend-url>/api/health   # b2_write_ok true, pipeline gmi, warnings []
```

Then in the browser:

- ☐ Console loads at Vercel URL, no CORS errors in devtools
- ☐ `/verify` loads
- ☐ Set `allow_gmi_burn: true` in `docs/LOOP_STATE.md`, run one hero Generate **on production**
- ☐ Paste resulting proxy URLs into `docs/DEMO_ASSETS.md` (`VERIFY_URL`, `CONSOLE_URL`, `API_HEALTH`)
- ☐ Tamper the hero asset once → confirm red verifier state → pin tampered URL too

## Gotchas already hit locally (don't repeat in prod)

- `B2_PUBLIC_URL_BASE` set → verifier can't fetch private-bucket assets. Leave it empty.
- Region mismatch (`us-west-004` vs bucket `us-east-005`) → warnings in health. Use `us-east-005`.
- S3/boto3 path gave false `InvalidAccessKeyId` — native `b2sdk` is the working path; nothing to configure, just don't "fix" it.
