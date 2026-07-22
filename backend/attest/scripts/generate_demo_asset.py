"""CLI: generate one compliant demo asset and print judge-pasteable URLs."""

from __future__ import annotations

import argparse
import asyncio
import uuid

from attest.pipeline.runner import run_demo_pipeline

DEFAULT_BRIEF = (
    "Spanish-market product launch video, 30 seconds, professional tone, "
    "includes voiceover and music bed."
)


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Generate a signed ATTEST demo asset")
    parser.add_argument("--brief", default=DEFAULT_BRIEF, help="Generation brief")
    args = parser.parse_args()

    asset_id = str(uuid.uuid4())
    result = await run_demo_pipeline(asset_id=asset_id, brief=args.brief)

    from attest.services.register import register_pipeline_result

    await register_pipeline_result(result, brief=args.brief, title="Demo asset (scripted)")

    print("Demo asset ready (registered in Console DB):\n")
    print(f"ASSET_URL={result.asset_url}")
    print(f"MANIFEST_URL={result.manifest_url}")
    print(f"SHA256={result.sha256}")
    print(f"RUN_ID={result.run_id}")
    print()
    print("Verifier deep link:")
    print(
        f"http://localhost:3000/verify?asset={result.asset_url}"
        f"&manifest={result.manifest_url}"
    )


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
