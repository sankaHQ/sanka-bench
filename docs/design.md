# Implemented v0.1 slice

This slice establishes the evaluator boundary before a converter or hosted API
is allowed to claim a successful DRF-to-FastAPI migration.

## Implemented

- JSON Schemas for tasks, candidates, and results.
- One pinned CRUD fixture with deterministic scenarios.
- Local and network-disabled, read-only Docker evaluation runners.
- Existing-test regression checks.
- Differential HTTP and SQLite row-state comparison.
- Static native-target compliance checks.
- Two clean evaluation repetitions and variance detection.
- No-op, Sanka PR #13 compatibility-bridge, and native human-reference
  baselines.

## Deliberate limits

- The fixture covers one model and CRUD behavior only.
- Side-effect ledgers are represented in the result contract but the first
  fixture has no Celery, email, file, signal, or webhook scenario.
- The public evaluator material is visible to candidates. A future Verified set
  must mount hidden tests only after the candidate is frozen.
- Docker build dependency resolution is pinned by `uv.lock`; the evaluation run
  itself has no network.
- No hosted execution, repository upload, leaderboard, API route, or product
  integration is included.

## Next implementation gates

1. Add authentication, object-permission, transaction rollback, and side-effect
   fixtures.
2. Replace public-only task execution with a private hidden-evaluator mount and
   signed result manifest.
3. Integrate the shared result schema into `sanka verify` without letting Sanka
   select or bypass evaluator assertions.
4. Design the separately reviewed `/v2/migrate/code-projects` and
   `/v2/migrate/code-migrations` API resources.
