.PHONY: sync format lint typecheck test check baselines docker-baselines report

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
BASELINES_001 = noop compatibility-bridge claude-code-alone claude-code-with-sanka native-reference sanka-native
BASELINES_002 = noop compatibility-bridge claude-code-alone claude-code-with-sanka native-reference sanka-native
BASELINES_003 = noop compatibility-bridge claude-code-alone claude-code-with-sanka native-reference sanka-native
BASELINES_004 = noop compatibility-bridge native-reference sanka-native
BASELINES_005 = noop compatibility-bridge native-reference sanka-native
BASELINES_006 = noop compatibility-bridge native-reference sanka-native
BASELINES_007 = noop compatibility-bridge native-reference sanka-native
BASELINES_008 = noop compatibility-bridge native-reference sanka-native
BASELINES_009 = noop compatibility-bridge native-reference sanka-native

baselines:
	@for name in $(BASELINES_001); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/drf-fastapi-001/$$name --output reports/drf-fastapi-001-$$name.json || exit 1; \
	done
	@for name in $(BASELINES_002); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-002 --candidate baselines/drf-fastapi-002/$$name --output reports/drf-fastapi-002-$$name.json || exit 1; \
	done
	@for name in $(BASELINES_003); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-003 --candidate baselines/drf-fastapi-003/$$name --output reports/drf-fastapi-003-$$name.json || exit 1; \
	done
	@for name in $(BASELINES_004); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-004 --candidate baselines/drf-fastapi-004/$$name --output reports/drf-fastapi-004-$$name.json || exit 1; \
	done
	@for name in $(BASELINES_005); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-005 --candidate baselines/drf-fastapi-005/$$name --output reports/drf-fastapi-005-$$name.json || exit 1; \
	done
	@for name in $(BASELINES_006); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-006 --candidate baselines/drf-fastapi-006/$$name --output reports/drf-fastapi-006-$$name.json || exit 1; \
	done
	@for name in $(BASELINES_007); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-007 --candidate baselines/drf-fastapi-007/$$name --output reports/drf-fastapi-007-$$name.json || exit 1; \
	done
	@for name in $(BASELINES_008); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-008 --candidate baselines/drf-fastapi-008/$$name --output reports/drf-fastapi-008-$$name.json || exit 1; \
	done
	@for name in $(BASELINES_009); do \
		uv run sanka-bench evaluate --runner local --task tasks/drf-fastapi/drf-fastapi-009 --candidate baselines/drf-fastapi-009/$$name --output reports/drf-fastapi-009-$$name.json || exit 1; \
	done

docker-baselines:
	@for name in $(BASELINES_001); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-001 --candidate baselines/drf-fastapi-001/$$name --output reports/drf-fastapi-001-$$name-docker.json || exit 1; \
	done
	@for name in $(BASELINES_002); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-002 --candidate baselines/drf-fastapi-002/$$name --output reports/drf-fastapi-002-$$name-docker.json || exit 1; \
	done
	@for name in $(BASELINES_003); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-003 --candidate baselines/drf-fastapi-003/$$name --output reports/drf-fastapi-003-$$name-docker.json || exit 1; \
	done
	@for name in $(BASELINES_004); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-004 --candidate baselines/drf-fastapi-004/$$name --output reports/drf-fastapi-004-$$name-docker.json || exit 1; \
	done
	@for name in $(BASELINES_005); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-005 --candidate baselines/drf-fastapi-005/$$name --output reports/drf-fastapi-005-$$name-docker.json || exit 1; \
	done
	@for name in $(BASELINES_006); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-006 --candidate baselines/drf-fastapi-006/$$name --output reports/drf-fastapi-006-$$name-docker.json || exit 1; \
	done
	@for name in $(BASELINES_007); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-007 --candidate baselines/drf-fastapi-007/$$name --output reports/drf-fastapi-007-$$name-docker.json || exit 1; \
	done
	@for name in $(BASELINES_008); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-008 --candidate baselines/drf-fastapi-008/$$name --output reports/drf-fastapi-008-$$name-docker.json || exit 1; \
	done
	@for name in $(BASELINES_009); do \
		uv run sanka-bench evaluate --runner docker --task tasks/drf-fastapi/drf-fastapi-009 --candidate baselines/drf-fastapi-009/$$name --output reports/drf-fastapi-009-$$name-docker.json || exit 1; \
	done

report:
	uv run sanka-bench report
