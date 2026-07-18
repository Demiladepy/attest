# DEVPOST_DRAFT.md — Copy ready to paste

**Project name:** ATTEST  
**Tagline:** Compliance-grade AI media gateway for EU AI Act Article 50 — provenance, signing, and tamper-evident B2 storage on Genblaze.

## Inspiration

August 2, 2026 approaches Article 50 obligations. Marketing teams generating AI media need proofs of provenance, integrity, and rejection lineage — not another creative tool. ATTEST treats compliance as the product.

## What it does

- **Compliance Console** — brief → SSE pipeline visualizer → signed asset in Backblaze B2  
- **Public verifier** — Ed25519 + SHA-256 checks, lineage tree for rejected iterations  
- **Tamper demo** — re-encode fails integrity while original remains in B2  
- **Genblaze Mode 2** — upstream Ed25519 signer contribution (PR URL)

## How we built it

- FastAPI + Genblaze (GMI Cloud image + classifier) + native B2 (`b2sdk`)  
- Next.js Compliance Console + verifier  
- Ed25519 ComplianceSink; SQLite audit trail; Object Lock / governance story for manifests  

## Challenges

Private B2 buckets vs judge-pasteable URLs → API storage proxy. Master Application Key vs S3 → switched uploads to native B2 API. Limited GMI credits → one hero pin, simulated remaining pipeline steps for demo speed.

## Accomplishments

End-to-end generate → sign → verify → tamper on real GMI output. Mode 2 signing branch for Genblaze. Deploy configs for Vercel + Railway.

## What’s next

Wire B2 Event Notifications, optional TrustMark, real voice/transcript steps when credits allow. Full C2PA after hackathon.

## Links (fill after deploy)

- Console: `https://app.attest.io`  
- Verifier: `https://verify.attest.io/?asset=…`  
- Genblaze PR: _(paste)_  
- Demo video: _(paste)_  
- GitHub: _(this repo)_  

## Built with

Python, FastAPI, Next.js, Genblaze, GMI Cloud, Backblaze B2, Ed25519, Tailwind
