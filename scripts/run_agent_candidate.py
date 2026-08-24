"""Produce a frozen coding-agent candidate for one benchmark task.

Runs a command-line coding agent headlessly against a pristine copy of the
task's source with a fixed migration prompt, collects every file the agent
added as the candidate overlay, and writes the candidate with full
disclosure: model, tool version, prompt verbatim, turn budget, turns used,
duration, and reported cost. The agent runs unattended — no human
intervention — and the frozen overlay is then graded by the ordinary
tool-neutral evaluator like any other candidate.

Two configurations, identical except for one paragraph of the prompt:

- ``--candidate-id claude-code-alone`` — the agent and the task, nothing else;
- ``--candidate-id claude-code-with-sanka`` (with ``--sanka-bin``) — the same
  agent, same budget, same contract, plus the Sanka CLI and three lines
  telling it that Sanka can generate the native candidate.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROMPT_CORE = """Migrate this Django REST Framework application to FastAPI, natively.

Deliverable contract (an automated evaluator enforces all of it):
1. Add new files only - never modify or delete existing source files.
2. Expose the FastAPI application as `app` in a new file `target_app.py` at the
   repository root.
3. The serving process must not import `rest_framework` or Django's
   request-serving machinery (`django.core.asgi`, `django.core.wsgi`,
   `django.core.handlers`, `django.test`). Django stays for the ORM only:
   create separate serving settings that remove every rest_framework app from
   INSTALLED_APPS, and point Django at them from target_app.py.
4. Behavior must match the original application exactly for every request in
   `public-tests/scenarios.json`: status codes, JSON bodies including exact
   error strings, and the resulting database rows. The evaluator seeds the
   database itself, replays each scenario against both applications from
   identical snapshots, repeats runs, and rejects nondeterminism.
5. The database path comes from the BENCH_DB_PATH environment variable through
   the existing settings module; reuse that mechanism unchanged.

A Python interpreter with django, djangorestframework, and fastapi installed
is available at: {python}
Use it to run the original app and your app side by side (django test client
vs fastapi TestClient) and verify every scenario before you finish. Do not
consider the task done until every scenario matches exactly.
"""

PROMPT_SANKA = """
The Sanka migration CLI is installed at: {sanka}
It can generate a native FastAPI candidate for you:

    {sanka} scan .
    {sanka} plan --to fastapi
    {sanka} apply --root . --bench-candidate ./bench-candidate

