# DEPLOY_RENDER.md — backend live in ~5 minutes

> **Note (2026):** Render retired its free web-service tier (Apr 23, 2026). The
> blueprint uses the **Starter** plan (~$7/mo) and Render will require a card at
> deploy. Cancel the service after the hackathon. Prefer no card? Use a Hugging
> Face Docker Space instead — ask and I'll wire it.

The blueprint (`render.yaml`) does everything except the parts only your account can
do: adding payment, connecting GitHub, and pasting secrets.

## 1. Create the service
- **One click:** the *Deploy to Render* button in the repo README, **or**
- **Manual:** **https://dashboard.render.com** → **New +** → **Blueprint** → pick
  **Demiladepy/attest** → **Apply**. Render reads `render.yaml` and creates the
  Starter Docker web service `attest-api` (add a card when prompted).

## 2. Paste the prompted values
Render will prompt for the `sync: false` variables. Copy each from local `backend/.env`:

| Variable | Where from | Note |
|----------|-----------|------|
| `B2_KEY_ID` | `.env` | |
| `B2_APPLICATION_KEY` | `.env` | secret |
| `ATTEST_SIGNING_KEY_HEX` | `.env` | secret — **never rotate** |
| `ATTEST_VERIFY_KEY_HEX` | `.env` | public key, but paste anyway |
| `GMI_API_KEY` | `.env` | secret |
| `API_PUBLIC_BASE_URL` | leave blank for now | fill in step 4 |

Click **Apply / Deploy**. First Docker build takes ~3–5 min.

## 3. Verify it booted
Render shows a URL like `https://attest-api-xxxx.onrender.com`. Test:
```
https://attest-api-xxxx.onrender.com/api/health
```
Expect `"b2_write_ok": true`, `"pipeline": "gmi"`, `"warnings": []`.

> Free tier sleeps after ~15 min idle; first hit after sleep takes ~30s to wake.
> For the demo/video, hit the URL once to warm it before recording.

## 4. Point the service at itself
In Render → the service → **Environment** → set:
```
API_PUBLIC_BASE_URL = https://attest-api-xxxx.onrender.com
```
Save → it redeploys. (This makes `/api/storage/…` proxy URLs absolute.)

## 5. Tell me the URL — I finish the rest
Paste the `onrender.com` URL here and I will:
```bash
cd frontend
vercel env add NEXT_PUBLIC_API_URL production   # your Render URL
vercel --prod                                    # redeploy
```
Then the live Console/Verifier stop showing "API unreachable" and light up with
real data — generate, sign, verify, tamper, audit, all live.

## 6. Hero pin (once live)
Set `allow_gmi_burn: true` in `docs/LOOP_STATE.md`, then from local:
```
cd backend && .\.venv\Scripts\python -m attest.scripts.gmi_smoke --full
```
It registers in the Console DB and prints the judge-pasteable VERIFY_URL.
