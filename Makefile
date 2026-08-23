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

# task-id:candidate-name pairs; baselines live at baselines/<task>/<candidate>/
BASELINES_001 = noop compatibility-bridge native-reference sanka-native
BASELINES_002 = noop compatibility-bridge native-reference sanka-native

baselines:
	@for name in $(BASELINES_001); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/drf-fastapi-001/$$name --output reports/drf-fastapi-001-$$name.json || exit 1; \
	done
	@for name in $(BASELINES_002); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-002 --candidate baselines/drf-fastapi-002/$$name --output reports/drf-fastapi-002-$$name.json || exit 1; \
	done

docker-baselines:
	@for name in $(BASELINES_001); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/drf-fastapi-001/$$name --output reports/drf-fastapi-001-$$name-docker.json || exit 1; \
	done
	@for name in $(BASELINES_002); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-002 --candidate baselines/drf-fastapi-002/$$name --output reports/drf-fastapi-002-$$name-docker.json || exit 1; \
	done
