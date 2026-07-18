# OPERATOR_15MIN.md — Between exams

Do these only when you have a spare 15–30 minutes. Agent handles the rest daily.

## Priority order

1. **Restart backend once** and open `http://localhost:8000/api/health`  
   Need: `"b2_write_ok": true`, `"pipeline": "gmi"` (or `demo` if GMI key off).

2. **`.env` sanity** (backend):
   ```env
   B2_REGION=us-east-005
   B2_PUBLIC_URL_BASE=
   GMI_API_KEY=<set>
   DEMO_MODE=true
   ```
   Leave `B2_PUBLIC_URL_BASE` empty for private bucket + `/api/storage/…` proxy.
   If `pin_status` / `/api/health` `warnings` mention region mismatch, fix region or clear the public base.

3. **When agent asks to burn GMI for hero asset:** set in `docs/LOOP_STATE.md`:
   ```yaml
   allow_gmi_burn: true
   ```
   Then run Generate once (or `python -m attest.scripts.gmi_smoke --full`). Paste resulting URLs into `docs/DEMO_ASSETS.md` VERIFY_URL.

4. **Deploy (when ready):** follow `docs/DEPLOY.md`. Secrets from local `.env` — never commit.

5. **Open Genblaze PR (you only):**
   ```bash
   cd genblaze-pr/genblaze
   git push -u origin feat/mode2-ed25519-signer
   ```
   Use body in `genblaze-pr/PR_BODY.md` against `backblaze-labs/genblaze`.

6. **Record demo** using `docs/DEMO_RECORDING.md` when live URLs exist.

7. **Submit Devpost** using `docs/DEVPOST_DRAFT.md` before Aug 3.

## Do not

- Rotate Ed25519 keys  
- Spend GMI credits on experiments  
- Ask for more features until Tier 0 (three URLs + video + submit) is done  
