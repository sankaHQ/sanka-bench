# Sanka Migration Bench — 11-task model matrix v5

Progress: **132/132 pass@1 cells terminal**, **105 fully migrated**, **108/132 reference-costed**, **88/132 incurred-costed**.
Completed rolling stages: **6**; observed coordinator time: **5.76 hours**.

The suite is frozen at 11 tasks and 170 method-routes at the exact SHA in
`bench-sha.txt`. One foreground rolling coordinator owns every worker.
Generation is capped independently by provider/model; local evaluation is a
separate four-process queue. No terminal cell is overwritten or retried.
This concurrency methodology differs from v3; quality/token results remain
cell-scoped, while raw wall time is not silently compared with v3.

| Model | Config | Cells | Tasks passed | Score | Agent time | Reference cost | Incurred cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 | alone | 11/11 | 11/11 | 100.0% | 266.6 min | $77.430420 | subscription |
| Claude Opus 4.8 | with-sanka-readiness-aware | 11/11 | 11/11 | 100.0% | 270.2 min | $76.316091 | subscription |
| Claude Sonnet 5 | alone | 11/11 | 10/11 | 91.8% | 203.2 min | $36.966806 | subscription |
| Claude Sonnet 5 | with-sanka-readiness-aware | 11/11 | 10/11 | 91.8% | 211.8 min | $46.101882 | subscription |
| gpt-5.6-sol | alone | 11/11 | 9/11 | 84.7% | 35.2 min | $6.616526 | $6.616526 |
| gpt-5.6-sol | with-sanka-readiness-aware | 11/11 | 8/11 | 75.3% | 35.7 min | $7.469566 | $7.469566 |
| DeepSeek V4 Pro | alone | 11/11 | 10/11 | 92.9% | 311.2 min | $6.637652–$13.275303 | $13.275303 |
| DeepSeek V4 Pro | with-sanka-readiness-aware | 11/11 | 10/11 | 90.6% | 356.6 min | unavailable | $16.608757 |
| GLM-5.3-Flash | alone | 11/11 | 7/11 | 67.1% | 157.7 min | unavailable | $2.797528 |
| GLM-5.3-Flash | with-sanka-readiness-aware | 11/11 | 7/11 | 72.4% | 175.4 min | unavailable | $3.504753 |
| gpt-5.6-luna | alone | 11/11 | 5/11 | 48.8% | 31.9 min | $0.466824 | $0.466824 |
| gpt-5.6-luna | with-sanka-readiness-aware | 11/11 | 7/11 | 67.1% | 32.6 min | $0.518963 | $0.518963 |

## Fireworks platform-cost reconciliation

| Ledger | Rated USD | Treatment |
| --- | ---: | --- |
| 44 benchmark cells | $36.186341038 | Attributed to exact Codex thread / Fireworks billing sessions |
| Non-cell recovery and validation | $0.000000000 | Operational overhead, excluded from pass@1 cell costs |
| Account-scoped cohort | $36.186341038 | Exact run-window control total; reconciled |

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
unreconciled values remain null. See `cost-methodology-v5.md`.
