"""Deploy the ATTEST backend to a free Hugging Face Docker Space (no card).

One-time prereq (operator, ~1 min):
    huggingface-cli login          # paste a WRITE token from
                                   # https://huggingface.co/settings/tokens

Then run:
    cd backend
    .\.venv\Scripts\python -m attest.scripts.deploy_hf_space

The script creates/updates the Space, uploads the backend, and sets every
NON-secret env var. It never uploads .env and never sets secret values — you set
those 4 in the Space UI (it prints the list). Re-run any time to push updates.
"""

from __future__ import annotations

import sys

from attest.config import get_settings

SPACE_NAME = "attest-api"
VERCEL_URL = "https://attest-black-two.vercel.app"

# HF Space README frontmatter — tells HF to build our Dockerfile and route :8000.
SPACE_README = """---
title: ATTEST API
emoji: 🔏
colorFrom: gray
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---

# ATTEST API

Compliance-grade AI media gateway backend (FastAPI + Genblaze + Backblaze B2).
Source & docs: https://github.com/Demiladepy/attest
"""

# Secrets the operator sets in the Space UI (never handled here).
REQUIRED_SECRETS = [
    "B2_KEY_ID",
    "B2_APPLICATION_KEY",
    "ATTEST_SIGNING_KEY_HEX",
    "GMI_API_KEY",
]


def main() -> None:
    from pathlib import Path

    # Windows consoles default to cp1252 and choke on → / ✓ in our output.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

    from huggingface_hub import HfApi, whoami

    backend_dir = Path(__file__).resolve().parents[2]  # .../backend
    settings = get_settings()

    try:
        me = whoami()["name"]
    except Exception:
        sys.exit(
            "Not logged in to Hugging Face.\n"
            "  Run:  huggingface-cli login   (paste a WRITE token from "
            "https://huggingface.co/settings/tokens)"
        )

    # Windows consoles default to cp1252 and choke on non-ASCII; force UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    api = HfApi()
    repo_id = f"{me}/{SPACE_NAME}"
    space_url = f"https://{me.lower()}-{SPACE_NAME}.hf.space"

    print(f"-> Creating/updating Space: {repo_id}")
    api.create_repo(
        repo_id=repo_id,
        repo_type="space",
        space_sdk="docker",
        exist_ok=True,
        private=False,
    )

    print("-> Uploading README (HF frontmatter)")
    api.upload_file(
        path_or_fileobj=SPACE_README.encode("utf-8"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="space",
    )

    print("-> Uploading backend (Dockerfile, requirements.txt, attest/)")
    api.upload_folder(
        folder_path=str(backend_dir),
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=[
            ".venv/**",
            "**/__pycache__/**",
            "*.pyc",
            "*.db",
            "demo_assets/**",
            "tests/**",
            "README.md",  # replaced by the HF-frontmatter one above
            ".env",  # NEVER upload secrets
            ".env.*",
            ".vercel/**",
            "railway.toml",
            "pytest.ini",
        ],
    )

    print("-> Setting non-secret Space variables")
    non_secret_vars = {
        "PORT": "8000",  # keep container port aligned with README app_port
        "DEMO_MODE": "true",
        "DEBUG": "false",
        "PYTHONUNBUFFERED": "1",
        "TENANT_ID": settings.tenant_id or "demo-workspace",
        "B2_REGION": settings.b2_region or "us-east-005",
        "B2_BUCKET": settings.b2_bucket or "attest-dma-2026",
        "CORS_ORIGINS": VERCEL_URL,
        "API_PUBLIC_BASE_URL": space_url,
        # public key — safe as a plain variable
        "ATTEST_VERIFY_KEY_HEX": settings.attest_verify_key_hex,
    }
    for key, value in non_secret_vars.items():
        if not value:
            continue
        api.add_space_variable(repo_id=repo_id, key=key, value=value)

    print("\n[OK] Space pushed:", space_url)
    print("\nNEXT - set these 4 secrets in the Space UI:")
    print("  Settings > Variables and secrets > New secret (copy values from backend/.env):")
    for key in REQUIRED_SECRETS:
        print(f"    - {key}")
    print("\nThe Space rebuilds automatically after secrets are set.")
    print(f"Health check once live:  {space_url}/api/health")


if __name__ == "__main__":
    main()
