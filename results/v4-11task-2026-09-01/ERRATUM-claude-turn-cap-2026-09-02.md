# Erratum — the v4 Claude "with-sanka regression" is a harness measurement defect

Date: **2026-09-02**  
Scope: the four cells named under P0 in `BENCH-V4-SUMMARY.md` (Opus 009 with-sanka;
Sonnet 001, 002, 003 with-sanka) and the six other v4 "agent-run failures".  
Status of v4 numbers: **unchanged**. This document corrects the causal claim, not the score.  
Follow-up: **the separately labelled ten-cell erratum study is complete**.

## Verdict

The ten v4 cells recorded as `agent-run-failed` were never evaluated because of a
runner regression, not because Sanka taxed Claude's turn budget. All ten are Claude
cells that reached the fixed 60-turn cap **during the recovery waves**, which ran a
runner revision (PR #26, `7679f93`) that treats any non-zero process exit as an
agent-run failure before it reads the agent's result. Claude Code exits 1 on
`error_max_turns` while printing a complete result event, so the budget-exhaustion
branch that freezes and evaluates the workspace became unreachable. The same terminal
state (`num_turns: 61`, `subtype: error_max_turns`) in the earlier calibration and
rolling waves, under the previous runner (`13bd9a8`), was frozen and evaluated 14 of
14 times, and 13 of those 14 cells passed all eight hard gates.

The asymmetry between arms (7 with-sanka failures vs 3 alone) is a scheduling
artifact: it is simply which cells were still untouched when the coordinator was
recovered. The surviving transcripts show no Sanka-induced turn tax for Claude, and
they show that Sonnet never invoked the Sanka CLI in 8 of its 11 with-sanka cells.

## Mechanism

1. **Code.** `scripts/run_agent_candidate.py` at the frozen benchmark SHA `13bd9a8`
   gated on `if not timed_out and outcome.returncode != 0 and not stats:`. PR #26
   (`7679f93`, merged 2026-09-01T08:52Z) changed it to
   `if not timed_out and outcome.returncode != 0:`, so a parseable
   `error_max_turns` result no longer reaches the freeze branch below it.
2. **CLI contract.** Probed on the same CLI (2.1.241): a `-p` run that hits
   `--max-turns` exits **1** with empty stderr and a full result event
   (`is_error: true`, `subtype: error_max_turns`, `num_turns: cap + 1`,
   `stop_reason: tool_use`). The runner therefore logged
   `agent run failed: no output`, returned 1, and the `TemporaryDirectory`
   workspace was deleted. The candidate directories hold only the result line.
3. **Timeline.** Stages `v4-boot-gate`, the four calibration stages and
   `v4-rolling-remaining` used the `13bd9a8` worktree runner. PR #26 was opened at
   08:04Z to recover the interrupted coordinator, merged at 08:52Z, and every
   `v4-recovery-*` stage from 08:54Z onward ran with `toolchain.agent_runner`
   pointing at `7679f93` (as pinned in `run-manifest.json`).
4. **Why tests passed.** The harness test double always exited 0, so
   `test_turn_budget_exhaustion_freezes_the_workspace` kept passing while the real
   CLI path was broken.

## Evidence: every Claude cell that reached the cap

| Wave family | Runner | Cap-hit Claude cells | Frozen and evaluated | Passed 8/8 |
| --- | --- | ---: | ---: | ---: |
| boot-gate, calibration, rolling-remaining | `13bd9a8` | 14 | 14 | 13 (Sonnet 007 alone failed 7/8) |
| recovery (final, resume1–3) | `7679f93` | 10 | 0 | — |

Recovery-wave cells that did **not** hit the cap (Opus 009/010/011 alone, Opus
010/011 with-sanka, Sonnet 010 with-sanka) were frozen and passed. The two 62-turn
`success` overruns (Sonnet 003 alone, Sonnet 006 with-sanka) were frozen and passed
in both wave families, because a successful result exits 0.

Cap hits by arm (from `agent-result.json` subtypes):

| Model | Config | Cap hits | Frozen | Frozen and passed | Discarded (unevaluated) |
| --- | --- | ---: | ---: | ---: | --- |
| Opus 4.8 | alone | 4 | 4 | 4 | — |
| Opus 4.8 | with-sanka | 3 | 2 | 2 | 009 |
| Sonnet 5 | alone | 8 | 5 | 4 | 009, 010, 011 |
| Sonnet 5 | with-sanka | 9 | 3 | 3 | 001, 002, 003, 007, 009, 011 |

Sonnet reaches the cap in 17 of 22 cells (plus two 62-turn overruns). At this prompt
the 60-turn ceiling binds Sonnet in **both** arms, so which Sonnet cells cross the
line is close to a coin flip, and the two arms differ by one cap hit.

## Turn accounting from the surviving transcripts

Claude Code persisted every v4 session under the Claude Code CLI session store (session ids are
in each `agent-result.json`); all 44 Claude transcripts were found. The classifier,
per-cell JSON and tables live in `diagnostics/claude-turn-accounting-2026-09-02.md` (tables only; the per-cell JSON and scripts stay in the workspace mirror).
Tool calls are classified as: `recon_src` (reading the task source), `recon_lib`
(reading Django/DRF/FastAPI library source), `sanka_cli`, `overlay_read`,
`oracle_probe` (running the source app to observe behaviour), `harness_write`
(writing probe/compare scripts), `implement` (writing deliverables), `target_probe`
(exercising the new app alone), `verify` (differential runs), `env`, `cleanup`.

Mean tool calls per cell:

| Model | Config | CLI turns | tool calls | recon_src | recon_lib | sanka_cli | overlay_read | oracle_probe | harness_write | implement | verify |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Opus 4.8 | alone | 50.9 | 49.9 | 7.8 | 2.4 | 0 | 0 | 10.0 | 9.9 | 9.1 | 3.7 |
| Opus 4.8 | with-sanka | 54.0 | 54.9 | 11.7 | 2.6 | 3.1 | 1.4 | 8.5 | 7.2 | 7.2 | 4.1 |
| Sonnet 5 | alone | 59.7 | 67.0 | 16.9 | 7.8 | 0 | 0 | 12.2 | 7.8 | 10.0 | 3.5 |
| Sonnet 5 | with-sanka | 59.7 | 66.7 | 15.1 | 7.5 | 0.8 | 0.3 | 15.0 | 7.5 | 6.8 | 4.5 |

Paired per-task sums (with-sanka minus alone, over 11 tasks):

- **Opus:** +55 tool calls in total (+5/cell): +34 `sanka_cli`, +15 `overlay_read`,
  +43 `recon_src`, offset by −30 `harness_write`, −21 `implement`, −17
  `oracle_probe`. Opus hit the cap in 3 with-sanka cells vs 4 alone cells. The
  Sanka CLI itself costs about three tool calls per cell (scan, plan, apply) and
  roughly one minute of wall time.
- **Sonnet:** −3 tool calls in total; turns are censored at 61 in both arms.
  Sonnet ran `sanka scan/plan/apply` in only 3 of 11 with-sanka cells (004, 007,
  009) and never mentioned Sanka in its own narration in the other 8. For Sonnet the
  with-sanka arm was, in practice, the alone arm plus an unused paragraph of prompt.

Where the time goes (mean minutes per cell): `oracle_probe` dominates every arm
(Opus 10.0 / 9.4, Sonnet 7.1 / 6.5), i.e. running the source app to learn its
exact semantics — the behaviour the prompt asks for. `sanka_cli` adds ~1.0 minute
per Opus with-sanka cell.

## State of the ten discarded cells at the cut-off

Transcript-based reading of the last tool results and the agent's last narration.
This is **not** an evaluation — the workspaces no longer exist — but it is the
only evidence of what the runner threw away.

| Cell | Deliverables written | Own differential verification at cut-off | Reading |
| --- | --- | --- | --- |
| Opus 009 with-sanka | yes (target_app.py 26.7 KB at call 22) | call 60: "target: 65 scenarios … DETERMINISM: identical across runs … compiles clean"; last step was an unused-import check | complete, polishing |
| Sonnet 001 with-sanka | yes | cleanup done; "re-run the full comparison suite one final time" was the pending call | complete, polishing |
| Sonnet 002 with-sanka | yes | "This matches my implementation exactly. Now let's clean up the scratch exploration files" | complete, cleaning up |
| Sonnet 003 with-sanka | yes | "All 16 public scenarios match exactly (status, body, and headers)"; probing extra edge cases | complete, extending checks |
| Sonnet 007 with-sanka | yes | last run raised `SynchronousOnlyOperation` (async handler on the ORM); mid-fix | incomplete |
| Sonnet 009 alone | yes | producing the FastAPI output file for a diff; diff not yet run | unknown |
| Sonnet 009 with-sanka | yes | last run: `FileResponse … no content attribute`; mid-fix of multipart parsing | incomplete |
| Sonnet 010 alone | yes | "83/83 response scenarios matched. Orders table matches exactly. Events table matches exactly." | complete |
| Sonnet 011 alone | yes | still building the FastAPI-side probe after seeding the DB | unknown |
| Sonnet 011 with-sanka | yes | last run raised `SynchronousOnlyOperation`; rewriting ORM access | incomplete |

All four P0 cells were in a complete-and-polishing state. Given that 13 of the 14
turn-capped cells the earlier runner did freeze passed every hard gate, the most
likely v4 outcome without the regression is Opus with-sanka 11/11 and a Sonnet
delta that is noise around the turn cap, not a 21.7-point regression.

## Erratum study result (2026-09-02, executed after authorization)

The ten discarded cells were re-executed as a separately labelled study
(`../v4-erratum-study-2026-09-02/`, run id `v4-erratum-20260901T213700Z-26d1afdc`)
at the same benchmark SHA, engine pins, prompt, 60-turn budget and evaluator, with the
fixed runner (PR #27 head `9238405`, merged as `522666e`), Claude CLI 2.1.241, four
concurrent Claude cells, one foreground coordinator. 10/10 cells terminal, makespan 59
minutes, $34.90 API-equivalent (Claude Max, no metered spend).

| Cell | Turns | Terminal | Gates | Result |
| --- | ---: | --- | ---: | --- |
| Opus 009 with-sanka | 50 | completed | 8/8 | passed |
| Sonnet 001 with-sanka | 67 | success overrun (disclosed) | 8/8 | passed |
| Sonnet 002 with-sanka | 61 | cap, frozen | 8/8 | passed |
| Sonnet 003 with-sanka | 54 | completed | 8/8 | passed |
| Sonnet 007 with-sanka | 61 | cap, frozen | 7/8 | failed: behavior parity on the same 4 ETag scenarios Sonnet alone failed in v4 |
| Sonnet 009 alone | 61 | cap, frozen | 8/8 | passed |
| Sonnet 009 with-sanka | 61 | cap, frozen | 8/8 | passed |
| Sonnet 010 alone | 61 | cap, frozen | 8/8 | passed |
| Sonnet 011 alone | 61 | cap, frozen | 8/8 | passed |
| Sonnet 011 with-sanka | 67 | success overrun (disclosed) | 7/8 | failed: native-serving evidence non-compliant on all 32 scenarios (behaviour and database parity 32/32) |

Every cell that returned `error_max_turns` was frozen and evaluated this time: six
cap hits, five of them passed. Two additional cells reported successful completion
after 67 turns. All four P0 cells passed.

Derived view (labelled; the official v4 rows are unchanged):

| Model | Config | v4 official | v4 with the discarded cells replaced by the study |
| --- | --- | ---: | ---: |
| Opus 4.8 | alone | 100.0% | 100.0% |
| Opus 4.8 | with-sanka | 92.9% | 100.0% |
| Sonnet 5 | alone | 78.8% | 91.8% |
| Sonnet 5 | with-sanka | 57.1% | 88.8% |

Under the derived view the Claude with-sanka "regressions" become 0.0 points for Opus
and −3.0 points for Sonnet, the latter being one 5-route task (011) lost to the
native-serving gate in a single pass@1 cell. That native failure is NOT the raw-Starlette
trap: its recorded route class is `fastapi.routing._IncludedRouter`, the lazy wrapper
FastAPI 0.141 leaves in `app.routes` for the ordinary `app.include_router(router)`
pattern, which the serving guard misreported as a non-APIRoute with no workspace
endpoint. That is an evaluator false negative, documented separately in
`ERRATUM-native-gate-included-router-2026-09-02.md` together with the three v4 cells it
also affected. The 007 failure is an ordinary quality failure the evaluator graded. Two cells reported `success` at 67 turns, above the requested 60,
which the runner discloses as a protocol deviation (the CLI's limiter and its turn
counter differ); this is the same behaviour seen in the 009 replication.

Publication language for v4 therefore becomes: "10 Claude cells were discarded
unevaluated by a runner exit-code regression; re-executed in a labelled study, 8 of 10
passed; the official v4 rows are unchanged." No Sanka turn tax is measured for Claude.
Study artifacts (transcripts, logs, manifest) contain local absolute paths and must be
scrubbed before publication; the key-leak scan of all 135 study files found no secret
values.

## What changes and what does not

- **v4 stays as recorded.** No cell is retried, rescored or repaired. The
  `agent-run-failed` rows remain, with this erratum attached.
- **The P0 narrative is withdrawn.** There is no measured "Sanka-induced
  instruction/verification turn tax" for Claude in v4. The regression rows are a
  runner defect that happened to land mostly on with-sanka cells.
- **Publication language.** Any v0.1 packaging must present the Claude rows as
  "10 unevaluated cells (harness exit-code regression, see erratum)", not as a
  Sanka regression, and must not present the Claude with-sanka deltas as
  evidence in either direction.

## Fix

Bench branch `turn-cap-freeze-exit-code`, PR sankaHQ/sanka-bench#27 (bot-authored via
sanka-pr-flow, approved head `9238405`, merged to main as `522666e` on 2026-09-02): the runner treats a parseable result as authoritative over
the exit code (only an unparseable non-zero exit is an agent-run failure); the test
double exits 1 whenever it reports an error, so the budget-exhaustion test pins the
real CLI contract; new tests cover the unparseable-exit path and transcript
preservation; Claude runs are captured with `--output-format stream-json --verbose`
so `agent-log.jsonl` is the per-turn transcript rather than a copy of the result
line; `docs/design.md` records the contract.

## Remaining recommended next steps

1. **Turn-budget policy for v5.** Sonnet hits 60 turns in 17/22 cells with the v4
   prompt (v3's shorter prompt averaged ~48). Either raise the cap (a new matrix
   version; 100 turns or a wall-clock-only budget are the obvious candidates) or
   keep 60 and disclose that the Sonnet rows measure a truncated agent. Codex has
   no turn cap at all, so cross-agent effort comparability already carries a
   caveat.
2. **Sonnet and the Sanka CLI.** With the current availability-style prompt,
   Sonnet ignores the tool in 8 of 11 cells. If the with-sanka arm is meant to
   measure the tool, the prompt must make invocation part of the contract (or
   the readiness-aware arm, which runs scan/plan before the agent starts, should
   be the official with-sanka arm). That is a prompt change and therefore a new
   labelled study.
3. **Publication hygiene.** The transcripts and the turn-accounting JSON contain
   local absolute paths and tool output; run the existing key-leak and path scan
   before anything under `diagnostics/` leaves this machine.

## Artifacts

- the turn-accounting scripts (kept in the workspace mirror, not published) — read-only analysis over `matrix-v4.json`, the candidate
  `agent-result.json` files, and the Claude session store.
- `diagnostics/claude-turn-accounting-2026-09-02.md`
  — per-cell tool-call sequences with phases, timings and result tails; the
  per-cell and per-arm tables.
- Session transcripts: `the Claude Code CLI session store (one JSONL per session id)`
  (44/44 present on 2026-09-02; the CLI's own store, outside the mirror).
