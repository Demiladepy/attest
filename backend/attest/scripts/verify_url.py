"""CLI: verify an asset URL against ATTEST compliance checks."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from attest.compliance.verify import verify_asset_url


async def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an ATTEST asset URL")
    parser.add_argument("url", help="Asset URL to verify")
    parser.add_argument("--manifest", help="Manifest URL (optional)")
    args = parser.parse_args()

    result = await verify_asset_url(args.url, manifest_url=args.manifest)
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.overall.value == "pass" else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
