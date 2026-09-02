# Sanka Migration Bench — 10-task model matrix v3

Progress: **120/120 pass@1 cells terminal**, **72 fully migrated**, **119/120 costed**.
Completed managed waves: **22**; observed wave makespan: **5.1 hours**.

The suite is frozen at 10 tasks and 165 method-routes at the exact SHA in
`bench-sha.txt`. Workers run under one foreground managed-wave coordinator.
No terminal cell is overwritten or automatically retried.
Per-cell time is measured under the recorded managed-wave concurrency; wave
makespan is reported separately and is not silently compared with sequential runs.

| Model | Config | Cells | Tasks passed | Score | Time | Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 | alone | 10/10 | 8/10 | 84.2% | 119.4 min | $29.268700 |
| Claude Opus 4.8 | with-sanka | 10/10 | 7/10 | 60.0% | 104.2 min | $28.740624 |
| Claude Sonnet 5 | alone | 10/10 | 7/10 | 73.3% | 112.5 min | $17.988562 |
| Claude Sonnet 5 | with-sanka | 10/10 | 7/10 | 75.8% | 102.1 min | $16.204960 |
| gpt-5.6-sol | alone | 10/10 | 7/10 | 75.8% | 16.1 min | $3.691348 |
| gpt-5.6-sol | with-sanka | 10/10 | 6/10 | 53.9% | 17.1 min | $3.959167 |
| DeepSeek V4 Pro | alone | 10/10 | 7/10 | 73.3% | 81.2 min | pending |
| DeepSeek V4 Pro | with-sanka | 10/10 | 7/10 | 62.4% | 107.3 min | $3.859752 |
| GLM-5.3-Flash | alone | 10/10 | 4/10 | 28.5% | 77.6 min | $0.677778 |
| GLM-5.3-Flash | with-sanka | 10/10 | 4/10 | 28.5% | 87.2 min | $0.728221 |
| gpt-5.6-luna | alone | 10/10 | 4/10 | 28.5% | 16.6 min | $0.268201 |
| gpt-5.6-luna | with-sanka | 10/10 | 4/10 | 28.5% | 17.6 min | $0.283889 |

Cost basis: Claude Code self-report; OpenAI official direct Standard price card
applied to exact terminal token classes; Fireworks rated-cost API readback for the
exact model and run window. Unreconciled values remain null.

## Disclosed infrastructure reruns

Two task-005/alone Fireworks cells received an explicitly authorized attempt 2 after attempt 1 ended before candidate generation with the same account-level HTTP 412 response. Original artifacts remain preserved under `infrastructure-reruns/`; no quality-failed cell was retried.
After both attempt-2 streams also failed, bounded direct validation later completed successfully on Chat Completions and on non-streaming plus fully consumed streaming Responses calls for both exact benchmark models. The two failed cells remain terminal; subsequent untouched cells may proceed.

Recorded rerun cells: **2**.
