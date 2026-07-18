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

## Historic local pin (2026-07-01 — not judge URL)

```
ASSET_URL=http://localhost:8000/assets/demo-workspace/14f58170-383f-487c-bd59-7ce8b5109f29/output.png
```
