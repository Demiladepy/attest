# DEMO_RECORDING.md — 3-minute screen record

Goal: one continuous capture matching `docs/DEMO_SCRIPT.md`. Retake max twice.

## Prep (5 min)

- [ ] Frontend: `npm run dev` or live `app.attest.io`
- [ ] Backend live or API URL set in `NEXT_PUBLIC_API_URL`
- [ ] One compliant asset already generated (do not wait on camera time for GMI)
- [ ] Verifier deep link ready in clipboard
- [ ] Genblaze PR tab open
- [ ] Silence notifications; 1080p; show cursor

## Beats

| Time | What to show | Say (approx) |
|------|--------------|--------------|
| 0:00–0:15 | Logo / title card | “August 2, 2026 — Article 50 means every AI asset needs provenance.” |
| 0:15–0:35 | Console | “ATTEST is a compliance gateway for EU fintech media teams.” Click Generate on prepared brief. |
| 0:35–1:35 | Pipeline visualizer | Walk left→right steps; point to B2 ops panel (manifest / Ed25519 / Object Lock / audit). |
| 1:35–2:00 | Verifier green | Paste/open deep link. Green checks + lineage tree briefly. |
| 2:00–2:35 | Tamper | Click Simulate tamper → red SHA-256. Say original stays locked in B2. |
| 2:35–3:00 | GitHub PR | Show Mode 2 Ed25519 PR. End with three URLs on screen. |

## Export

- MP4 H.264, under 100MB if possible  
- Filename: `attest-demo-3min.mp4`  
- Paste YouTube/Drive/Devpost link into `docs/DEMO_ASSETS.md`

## Pass criteria

Judge can understand generate → sign → verify → tamper → upstream Genblaze with no voice? If yes, ship.
