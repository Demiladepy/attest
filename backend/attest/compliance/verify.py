"""Verification orchestration for public verifier endpoint."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

from attest.compliance.signing import SignatureBundle, signature_from_dict


class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class VerificationCheck:
    id: str
    label: str
    status: CheckStatus
    detail: str = ""


@dataclass
class LineageNode:
    run_id: str
    parent_run_id: str | None
    status: str
    created_at: str


@dataclass
class VerificationResult:
    asset_url: str
    overall: CheckStatus
    checks: list[VerificationCheck] = field(default_factory=list)
    lineage: list[LineageNode] = field(default_factory=list)
    manifest: dict[str, Any] | None = None
    signature: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_url": self.asset_url,
            "overall": self.overall.value,
            "checks": [
                {"id": c.id, "label": c.label, "status": c.status.value, "detail": c.detail}
                for c in self.checks
            ],
            "lineage": [node.__dict__ for node in self.lineage],
            "manifest": self.manifest,
            "signature": self.signature,
        }


async def fetch_bytes(url: str, max_bytes: int = 64 * 1024 * 1024) -> bytes:
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        content = resp.content
        if len(content) > max_bytes:
            raise ValueError(f"Asset exceeds {max_bytes} bytes")
        return content


async def fetch_json(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


def _overall(checks: list[VerificationCheck]) -> CheckStatus:
    if any(c.status == CheckStatus.FAIL for c in checks):
        return CheckStatus.FAIL
    if any(c.status == CheckStatus.WARN for c in checks):
        return CheckStatus.WARN
    return CheckStatus.PASS


async def verify_asset_url(
    asset_url: str,
    *,
    manifest_url: str | None = None,
    expected_sha256: str | None = None,
) -> VerificationResult:
    checks: list[VerificationCheck] = []
    manifest: dict[str, Any] | None = None
    signature_data: dict[str, Any] | None = None
    lineage: list[LineageNode] = []

    # Fetch asset and hash
    try:
        asset_bytes = await fetch_bytes(asset_url)
        actual_sha256 = hashlib.sha256(asset_bytes).hexdigest()
        checks.append(
            VerificationCheck(
                id="asset_fetch",
                label="Asset reachable",
                status=CheckStatus.PASS,
                detail=f"sha256:{actual_sha256[:16]}…",
            )
        )
    except Exception as exc:
        checks.append(
            VerificationCheck(
                id="asset_fetch",
                label="Asset reachable",
                status=CheckStatus.FAIL,
                detail=str(exc),
            )
        )
        return VerificationResult(asset_url=asset_url, overall=CheckStatus.FAIL, checks=checks)

    # Manifest
    resolved_manifest_url = manifest_url
    if not resolved_manifest_url and asset_url.endswith(".mp4"):
        resolved_manifest_url = asset_url.rsplit(".", 1)[0] + ".manifest.json"

    if resolved_manifest_url:
        try:
            manifest = await fetch_json(resolved_manifest_url)
            checks.append(
                VerificationCheck(
                    id="manifest_parse",
                    label="Manifest parsed",
                    status=CheckStatus.PASS,
                )
            )
        except Exception as exc:
            checks.append(
                VerificationCheck(
                    id="manifest_parse",
                    label="Manifest parsed",
                    status=CheckStatus.FAIL,
                    detail=str(exc),
                )
            )
    else:
        checks.append(
            VerificationCheck(
                id="manifest_parse",
                label="Manifest parsed",
                status=CheckStatus.WARN,
                detail="No manifest URL provided",
            )
        )

    # SHA256 match
    manifest_sha = None
    if manifest:
        outputs = manifest.get("outputs") or manifest.get("assets") or []
        if outputs and isinstance(outputs, list):
            first = outputs[0] if outputs else {}
            manifest_sha = first.get("sha256") or first.get("hash")
        manifest_sha = manifest_sha or manifest.get("sha256")

    if expected_sha256 or manifest_sha:
        expected = (expected_sha256 or manifest_sha or "").lower()
        if actual_sha256.lower() == expected:
            checks.append(
                VerificationCheck(
                    id="sha256",
                    label="SHA-256 integrity",
                    status=CheckStatus.PASS,
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    id="sha256",
                    label="SHA-256 integrity",
                    status=CheckStatus.FAIL,
                    detail=f"expected {expected[:16]}… got {actual_sha256[:16]}…",
                )
            )
    else:
        checks.append(
            VerificationCheck(
                id="sha256",
                label="SHA-256 integrity",
                status=CheckStatus.WARN,
                detail="No reference hash in manifest",
            )
        )

    # Ed25519 signature (Mode 2)
    if manifest:
        attest = manifest.get("attest") or {}
        signature_data = attest.get("signature")
        if signature_data:
            bundle = signature_from_dict(signature_data)
            core_manifest = {k: v for k, v in manifest.items() if k != "attest"}
            try:
                from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
                import base64

                public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(bundle.public_key_hex))
                public_key.verify(
                    base64.b64decode(bundle.signature_b64),
                    bundle.manifest_sha256.encode("utf-8"),
                )
                canonical_ok = hashlib.sha256(
                    json.dumps(core_manifest, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest() == bundle.manifest_sha256
                checks.append(
                    VerificationCheck(
                        id="ed25519",
                        label="Ed25519 signature",
                        status=CheckStatus.PASS if canonical_ok else CheckStatus.FAIL,
                        detail="" if canonical_ok else "Manifest changed since signing",
                    )
                )
            except Exception as exc:
                checks.append(
                    VerificationCheck(
                        id="ed25519",
                        label="Ed25519 signature",
                        status=CheckStatus.FAIL,
                        detail=str(exc),
                    )
                )
        else:
            checks.append(
                VerificationCheck(
                    id="ed25519",
                    label="Ed25519 signature",
                    status=CheckStatus.WARN,
                    detail="No signature block in manifest",
                )
            )

        # C2PA
        c2pa = attest.get("c2pa") or {}
        if c2pa.get("embedded"):
            checks.append(
                VerificationCheck(
                    id="c2pa",
                    label="C2PA claim",
                    status=CheckStatus.PASS if c2pa.get("valid", True) else CheckStatus.FAIL,
                    detail=c2pa.get("detail", "Embedded in asset"),
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    id="c2pa",
                    label="C2PA claim",
                    status=CheckStatus.WARN,
                    detail="Not embedded (roadmap: Mode 3)",
                )
            )

        # Watermark
        wm = attest.get("watermark") or {}
        if wm.get("detected"):
            score = wm.get("confidence", 1.0)
            checks.append(
                VerificationCheck(
                    id="watermark",
                    label="Invisible watermark",
                    status=CheckStatus.PASS if score >= 0.5 else CheckStatus.FAIL,
                    detail=f"confidence={score:.2f}",
                )
            )
        else:
            checks.append(
                VerificationCheck(
                    id="watermark",
                    label="Invisible watermark",
                    status=CheckStatus.WARN,
                    detail=wm.get("detail", "Not detected or not applicable"),
                )
            )

        # Lineage
        for node in attest.get("lineage") or []:
            lineage.append(
                LineageNode(
                    run_id=node.get("run_id", ""),
                    parent_run_id=node.get("parent_run_id"),
                    status=node.get("status", "unknown"),
                    created_at=node.get("created_at", ""),
                )
            )
        if manifest.get("parent_run_id"):
            lineage.insert(
                0,
                LineageNode(
                    run_id=manifest.get("run_id", ""),
                    parent_run_id=manifest.get("parent_run_id"),
                    status="approved",
                    created_at=manifest.get("created_at", ""),
                ),
            )

    return VerificationResult(
        asset_url=asset_url,
        overall=_overall(checks),
        checks=checks,
        lineage=lineage,
        manifest=manifest,
        signature=signature_data,
    )
