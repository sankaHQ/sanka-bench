from __future__ import annotations

from pathlib import Path

import pytest

from sanka_bench.schema import SchemaError, load_and_validate, load_schema, validate_payload


def test_all_versioned_schemas_are_valid() -> None:
    for name in ("task", "candidate", "result"):
        assert load_schema(name)["$schema"].endswith("2020-12/schema")


def test_checked_in_task_and_candidates_validate(repository_root: Path, task_dir: Path) -> None:
    assert load_and_validate(task_dir / "task.yaml", "task")["id"] == "drf-fastapi-001"
    for path in sorted((repository_root / "baselines").glob("*/*/candidate.yaml")):
        load_and_validate(path, "candidate")


def test_overlay_candidate_requires_overlay_path() -> None:
    payload = {
        "schema_version": "sanka-bench/candidate/v0.1",
        "id": "missing-overlay",
        "kind": "overlay",
        "provenance": {"producer": "test", "revision": "1", "command": ""},
    }
    with pytest.raises(SchemaError, match="overlay"):
        validate_payload(payload, "candidate", label="candidate")
