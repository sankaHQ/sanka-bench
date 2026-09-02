# Sanka Migration Bench v5 — prelaunch checklist

Status: **draft; PR #29 not yet landed; no manifest finalized; no cell launched**.

This run measures the complete 11-task `drf-fastapi` suite after task 011 and
the published `sanka-migrate==0.1.0a10` baseline refresh have landed. It keeps
Migration Quality Score v0.2 unchanged so v3 and v4 remain comparable.

## Matrix

Pre-declared deltas from v4 are listed in `PLAN.md`
(D1–D10) and in `run-manifest.template.json` under `pre_declared_deltas`.

- 11 tasks (`drf-fastapi-001` through `drf-fastapi-011`)
- 6 unchanged model selections
- 2 configurations: `alone` and `with-sanka-readiness-aware` (published as "with Sanka")
- 132 pass@1 cells
- 170 verified method-routes
- no quality retries and no model substitutions

## Cost planning

Metered spend only covers OpenAI and Fireworks. v4 recorded $17.70 of Fireworks rated
usage and an unread OpenAI organization bill (estimated ≈ $9). Use **$30 as the central
metered estimate** and **$60 as the authorization ceiling**. Claude cells run on Claude
Max ($0 marginal while limits hold; API-equivalent self-report recorded per cell, ≈ $230
in v4). Any account credit, tax, subscription fee, or provider-side pricing change is
outside the estimate and must be read back.

## Hard launch gates

1. PR #29 is merged through `sanka-pr-flow` after CI green and an authorized
   human approval of its exact final head.
2. A fresh clean worktree is pinned to that exact merge SHA; the SHA replaces
   every `PENDING_PR29_MERGE_SHA` value in the final manifest and runner.
3. The worktree passes `uv run --frozen sanka-bench validate` and the baseline
   control evidence remains green.
4. The pinned environment resolves `sanka-cli==0.1.8` and
   `sanka-migrate==0.1.0a10` (unchanged from v4 by design); agent CLIs and all six exact model IDs are
   re-read without substitution.
5. The `.env` link and mode are verified without printing secrets, and the
   durable mirror contains no terminal v4 rows or active coordinator marker.
6. Memory pressure and free disk are healthy, with no competing pytest,
   benchmark coordinator, or benchmark-agent process.
7. The user gives a new explicit paid-run authorization for the 132-cell v5
   matrix and its cost ceiling. Prior authorization for the eight-cell gate or for v4 is
   not authorization for v5.

## Execution policy after authorization

1. Sequential boot proof for the first `with-sanka-readiness-aware` cell.
2. Progressive official-cell calibration at one, three, four, then six
   concurrent generations per provider (3, 9, 12, then 18 total). Every stage
   must finish without provider or resource failures before promotion.
3. Remaining untouched cells use a rolling provider queue: at most 18 model
   generations, six per provider, and three per exact model. The coordinator
   starts the next eligible cell as soon as a slot opens instead of waiting for
   unrelated slow cells. It falls back to 12, 9, 6, or 3 total when the most
   recent healthy calibration requires it.
4. Local evaluation is a separate queue capped at four processes, so network-
   bound model concurrency cannot create an unbounded pytest fan-out.
5. One foreground coordinator owns all workers. Workers write isolated
   artifacts; only the coordinator rebuilds aggregate files.
6. Pass@1 is strict. Quality failures are terminal. Infrastructure failures are
   stopped, classified, and preserved; no retry occurs without new explicit
   authorization.
7. The run never ends a turn with detached workers or an ambiguous coordinator.

The foreground entrypoint is `run-matrix-v5.sh` and its required order remains:

```text
run-matrix-v5.sh boot-gate
run-matrix-v5.sh calibrate
run-matrix-v5.sh remaining
```

`run-matrix-v5.sh plan` and `run-matrix-v5.sh test-scheduler` are non-provider
operations. Every generation path independently verifies the finalized manifest
authorization and unique coordinator run ID; the coordinator also owns an
exclusive durable lock. An interrupted stale lock is evidence requiring
inspection, not something the runner silently deletes.

## Completion proof

- 132/132 rows terminal with candidate, logs, reports, timestamps, and digests
- `matrix-v4.json` and `REPORT-v4.md` rebuilt by the sole aggregate writer
- per-task and per-model/config task-level score plus scenario diagnostics
- provider usage/cost reconciliation from recorded evidence only
- infrastructure deviations disclosed without overwriting original attempts
- durable artifacts scanned for credentials, local absolute paths, and secrets
- v3 comparison clearly labels v3 as a8/old-prompt historical evidence
