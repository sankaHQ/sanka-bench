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

Two agent families share the same contract, prompt, and freezing logic:

- ``--agent claude-code`` (default) drives the Claude CLI headlessly and uses
  its self-reported turns, duration, and cost;
- ``--agent codex`` drives OpenAI's Codex CLI (``codex exec``) against the
  OpenAI API or any OpenAI-compatible provider (``--provider deepinfra``,
  ``fireworks``, ``together``). Codex does not self-report dollar cost, so the
  run records measured wall-clock and token usage, and computes cost from the
  per-model prices passed via ``--price-in``/``--price-out`` (USD per million
  tokens) — the disclosure names that basis explicitly.

Candidate ids stay free-form (``<agent>-<model-slug>-alone`` /
``...-with-sanka``); the ``*-with-sanka`` suffix selects the extra prompt
paragraph.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
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

The complete generated deliverable is the contents of bench-candidate/overlay/.
Copy every file and directory from that overlay to the repository root, for
example with `cp -R bench-candidate/overlay/. .`. This includes non-Python
runtime files such as sanka-manifest.json and requirements.txt; do not copy
only target_app.py or sanka_*.py. Then verify the scenarios and adjust the
copied files if needed.
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
        help="<agent>-<model-slug>-alone or ...-with-sanka",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--agent", default="claude-code", choices=("claude-code", "codex"))
    parser.add_argument("--agent-bin", default=None)
    parser.add_argument("--model", default="claude-sonnet-5")
    parser.add_argument(
        "--provider",
        default="openai",
        choices=("openai", "deepinfra", "fireworks", "together"),
        help="codex only: which OpenAI-compatible API serves the model",
    )
    parser.add_argument(
        "--price-in",
        type=float,
        default=None,
        help="codex only: USD per million input tokens, for computed cost",
    )
    parser.add_argument(
        "--price-out",
        type=float,
        default=None,
        help="codex only: USD per million output tokens, for computed cost",
    )
    parser.add_argument("--max-turns", type=int, default=60)
    parser.add_argument("--sanka-bin", type=Path, default=None)
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument(
        "--prior-failure",
        default=None,
        help="disclosed reason the previous attempt failed (infrastructure retries only)",
    )
    args = parser.parse_args()

    task_dir = args.task.resolve()
    source = task_dir / "source"
    scenarios = task_dir / "public-tests" / "scenarios.json"
    if not source.is_dir() or not scenarios.is_file():
        print(f"not a benchmark task: {task_dir}", file=sys.stderr)
        return 2
    with_sanka = args.candidate_id.endswith("-with-sanka")
    if not with_sanka and not args.candidate_id.endswith("-alone"):
        print("candidate id must end in -alone or -with-sanka", file=sys.stderr)
        return 2
    if with_sanka and args.sanka_bin is None:
        print(f"{args.candidate_id} requires --sanka-bin", file=sys.stderr)
        return 2
    if args.agent_bin is None:
        args.agent_bin = "claude" if args.agent == "claude-code" else "codex"

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
        if with_sanka:
            prompt += PROMPT_SANKA.format(sanka=args.sanka_bin.resolve())

        env = dict(os.environ)
        for name in (
            "DJANGO_SETTINGS_MODULE",
            "BENCH_DB_PATH",
            "CLAUDECODE",
            "CLAUDE_CODE_ENTRYPOINT",
        ):
            env.pop(name, None)
        if args.agent == "codex":
            codex_home = Path(temp) / "codex-home"
            command = _codex_command(args, prompt, codex_home)
            env["CODEX_HOME"] = str(codex_home)
        else:
            command = [
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
            ]
        started = time.monotonic()
        outcome = subprocess.run(
            command,
            cwd=workspace,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=3600,
            check=False,
        )
        measured_ms = (time.monotonic() - started) * 1000
        if args.agent == "codex":
            stats = _codex_stats(outcome.stdout, args, measured_ms)
        else:
            stats = _agent_stats(outcome.stdout)
        out_dir = args.out.resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        raw = outcome.stdout.strip().splitlines()
        if raw:
            (out_dir / "agent-result.json").write_text(raw[-1] + "\n", encoding="utf-8")
        if outcome.stdout:
            (out_dir / "agent-log.jsonl").write_text(outcome.stdout, encoding="utf-8")
        if outcome.stderr:
            (out_dir / "agent-stderr.log").write_text(outcome.stderr, encoding="utf-8")
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
        _write_candidate(out_dir, args, agent_version, stats)
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


PROVIDER_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "deepinfra": "https://api.deepinfra.com/v1/openai",
    "fireworks": "https://api.fireworks.ai/inference/v1",
    "together": "https://api.together.xyz/v1",
}
PROVIDER_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "deepinfra": "DEEPINFRA_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "together": "TOGETHER_API_KEY",
}


