"""CLI: simulate tamper (re-encode) on a local /assets/ URL."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from attest.compliance.tamper import tamper_asset_url


async def main() -> int:
    parser = argparse.ArgumentParser(description="Tamper-simulate an ATTEST asset (local dev)")
    parser.add_argument("url", help="Original asset URL")
    args = parser.parse_args()

    result = await tamper_asset_url(args.url)
    print(json.dumps(result.__dict__, indent=2))
    print("\nPaste tampered_url into verifier — expect FAIL on SHA-256.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
