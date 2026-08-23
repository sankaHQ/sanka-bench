"""Tool-neutral local evaluator for one repository migration candidate."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from sanka_bench import __version__
from sanka_bench.hashing import digest_payload, digest_tree
from sanka_bench.process import run_command
from sanka_bench.schema import load_and_validate, validate_payload


class EvaluationError(RuntimeError):
    """Raised when an evaluator input is unsafe or structurally incomplete."""


def evaluate_local(task_dir: Path, candidate_dir: Path) -> dict[str, Any]:
    task_dir = task_dir.resolve()
    candidate_dir = candidate_dir.resolve()
    task = load_and_validate(task_dir / "task.yaml", "task")
    candidate = load_and_validate(candidate_dir / "candidate.yaml", "candidate")

    source_dir = _resolve_within(task_dir, cast(str, task["source"]["path"]))
    driver_path = _resolve_within(task_dir, cast(str, task["evaluation"]["driver"]))
    scenarios_path = _resolve_within(task_dir, cast(str, task["evaluation"]["scenarios"]))
    scenarios = _load_scenarios(scenarios_path)
    repeat = cast(int, task["evaluation"]["repeat"])
    timeout = cast(int, task["evaluation"]["timeout_seconds"])

    errors: list[str] = []
    actual_source_digest = digest_tree(source_dir)
    expected_source_digest = cast(str, task["source"]["provenance"]["digest"])
    provenance_matches = actual_source_digest == expected_source_digest
    if not provenance_matches:
        errors.append(
            "source digest mismatch: "
            f"expected {expected_source_digest}, observed {actual_source_digest}"
        )

    source_regression = _run_regression(task, source_dir, timeout=timeout)
    if not source_regression[0]:
        errors.extend(f"source regression: {detail}" for detail in source_regression[1])

    source_runs: list[list[dict[str, Any] | None]] = []
    candidate_runs: list[list[dict[str, Any] | None]] = []
    regression_runs: list[bool] = []
    compliance_runs: list[bool] = []
    compliance_details: list[str] = []

    for run_index in range(repeat):
        with tempfile.TemporaryDirectory(prefix=f"sanka-bench-{run_index + 1}-") as temp:
            temp_root = Path(temp)
            workspace = temp_root / "candidate"
            shutil.copytree(source_dir, workspace)
            _apply_candidate(candidate, candidate_dir, workspace)

            regression_passed, regression_details = _run_regression(
                task,
                workspace,
                timeout=timeout,
            )
            regression_runs.append(regression_passed)
            errors.extend(
                f"candidate regression run {run_index + 1}: {detail}"
                for detail in regression_details
            )

            compliance_passed, detail = _check_target_compliance(task, workspace)
            compliance_runs.append(compliance_passed)
            compliance_details.append(detail)

            oracle_results: list[dict[str, Any] | None] = []
            target_results: list[dict[str, Any] | None] = []
            for scenario in scenarios:
                oracle, oracle_error = _run_driver(
                    driver_path,
                    mode="source",
                    workspace=source_dir,
                    scenario=scenario,
                    database=temp_root / f"source-{scenario['id']}.sqlite3",
                    timeout=timeout,
                )
                target, target_error = _run_driver(
                    driver_path,
                    mode="candidate",
                    workspace=workspace,
                    scenario=scenario,
                    database=temp_root / f"candidate-{scenario['id']}.sqlite3",
                    timeout=timeout,
                )
                oracle_results.append(oracle)
                target_results.append(target)
                if oracle_error:
                    errors.append(
                        f"source scenario {scenario['id']} run {run_index + 1}: {oracle_error}"
                    )
                if target_error:
                    errors.append(
                        f"candidate scenario {scenario['id']} run {run_index + 1}: {target_error}"
                    )
            source_runs.append(oracle_results)
            candidate_runs.append(target_results)

    scenario_reports = _scenario_reports(scenarios, source_runs, candidate_runs)
    source_scenarios_valid = all(
        result is not None for source_run in source_runs for result in source_run
    )
    source_qualified = provenance_matches and source_regression[0] and source_scenarios_valid
    regression_tests = bool(regression_runs) and all(regression_runs)
    native_target = bool(compliance_runs) and all(compliance_runs)
    target_boot = all(report["target_ran"] for report in scenario_reports)
    behavior_parity = all(report["behavior_match"] for report in scenario_reports)
    database_parity = all(report["database_match"] for report in scenario_reports)
    side_effect_parity = all(report["side_effect_match"] for report in scenario_reports)
    deterministic = all(report["stable"] for report in scenario_reports)

    hard_gates = {
        "source_qualified": source_qualified,
        "regression_tests": regression_tests,
        "target_boot": target_boot,
        "native_target": native_target,
        "behavior_parity": behavior_parity,
        "database_parity": database_parity,
        "side_effect_parity": side_effect_parity,
        "deterministic": deterministic,
    }
    fully_migrated = all(hard_gates.values())
    if not native_target:
        errors.extend(
            f"native-target compliance run {index + 1}: {detail}"
            for index, detail in enumerate(compliance_details)
            if detail != "ok"
        )

    result: dict[str, Any] = {
        "schema_version": "sanka-bench/result/v0.1",
        "task_id": cast(str, task["id"]),
        "candidate_id": cast(str, candidate["id"]),
        "status": "invalid" if not source_qualified else ("passed" if fully_migrated else "failed"),
        "fully_migrated": fully_migrated,
        "hard_gates": hard_gates,
        "metrics": {
            "scenario_count": len(scenario_reports),
            "route_coverage": _fraction(scenario_reports, "target_ran"),
            "behavioral_parity": _fraction(scenario_reports, "behavior_match"),
            "database_parity": _fraction(scenario_reports, "database_match"),
            "side_effect_parity": _fraction(scenario_reports, "side_effect_match"),
        },
        "scenarios": scenario_reports,
        "provenance": {
            "task_digest": digest_tree(task_dir),
            "source_digest": actual_source_digest,
            "candidate_digest": digest_tree(candidate_dir),
            "evaluator_version": __version__,
            "repeat": repeat,
        },
        "errors": _deduplicate(errors),
    }
    validate_payload(result, "result", label="evaluation result")
    return result


def _resolve_within(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise EvaluationError(f"path escapes its benchmark root: {relative}")
    if not candidate.exists():
        raise EvaluationError(f"required path does not exist: {candidate}")
    return candidate


def _load_scenarios(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise EvaluationError(f"{path} must contain at least one scenario")
    scenarios: list[dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise EvaluationError(f"scenario {index} must contain a string id")
        scenarios.append(cast(dict[str, Any], item))
    return scenarios


def _apply_candidate(
    candidate: dict[str, Any],
    candidate_dir: Path,
    workspace: Path,
) -> None:
    kind = cast(str, candidate["kind"])
    if kind == "noop":
        return
    overlay = _resolve_within(candidate_dir, cast(str, candidate["overlay"]))
    if not overlay.is_dir():
        raise EvaluationError(f"candidate overlay is not a directory: {overlay}")
    shutil.copytree(overlay, workspace, dirs_exist_ok=True)


def _run_regression(
    task: dict[str, Any],
    workspace: Path,
    *,
    timeout: int,
) -> tuple[bool, list[str]]:
    details: list[str] = []
    passed = True
    commands = cast(list[list[str]], task["commands"]["regression"])
    for command in commands:
        argv = [sys.executable if part == "{python}" else part for part in command]
        outcome = run_command(argv, cwd=workspace, timeout=timeout)
        if outcome.passed:
            continue
        passed = False
        rendered = outcome.stderr.strip() or outcome.stdout.strip() or "no output"
        details.append(f"{' '.join(command)} exited {outcome.returncode}: {rendered}")
    return passed, details


def _check_target_compliance(
    task: dict[str, Any],
    workspace: Path,
) -> tuple[bool, str]:
    target = cast(dict[str, Any], task["target"])
    entrypoint = workspace / cast(str, target["entrypoint"])
    if not entrypoint.is_file():
        return False, f"missing target entrypoint {target['entrypoint']}"
    source = entrypoint.read_text(encoding="utf-8")
    missing = [
        pattern for pattern in cast(list[str], target["required_patterns"]) if pattern not in source
    ]
    forbidden = [
        pattern for pattern in cast(list[str], target["forbidden_patterns"]) if pattern in source
    ]
    if missing or forbidden:
        parts = []
        if missing:
            parts.append(f"missing required patterns: {', '.join(missing)}")
        if forbidden:
            parts.append(f"forbidden serving patterns: {', '.join(forbidden)}")
        return False, "; ".join(parts)
    return True, "ok"


def _run_driver(
    driver_path: Path,
    *,
    mode: str,
    workspace: Path,
    scenario: dict[str, Any],
    database: Path,
    timeout: int,
) -> tuple[dict[str, Any] | None, str | None]:
    outcome = run_command(
        [
            sys.executable,
            str(driver_path),
            "--mode",
            mode,
            "--workspace",
            str(workspace),
            "--scenario",
            json.dumps(scenario, ensure_ascii=False, separators=(",", ":")),
            "--database",
            str(database),
        ],
        cwd=driver_path.parent,
        timeout=timeout,
    )
    if not outcome.passed:
        detail = outcome.stderr.strip() or outcome.stdout.strip() or "no output"
        return None, f"driver exited {outcome.returncode}: {detail}"
    lines = [line for line in outcome.stdout.splitlines() if line.strip()]
    if not lines:
        return None, "driver returned no JSON"
    try:
        payload = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        return None, f"driver returned invalid JSON: {exc}"
    if not isinstance(payload, dict):
        return None, "driver result must be an object"
    return cast(dict[str, Any], payload), None


def _scenario_reports(
    scenarios: Sequence[dict[str, Any]],
    source_runs: Sequence[Sequence[dict[str, Any] | None]],
    candidate_runs: Sequence[Sequence[dict[str, Any] | None]],
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for scenario_index, scenario in enumerate(scenarios):
        sources = [run[scenario_index] for run in source_runs]
        candidates = [run[scenario_index] for run in candidate_runs]
        target_ran = all(candidate is not None for candidate in candidates)
        behavior = target_ran and all(
            _view(source, "response") == _view(candidate, "response")
            for source, candidate in zip(sources, candidates, strict=True)
        )
        database = target_ran and all(
            _view(source, "database") == _view(candidate, "database")
            for source, candidate in zip(sources, candidates, strict=True)
        )
        side_effects = target_ran and all(
            _view(source, "side_effects") == _view(candidate, "side_effects")
            for source, candidate in zip(sources, candidates, strict=True)
        )
        candidate_fingerprints = [
            digest_payload(candidate) for candidate in candidates if candidate is not None
        ]
        stable = target_ran and len(set(candidate_fingerprints)) == 1
        mismatches = []
        if not target_ran:
            mismatches.append("target did not run")
        if not behavior:
            mismatches.append("HTTP behavior differs")
        if not database:
            mismatches.append("database state differs")
        if not side_effects:
            mismatches.append("side effects differ")
        if not stable:
            mismatches.append("candidate output varies between clean runs")
        reports.append(
            {
                "id": cast(str, scenario["id"]),
                "target_ran": target_ran,
                "behavior_match": behavior,
                "database_match": database,
                "side_effect_match": side_effects,
                "stable": stable,
                "detail": "; ".join(mismatches) if mismatches else "ok",
            }
        )
    return reports


def _view(payload: dict[str, Any] | None, field: str) -> Any:
    if payload is None:
        return None
    return payload.get(field)


def _fraction(reports: Sequence[dict[str, Any]], field: str) -> dict[str, Any]:
    total = len(reports)
    passed = sum(bool(report[field]) for report in reports)
    return {
        "passed": passed,
        "total": total,
        "rate": passed / total if total else 0.0,
    }


def _deduplicate(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
