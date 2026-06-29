# ATTEST Backend

FastAPI service wrapping Genblaze with `ComplianceSink` compliance primitives.

## Run locally

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn attest.main:app --reload --port 8000
```

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/assets` | List compliance-tracked assets |
| `POST /api/assets/generate` | Run compliance pipeline |
| `POST /api/assets/generate/stream` | SSE pipeline visualizer |
| `POST /api/verify` | Public verifier backend |
| `GET /api/audit` | Tamper-evident audit log |
| `POST /api/webhooks/b2` | B2 Event Notifications |

## PM

Product scope is owned by **Claude (PM)**. See [`../docs/PM.md`](../docs/PM.md).