The bench-candidate overlay contains target_app.py and its supporting files;
copy them to the repository root as your deliverable, verify the scenarios,
and adjust them if needed.
"""

EXCLUDED_PARTS = {
    ".claude",
    ".git",
    ".sanka",
    ".venv",
    "__pycache__",
    "bench-candidate",
    "node_modules",
    "public-tests",
}
EXCLUDED_SUFFIXES = {".log", ".pyc", ".sqlite3"}
EXCLUDED_NAMES = {".DS_Store", "AGENT_TASK.md", "CLAUDE.md"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument(
        "--candidate-id",
        required=True,
        choices=("claude-code-alone", "claude-code-with-sanka"),
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--agent-bin", default="claude")
    parser.add_argument("--model", default="claude-sonnet-5")
    parser.add_argument("--max-turns", type=int, default=60)
    parser.add_argument("--sanka-bin", type=Path, default=None)
    args = parser.parse_args()

    task_dir = args.task.resolve()
    source = task_dir / "source"
    scenarios = task_dir / "public-tests" / "scenarios.json"
    if not source.is_dir() or not scenarios.is_file():
        print(f"not a benchmark task: {task_dir}", file=sys.stderr)
        return 2
    if args.candidate_id == "claude-code-with-sanka" and args.sanka_bin is None:
        print("claude-code-with-sanka requires --sanka-bin", file=sys.stderr)
        return 2

    agent_version = subprocess.run(
        [args.agent_bin, "--version"], capture_output=True, text=True, check=False
    ).stdout.strip()

    with tempfile.TemporaryDirectory(prefix="sanka-agent-") as temp:
        workspace = Path(temp) / "workspace"
        shutil.copytree(source, workspace)
        public_tests = workspace / "public-tests"
        public_tests.mkdir()
        shutil.copy2(scenarios, public_tests / "scenarios.json")

        prompt = PROMPT_CORE.format(python=sys.executable)
        if args.candidate_id == "claude-code-with-sanka":
            prompt += PROMPT_SANKA.format(sanka=args.sanka_bin.resolve())

        env = dict(os.environ)
        for name in (
            "DJANGO_SETTINGS_MODULE",
            "BENCH_DB_PATH",
            "CLAUDECODE",
            "CLAUDE_CODE_ENTRYPOINT",
        ):
            env.pop(name, None)
        outcome = subprocess.run(
            [
                args.agent_bin,
                "-p",
                prompt,
                "--model",
                args.model,
                "--max-turns",
                str(args.max_turns),
                "--output-format",
                "json",
                "--dangerously-skip-permissions",
            ],
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
            timeout=3600,
            check=False,
        )
        stats = _agent_stats(outcome.stdout)
        out_dir = args.out.resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        raw = outcome.stdout.strip().splitlines()
        if raw:
            (out_dir / "agent-result.json").write_text(raw[-1] + "\n", encoding="utf-8")
        if outcome.returncode != 0 and not stats:
            detail = outcome.stderr.strip()[:2000] or "no output"
            print(f"agent run failed: {detail}", file=sys.stderr)
            return 1
        if stats.get("is_error"):
            print(f"agent reported an error: {stats.get('result') or stats}", file=sys.stderr)
            return 1

        pristine = {
            path.relative_to(source).as_posix(): path.read_bytes()
            for path in sorted(source.rglob("*"))
            if path.is_file()
        }
        added: list[str] = []
        modified: list[str] = []
        for path in sorted(workspace.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(workspace)
            if _excluded(relative):
                continue
            key = relative.as_posix()
            if key not in pristine:
                added.append(key)
            elif path.read_bytes() != pristine[key]:
                modified.append(key)

        overlay = out_dir / "overlay"
        if overlay.exists():
            shutil.rmtree(overlay)
        for key in added:
            destination = overlay / key
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(workspace / key, destination)

        if not added:
            print(
                "agent produced no new files; refusing to freeze an empty candidate",
                file=sys.stderr,
            )
            return 1
        _write_candidate(out_dir, args, agent_version)
        _write_disclosure(
            out_dir,
            args,
            agent_version=agent_version,
            prompt=prompt,
            stats=stats,
            added=added,
            modified=modified,
        )
    print(
        f"{args.candidate_id}: {len(added)} file(s) in overlay"
        + (f", {len(modified)} contract-violating modification(s) DROPPED" if modified else "")
        + (f", {stats.get('num_turns', '?')} turns" if stats else "")
    )
    return 0


def _excluded(relative: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return True
    if relative.suffix in EXCLUDED_SUFFIXES:
        return True
    return relative.name in EXCLUDED_NAMES


def _agent_stats(stdout: str) -> dict[str, object]:
    for line in reversed([line for line in stdout.splitlines() if line.strip()]):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and "num_turns" in payload:
            return {
                key: payload.get(key)
                for key in (
                    "num_turns",
                    "duration_ms",
                    "total_cost_usd",
                    "is_error",
                    "subtype",
                    "result",
                )
            }
    return {}


def _write_candidate(out_dir: Path, args: argparse.Namespace, agent_version: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "candidate.yaml").write_text(
        "schema_version: sanka-bench/candidate/v0.1\n"
        f"id: {args.candidate_id}\n"
        "kind: overlay\n"
        "overlay: overlay\n"
        "provenance:\n"
        "  producer: claude-code\n"
        f"  revision: {args.model} via {agent_version or 'claude cli'}\n"
        "  command: scripts/run_agent_candidate.py (prompt and budget in GENERATED.md)\n",
        encoding="utf-8",
    )


def _write_disclosure(
    out_dir: Path,
    args: argparse.Namespace,
    *,
    agent_version: str,
    prompt: str,
    stats: dict[str, object],
    added: list[str],
    modified: list[str],
) -> None:
    duration = stats.get("duration_ms")
    minutes = f"{int(duration) / 60000:.1f} min" if isinstance(duration, int | float) else "unknown"
    cost = stats.get("total_cost_usd")
    cost_text = f"${float(cost):.2f}" if isinstance(cost, int | float) else "unknown"
    modified_text = (
        "\n".join(f"- `{name}`" for name in modified)
        if modified
        else "none — the add-only contract was respected"
    )
    (out_dir / "GENERATED.md").write_text(
        f"""# Coding-agent baseline provenance: {args.candidate_id}

Produced unattended by `scripts/run_agent_candidate.py` — no human
intervention between prompt and frozen overlay.

| Disclosure | Value |
|---|---|
| Agent | Claude Code (`{agent_version or "claude cli"}`) |
| Model | `{args.model}` |
| Turn budget | {args.max_turns} |
| Turns used | {stats.get("num_turns", "unknown")} |
| Duration | {minutes} |
| Reported cost | {cost_text} |
| Attempts | 1 (pass@1; no retries) |

Files added by the agent: {len(added)}. Contract-violating modifications to
existing source files (dropped from the overlay, since candidates are
add-only):
{modified_text}

## Prompt (verbatim)

```
{prompt}
```
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
