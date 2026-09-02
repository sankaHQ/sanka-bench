# Sanka Migration Bench v5 — developer overview and handoff

Status: **complete and frozen**  
Date: **2026-09-02**  
Lane: **DRF → FastAPI (`drf-fastapi`)**  
Score: **Migration Quality Score v0.2** (route-weighted, all-or-nothing per task, pass@1)  
Benchmark SHA: **`bb51edf6d8a42b9bcb0d4507a2abdc211fb0c56d`** · evaluator 0.0.3 · engine sanka-cli 0.1.8 + sanka-migrate 0.1.0a10

This is the current record of the bench. The full row-level evidence is in [`matrix-v5.json`](matrix-v5.json); the generated table is [`REPORT-v5.md`](REPORT-v5.md); the pre-declared design is [`PLAN.md`](PLAN.md). v3 and v4 remain published as history with their errata.

## What changed from v4 (all pre-declared before launch)

- Runner: a parsed result is authoritative over the CLI exit code, so turn-capped Claude cells are frozen and graded; Claude transcripts are captured as stream-json (sanka-bench PR #27).
- Evaluator 0.0.3: FastAPI `include_router` targets resolve to the serving route (PR #28); `APIRoute` subclasses with workspace endpoints are native; catch-all serving of non-404 scenarios is a diagnostic (PR #29).
- Claude turn budget 120 instead of 60. Codex cells remain bounded by the 3600 s wall clock only.
- The with-Sanka arm is the readiness-aware arm: the harness runs `sanka scan` and `sanka plan` first, freezes `sanka-readiness.json`, injects the readiness percentage, the unsupported-route checklist and the skipped URLs into the prompt, and offers the generated scaffold only at 50 % readiness or above. Published as "with Sanka".
- Same eleven tasks, 170 routes, six models, engine pins and evaluator suite as v4 otherwise.

## Results

| Model | Alone | With Sanka | Delta | Agent time alone → with | Cost alone → with |
| --- | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 | 100.0% | 100.0% | +0.0 | 267 → 270 min | $77.43 → $76.32 |
| Claude Sonnet 5 | 91.8% | 91.8% | +0.0 | 203 → 212 min | $36.97 → $46.10 |
| gpt-5.6-sol | 84.7% | 75.3% | -9.4 | 35 → 36 min | $6.62 → $7.47 |
| DeepSeek V4 Pro | 92.9% | 90.6% | -2.3 | 311 → 357 min | $13.28 → $16.61 |
| GLM-5.3-Flash | 67.1% | 72.4% | +5.3 | 158 → 175 min | $2.80 → $3.50 |
| gpt-5.6-luna | 48.8% | 67.1% | +18.3 | 32 → 33 min | $0.47 → $0.52 |
| **All six** | **80.9%** | **82.8%** | **+2.0** | | |

All 132 cells are terminal and evaluated: 105 fully migrated, 27 failed one or more hard gates, 0 agent-run or provider failures. Sanka raised the score for 2 models (GLM-5.3-Flash, gpt-5.6-luna), lowered it for 2 (gpt-5.6-sol, DeepSeek V4 Pro), and left 2 unchanged. The six-model route-weighted change is +2.0 points (825 → 845 of 1020 routes). Every delta is a single pass@1 pair; a one-task flip on a 16- or 36-route task moves a model by 9 to 21 points, so read the per-task heat map before the average.

### Where Sanka's envelope stood

Readiness recorded for 66/66 with-Sanka cells, mean 38.1 %. The scaffold was emitted in 24 cells and withheld (gap report only) in 42. Per task: 001 100 %, 002 100 %, 003 100 %, 004 54 %, 005 12 %, 006 14 %, 007 14 %, 008 24 %, 009 0 %, 010 0 %, 011 0 %. On tasks 005–011 the arm therefore consisted of the readiness report and checklists alone; the scaffold only reached tasks 001–004.

### Failures by task and gate

| Task | Failed cells / 12 |
| --- | ---: |
| 004 | 1 |
| 005 | 6 |
| 006 | 4 |
| 007 | 7 |
| 009 | 7 |
| 010 | 1 |
| 011 | 1 |

Failed gates across the 27 failed cells: behavior_parity 27, database_parity 9, side_effect_parity 8, deterministic 3, native_target 3, target_boot 3. Catch-all diagnostics: 94 scenario observations, informational only.

### Turn budgets

- Opus 4.8: min 22, median 49, max 96 turns of a 120-turn budget; 0 cell(s) above the budget.
- Sonnet 5: min 52, median 68, max 131 turns of a 120-turn budget; 1 cell(s) above the budget.
- The one over-budget cell (Sonnet 5, task 005, with Sanka, 131 turns) ended as a CLI-reported success; the runner froze it once and disclosed the overrun, as designed. It passed all gates. Codex cells have no turn cap; none approached the 3600 s wall clock.

## Cost ledgers

| Ledger | USD | Basis |
| --- | ---: | --- |
| Fireworks (44 cells) | $36.19 | exact rated-cost readback, 44 billing sessions ↔ 44 cells, attribution COMPLETE; before credits, fees, discounts and taxes |
| OpenAI (44 cells) | $15.07 | reference: recorded token classes × verified Standard price card (short-context tier, a lower bound); the organization bill was not read (project key lacks Admin scope) |
| Claude (44 cells) | $236.82 | API-equivalent self-report; run on Claude Max, $0 marginal |
| **Metered total** | **$51.26** | against the authorized $60 ceiling |

## Recorded deviations

- 2026-09-02T01:10:55Z · v5-boot-gate · aggregate-builder-bug: stage reported failures=1 because build_matrix_v5.py crashed; no cell artifact affected; boot gate re-checked with the fixed builder (terminal cell skipped, never overwritten) Quality effect: none.
- Sonnet 5 · 005 · with Sanka reported success at 131 turns against a 120-turn request; frozen once, disclosed in GENERATED.md, graded normally (passed).
- Hygiene finding, no exposure: the cell driver exports both provider API keys into every cell's environment, including Claude cells. A post-run scan of all 1,701 mirror files found no key values in any transcript; the single hit was the non-secret `PARENT_HOST` hostname inside a path. Future drivers should pass only the provider's own key.
- Concurrency: sequential boot gate, calibration at 1 → 3 → 4 → 6 per provider, then a rolling queue (≤ 18 total, ≤ 6 per provider, ≤ 3 per model); 6 stage records; observed coordinator time 5.8 h. Per-cell wall time is measured under that contention and is not comparable with sequential runs.

## Comparison with v4 (labelled; different harness and arm)

v4 official: 59.8 % → 68.7 % (+8.9). v4 corrected under both errata: 70.4 % → 80.6 % (+10.2). v5: 80.9% → 82.8% (+2.0). The alone baselines are higher in v5 for every non-Claude model because the evaluator no longer rejects `include_router` candidates or `APIRoute` subclasses and because turn-capped work is graded; the with-Sanka arm changed from an optional tool to a harness preflight. The three runs are not one series.

## Immutable boundaries

- Do not retry, overwrite, or repair a terminal v5 cell.
- Do not change the v0.2 rule after seeing the outcome; the `APIRoute`-subclass reading was declared before launch (Erratum 2 of v4).
- New prompt, engine, provider, timeout or turn-budget policies require a new labelled matrix version.

## Artifact map

- `matrix-v5.json` — authoritative 132-row matrix.
- `REPORT-v5.md` — generated result table.
- `run-manifest.json`, `bench-sha.txt`, `model-selection-v5.json` — pins, probes, authorization, deviations.
- `pricing-evidence.json`, `cost-methodology-v5.md`, `platform-cost-reconciliation-v5.json`, `cost-readbacks/` — the two cost ledgers.
- `candidates/`, `reports/`, `logs/`, `waves/`, `scheduler-events.jsonl` — frozen cell-level evidence (transcripts included).
