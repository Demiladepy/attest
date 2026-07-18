"""Lineage tree builder tests."""

from attest.compliance.lineage import build_lineage_tree


def test_build_lineage_tree_empty():
    assert build_lineage_tree(None) == []
    assert build_lineage_tree({}) == []


def test_build_lineage_tree_single_approved():
    manifest = {
        "run_id": "run-c",
        "parent_run_id": "run-b",
        "created_at": "2026-06-29T12:00:00Z",
        "attest": {"lineage": []},
    }
    tree = build_lineage_tree(manifest)
    assert len(tree) == 1
    assert tree[0]["run_id"] == "run-c"
    assert tree[0]["status"] == "approved"
    assert tree[0]["depth"] == 0


def test_build_lineage_tree_with_ancestors():
    manifest = {
        "run_id": "run-c",
        "parent_run_id": "run-b",
        "created_at": "2026-06-29T12:00:00Z",
        "attest": {
            "lineage": [
                {
                    "run_id": "run-a",
                    "parent_run_id": None,
                    "status": "rejected",
                    "created_at": "2026-06-29T10:00:00Z",
                },
                {
                    "run_id": "run-b",
                    "parent_run_id": "run-a",
                    "status": "rejected",
                    "created_at": "2026-06-29T11:00:00Z",
                },
            ]
        },
    }
    tree = build_lineage_tree(manifest)
    assert [n["run_id"] for n in tree] == ["run-a", "run-b", "run-c"]
    assert [n["status"] for n in tree] == ["rejected", "rejected", "approved"]
    assert [n["depth"] for n in tree] == [0, 1, 2]
