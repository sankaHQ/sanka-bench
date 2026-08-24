from __future__ import annotations

import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


@pytest.fixture(scope="module")
def harness() -> object:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_agent_candidate", SCRIPTS / "run_agent_candidate.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_overlay_exclusions(harness: object) -> None:
    excluded = harness._excluded  # type: ignore[attr-defined]
    assert excluded(Path("public-tests/scenarios.json"))
    assert excluded(Path(".sanka/scan.json"))
    assert excluded(Path("bench-candidate/overlay/target_app.py"))
    assert excluded(Path("__pycache__/x.pyc"))
    assert excluded(Path("db.sqlite3"))
    assert excluded(Path("CLAUDE.md"))
    assert not excluded(Path("target_app.py"))
    assert not excluded(Path("serving_settings.py"))


def test_agent_stats_parses_last_json_line(harness: object) -> None:
    stats_of = harness._agent_stats  # type: ignore[attr-defined]
    payload = json.dumps(
        {
            "num_turns": 12,
            "duration_ms": 61000,
            "total_cost_usd": 1.25,
            "is_error": False,
            "subtype": "success",
            "result": "done",
        }
    )
    stats = stats_of(f"noise\n{payload}\n")
    assert stats["num_turns"] == 12
    assert stats["is_error"] is False
    assert stats_of("no json here") == {}


def test_prompts_differ_only_by_the_sanka_paragraph(harness: object) -> None:
    core = harness.PROMPT_CORE  # type: ignore[attr-defined]
    extra = harness.PROMPT_SANKA  # type: ignore[attr-defined]
    assert "Add new files only" in core
    assert "target_app.py" in core
    assert "rest_framework" in core
    assert "must not import" in core
    # the +Sanka variant is strictly additive: same contract, one extra tool
    assert "scan" in extra and "plan --to fastapi" in extra and "bench-candidate" in extra
    assert "contract" not in extra.lower()
