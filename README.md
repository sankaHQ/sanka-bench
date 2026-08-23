# Sanka Migration Bench

Sanka Migration Bench (`sanka-bench`) is a tool-neutral, repository-level
benchmark for evaluating whether a software migration preserves behavior and
actually reaches its declared target architecture.

The first benchmark lane is intentionally narrow:

> Django REST Framework to FastAPI, retaining the Django ORM and database
> schema while replacing the request-serving layer.

The original application is the behavior oracle. Candidates are compared on
HTTP behavior, database mutations, and target-framework compliance rather than
source-code similarity to one preferred implementation.

## Status

Private implementation preview. This repository is not a published benchmark,
leaderboard, package, or public claim.

The first fixture proves three required controls:

| Baseline | Expected result |
| --- | --- |
| No-op | Fails target boot and native-target compliance |
| Sanka PR #13 compatibility bridge | Preserves behavior but fails the anti-proxy compliance gate |
| Native human reference | Passes behavior, database, regression, and native FastAPI gates |

## Run locally

```bash
uv sync --frozen --extra fixture --group dev
uv run sanka-bench validate
uv run sanka-bench evaluate \
  --runner local \
  --task tasks/drf-fastapi/drf-fastapi-001 \
  --candidate baselines/native-reference
```

The default runner is Docker and disables network access while evaluating:

```bash
uv run sanka-bench evaluate \
  --task tasks/drf-fastapi/drf-fastapi-001 \
  --candidate baselines/native-reference
```

Evaluate every required baseline locally or in the isolated container:

```bash
make baselines
make docker-baselines
```

## Repository boundary

- This repository owns evaluator schemas, public fixtures, isolation, baseline
  runners, and reports.
- `sankaHQ/sanka` owns the Sanka runtime and the `sanka scan`, `plan`, `apply`,
  and `verify` product experience.
- Hidden Verified-set tests must remain outside candidate-visible public source.
- The evaluator must be able to grade Sanka and non-Sanka candidates through the
  same candidate contract.

See [docs/design.md](docs/design.md) for the implemented slice and next gates.

## License

Apache License 2.0. Third-party fixture repositories will retain their own
licenses and provenance records when added.
