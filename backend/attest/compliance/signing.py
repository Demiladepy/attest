"""Ed25519 signing for ATTEST manifests (Genblaze Mode 2 candidate)."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


@dataclass(frozen=True)
class SignatureBundle:
    algorithm: str
    public_key_hex: str
    signature_b64: str
    signed_at: str
    manifest_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "public_key_hex": self.public_key_hex,
            "signature_b64": self.signature_b64,
            "signed_at": self.signed_at,
            "manifest_sha256": self.manifest_sha256,
        }


class Ed25519Signer:
    """Sign canonical manifest JSON with Ed25519."""

    def __init__(self, private_key: Ed25519PrivateKey) -> None:
        self._private_key = private_key
        self._public_key = private_key.public_key()

    @classmethod
    def generate(cls) -> Ed25519Signer:
        return cls(Ed25519PrivateKey.generate())

    @classmethod
    def from_hex_seed(cls, seed_hex: str) -> Ed25519Signer:
        seed = bytes.fromhex(seed_hex)
        if len(seed) != 32:
            raise ValueError("Ed25519 seed must be 32 bytes (64 hex chars)")
        return cls(Ed25519PrivateKey.from_private_bytes(seed))

    @property
    def public_key_hex(self) -> str:
        raw = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return raw.hex()

    def canonical_bytes(self, manifest: dict[str, Any]) -> bytes:
        return json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def manifest_sha256(self, manifest: dict[str, Any]) -> str:
        return hashlib.sha256(self.canonical_bytes(manifest)).hexdigest()

    def sign_manifest(self, manifest: dict[str, Any], signed_at: str) -> SignatureBundle:
        digest = self.manifest_sha256(manifest)
        signature = self._private_key.sign(digest.encode("utf-8"))
        return SignatureBundle(
            algorithm="ed25519",
            public_key_hex=self.public_key_hex,
            signature_b64=base64.b64encode(signature).decode("ascii"),
            signed_at=signed_at,
            manifest_sha256=digest,
        )

    def verify(self, manifest: dict[str, Any], bundle: SignatureBundle) -> bool:
        if bundle.algorithm != "ed25519":
            return False
        if bundle.manifest_sha256 != self.manifest_sha256(manifest):
            return False
        try:
            public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(bundle.public_key_hex))
            public_key.verify(
                base64.b64decode(bundle.signature_b64),
                bundle.manifest_sha256.encode("utf-8"),
            )
            return True
        except Exception:
            return False


def signature_from_dict(data: dict[str, Any]) -> SignatureBundle:
    return SignatureBundle(
        algorithm=data["algorithm"],
        public_key_hex=data["public_key_hex"],
        signature_b64=data["signature_b64"],
        signed_at=data["signed_at"],
        manifest_sha256=data["manifest_sha256"],
    )
