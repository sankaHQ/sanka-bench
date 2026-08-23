# Implemented v0.1 slice

This slice establishes the evaluator boundary before a converter or hosted API
is allowed to claim a successful DRF-to-FastAPI migration.

## Implemented

- JSON Schemas for tasks, candidates, and results.
- One pinned CRUD fixture with deterministic scenarios.
- Local and network-disabled, read-only Docker evaluation runners.
- Existing-test regression checks.
- Differential HTTP and SQLite row-state comparison.
- Runtime native-target compliance: every candidate scenario is served in a
  fresh guarded child process that arms a PEP 578 audit hook before candidate
  code loads. The hook cannot be removed once installed. It records imports of
  forbidden module prefixes (DRF and Django request-serving machinery),
  process creation, and socket connections. The guard also records whether the
  scenario was matched by a `fastapi.routing.APIRoute` whose endpoint code
  lives inside the candidate workspace. The guard observes and records rather
  than blocking, so facade candidates still demonstrate behavioral parity
  while failing the gate on evidence.
- Textual pattern checks demoted to result diagnostics over every
  candidate-contributed file (they previously gated on the entrypoint file
  only, which a helper-module facade trivially bypassed; the
  `tests/fixtures/obfuscated-bridge` control pins that bypass as caught).
- The native reference serves through DRF-free settings, proving the DRF
  request layer is genuinely absent from a native serving process while the
  retained Django test suite still exercises the source application.
- Two clean evaluation repetitions and variance detection; recorded serving
  evidence participates in the determinism fingerprint.
- No-op, Sanka PR #13 compatibility-bridge, and native human-reference
  baselines.

## Deliberate limits

- The fixture covers one model and CRUD behavior only.
- Scenarios are served through an in-process ASGI test client, not through
  independently booted server processes.
- The serving guard defends against converters that Goodhart the visible
  checks, not against deliberate audit-hook evasion; adversarial custody
  belongs to the future hidden evaluator.
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
