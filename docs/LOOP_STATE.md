# LOOP_STATE.md — Daily finish-first build loop

> Agent reads this first every tick. Operator exams take priority; loops must not ask for long attention.

**Started:** 2026-07-13  
**Submission target:** 2026-07-31 (hard deadline 2026-08-03 — 2-day safety buffer)  
**Cadence:** ~24h dynamic wake (`AGENT_LOOP_WAKE_attest_finish`)  
**Strategy:** Tier 0 only until three judge URLs + demo video + Devpost are done. Cut Tier 2.  
**Code status (2026-07-22):** All agent-buildable work complete. genblaze upgraded to 0.6.0 line, 23 tests green, CI green, Mode 2 PR branch verified clean-merge onto upstream. Remaining work is 100% operator (deploy + pin + PR + video + submit).

## Goal (winning definition)

1. Live Console URL  
2. Live Verifier URL with pinned real asset (pass + tamper-fail)  
3. Genblaze Mode 2 PR URL (operator opens)  
4. 3-minute demo video  
5. Devpost submitted before Aug 3

## Operator blockers (agent cannot finish alone)

| Blocker | Owner action | Est. time |
|---------|--------------|-----------|
| Push / open Genblaze PR | Fork + push `feat/mode2-ed25519-signer` + PR body | 30m |
| Live deploy secrets | Paste `.env` into Railway/Vercel; set domains | 45–90m |
| DNS `*.attest.io` | Cloudflare CNAMEs | 15m |
| Record demo | Follow `docs/DEMO_SCRIPT.md` | 2–3h |
| Devpost submit | Paste links + video | 1–2h |
| GMI burn approval | Set `allow_gmi_burn: true` below when credits OK | 1 decision |

## Loop controls

```yaml
allow_gmi_burn: false   # flip true only for one hero B2-pin run
allow_git_commit: false # flip true if operator wants autocommits
stop_loop: false        # flip true to halt daily wakes
```

## Queue (check off in order)

### A — Agent-owned (code/docs, no secrets)

- [x] A1 Create `docs/LOOP_STATE.md` + finish-first policy (2026-07-13)
- [x] A2 Refresh `CLAUDE_HANDOFF.md` to match Reality (B2 native OK; lineage tree done)
- [x] A3 Update `docs/DEPLOY.md` for GMI + native B2 + current env matrix
- [x] A4 Write `docs/DEVPOST_DRAFT.md` (copy ready to paste)
- [x] A5 Write `docs/DEMO_RECORDING.md` (screen-record checklist)
- [x] A6 Write `docs/OPERATOR_15MIN.md` (exam-friendly operator checklist)
- [x] A7 Add backend script `attest.scripts.pin_status` (health + last asset summary, no GMI spend)
- [x] A8 Align `docs/DEMO_ASSETS.md` structure for production pin (no fake URLs)
- [x] A9 Frontend polish — **skipped** (does not block demo beats)
- [x] A10 Smoke pytest — **12 passed** (2026-07-13)
- [x] A11 README finish-first pointer
- [x] A12 B2 region / public URL base warnings (`b2_config_warnings` in health + pin_status) — 2026-07-14
- [x] A13 Deploy env checklist from live pin_status → `docs/DEPLOY_ENV_CHECKLIST.md` (2026-07-18)

### B — Needs operator (loop prepares; waits)

- [x] B1 Confirm B2 write — `b2_write_ok: true` via `pin_status` (2026-07-13) **but** clear `B2_PUBLIC_URL_BASE` for private-bucket proxy URLs before hero pin
- [ ] B2 One hero GMI run when `allow_gmi_burn: true` → pin VERIFY_URL
- [ ] B3 Deploy Railway API + Vercel frontend
- [ ] B4 Open Genblaze PR
- [ ] B5 Record + upload demo video
- [ ] B6 Submit Devpost

### C — Explicitly deferred (do not touch in loop)

- Full C2PA, TrustMark, ElevenLabs/AssemblyAI real providers, video hero, Postgres, blogs

## Tick log

| Date | Item | Result |
|------|------|--------|
| 2026-07-13 | A1–A11 packaging | Docs, pin_status, handoff/DEPLOY/README; pytest 12 ok; B2 write OK native; loop armed |
| 2026-07-14 | A12 | Region/public-base warnings in urls + health + pin_status; tests extended; old sleeper killed + re-armed |
| 2026-07-18 | A13 + env fix | `.env` fixed live with operator (region us-east-005, public base cleared, dup-key typo); pin_status **zero warnings**, storage_proxy true; `DEPLOY_ENV_CHECKLIST.md` written; pytest 14 ok; safety commit of all work since Jun 29 |
| 2026-07-19 | Failsafe + registration | GMI-outage failsafe in run_genblaze_pipeline (visible fallback step, demo can't die; unit-tested). Scripted runs (generate_demo_asset, gmi_smoke --full) now register AssetRecord + audit events so pinned heroes show in Console/lineage. Endpoint security tests (traversal/tenant/422). README judge section + CI badge; Devpost draft refreshed. pytest 23 |
| 2026-07-18 | Core bug + redesign + audit | **Fixed Ed25519 verify-fail bug** (sink signed manifest incl. attest stub; verifier excludes attest → every pipeline asset failed verify). Verifier deep-link stale-closure bug fixed. ElevenLabs-style light redesign. Security audit: path traversal (storage proxy + tamper) fixed, tamper tenant-scoped, health B2 probe cached 5m, stream endpoint 422s. CI added (.github/workflows). E2E proven: verify pass → tamper → fail, revise lineage, audit log, traversal 404s. pytest 18, lint + build clean |
| 2026-07-18 | Core fix + verifier UX | **CRITICAL: Ed25519 canonicalization bug** — pipelines pre-seed `attest.transcript`, sink signed it, verifier strips whole `attest` key → every real asset failed verification. Fixed in `sink.py` (+regression test, 15 pass). Also fixed verifier deep-link race (auto-verified empty URL → red FAIL on judge links). New verifier UX: verdict banner, image preview w/ VERIFIED/TAMPERED stamp, provenance card, copy-link. Console offline banner. Full loop browser-verified: generate → green → tamper → red, via B2 proxy URLs. Pushed to github.com/Demiladepy/attest |

## Next tick instruction

Read this file. If `stop_loop: true`, do not re-arm. Else: if any A-item open, do the first unchecked. If only B remains and `allow_gmi_burn` is false, append WAITING ON OPERATOR note (no feature work) and re-arm 24h. Never open upstream PR. Never burn GMI unless `allow_gmi_burn: true`. Update tick log.