def _codex_command(args: argparse.Namespace, prompt: str, codex_home: Path) -> list[str]:
    codex_home.mkdir(parents=True, exist_ok=True)
    # The isolated CODEX_HOME has no login session, so every provider —
    # OpenAI included — authenticates through an env-var API key declared on
    # a custom model_providers entry. Codex CLI >= 0.150 refuses
    # `wire_api = "chat"` outright, so every provider speaks the responses
    # wire API; it also reserves the built-in `openai` provider id (and the
    # built-in provider sends no bearer from a loginless CODEX_HOME), so the
    # OpenAI entry is registered as `openai-custom` against the same base URL.
    provider_id = "openai-custom" if args.provider == "openai" else args.provider
    config = (
        f'preferred_auth_method = "apikey"\n'
        f"[model_providers.{provider_id}]\n"
        f'name = "{provider_id}"\n'
        f'base_url = "{PROVIDER_BASE_URLS[args.provider]}"\n'
        f'env_key = "{PROVIDER_ENV_KEYS[args.provider]}"\n'
        f'wire_api = "responses"\n'
    )
    (codex_home / "config.toml").write_text(config, encoding="utf-8")
    command = [
        args.agent_bin,
        "exec",
        "--model",
        args.model,
        "--json",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
    ]
    command += ["--config", f'model_provider="{provider_id}"']
    command.append(prompt)
    return command


def _codex_stats(stdout: str, args: argparse.Namespace, measured_ms: float) -> dict[str, object]:
    turns = 0
    input_tokens = 0
    output_tokens = 0
    is_error = False
    last_error: str | None = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        kind = str(event.get("type") or event.get("msg", {}).get("type") or "")
        if "turn" in kind and kind.endswith("completed"):
            turns += 1
        if kind in {"error", "turn.failed"}:
            is_error = True
            last_error = json.dumps(event)[:500]
        usage = _find_usage(event)
        if usage:
            input_tokens = max(input_tokens, int(usage.get("input_tokens") or 0)) or input_tokens
            output_tokens = (
                max(output_tokens, int(usage.get("output_tokens") or 0)) or output_tokens
            )
    cost: float | None = None
    basis = "measured wall-clock; token usage unavailable"
    if input_tokens or output_tokens:
        basis = f"computed from token usage ({input_tokens} in / {output_tokens} out)"
        if args.price_in is not None and args.price_out is not None:
            cost = (input_tokens * args.price_in + output_tokens * args.price_out) / 1_000_000
            basis += f" at ${args.price_in}/M in, ${args.price_out}/M out"
    stats: dict[str, object] = {
        "num_turns": turns or None,
        "duration_ms": measured_ms,
        "total_cost_usd": cost,
        "is_error": is_error,
        "subtype": "codex-exec",
        "result": last_error,
        "cost_basis": basis,
        "input_tokens": input_tokens or None,
        "output_tokens": output_tokens or None,
    }
    return stats


def _find_usage(event: dict) -> dict | None:
    for key in ("usage", "token_usage"):
        value = event.get(key)
        if isinstance(value, dict):
            return value
    info = event.get("info") or event.get("msg") or {}
    if isinstance(info, dict):
        for key in ("usage", "token_usage", "total_token_usage"):
            value = info.get(key)
            if isinstance(value, dict):
                return value
    return None


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


def _write_candidate(
    out_dir: Path, args: argparse.Namespace, agent_version: str, stats: dict[str, object]
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "schema_version: sanka-bench/candidate/v0.2",
        f"id: {args.candidate_id}",
        "kind: overlay",
        "overlay: overlay",
        "provenance:",
        f"  producer: {args.agent}",
        f"  revision: {args.model} via {agent_version or 'claude cli'}",
        "  command: scripts/run_agent_candidate.py (prompt and budget in GENERATED.md)",
    ]
    duration = stats.get("duration_ms")
    cost = stats.get("total_cost_usd")
    turns = stats.get("num_turns")
    if any(isinstance(value, int | float) for value in (duration, cost, turns)):
        lines.append("stats:")
        if isinstance(turns, int | float):
            lines.append(f"  turns: {int(turns)}")
        if isinstance(duration, int | float):
            lines.append(f"  duration_seconds: {round(duration / 1000, 1)}")
        if isinstance(cost, int | float):
            lines.append(f"  cost_usd: {round(float(cost), 4)}")
    (out_dir / "candidate.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    attempt_text = str(args.attempt)
    if args.prior_failure:
        attempt_text += (
            f" (previous attempt failed on infrastructure, not agent quality: {args.prior_failure})"
        )
    elif args.attempt == 1:
        attempt_text += " (pass@1; no retries)"
    agent_label = "Claude Code" if args.agent == "claude-code" else "Codex CLI"
    provider = "anthropic" if args.agent == "claude-code" else args.provider
    version = agent_version or args.agent_bin
    (out_dir / "GENERATED.md").write_text(
        f"""# Coding-agent baseline provenance: {args.candidate_id}

Produced unattended by `scripts/run_agent_candidate.py` — no human
intervention between prompt and frozen overlay.

| Disclosure | Value |
|---|---|
| Agent | {agent_label} (`{version}`) |
| Provider | {provider} |
| Cost basis | {stats.get("cost_basis", "agent-reported")} |
| Model | `{args.model}` |
| Turn budget | {args.max_turns} |
| Turns used | {stats.get("num_turns", "unknown")} |
| Duration | {minutes} |
| Reported cost | {cost_text} |
| Attempt | {attempt_text} |

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
