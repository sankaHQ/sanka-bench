from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from sanka_bench.report import ReportError, collect, render_html, render_svg, write_report

GATES_PASS = {
    "source_qualified": True,
    "regression_tests": True,
    "target_boot": True,
    "native_target": True,
    "behavior_parity": True,
    "database_parity": True,
    "side_effect_parity": True,
    "deterministic": True,
}


def _result(
    task: str,
    candidate: str,
    *,
    migrated: bool,
    native: bool = True,
    stats: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gates = dict(GATES_PASS)
    gates["native_target"] = native
    provenance: dict[str, Any] = {"evaluator_version": "0.0.1"}
    if stats is not None:
        provenance["candidate_stats"] = stats
    return {
        "task_id": task,
        "candidate_id": candidate,
        "fully_migrated": migrated,
        "hard_gates": gates,
        "provenance": provenance,
    }


def _write(reports: Path, name: str, payload: dict[str, Any]) -> None:
    (reports / name).write_text(json.dumps(payload), encoding="utf-8")


@pytest.fixture
def reports_dir(tmp_path: Path) -> Path:
    reports = tmp_path / "reports"
    reports.mkdir()
    _write(reports, "t1-noop.json", _result("task-1", "noop", migrated=False, native=False))
    _write(
        reports,
        "t1-bridge.json",
        _result("task-1", "sanka-pr13-compatibility-bridge", migrated=False, native=False),
    )
    _write(reports, "t1-native.json", _result("task-1", "sanka-native", migrated=True))
    _write(
        reports,
        "t1-native-docker.json",
        _result("task-1", "sanka-native", migrated=True),
    )
    _write(
        reports,
        "t2-bridge.json",
        _result("task-2", "sanka-compatibility-bridge", migrated=False, native=False),
    )
    _write(reports, "t2-ref.json", _result("task-2", "native-reference", migrated=True))
    _write(
        reports,
        "t1-agent.json",
        _result(
            "task-1",
            "claude-code-alone",
            migrated=True,
            stats={"turns": 36, "duration_seconds": 300.0, "cost_usd": 1.5},
        ),
    )
    _write(
        reports,
        "t2-agent.json",
        _result(
            "task-2",
            "claude-code-alone",
            migrated=True,
            stats={"turns": 40, "duration_seconds": 180.0, "cost_usd": 0.5},
        ),
    )
    return reports


def test_collect_groups_families_and_parity(reports_dir: Path) -> None:
    data = collect(reports_dir)
    assert data["tasks"] == ["task-1", "task-2"]
    rows = {row["family"]: row for row in data["rows"]}
    # both bridge candidate ids fold into one family across tasks
    assert rows["compatibility-bridge"]["covered"] == ["task-1", "task-2"]
    assert rows["compatibility-bridge"]["migrated"] == []
    assert rows["sanka-native"]["migrated"] == ["task-1"]
    assert data["parity_checked"] == 1
    assert data["parity_matched"] == 1
    assert data["evaluator_versions"] == ["0.0.1"]
    # story order: controls, agents, converter, then the human reference
    assert [row["family"] for row in data["rows"]] == [
        "noop",
        "compatibility-bridge",
        "claude-code-alone",
        "sanka-native",
        "native-reference",
    ]
    agent = rows["claude-code-alone"]
    assert agent["cost_usd"] == pytest.approx(2.0)
    assert agent["duration_seconds"] == pytest.approx(480.0)
    assert rows["sanka-native"]["cost_usd"] is None


def test_html_and_svg_render_the_headline(reports_dir: Path) -> None:
    data = collect(reports_dir)
    page = render_html(data)
    assert "Sanka compatibility bridge" in page
    assert "0/2" in page
    assert "permanent negative control" in page
    assert 'class="gate-fail"' in page and 'class="gate-pass"' in page
    assert "1/1 local↔Docker runs agree" in page
    assert "$2.00 · 8 min agent time" in page
    assert "single unattended attempts" in page
    svg = render_svg(data)
    assert svg.startswith("<svg") and svg.endswith("</svg>")
    assert "tasks fully migrated" in svg


def test_render_is_deterministic(reports_dir: Path) -> None:
    first = collect(reports_dir)
    second = collect(reports_dir)
    assert render_html(first) == render_html(second)
    assert render_svg(first) == render_svg(second)


def test_write_report_outputs_files(reports_dir: Path, tmp_path: Path) -> None:
    html_path = tmp_path / "out" / "index.html"
    svg_path = tmp_path / "out" / "summary.svg"
    data = write_report(reports_dir, html_path, svg_path)
    assert html_path.is_file() and svg_path.is_file()
    assert len(data["rows"]) == 5


def test_empty_reports_dir_raises(tmp_path: Path) -> None:
    empty = tmp_path / "reports"
    empty.mkdir()
    with pytest.raises(ReportError):
        collect(empty)
