# Genblaze upstream PR workspace

Local clone of [backblaze-labs/genblaze](https://github.com/backblaze-labs/genblaze) for the ATTEST **Mode 2 Ed25519 signer** upstream contribution.

## Layout

```
genblaze-pr/
├── genblaze/                  # cloned upstream (develop PR branch here)
├── MODE2_ED25519_SIGNER.md    # PR spec + description draft
└── README.md                  # this file
```

## Clone (already done)

```bash
cd genblaze-pr
git clone https://github.com/backblaze-labs/genblaze.git genblaze
```

Current upstream HEAD when cloned: `7301e80` (v0.4.0 wave prep).

## PR workflow

1. **Read** `genblaze/docs/features/trust-modes.md` — Mode 2 definition
2. **Branch** inside the clone:
   ```bash
   cd genblaze-pr/genblaze
   git checkout -b feat/mode2-ed25519-signer
   ```
3. **Implement** using reference code in `backend/attest/compliance/signing.py`
4. **Open PR** to `backblaze-labs/genblaze` — paste body from `MODE2_ED25519_SIGNER.md`
5. **Tag** @ppatterson and @jdeleon in the PR description

## Key upstream paths

| Path | Purpose |
|------|---------|
| `docs/features/trust-modes.md` | Trust mode roadmap (Mode 2 = Ed25519) |
| `packages/genblaze-core/` | Manifest, Sink, Pipeline core |
| `docs/features/object-storage.md` | Object Lock + manifest persistence |

## PM note

Product scope for what goes in the PR is owned by **Claude (PM)**. See [`../docs/PM.md`](../docs/PM.md).
