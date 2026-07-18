"""Build lineage chain for parent_run_id revisions."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from attest.models import AssetRecord, ComplianceStatus


async def build_lineage(
    db: AsyncSession,
    parent_run_id: str | None,
) -> list[dict[str, Any]]:
    """Walk parent chain oldest → newest; each node marked rejected for manifest."""
    if not parent_run_id:
        return []

    chain: list[dict[str, Any]] = []
    current_id: str | None = parent_run_id
    seen: set[str] = set()

    while current_id and current_id not in seen:
        seen.add(current_id)
        result = await db.execute(select(AssetRecord).where(AssetRecord.run_id == current_id))
        record = result.scalars().first()
        if not record:
            break
        chain.append(
            {
                "run_id": record.run_id,
                "parent_run_id": record.parent_run_id,
                "status": "rejected",
                "created_at": record.created_at.isoformat(),
            }
        )
        current_id = record.parent_run_id

    chain.reverse()
    return chain


async def mark_parent_rejected(db: AsyncSession, parent_run_id: str) -> None:
    result = await db.execute(select(AssetRecord).where(AssetRecord.run_id == parent_run_id))
    for record in result.scalars().all():
        record.status = ComplianceStatus.REJECTED
    await db.commit()
