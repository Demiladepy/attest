# DEPLOY_OPENSHIP.md — backend on OpenShip

OpenShip (openship.io, github.com/oblien/openship) is self-hosted, so unlike Vercel
there is **no hosted endpoint to push to** — you deploy to a server you own running
OpenShip. This guide assumes that server exists.

## Prerequisite (one-time, operator)

You need an OpenShip instance before anything can deploy:

1. A VPS / dedicated server / cloud VM you control (any provider, or a homelab box).
2. OpenShip installed on it (see openship.io install docs).
3. Access via **one** of: the web dashboard, the CLI, or the MCP connector.

Until that instance exists and is reachable, the backend cannot be deployed to it —
there is no server to receive it. Everything below is ready to go the moment it does.

## What OpenShip consumes

The backend is already Docker + Git based, which is exactly OpenShip's model:

| OpenShip concept | ATTEST value |
|------------------|--------------|
| Source | `github.com/Demiladepy/attest`, root `backend/` |
| Build | `backend/Dockerfile` (Docker deployment) |
| Port | container honors injected `$PORT` (defaults 8000) |
| Health check | `GET /api/health` (expect `b2_write_ok:true`, `pipeline:gmi`) |
| SSL / domain | OpenShip automatic SSL + domain |
| Secrets | OpenShip secrets management (table below) |

## Deploy steps (once the instance exists)

### Via dashboard / CLI
1. New Application → connect `github.com/Demiladepy/attest`.
2. Root directory `backend/`, build from `Dockerfile`.
3. Set env vars + secrets (below).
4. Health check path `/api/health`.
5. Deploy (Git-based, zero-downtime). Note the assigned URL.

### Via MCP (agent-driven)
If you connect OpenShip's MCP connector to this session, I can drive the create +
deploy directly — tell me once it's connected. I still won't handle raw secret
values; set `ATTEST_SIGNING_KEY_HEX`, `B2_APPLICATION_KEY`, and `GMI_API_KEY` in
OpenShip's secrets UI yourself.

## Env vars & secrets (same matrix as DEPLOY_ENV_CHECKLIST.md)

| Variable | Kind | Value |
|----------|------|-------|
| `DEMO_MODE` | env | `true` |
| `DEBUG` | env | `false` |
| `TENANT_ID` | env | `demo-workspace` |
| `CORS_ORIGINS` | env | `https://attest-black-two.vercel.app` (+ any custom domain) |
| `B2_REGION` | env | `us-east-005` |
| `B2_PUBLIC_URL_BASE` | env | *(leave empty — private bucket + proxy)* |
| `API_PUBLIC_BASE_URL` | env | the OpenShip-assigned backend URL (no trailing slash) |
| `B2_BUCKET` | env | `attest-dma-2026` |
| `B2_KEY_ID` | secret | from local `.env` |
| `B2_APPLICATION_KEY` | secret | from local `.env` |
| `ATTEST_SIGNING_KEY_HEX` | secret | from local `.env` — **never rotate** |
| `ATTEST_VERIFY_KEY_HEX` | secret | from local `.env` |
| `GMI_API_KEY` | secret | from local `.env` |

## After the backend is live — connect the frontend

The Vercel frontend is already deployed but points at localhost. Once you have the
OpenShip backend URL:

```bash
cd frontend
vercel env add NEXT_PUBLIC_API_URL production   # paste the OpenShip URL
vercel --prod                                    # redeploy
```

Then smoke test: open the Vercel Console — the "API unreachable" banner should be
gone and the audit log should populate.

## Note on state
SQLite lives in the container filesystem, so a redeploy resets the assets DB. Assets
and manifests persist in B2 regardless. If you want the Console history to survive
redeploys, provision an OpenShip **PostgreSQL** service (one click) and set
`DATABASE_URL` to it — optional, not required for the demo.
