"""Build lineage tree structures for verifier UI."""

from __future__ import annotations

from typing import Any


def build_lineage_tree(manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    """
    Flat list of nodes with depth for tree rendering.
    Order: root (oldest rejected) → … → current approved run.
    """
    if not manifest:
        return []

    nodes: list[dict[str, Any]] = []
    attest = manifest.get("attest") or {}

    for entry in attest.get("lineage") or []:
        nodes.append(
            {
                "run_id": entry.get("run_id", ""),
                "parent_run_id": entry.get("parent_run_id"),
                "status": entry.get("status", "rejected"),
                "created_at": entry.get("created_at", ""),
                "depth": len(nodes),
            }
        )

    current_id = manifest.get("run_id", "")
    parent_id = manifest.get("parent_run_id")
    if current_id:
        nodes.append(
            {
                "run_id": current_id,
                "parent_run_id": parent_id,
                "status": "approved",
                "created_at": manifest.get("created_at", ""),
                "depth": len(nodes),
            }
        )

    return nodes
