# Sanka Migration Bench v4 — developer overview and handoff

Status: **v4 frozen; Claude erratum study complete**  
Date: **2026-09-02**  
Lane: **DRF → FastAPI (`drf-fastapi`)**  
Score: **Migration Quality Score v0.2**  
Benchmark SHA: **`13bd9a863a76f813495c4483c1e39cd8aa7bba44`**

This is the short entrypoint for developers. The full row-level evidence is in
[`matrix-v4.json`](matrix-v4.json), and the generated result table is in
[`REPORT-v4.md`](REPORT-v4.md).

## What the benchmark measures

The suite measures whether an agent can migrate a Django REST Framework
application to a native FastAPI application while preserving externally
observable behavior, database effects, and native-serving evidence.

The v4 suite contains 11 tasks and 170 independently weighted HTTP
method-routes:

| Task | Primary behavior | Routes |
| --- | --- | ---: |
| 001 | CRUD parity | 14 |
| 002 | Token authentication and object permissions | 14 |
| 003 | Writable nested serializers and transaction rollback | 14 |
| 004 | Signal-driven side effects | 26 |
| 005 | Authentication and permission matrix | 16 |
| 006 | Three-level writable nested graphs | 14 |
| 007 | Pagination, filtering, representation, and conditional responses | 14 |
| 008 | Mixed DRF view styles, regex routes, and dynamic registration | 36 |
| 009 | Multipart files, downloads, and content negotiation | 12 |
| 010 | State transitions and optimistic concurrency | 5 |
| 011 | Aggregates and computed fields | 5 |
| **Total** |  | **170** |

The scoring rule remains deliberately strict: a task contributes all of its
routes only when every hard gate passes. A partially correct task contributes
zero routes. Every cell is pass@1; quality failures are not retried.

## v4 experiment design

- 6 models × 2 configurations × 11 tasks = **132 cells**.
- Configurations: `alone` and `with-sanka`.
- Sanka pin: **`sanka-cli 0.1.8` + `sanka-migrate 0.1.0a10` from PyPI**.
- Claude ran through Claude Max; OpenAI models used `api-standard`; DeepSeek
  and GLM used Fireworks `serverless-standard`.
- One foreground coordinator owned bounded provider queues and a separate
  four-process evaluation queue. One process rebuilt aggregate artifacts.
- Terminal candidates, agent logs, evaluator reports, token usage, timing,
  digests, model IDs, provider variants, and deviations are preserved.

### Agent-scaffold policy for future matrices

Keep Claude Code for Anthropic Opus/Sonnet cohorts. Keep Codex CLI for OpenAI
models and for Responses-compatible Fireworks cohorts through an isolated
`openai-custom` provider. Record the complete cohort identity: model, agent
scaffold and version, serving provider and variant, wire API, auth mode, and
budget.

The headline comparison is paired within that fixed cohort: alone versus with
Sanka. Cross-model rankings are secondary because their scaffolds differ.
Driving Claude through Codex would require a translation proxy or third-party
deployment that changes the measured cohort; it is not a neutral swap. A
future scaffold-neutral model leaderboard, if wanted, should be a separate
lane with a minimal reference agent and vendor-native APIs.

Claude Max versus an Anthropic API key is an auth and cost-ledger decision, not
an agent-scaffold decision. Pin the selected mode across both arms and disclose
subscription coverage, rate-limit sharing, and incurred-cost status.

The initial and rolling waves used the frozen benchmark runner. Recovery waves
used the PR #26 reliability runner, whose exit-code regression caused the
Claude measurement defect described below. Runner revisions and hashes are
pinned in [`run-manifest.json`](run-manifest.json).

## Frozen v4 scores and interpretation

These numbers reproduce the immutable v4 aggregate. The Claude values remain
part of the historical record, but their deltas are not causally interpretable:
ten Claude cells were discarded before evaluation by a recovery-runner defect.

| Model | Alone | With Sanka | Recorded delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Claude Opus 4.8 | 100.0% | 92.9% | −7.1 | **Invalid comparison: one with-Sanka cell was discarded before evaluation** |
| Claude Sonnet 5 | 78.8% | 57.1% | −21.7 | **Invalid comparison: nine cells across both arms were discarded before evaluation** |
| gpt-5.6-sol | 48.2% | 84.7% | +36.5 | Improvement |
| DeepSeek V4 Pro | 63.5% | 84.7% | +21.2 | Improvement |
| GLM-5.3-Flash | 22.4% | 44.1% | +21.7 | Improvement |
| gpt-5.6-luna | 45.9% | 48.8% | +2.9 | Improvement |

