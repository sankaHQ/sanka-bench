# Sanka Migration Bench — 11-task model matrix v4

Progress: **132/132 pass@1 cells terminal**, **86 fully migrated**, **65/132 reference-costed**, **44/132 incurred-costed**.
Completed rolling stages: **14**; observed coordinator time: **11.59 hours**.

The suite is frozen at 11 tasks and 170 method-routes at the exact SHA in
`bench-sha.txt`. One foreground rolling coordinator owns every worker.
Generation is capped independently by provider/model; local evaluation is a
separate four-process queue. No terminal cell is overwritten or retried.
This concurrency methodology differs from v3; quality/token results remain
cell-scoped, while raw wall time is not silently compared with v3.

| Model | Config | Cells | Tasks passed | Score | Agent time | Reference cost | Incurred cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 | alone | 11/11 | 11/11 | 100.0% | 282.5 min | $79.907759 | subscription |
| Claude Opus 4.8 | with-sanka | 11/11 | 10/11 | 92.9% | 291.4 min | $77.298125 | subscription |
| Claude Sonnet 5 | alone | 11/11 | 7/11 | 78.8% | 205.8 min | $34.977664 | subscription |
| Claude Sonnet 5 | with-sanka | 11/11 | 5/11 | 57.1% | 195.0 min | $35.098467 | subscription |
| gpt-5.6-sol | alone | 11/11 | 7/11 | 48.2% | 66.4 min | unavailable | pending |
| gpt-5.6-sol | with-sanka | 11/11 | 9/11 | 84.7% | 98.5 min | unavailable | pending |
| DeepSeek V4 Pro | alone | 11/11 | 8/11 | 63.5% | 388.7 min | unavailable | $17.320578 |
| DeepSeek V4 Pro | with-sanka | 11/11 | 9/11 | 84.7% | 398.8 min | $8.849248–$17.698495 | $17.698495 |
| GLM-5.3-Flash | alone | 11/11 | 4/11 | 22.4% | 516.2 min | unavailable | $7.242043 |
| GLM-5.3-Flash | with-sanka | 11/11 | 5/11 | 44.1% | 583.8 min | unavailable | $8.984981 |
| gpt-5.6-luna | alone | 11/11 | 6/11 | 45.9% | 67.0 min | unavailable | pending |
| gpt-5.6-luna | with-sanka | 11/11 | 5/11 | 48.8% | 66.5 min | unavailable | pending |

## Fireworks platform-cost reconciliation

| Ledger | Rated USD | Treatment |
| --- | ---: | --- |
| 44 benchmark cells | $51.246097914 | Attributed to exact Codex thread / Fireworks billing sessions |
| Non-cell recovery and validation | $2.711456404 | Operational overhead, excluded from pass@1 cell costs |
| Account-scoped cohort | $53.957554318 | Exact run-window control total; reconciled |

These are Fireworks rated serverless costs before credits, fixed fees,
invoice-level discounts, taxes, and final settlement.

OpenAI `api-standard` cells are API-billed and are not covered by a
ChatGPT subscription. The available project key received HTTP 403 from
the organization Costs API, which requires an Admin API key, so actual
OpenAI incurred costs remain pending rather than estimated as actuals.

Reference cost normalizes recorded usage to exact first-party model pricing;
incurred cost records the platform that served the cell. Claude subscription
cells are not assigned a false zero per-cell cost. DeepSeek first-party pricing
is a peak/off-peak range; exact GLM-5.3-Flash first-party pricing is currently
unpublished. Fireworks incurred values use rated-cost readbacks. Missing or
unreconciled values remain null. See `cost-methodology-v4.md`.
