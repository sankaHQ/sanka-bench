from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("source", "candidate"), required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--database", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    workspace = args.workspace.resolve()
    sys.path.insert(0, str(workspace))
    os.environ["DJANGO_SETTINGS_MODULE"] = "fixture_project.settings"
    os.environ["BENCH_DB_PATH"] = str(args.database.resolve())

    import django

    django.setup()
    from django.core.management import call_command

    call_command("migrate", interactive=False, verbosity=0)

    from widgets.models import Widget

    Widget.objects.all().delete()
    Widget.objects.create(id=1, name="Alpha", quantity=3)
    scenario: dict[str, Any] = json.loads(args.scenario)
    response = _request(args.mode, scenario)
    payload = {
        "response": {
            "status": response.status_code,
            "body": _body(response),
        },
        "database": list(Widget.objects.order_by("id").values("id", "name", "quantity")),
        "side_effects": [],
    }
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
    return 0


def _request(mode: str, scenario: dict[str, Any]) -> Any:
    method = str(scenario["method"])
    path = str(scenario["path"])
    body = scenario.get("body")
    if mode == "source":
        from django.test import Client

        client = Client()
        return client.generic(
            method,
            path,
            data=json.dumps(body) if body is not None else "",
            content_type="application/json",
        )

    from fastapi.testclient import TestClient
    from target_app import app

    client = TestClient(app, follow_redirects=False)
    return client.request(method, path, json=body)


def _body(response: Any) -> Any:
    content = bytes(response.content)
    if not content:
        return None
    try:
        return response.json()
    except (ValueError, json.JSONDecodeError):
        return content.decode("utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