Across all six models, the frozen route-weighted record changes from **59.8% to
68.7%**: **+8.9 percentage points and +91 verified routes**. That historical
aggregate is not a clean whole-matrix treatment estimate because ten Claude
cells were never evaluated. The four non-Claude comparisons are unaffected by
the defect and all improved with Sanka in the frozen matrix.

All 132 artifact rows are terminal:

- 86 fully migrated;
- 36 evaluated but failed one or more hard gates;
- 10 unevaluated Claude rows affected by the runner defect.

Every unevaluated row reached the fixed 60-turn ceiling. Claude Code returned a
complete, parseable `error_max_turns` result while exiting with status 1. The
PR #26 recovery runner returned early on that exit code, so it deleted the
temporary workspace before freeze and evaluation. The earlier runner evaluated
the same terminal state in 14 cells and 13 passed every hard gate.

The discarded rows split seven with-Sanka versus three alone only because
those were the untouched cells remaining when recovery began. The imbalance is
a scheduling artifact, not evidence of a Sanka-induced turn tax. See
[`ERRATUM-claude-turn-cap-2026-09-02.md`](ERRATUM-claude-turn-cap-2026-09-02.md).

## Cost interpretation

Two ledgers answer different questions:

1. **Model-reference cost** normalizes recorded usage to the model creator's
   public API price. It supports economic comparison and is not an invoice.
2. **Platform-incurred cost** records the platform that actually served the
   cell. It must not be replaced with another provider's price card.

Fireworks rated-cost reconciliation is complete:

| Ledger | Rated USD |
| --- | ---: |
| 44 benchmark cells | $51.246097914 |
| Non-cell recovery and validation sessions | $2.711456404 |
| Account-scoped control total | **$53.957554318** |

The Fireworks amount is rated serverless usage before credits, fixed fees,
invoice-level discounts, taxes, and final settlement. Claude cells are marked
as subscription-covered without assigning a false zero per-cell cost. OpenAI
cells used the API rather than a ChatGPT subscription; their organization cost
readback remains pending because the available project key lacks Admin billing
scope. See [`cost-methodology-v4.md`](cost-methodology-v4.md) and
[`platform-cost-reconciliation-v4.json`](platform-cost-reconciliation-v4.json).

## Recorded deviations

- One separately authorized infrastructure rerun occurred for DeepSeek task
  007 alone after the prior parser discarded a recoverable workspace. Both
  attempts and the authorization are preserved; retry overhead is excluded
  from pass@1 cell cost.
- The frozen v4 candidate schema rejected the new `provider_variant`
  provenance property. The harness removed only that metadata property from
  `candidate.yaml`; the overlay was not edited, and the same provider variant
  remains disclosed in the generated evidence and logs.
- Fireworks emitted a reconnect/idle-timeout notice during GLM task 001 with
  Sanka, but the agent completed, the candidate was frozen, and all gates
  passed. It remains an honest passing cell.
- v4 used rolling provider queues, unlike v3. Cell quality remains comparable;
  raw wall-time comparisons between v3 and v4 are not presented as equivalent.

## Recommended next steps

### P0 — complete the Claude measurement erratum

