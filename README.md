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

Three synthetic fixtures exist. `drf-fastapi-001` covers CRUD and validation;
`drf-fastapi-002` adds database-backed `TokenAuthentication`, `IsAuthenticated`,
and object-level permissions (author-or-read-only), with 401-variant,
403, and `WWW-Authenticate`/`Allow` header scenarios — a native candidate must
reimplement token authentication without loading DRF. `drf-fastapi-003` adds
writable nested serializers with DRF's index-keyed nested error format, a
transactional create whose business-rule failure must leave the database
unchanged (the rollback contract is proven by database parity), unique-field
messages, decimal digit/precision errors with string representation, and
choice-field errors.

Baselines live at `baselines/<task>/<candidate>/`. The first fixture proves
the required controls:

| Baseline | Expected result |
| --- | --- |
| No-op | Fails target boot and native-target compliance |
| Sanka PR #13 compatibility bridge | Preserves behavior but fails the anti-proxy compliance gate |
| Native human reference | Passes behavior, database, regression, and native FastAPI gates |
| Sanka native converter (`sanka apply --bench-candidate`) | Passes every hard gate, including runtime native-target evidence |

`drf-fastapi-002` carries noop, compatibility-bridge, human
native-reference, and Sanka native-converter baselines. The converter's
envelope caught up with the fixture (sanka PR #17): its untouched
`--bench-candidate` output passes every hard gate, serving token
authentication natively without loading DRF.

`drf-fastapi-003` carries noop, compatibility-bridge, human
native-reference, and Sanka native-converter baselines. The converter's
envelope caught up again (sanka PR #21): writable nested serializers are
generated natively, and the author's transactional `create()` — business
rule, rollback and all — is carried over verbatim with its DRF exception
swapped for a native shim.

The native-target gate is decided by recorded serving evidence, not source
text. Every candidate scenario is served in a fresh guarded process that arms
an un-removable audit hook before any candidate code loads. The hook records
imports of DRF and Django request-serving machinery, process creation, and
socket connections; the guard also verifies the scenario was served by a
FastAPI `APIRoute` whose endpoint code lives inside the candidate workspace.
A facade that hides DRF dispatch behind an imported helper therefore fails
even though its entrypoint text looks clean (see
`tests/fixtures/obfuscated-bridge`). Textual pattern checks remain in results
as diagnostics only.

## Run locally

```bash
uv sync --frozen --extra fixture --group dev
uv run sanka-bench validate
uv run sanka-bench evaluate \
  --runner local \
  --task tasks/drf-fastapi/drf-fastapi-001 \
  --candidate baselines/drf-fastapi-001/native-reference
```

The default runner is Docker and disables network access while evaluating:

```bash
uv run sanka-bench evaluate \
  --task tasks/drf-fastapi/drf-fastapi-001 \
  --candidate baselines/drf-fastapi-001/native-reference
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
