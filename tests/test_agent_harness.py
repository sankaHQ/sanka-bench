from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

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
    # the grading basis is disclosed: a hidden superset extends the public sample
    assert "hidden superset" in core
    assert "representative sample" in core
    # the +Sanka variant is strictly additive: same contract, one extra tool
    assert "scan" in extra and "plan --to fastapi" in extra and "bench-candidate" in extra
    # readiness-aware availability, not a copy mandate: the agent is told to read
    # the readiness report and treat low-readiness output as reference material,
    # with the source application staying the specification
    assert "readiness" in extra
    assert "reference material" in extra
    assert "remains the specification" in extra
    assert "cp -R" not in extra
    assert "contract" not in extra.lower()


def test_as_text_normalizes_timeout_output(harness: object) -> None:
    as_text = harness._as_text  # type: ignore[attr-defined]
    assert as_text(None) == ""
    assert as_text(b"partial \xff output") == "partial � output"
    assert as_text("already text") == "already text"


def test_codex_command_uses_responses_and_custom_openai_provider(
    harness: object, tmp_path: Path
) -> None:
    command = harness._codex_command(  # type: ignore[attr-defined]
        SimpleNamespace(agent_bin="codex", model="gpt-test", provider="openai"),
        "migrate it",
        tmp_path,
    )
    config = (tmp_path / "config.toml").read_text(encoding="utf-8")
    assert 'wire_api = "responses"' in config
    assert "[model_providers.openai-custom]" in config
    assert 'env_key = "OPENAI_API_KEY"' in config
    assert "--json" in command
    assert 'model_provider="openai-custom"' in command
    assert command[-1] == "migrate it"


def test_codex_stats_reads_usage_and_computes_disclosed_cost(harness: object) -> None:
    event = json.dumps(
        {
            "type": "turn.completed",
            "usage": {"input_tokens": 2_000_000, "output_tokens": 500_000},
        }
    )
    stats = harness._codex_stats(  # type: ignore[attr-defined]
        event,
        SimpleNamespace(price_in=1.0, price_out=2.0),
        12_345.0,
    )
    assert stats["num_turns"] == 1
    assert stats["duration_ms"] == 12_345.0
    assert stats["input_tokens"] == 2_000_000
    assert stats["output_tokens"] == 500_000
    assert stats["total_cost_usd"] == 3.0
    assert stats["is_error"] is False


def _fake_agent(tmp_path: Path, *, result: dict, touch: str | None) -> Path:
    script = tmp_path / "fake-agent"
    payload = json.dumps(result)
    touch_line = f"touch '{touch}'" if touch else ":"
    script.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "--version" ]; then echo fake-agent-1.0; exit 0; fi\n'
        f"{touch_line}\n"
        f"printf '%s\\n' '{payload}'\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def _run_adapter(task: Path, agent: Path, out: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "run_agent_candidate.py"),
            "--task",
            str(task),
            "--candidate-id",
            "claude-code-fake-alone",
            "--out",
            str(out),
            "--agent-bin",
            str(agent),
            "--max-turns",
            "60",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_turn_budget_exhaustion_freezes_the_workspace(tmp_path: Path) -> None:
    task = Path(__file__).resolve().parents[1] / "tasks" / "drf-fastapi" / "drf-fastapi-001"
    agent = _fake_agent(
        tmp_path,
        result={
            "num_turns": 60,
            "duration_ms": 1000,
            "total_cost_usd": 0.1,
            "is_error": True,
            "subtype": "error_max_turns",
            "result": "max turns reached",
        },
        touch="target_app.py",
    )
    out = tmp_path / "candidate"
    outcome = _run_adapter(task, agent, out)
    assert outcome.returncode == 0, outcome.stderr
    assert (out / "overlay" / "target_app.py").is_file()
    disclosure = (out / "GENERATED.md").read_text(encoding="utf-8")
    assert "turn budget (60) exhausted" in disclosure
    assert "frozen as-is" in disclosure


def test_empty_workspace_exits_with_classification_code(tmp_path: Path) -> None:
    task = Path(__file__).resolve().parents[1] / "tasks" / "drf-fastapi" / "drf-fastapi-001"
    agent = _fake_agent(
        tmp_path,
        result={
            "num_turns": 1,
            "duration_ms": 500,
            "total_cost_usd": 0.0,
            "is_error": False,
            "subtype": "success",
            "result": "done",
        },
        touch=None,
    )
    out = tmp_path / "candidate"
    outcome = _run_adapter(task, agent, out)
    assert outcome.returncode == 3
    assert "refusing to freeze an empty candidate" in outcome.stderr
    assert "infrastructure" in outcome.stderr
    assert not (out / "overlay").exists()


def test_non_budget_agent_error_stays_unfrozen(tmp_path: Path) -> None:
    task = Path(__file__).resolve().parents[1] / "tasks" / "drf-fastapi" / "drf-fastapi-001"
    agent = _fake_agent(
        tmp_path,
        result={
            "num_turns": 1,
            "duration_ms": 500,
            "total_cost_usd": 0.0,
            "is_error": True,
            "subtype": "error_during_execution",
            "result": "provider exploded",
        },
        touch="target_app.py",
    )
    out = tmp_path / "candidate"
    outcome = _run_adapter(task, agent, out)
    assert outcome.returncode == 1
    assert "agent reported an error" in outcome.stderr
    assert not (out / "overlay").exists()