> **Erratum (2026-09-02):** ten Claude cells were never evaluated because the recovery-wave runner
> (PR #26) misfiled Claude's `error_max_turns` exit code 1 as an agent-run
> failure; earlier waves froze and passed the same terminal state 13/14 times.
> The "Sanka-induced turn tax" reading is withdrawn. See
> [`ERRATUM-claude-turn-cap-2026-09-02.md`](ERRATUM-claude-turn-cap-2026-09-02.md).
> Re-executed in a labelled study the same day: 8 of the 10 discarded cells passed,
> all four P0 cells among them (`../v4-erratum-study-2026-09-02/REPORT.md`).
> **Erratum 2 (2026-09-02):** the native-serving gate rejected every candidate using
> FastAPI's `include_router` (FastAPI 0.141 `_IncludedRouter`) and, by exact-class
> matching, `APIRoute` subclasses; both fixed (PR #28, #29) and the affected frozen
> cells re-evaluated in labelled studies (six of seven now pass); see
> [`ERRATUM-native-gate-included-router-2026-09-02.md`](ERRATUM-native-gate-included-router-2026-09-02.md).

An authorized, separately labelled study re-executed all ten discarded Claude
cells with the same suite SHA, prompt, engine pins, 60-turn ceiling, evaluator,
and pass@1 rule, using the corrected runner from PR #27. All ten drivers exited
zero in a 59-minute, four-concurrent run. Eight cells passed every hard gate;
Sonnet 007 with Sanka failed behavior parity and Sonnet 011 with Sanka failed
the native-target gate.

| Model | Config | Frozen v4 | Derived view | Interpretation |
| --- | --- | ---: | ---: | --- |
| Claude Opus 4.8 | alone | 100.0% (170/170) | 100.0% (170/170) | unchanged |
| Claude Opus 4.8 | with-sanka | 92.9% (158/170) | 100.0% (170/170) | discarded 009 replacement passed |
| Claude Sonnet 5 | alone | 78.8% (134/170) | 91.8% (156/170) | all three discarded alone cells passed |
| Claude Sonnet 5 | with-sanka | 57.1% (97/170) | 88.8% (151/170) | four of six discarded with-Sanka cells passed |

The derived view removes the apparent Opus regression and shrinks Sonnet's
recorded −21.7-point difference to −3.0 points. It is diagnostic evidence, not
the v4 record or an official treatment estimate. Its results belong beside v4;
they never overwrite, repair, or rescore an original row. Eight of ten cells
reached or exceeded the requested 60 turns, confirming that the cap binds.

For v5, predeclare a non-binding Claude turn ceiling after a pilot. The current
recommendation is 120 turns with a 3,600-second outer wall-clock guard and
published turn distributions. Promote the readiness-aware arm to the official
with-Sanka treatment so scan and plan are exercised before the agent and do not
consume its turn budget.

### P1 — qualify provider substitution

Keep model-reference economics separate from platform cost, but do not assume
quality equivalence from a shared model name. Before moving Fireworks cells to
on-demand Fast, DeepInfra, or another provider, run a small sentinel study that
pins:

- exact model revision;
- quantization/precision and context limits;
- chat template and tool behavior;
- Responses/API adapter semantics;
- sampling and output limits.

Tasks 005, 008, and 009 are strong sentinels because they cover authentication
branches, route/redirect precision, multipart data, binary responses, and
content negotiation. A qualified provider becomes a new disclosed cohort;
there is never a silent substitution.

### P1 — finish actual-cost reconciliation

Use an OpenAI organization Admin API key to read the Costs API for the v4
window and project/API-key scope. Until then, keep OpenAI incurred cost null.
Do not infer an actual bill from model-reference pricing.

### P2 — public v0.1 packaging

When publishing the proposed `sankaHQ/bench` v0.1 repository:

- preserve v4 unchanged as the current pass@1 record;
- label v3 as historical a8/old-prompt evidence;
- publish the scoring rule, suite SHA, provider variants, deviations, and both
  cost ledgers;
- state the four valid non-Claude improvements and disclose that the Claude
  comparison is invalid because ten rows were never evaluated;
- publish the erratum study only as a separately labelled derived view;
- avoid a universal “Sanka improves every agent” claim until a future
  predeclared matrix confirms it.

## Artifact map

- [`REPORT-v4.md`](REPORT-v4.md) — generated model/config result table.
- [`matrix-v4.json`](matrix-v4.json) — authoritative 132-row matrix.
- [`run-manifest.json`](run-manifest.json) — suite, model, provider, toolchain,
  concurrency, retry, and compatibility pins.
- [`bench-sha.txt`](bench-sha.txt) — frozen benchmark commit.
- [`cost-methodology-v4.md`](cost-methodology-v4.md) — dual-ledger definitions.
- [`platform-cost-reconciliation-v4.json`](platform-cost-reconciliation-v4.json)
  — Fireworks account/session reconciliation.
- [`openai-platform-cost-readback-v4.json`](openai-platform-cost-readback-v4.json)
  — current OpenAI billing-readback blocker.
- `candidates/`, `reports/`, and `logs/` — frozen cell-level evidence.
- `infrastructure-reruns-v4.json` and `infrastructure-reruns/` — authorized
  retry ledger and preserved attempt evidence.

## Immutable boundaries

- Do not retry, overwrite, or “repair” a terminal v4 cell.
- Do not change v4's v0.2 all-or-nothing scoring after seeing the outcome.
- Do not silently replace a model, provider, provider variant, or wire API.
- Do not present reference-price estimates as platform-incurred spend.
- New prompt, engine, provider, timeout, or turn-budget policies require a new
  labeled study or matrix version.
