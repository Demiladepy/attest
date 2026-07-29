"""Re-sign the real demo image with the CURRENT signer and write the public demo
bundle (frontend/public/demo/) used by the live client-side verifier.

Run:  cd backend && .\.venv\Scripts\python -m attest.scripts.build_public_demo
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import json
from pathlib import Path

from attest.compliance.sink import apply_compliance_to_manifest

REPO = Path(__file__).resolve().parents[3]
DEMO = REPO / "frontend" / "public" / "demo"
SRC_IMG = DEMO / "output.png"  # real seedream hero image (already bundled)


async def main() -> None:
    img = SRC_IMG.read_bytes()
    sha = hashlib.sha256(img).hexdigest()

    # Reuse the existing manifest's descriptive fields, drop the stale attest block.
    src_manifest = json.loads((DEMO / "manifest.json").read_text(encoding="utf-8"))
    core = {k: v for k, v in src_manifest.items() if k != "attest"}
    if core.get("outputs"):
        core["outputs"][0]["sha256"] = sha  # keep the integrity hash aligned

    manifest = await apply_compliance_to_manifest(
        core,
        tenant_id=core.get("tenant_id", "demo-workspace"),
        asset_sha256=sha,
    )

    (DEMO / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Tampered copy: same image, re-encoded → different bytes → hash mismatch.
    from PIL import Image

    im = Image.open(io.BytesIO(img))
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True, compress_level=9)
    (DEMO / "output-tampered.png").write_bytes(buf.getvalue())

    print("asset sha256      :", sha)
    print("signed manifest_sha:", manifest["attest"]["signature"]["manifest_sha256"])
    print("wrote:", DEMO)


if __name__ == "__main__":
    asyncio.run(main())
