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

Published benchmark, early and growing. The current suite is **v0: one lane
(`drf-fastapi`), three tasks, 42 verifiable endpoints**. Recorded results —
six models, with and without the Sanka engine, pass@1 — live at
[sanka.com/developer/bench](https://sanka.com/developer/bench). Numbers on
that page come only from runs whose frozen candidates, evaluator reports, and
full agent logs exist; nothing is estimated.

## Scoring

**Migration Quality Score = verified routes ÷ total routes in the lane's
suite, pass@1.** A route (here: an HTTP method-route) counts only when its
whole task passes every hard gate; a run that produces no bootable candidate
scores zero. Denominators are frozen per suite version and grow only by
adding tasks. Lanes are scored separately — framework, data, and object
lanes will never be blended into one number, because their route units are
not commensurable. Score changes bump the score version (current: v0.2).

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

Every fixture also carries two frozen coding-agent baselines —
`claude-code-alone` and `claude-code-with-sanka` — produced unattended by
`scripts/run_agent_candidate.py` with identical model, turn budget, and
contract (the with-Sanka prompt only adds that the Sanka CLI exists). Each
candidate's `GENERATED.md` discloses the prompt verbatim, turns, wall time,
and reported cost; `make report` renders those figures beside the tally.
Agent results are empirical, not pinned by tests — the report shows the
current state.

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

## Roadmap

The suite is deliberately small and verification-heavy today; the plan is to
grow it the same way it started — every task ships with its behavior oracle,
public scenarios, and hard gates, never as a prompt list.

1. **Hard tier (next ~5 tasks).** The current three tasks saturate at 100%
   for strong models; these are designed to break that, each targeting a
   failure mode already observed in recorded runs or real-app scans:
   auth-and-permission matrices (multiple authentication schemes, per-action
   and object-level permissions, 401/403 branch coverage); signal-driven
   side-effects and transaction boundaries (`post_save` chains, `F()`
   updates, `select_for_update` — database-mutation parity does the work);
   deep writable-nested graphs with DRF's index-keyed error shapes; exact
   response-shape parity (cursor pagination, ordering/search filters,
   Decimal string forms, timezone boundaries, conditional responses); and a
   legacy mixed-style app (function views + `APIView` + ViewSets, regex and
   dynamic routes).
2. **Real-application tasks.** Oracle-ized slices of permissively licensed
   OSS Django apps (readthedocs and peering-manager are already pinned as
   corpus candidates in
   [sanka-examples](https://github.com/sankaHQ/sanka-examples)), lifting the
   suite from 42 endpoints toward hundreds.
3. **Scale.** On the order of fifty tasks across tiers, with the task list
   published the way mature benchmarks publish theirs.
4. **New lanes.** Data-systems migrations (e.g. `markdown-sqlite`,
   `pg-clickhouse`) and object migrations (e.g. `sfdc-hubspot`), each with
   its own route unit, gates, and per-lane score.

## Contributing

Task proposals are welcome once this repository is public: open an issue
describing the source application, the behaviors the oracle must capture,
and why existing tasks do not already cover the failure mode. A task lands
only with its scenarios, evaluation config, and at least the no-op and
human-reference baselines.

## License

Apache-2.0. Candidate outputs under `baselines/` retain the disclosures in
their `GENERATED.md`.

Produce a frozen coding-agent baseline for one task (unattended, one
attempt, full disclosure of model, tool version, prompt, budget, turns,
duration, and reported cost in the candidate's GENERATED.md):

```bash
uv run python scripts/run_agent_candidate.py \
  --task tasks/drf-fastapi/drf-fastapi-001 \
  --candidate-id claude-code-alone \
  --out baselines/drf-fastapi-001/claude-code-alone \
  --agent-bin ~/.claude/local/claude
# claude-code-with-sanka additionally takes --sanka-bin <path to sanka>
```

The same harness can drive Codex against OpenAI or a supported
OpenAI-compatible provider. Codex runs use an isolated `CODEX_HOME`, the
Responses API, the provider's environment-variable API key, measured wall
time, and token-based cost only when explicit per-million prices are supplied:

```bash
uv run python scripts/run_agent_candidate.py \
  --agent codex \
  --agent-bin codex \
  --provider openai \
  --model gpt-5.3-codex \
  --task tasks/drf-fastapi/drf-fastapi-001 \
  --candidate-id codex-gpt-5-3-codex-with-sanka \
  --sanka-bin ../sanka/.venv/bin/sanka \
  --out baselines/drf-fastapi-001/codex-gpt-5-3-codex-with-sanka
```

The two configurations share the same model, budget, and contract; the
with-Sanka prompt is strictly additive — it only tells the agent the Sanka
CLI exists. The frozen overlay is graded by the same evaluator as every
other candidate.

Render the collected reports into a static page and summary SVG — the hero
tally (tasks fully migrated per approach) and the per-task hard-gate matrix:

```bash
make baselines && make docker-baselines   # produce reports/*.json
make report                               # -> reports/index.html + reports/summary.svg
```

The render is deterministic for a given set of reports; the headline stays the
binary Fully Migrated count, never a blended score.

See [docs/design.md](docs/design.md) for the implemented slice and next gates.

## License

Apache License 2.0. Third-party fixture repositories will retain their own
licenses and provenance records when added.
