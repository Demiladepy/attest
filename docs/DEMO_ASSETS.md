# Demo assets

Judge-pasteable URLs for Devpost. **Only pin production or stable API URLs here.**

## Status (2026-07-13)

| Slot | State |
|------|--------|
| Local GMI smoke (Jul 1) | Historic — may be local `/assets/` only |
| Production VERIFY_URL | **EMPTY — next hero pin after `allow_gmi_burn: true` + B2 OK** |
| Tampered demo URL | Fill after live tamper beat |
| Genblaze PR | Operator opens — paste URL |
| Demo video | Paste after recording |

## Pin for Devpost (fill these)

```
CONSOLE_URL=
VERIFY_URL=
API_HEALTH=
GENBLAZE_PR=
DEMO_VIDEO=
```

### VERIFY_URL shape (private B2 + proxy)

```
https://<api-host>/api/storage/demo-workspace/<run_id>/output.png
https://<api-host>/api/storage/demo-workspace/<run_id>/manifest.json

Verifier:
https://<app-host>/verify?asset=<asset>&manifest=<manifest>
```

## Local patterns (dev only — not for judges)

```
http://localhost:8000/assets/demo-workspace/{run_id}/output.png
http://localhost:8000/api/storage/demo-workspace/{run_id}/output.png
```

Check status without spending GMI:

```bash
cd backend
.\.venv\Scripts\python -m attest.scripts.pin_status
```

Hero generate (costs GMI):

```bash
.\.venv\Scripts\python -m attest.scripts.gmi_smoke --full
```

## Local pin (2026-07-18 — signed post-canonicalization-fix, B2-backed, not judge URL)

```
ASSET_URL=http://localhost:8000/api/storage/demo-workspace/0c13df8b-ee35-4e0b-b720-52be995d197b/output.png
MANIFEST_URL=http://localhost:8000/api/storage/demo-workspace/0c13df8b-ee35-4e0b-b720-52be995d197b/manifest.json
```

> ⚠️ Assets generated **before 2026-07-18** (e.g. run `14f58170…`) fail Ed25519 verification by
> design: they were signed with the pre-fix canonicalization (attest stub included in the signed
> payload). Do not use them for the pass beat. Regenerate instead.
