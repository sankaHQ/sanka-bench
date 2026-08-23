.PHONY: sync format lint typecheck test check baselines docker-baselines

sync:
	uv sync --frozen --extra fixture --group dev

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff format --check .
	uv run ruff check .

typecheck:
	uv run mypy

test:
	uv run python -m pytest

check: lint typecheck test
	uv run sanka-bench validate

baselines:
	uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/noop --output reports/noop.json
	uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/compatibility-bridge --output reports/compatibility-bridge.json
	uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/native-reference --output reports/native-reference.json
	uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/sanka-native --output reports/sanka-native.json

docker-baselines:
	uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/noop --output reports/noop-docker.json
	uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/compatibility-bridge --output reports/compatibility-bridge-docker.json
	uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/native-reference --output reports/native-reference-docker.json
	uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/sanka-native --output reports/sanka-native-docker.json
