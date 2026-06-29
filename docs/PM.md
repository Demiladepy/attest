# ATTEST — Product Management

**PM:** Claude (conversation spec is source of truth for scope, demo script, and rubric alignment)

**Engineering:** Cursor agent implements against the PM brief. When scope conflicts arise, the 3-minute demo script wins.

## Decision filter

Every change must answer: **does this make ATTEST win?**

## Locked scope (hackathon)

- Article 50 compliance gateway — provenance, signing, watermarking, audit trail
- Compliance Console (`app.attest.io`) + public verifier (`verify.attest.io`)
- Genblaze pipeline + custom `ComplianceSink`
- B2: Object Lock, Event Notifications, Lifecycle, Durable URLs
- Upstream: Mode 2 Ed25519 PR to `backblaze-labs/genblaze`

## Explicitly out of scope

Creative tooling, deepfake detection, DAM, multi-tenant UI, blockchain.

## Demo script

See [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) — build to the script, not the other way around.

## Regulatory references

- EU AI Act Article 50 (transparency for AI-generated content)
- Code of Practice on Transparency (published June 10, 2026)
- Genblaze [trust modes](https://github.com/backblaze-labs/genblaze/blob/main/docs/features/trust-modes.md)
