"""CLI: smoke-test GMI classify + optional full pipeline."""

from __future__ import annotations

import argparse
import asyncio
import uuid

from attest.config import get_settings
from attest.pipeline.genblaze_gmi import _classify_sync, is_configured, run_gmi_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="GMI Cloud smoke test")
    parser.add_argument("--full", action="store_true", help="Run classify + image + B2 persist")
    parser.add_argument("--brief", default="Professional fintech hero image, modern, no text")
    args = parser.parse_args()

    settings = get_settings()
    if not settings.gmi_configured:
        raise SystemExit("GMI_API_KEY not set in .env")

    print("Classifying…")
    result = _classify_sync(brief=args.brief, api_key=settings.gmi_api_key)
    print(result["summary"])

    if not args.full:
        print("\nOK (classify only). Run with --full for image + B2 upload.")
        return

    if not is_configured():
        raise SystemExit("Full pipeline needs B2 + ATTEST_SIGNING_KEY_HEX")

    async def _run() -> None:
        print("\nRunning full GMI pipeline (may take 1–3 min)…")
        out = await run_gmi_pipeline(asset_id=str(uuid.uuid4()), brief=args.brief)
        print(f"RUN_ID={out.run_id}")
        print(f"ASSET_URL={out.asset_url}")
        print(f"MANIFEST_URL={out.manifest_url}")
        print(f"SHA256={out.sha256}")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
