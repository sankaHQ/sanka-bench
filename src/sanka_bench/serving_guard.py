"""Guarded serving process that records native-target evidence.

The evaluator must not trust a candidate's own claims about how it serves
requests. This module is executed as a fresh child process per scenario. It
arms a PEP 578 audit hook *before* any candidate code is imported, then loads
the candidate entrypoint, serves exactly one scenario through an in-process
ASGI test client, and reports both the HTTP response and the collected serving
evidence:

- every first import of a forbidden module prefix, through three layers: an
  observing meta-path finder (sees every module resolution, including
  ``importlib.import_module`` calls that bypass ``__import__``), a PEP 578
  audit hook (cannot be removed once installed), and a final ``sys.modules``
  sweep after serving;
- process-creation events (a candidate must not spawn a source server);
- socket connections (the in-process client needs none, so any connect means
  the candidate reached for an external server);
- the class of the route object that matches the scenario and whether the
  matched endpoint's code lives inside the candidate workspace.

The guard observes and records rather than blocking, so a compatibility facade
still demonstrates its behavioral parity while failing the native-target gate
on the recorded evidence.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sanka-bench-serving-guard")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--entrypoint", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--forbidden-imports", required=True)
    return parser


_PROCESS_EVENTS = {
    "os.exec",
    "os.fork",
    "os.forkpty",
    "os.posix_spawn",
    "os.spawn",
    "os.system",
    "subprocess.Popen",
}
_SOCKET_EVENTS = {"socket.connect"}


def _matched_prefix(module: str, forbidden: list[str]) -> str | None:
    for prefix in forbidden:
        if module == prefix or module.startswith(prefix + "."):
            return prefix
    return None


class _ImportObserver:
    """Meta-path finder that records module resolutions without resolving.

    The ``import`` audit event only fires on the ``__import__`` path, so a
    direct ``importlib.import_module`` call would slip past the audit hook
    alone. Every import route consults ``sys.meta_path``, so this observer
    sees them all.
    """

    def __init__(self, forbidden: list[str], seen: set[str]) -> None:
        self._forbidden = forbidden
        self._seen = seen

    def find_spec(self, fullname: str, path: Any = None, target: Any = None) -> None:
        prefix = _matched_prefix(fullname, self._forbidden)
        if prefix is not None:
            self._seen.add(prefix)
        return None


def _arm_recorder(forbidden: list[str]) -> dict[str, set[str]]:
    evidence: dict[str, set[str]] = {
        "forbidden_imports": set(),
        "process_events": set(),
        "socket_events": set(),
    }

    def _hook(event: str, args: tuple[Any, ...]) -> None:
        if event == "import":
            module = args[0]
            if isinstance(module, str):
                prefix = _matched_prefix(module, forbidden)
                if prefix is not None:
                    evidence["forbidden_imports"].add(prefix)
        elif event in _PROCESS_EVENTS:
            evidence["process_events"].add(event)
        elif event in _SOCKET_EVENTS:
            evidence["socket_events"].add(event)

    sys.addaudithook(_hook)
    sys.meta_path.insert(0, _ImportObserver(forbidden, evidence["forbidden_imports"]))
    return evidence


def _sweep_loaded_modules(forbidden: list[str], seen: set[str]) -> None:
    for module in list(sys.modules):
        prefix = _matched_prefix(module, forbidden)
        if prefix is not None:
            seen.add(prefix)


def _matched_route(app: Any, method: str, path: str) -> Any:
    routes = getattr(app, "routes", None)
    if not isinstance(routes, list):
        return None
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "root_path": "",
        "headers": [],
        "query_string": b"",
    }
    from starlette.routing import Match

    partial = None
    for route in routes:
        match, _ = route.matches(scope)
        if match == Match.FULL:
            return route
        if match == Match.PARTIAL and partial is None:
            partial = route
    return partial


def _endpoint_in_workspace(route: Any, workspace: Path) -> bool:
    endpoint = getattr(route, "endpoint", None)
    if endpoint is None:
        return False
    try:
        unwrapped = inspect.unwrap(endpoint)
    except ValueError:
        return False
    code = getattr(unwrapped, "__code__", None)
    filename = getattr(code, "co_filename", None)
    if not isinstance(filename, str):
        return False
    try:
        return Path(filename).resolve().is_relative_to(workspace)
    except OSError:
        return False


def _class_name(value: Any) -> str | None:
    if value is None:
        return None
    cls = type(value)
    return f"{cls.__module__}.{cls.__qualname__}"


def _body(response: Any) -> Any:
    content = bytes(response.content)
    if not content:
        return None
    try:
        return response.json()
    except (ValueError, json.JSONDecodeError):
        return content.decode("utf-8")


def main() -> int:
    args = _parser().parse_args()
    workspace = args.workspace.resolve()
    scenario: dict[str, Any] = json.loads(args.scenario)
    forbidden = json.loads(args.forbidden_imports)
    if not isinstance(forbidden, list) or not all(isinstance(p, str) for p in forbidden):
        print("forbidden-imports must be a JSON array of module prefixes", file=sys.stderr)
        return 2

    # Arm the un-removable recorder before anything non-stdlib is imported.
    evidence = _arm_recorder(forbidden)
    sys.path.insert(0, str(workspace))

    import fastapi
    from fastapi.testclient import TestClient

    module_name = Path(args.entrypoint).stem
    module = importlib.import_module(module_name)
    app = getattr(module, "app", None)
    if app is None:
        print(f"candidate entrypoint {args.entrypoint} does not expose `app`", file=sys.stderr)
        return 3

    method = str(scenario["method"])
    path = str(scenario["path"])
    route = _matched_route(app, method, path)
    native: dict[str, Any] = {
        "app_is_fastapi": isinstance(app, fastapi.FastAPI),
        "route_class": _class_name(route),
        "endpoint_in_workspace": route is not None and _endpoint_in_workspace(route, workspace),
    }

    client = TestClient(app, follow_redirects=False)
    headers = {str(key): str(value) for key, value in dict(scenario.get("headers") or {}).items()}
    response = client.request(method, path, json=scenario.get("body"), headers=headers)

    import os

    _sweep_loaded_modules(forbidden, evidence["forbidden_imports"])
    native.update(
        {
            "forbidden_imports": sorted(evidence["forbidden_imports"]),
            "process_events": sorted(evidence["process_events"]),
            "socket_events": sorted(evidence["socket_events"]),
            "settings_module": os.environ.get("DJANGO_SETTINGS_MODULE"),
        }
    )
    served: dict[str, Any] = {"status": response.status_code, "body": _body(response)}
    capture = scenario.get("capture_headers")
    if capture:
        served["headers"] = {
            str(name).lower(): response.headers.get(str(name).lower(), "") for name in capture
        }
    payload = {
        "response": served,
        "native": native,
    }
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
