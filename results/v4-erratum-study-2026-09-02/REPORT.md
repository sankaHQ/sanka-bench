# v4 erratum study — the ten discarded Claude cells, re-executed

Benchmark SHA `13bd9a863a76f813495c4483c1e39cd8aa7bba44`; engine 0.1.8 / 0.1.0a10; runner `92384056f706b4ff89488c3eed6e0f2b15ba697a`; Claude CLI 2.1.241 (Claude Code).
Same prompt, 60-turn budget, evaluator and pass@1 rule as v4. These rows are published beside v4 and are never merged into the v4 record.

Stage: 10/10 driver exit 0; makespan 59 min at 4 concurrent Claude cells.

| Cell | v4 status | v4 turns | Study turns | Study terminal | Gates | Fully migrated | Agent min | Cost (API-equiv) |
|---|---|---:|---:|---|---:|---|---:|---:|
| 009-claude-opus48-with-sanka | agent-run-failed | 61 | 50 | completed within budget | 8/8 | True | 31 | $6.07 |
| 009-claude-sonnet5-alone | agent-run-failed | 61 | 61 | turn budget (60) exhausted; the workspace was frozen as-is | 8/8 | True | 16 | $3.22 |
| 009-claude-sonnet5-with-sanka | agent-run-failed | 61 | 61 | turn budget (60) exhausted; the workspace was frozen as-is | 8/8 | True | 18 | $3.33 |
| 007-claude-sonnet5-with-sanka | agent-run-failed | 61 | 61 | turn budget (60) exhausted; the workspace was frozen as-is | 7/8 | False | 20 | $3.58 |
| 011-claude-sonnet5-alone | agent-run-failed | 61 | 61 | turn budget (60) exhausted; the workspace was frozen as-is | 8/8 | True | 19 | $3.51 |
| 011-claude-sonnet5-with-sanka | agent-run-failed | 61 | 67 | Claude CLI reported successful completion after 67 turns, exceeding the requested 60-turn limit; the workspace was frozen as-is and the overrun is disclosed | 7/8 | False | 18 | $3.45 |
| 010-claude-sonnet5-alone | agent-run-failed | 61 | 61 | turn budget (60) exhausted; the workspace was frozen as-is | 8/8 | True | 18 | $3.19 |
| 003-claude-sonnet5-with-sanka | agent-run-failed | 61 | 54 | completed within budget | 8/8 | True | 17 | $2.69 |
| 002-claude-sonnet5-with-sanka | agent-run-failed | 61 | 61 | turn budget (60) exhausted; the workspace was frozen as-is | 8/8 | True | 18 | $3.30 |
| 001-claude-sonnet5-with-sanka | agent-run-failed | 61 | 67 | Claude CLI reported successful completion after 67 turns, exceeding the requested 60-turn limit; the workspace was frozen as-is and the overrun is disclosed | 8/8 | True | 13 | $2.56 |

## Derived view (labelled; not the v4 record)

| Model | Config | v4 official | Derived (discarded cells replaced) | Cells substituted |
|---|---|---:|---:|---|
| Claude Opus 4.8 | alone | 100.0% (170/170) | 100.0% (170/170) | — |
| Claude Opus 4.8 | with-sanka | 92.9% (158/170) | 100.0% (170/170) | 009-claude-opus48-with-sanka |
| Claude Sonnet 5 | alone | 78.8% (134/170) | 91.8% (156/170) | 009-claude-sonnet5-alone, 011-claude-sonnet5-alone, 010-claude-sonnet5-alone |
| Claude Sonnet 5 | with-sanka | 57.1% (97/170) | 88.8% (151/170) | 009-claude-sonnet5-with-sanka, 007-claude-sonnet5-with-sanka, 011-claude-sonnet5-with-sanka, 003-claude-sonnet5-with-sanka, 002-claude-sonnet5-with-sanka, 001-claude-sonnet5-with-sanka |
