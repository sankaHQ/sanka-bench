from __future__ import annotations

import json
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
    # the +Sanka variant is strictly additive: same contract, one extra tool
    assert "scan" in extra and "plan --to fastapi" in extra and "bench-candidate" in extra
    assert "cp -R bench-candidate/overlay/. ." in extra
    assert "sanka-manifest.json" in extra
    assert "do not copy\nonly target_app.py" in extra
    assert "contract" not in extra.lower()


def test_candidate_modes_preserve_official_arms_and_add_diagnostic_arm(
    harness: object,
) -> None:
    mode = harness._candidate_mode  # type: ignore[attr-defined]
    assert mode("opus-alone") == "alone"
    assert mode("opus-with-sanka") == "with-sanka"
    assert mode("opus-with-sanka-readiness-aware") == "readiness-aware"
    assert mode("opus-experimental") is None


def test_readiness_context_abstains_and_renders_route_checklist(harness: object) -> None:
    context = harness._readiness_context(  # type: ignore[attr-defined]
        {
            "readiness": 0.034,
            "native_routes": 1,
            "native_eligible_routes": 29,
            "needs_adaptation_routes": 1,
            "plan_hash": "sha256:task008",
            "routes": [
                {
                    "automatic": False,
                    "method": "GET",
                    "path": "/api/dynamic/entries/{code}/",
                    "operation": "get",
                    "strategy": "needs-manual-adaptation",
                    "adaptation_reasons": [
                        {
                            "code": "SANKA_DRF_ROUTE_PATTERN_UNSUPPORTED",
                            "feature": "route-pattern",
                            "message": "Regex route requires manual adaptation.",
                        }
                    ],
                },
                {
                    "automatic": True,
                    "method": "GET",
                    "path": "/api/",
                    "operation": "get",
                    "strategy": "native-fastapi-api-root",
                    "adaptation_reasons": [],
                },
            ],
        },
        0.5,
        {
            "skipped_routes": [
                {
                    "pattern": "api/class/entries/",
                    "view": "legacy_project.urls.permanent_style_redirect",
                    "reason": "non-drf-view",
                }
            ]
        },
    )
    assert context["decision"] == "gap-report-only"
    assert len(context["unsupported_routes"]) == 1
    prompt = harness._readiness_prompt(context)  # type: ignore[attr-defined]
    assert "3.4% (1/29" in prompt
    assert "did not generate a scaffold" in prompt
    assert "Do not run `sanka apply`" in prompt
    assert "SANKA_DRF_ROUTE_PATTERN_UNSUPPORTED" in prompt
    assert "api/class/entries/ -> legacy_project.urls.permanent_style_redirect" in prompt
    assert "Allow, Location, and WWW-Authenticate" in prompt
    assert "not a framework\n  redirect" in prompt


def test_readiness_context_emits_scaffold_at_threshold(harness: object) -> None:
    context = harness._readiness_context(  # type: ignore[attr-defined]
        {
            "readiness": 0.75,
            "native_routes": 3,
            "native_eligible_routes": 4,
            "needs_adaptation_routes": 1,
            "plan_hash": "sha256:ready",
            "routes": [],
        },
        0.5,
    )
    assert context["decision"] == "emit-scaffold"
    prompt = harness._readiness_prompt(context)  # type: ignore[attr-defined]
    assert "generated `bench-candidate/overlay/`" in prompt


@pytest.mark.parametrize(
    ("readiness", "expected_decision", "expects_apply"),
    [(0.034, "gap-report-only", False), (0.75, "emit-scaffold", True)],
)
def test_readiness_preflight_mechanically_gates_scaffold(
    harness: object,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    readiness: float,
    expected_decision: str,
    expects_apply: bool,
) -> None:
    plan_dir = tmp_path / ".sanka"
    plan_dir.mkdir()
    (plan_dir / "plan-fastapi.json").write_text(
        json.dumps(
            {
                "readiness": readiness,
                "native_routes": 3 if readiness >= 0.5 else 1,
                "native_eligible_routes": 4 if readiness >= 0.5 else 29,
                "needs_adaptation_routes": 1,
                "plan_hash": "sha256:preflight",
                "routes": [],
            }
        ),
        encoding="utf-8",
    )
    (plan_dir / "scan.json").write_text(
        json.dumps(
            {
                "skipped_routes": [
                    {
                        "pattern": "legacy/redirect/",
                        "view": "config.urls.legacy_redirect",
                        "reason": "non-drf-view",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    commands: list[list[str]] = []

    def fake_run(command: list[str], *, workspace: Path, env: dict[str, str]) -> SimpleNamespace:
        assert workspace == tmp_path
        assert env == {"BENCH": "1"}
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(harness, "_run_sanka_command", fake_run)
    context = harness._prepare_readiness_context(  # type: ignore[attr-defined]
        tmp_path,
        Path("/tools/sanka"),
        {"BENCH": "1"},
        0.5,
    )
    assert context["decision"] == expected_decision
    assert context["skipped_routes"] == [
        {
            "pattern": "legacy/redirect/",
            "view": "config.urls.legacy_redirect",
            "reason": "non-drf-view",
        }
    ]
    assert [command[1] for command in commands] == [
        "scan",
        "plan",
        *(("apply",) if expects_apply else ()),
    ]
    if expects_apply:
        assert "--plan-hash" in commands[-1]
        assert "sha256:preflight" in commands[-1]


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
