# DEPLOY_HF.md — backend on Hugging Face (requires PRO)

> **2026 update:** Hugging Face now requires a **PRO subscription ($9/mo)** to host
> Gradio/Docker Spaces on cpu-basic (only *static* Spaces are free). Confirmed via a
> 402 on `create_repo`. So this is **not** the cheap path — Railway Hobby (~$5) or
> Render ($7) are cheaper. Keep this only if you already have HF PRO. The script
> below still works once PRO is active.

A script does the create + upload + all non-secret config; you do the login and
paste 4 secrets.

## 1. Log in (one-time, ~1 min — only you can do this)
1. Make a free account at **https://huggingface.co** if you don't have one.
2. Create a **WRITE** token: https://huggingface.co/settings/tokens → New token → role **Write**.
3. In a terminal:
   ```
   huggingface-cli login
   ```
   Paste the WRITE token when prompted.

## 2. Deploy (I can run this for you once you're logged in)
```
cd backend
.\.venv\Scripts\python -m attest.scripts.deploy_hf_space
```
This creates the Space `you/attest-api`, uploads the backend, and sets every
non-secret variable (DEMO_MODE, CORS, region, bucket, API base URL, public verify
key, port). It prints your Space URL.

## 3. Set the 4 secrets in the Space UI (only you)
Space → **Settings → Variables and secrets → New secret** — copy each value from
local `backend/.env`:
- `B2_KEY_ID`
- `B2_APPLICATION_KEY`
- `ATTEST_SIGNING_KEY_HEX`  (never rotate)
- `GMI_API_KEY`

The Space rebuilds automatically. First Docker build ~3–5 min.

## 4. Verify
```
https://<you>-attest-api.hf.space/api/health
```
Expect `"b2_write_ok": true`, `"pipeline": "gmi"`, `"warnings": []`.

> Free Spaces sleep when idle and cold-start in ~30s. Hit the URL once to warm it
> before recording the demo.

## 5. Tell me the Space URL — I finish the rest
I'll wire `NEXT_PUBLIC_API_URL` into Vercel and redeploy the frontend, then the live
Console/Verifier light up with real data. Then one command pins the hero asset.

## Notes
- `deploy_hf_space.py` never uploads `.env` and never sets secret values.
- Re-run the script any time to push code updates to the Space.
- SQLite/asset files are ephemeral on the Space; B2 holds the durable copies.
