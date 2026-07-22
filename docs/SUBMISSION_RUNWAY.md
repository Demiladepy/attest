# SUBMISSION_RUNWAY.md — July 31 target

**Today:** 2026-07-22 · **Target:** 2026-07-31 · **Hard deadline:** 2026-08-03
9 days of runway to target, 2-day safety buffer after.

## Status at a glance

| Layer | State |
|-------|-------|
| Backend | ✅ Done. 23 tests, CI green, genblaze 0.6.0 line, provider failsafe, security-audited proxy |
| Frontend | ✅ Done. ElevenLabs-style redesign, verify/tamper/lineage all live, lint+build clean |
| Repo | ✅ Pushed to github.com/Demiladepy/attest, CI on every push |
| Mode 2 PR branch | ✅ Verified clean-merge onto upstream 0.6.0; PR body ready |
| **Live deploy** | ⛔ Operator — not started |
| **Hero pin** | ⛔ Operator — needs deploy + `allow_gmi_burn` |
| **Genblaze PR opened** | ⛔ Operator — branch + body ready |
| **Demo video** | ⛔ Operator — needs live URLs |
| **Devpost** | ⛔ Operator — draft ready |

## Critical path (each step unblocks the next)

```
deploy backend+frontend ──▶ hero pin on prod ──▶ record video ──▶ Devpost
        │                                              ▲
        └──▶ (parallel) open Genblaze PR ──────────────┘
```

## Day-by-day plan

### Jul 22–23 — Deploy (90 min)
Follow [`DEPLOY_ENV_CHECKLIST.md`](DEPLOY_ENV_CHECKLIST.md). Railway backend → Vercel frontend → cross-wire URLs → redeploy.
- [ ] Backend live, `curl <api>/api/health` → `b2_write_ok:true`, `pipeline:gmi`, `warnings:[]`
- [ ] Frontend live, Console loads with no CORS errors
- [ ] `DEBUG=false` in Railway (local `.env` has it true)

### Jul 24 — Hero pin (30 min)
- [ ] Set `allow_gmi_burn: true` in `LOOP_STATE.md`
- [ ] `python -m attest.scripts.gmi_smoke --full` **against prod** (now registers in Console DB automatically)
- [ ] Optional: `genblaze verify --fetch` on the output for byte-level proof (new in 0.6.0)
- [ ] Paste `CONSOLE_URL`, `VERIFY_URL`, `API_HEALTH` into [`DEMO_ASSETS.md`](DEMO_ASSETS.md)
- [ ] Tamper the hero once → confirm red verifier → pin tampered URL

### Jul 24 (parallel) — Genblaze PR (30 min)
Branch verified clean-merge; just push to your fork and open.
```bash
cd genblaze-pr/genblaze
git remote add fork https://github.com/Demiladepy/genblaze.git   # your fork
git push fork feat/mode2-ed25519-signer
```
- [ ] Open PR against `backblaze-labs/genblaze` using [`../genblaze-pr/PR_BODY.md`](../genblaze-pr/PR_BODY.md)
- [ ] Paste PR URL into `DEMO_ASSETS.md`

### Jul 25–28 — Record demo (buffer for retakes)
Follow [`DEMO_RECORDING.md`](DEMO_RECORDING.md) + [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md). Beats: generate → SSE pipeline → verify green → tamper red → audit log → B2 durability.
- [ ] 3-min video recorded against **live** URLs
- [ ] Uploaded (YouTube unlisted / Loom); paste `DEMO_VIDEO` into `DEMO_ASSETS.md`

### Jul 29–30 — Devpost
- [ ] Fill [`DEVPOST_DRAFT.md`](DEVPOST_DRAFT.md) links, paste into Devpost
- [ ] All 5 links resolve: Console, Verifier, PR, Video, GitHub

### Jul 31 — Submit
- [ ] Final click. 2 days of buffer remain before Aug 3.

## Do-not-forget
- Never rotate `ATTEST_SIGNING_KEY_HEX` — the pinned asset and `attest-pubkey.pem` depend on it.
- Never commit `.env` (`.gitignore` covers it).
- Hero pin must run **on prod**, not local, so the pasted URL is a real judge URL.
