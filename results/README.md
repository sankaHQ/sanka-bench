# Results

Recorded measurement runs of the Sanka Migration Bench, published beside the frozen
benchmark source. Every directory is a snapshot of a durable run mirror: the matrix
rows, the generated report, the run manifest with tool and model pins, the model
probes, and the cost ledgers. Cell-level artifacts (frozen candidates, agent
transcripts, evaluator reports, logs) are large and stay in the run mirror; they are
available on request.

Rules that apply to everything here:

- A recorded run is never rescored, retried or repaired in place. Corrections are
  published as labelled errata and separately labelled studies beside the original.
- Scores are Migration Quality Score v0.2: route-weighted, all-or-nothing per task,
  pass@1. See `docs/design.md` in this repository for the gates.
- Local absolute paths were replaced with `<workspace>`, `<home>` and `<claude-cli>`
  placeholders before publication; no credentials are present.

| Directory | What it is |
| --- | --- |
| `v5-11task-2026-09-02/` | **Current record.** Eleven tasks, 170 routes, engine 0.1.0a10, corrected runner and evaluator 0.0.3, 120-turn Claude budget, readiness-aware with-Sanka arm, pre-declared in `PLAN.md`. 132/132 cells terminal, 0 agent or provider failures. |
| `v3-10task-2026-08-30/` | Ten tasks, 165 routes, engine 0.1.0a8, the old copy-the-overlay prompt. Historical. `ANALYSIS-with-sanka-regression.md` explains the prompt-mandate regression that led to the v4 prompt. |
| `v4-11task-2026-09-01/` | Eleven tasks, 170 routes, engine 0.1.0a10, readiness-aware prompt. The recorded pass@1 record, with two errata: `ERRATUM-claude-turn-cap-2026-09-02.md` (ten Claude cells discarded unevaluated by a runner exit-code regression) and `ERRATUM-native-gate-included-router-2026-09-02.md` (native-gate false negatives for `include_router` candidates and `APIRoute` subclasses). |
| `v4-erratum-study-2026-09-02/` | The ten discarded v4 cells re-executed with the fixed runner, same SHA, pins, prompt and budget. |
| `v4-native-gate-reevaluation-a-2026-09-02/` | Frozen candidates re-evaluated with the include_router fix (evaluator 0.0.2). |
| `v4-native-gate-reevaluation-b-2026-09-02/` | The same plus the accepted `APIRoute` subclass rule and catch-all diagnostic (evaluator 0.0.3). |

v5 is the current record; v3 and v4 stay as history with their errata.
