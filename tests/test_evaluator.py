from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from sanka_bench.evaluator import evaluate_local
from sanka_bench.hashing import digest_tree
from sanka_bench.schema import load_and_validate


@pytest.fixture(scope="module")
def baseline_results(repository_root: Path, task_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        name: evaluate_local(task_dir, repository_root / "baselines" / name)
        for name in ("noop", "compatibility-bridge", "native-reference")
    }


def test_source_digest_is_pinned_to_fixture(task_dir: Path) -> None:
    task = load_and_validate(task_dir / "task.yaml", "task")
    assert task["source"]["provenance"]["digest"] == digest_tree(task_dir / "source")


def test_noop_fails_without_a_target(baseline_results: dict[str, dict[str, Any]]) -> None:
    result = baseline_results["noop"]
    assert result["status"] == "failed"
    assert result["fully_migrated"] is False
    assert result["hard_gates"]["source_qualified"] is True
    assert result["hard_gates"]["regression_tests"] is True
    assert result["hard_gates"]["target_boot"] is False
    assert result["hard_gates"]["native_target"] is False


def test_pr13_bridge_preserves_behavior_but_fails_native_gate(
    baseline_results: dict[str, dict[str, Any]],
) -> None:
    result = baseline_results["compatibility-bridge"]
    assert result["candidate_id"] == "sanka-pr13-compatibility-bridge"
    assert result["fully_migrated"] is False
    assert result["hard_gates"]["target_boot"] is True
    assert result["hard_gates"]["behavior_parity"] is True
    assert result["hard_gates"]["database_parity"] is True
    assert result["hard_gates"]["native_target"] is False
    assert any("get_asgi_application" in error for error in result["errors"])


def test_native_reference_passes_every_hard_gate(
    baseline_results: dict[str, dict[str, Any]],
) -> None:
    result = baseline_results["native-reference"]
    assert result["status"] == "passed"
    assert result["fully_migrated"] is True
    assert all(result["hard_gates"].values())
    assert result["metrics"]["behavioral_parity"] == {"passed": 5, "total": 5, "rate": 1.0}
    assert result["metrics"]["database_parity"] == {"passed": 5, "total": 5, "rate": 1.0}
    assert result["errors"] == []
