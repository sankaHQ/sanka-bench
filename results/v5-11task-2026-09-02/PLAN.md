# Sanka Migration Bench v5 — pre-declared plan (draft, 2026-09-02)

Status: **draft for approval; nothing launched.**  
Purpose: a clean headline record under the corrected harness and evaluator and the
policy decisions taken after v4. v5 replaces v3 on sanka.com/bench; v3 and v4 move to a
history section with their errata. Same eleven tasks, six models, two arms, pass@1.

## Frozen inputs (pinned at launch, never substituted)

| Input | v5 value | Note |
| --- | --- | --- |
| Benchmark SHA | `main` after sanka-bench PR #29 lands | tasks/ and baselines/ identical to v4's `13bd9a8`; runner carries #27 (exit code, stream-json) and #28 (include_router); evaluator 0.0.3 (#29) |
| Engine | `sanka-cli 0.1.8` + `sanka-migrate 0.1.0a10` (PyPI) | unchanged from v4 so the only differences are the pre-declared deltas below |
| Claude Code CLI | recorded at launch (2.1.241 today) | auto-updates; the run manifest pins whatever is live and the study aborts on drift mid-run |
| Codex CLI | 0.150.1 from `.bench-tools` | unchanged |
| Models | the six v4 models, exact ids re-probed at launch | Opus 4.8, Sonnet 5, gpt-5.6-sol, gpt-5.6-luna, DeepSeek V4 Pro (Fireworks serverless-standard), GLM-5.3-Flash (Fireworks serverless-standard) |
| Score | Migration Quality Score v0.2, route-weighted all-or-nothing, 170 routes | rule text clarified: served by a FastAPI `APIRoute` *or subclass* with a workspace endpoint (Erratum 2) |

## Pre-declared deltas from v4

- **D1 runner.** Parsed result is authoritative over the CLI exit code; turn-capped
  Claude workspaces are frozen and graded (PR #27). Claude transcripts captured as
  stream-json.
- **D2 evaluator 0.0.3.** `include_router` resolution (PR #28); `APIRoute` subclasses
  accepted; catch-all serving of non-404 scenarios reported as a diagnostic (PR #29).
- **D3 turn budget.** Claude `--max-turns 120`, intended to be non-binding; the turn
  distribution is published so the claim can be checked. Codex remains uncapped by
  turns and bounded by the 3600 s wall clock, as in v4; the asymmetry stays disclosed.
  v5 turn counts are not comparable with v4's.
- **D4 with-Sanka arm.** The readiness-aware arm is the official "with Sanka" arm: the
  harness runs `sanka scan` and `sanka plan` before the agent starts, freezes
  `sanka-readiness.json`, injects readiness, the unsupported-route checklist and the
  skipped-URL list into the prompt, and offers the scaffold only at ≥ 50 % readiness.
  Candidate suffix `-with-sanka-readiness-aware`; page label "with Sanka". The v4
  availability-style arm is retired (Sonnet ignored the optional tool in 8 of 11 cells).
- **D5 arms.** Two arms only; no third diagnostic arm (cost).
- **D6 Claude authentication.** DECISION NEEDED: Claude Max (v4 style; API-equivalent
  self-reported cost, shares your rate limit while running) or an Anthropic API key
  (real incurred cost on the same footing as Fireworks; ≈ $230 at v4 volumes).
- **D7 concurrency.** v4's calibration ladder: sequential boot gate, then 1 → 3 → 4 → 6
  per provider, then the rolling queue (≤ 18 total, ≤ 6 per provider, ≤ 3 per exact
  model). Four-process local evaluation queue. One foreground coordinator.
- **D8 cost.** Metered: v4 recorded $17.70 Fireworks rated and an unread OpenAI bill
  (est. ≈ $9). Central estimate $30 metered, ceiling $60. Claude: $0 marginal on Max
  (≈ $230 API-equivalent) or ≈ $230 actual on an API key. DECISION NEEDED: ceiling.
- **D9 publication.** sanka.com/bench regenerated from `matrix-v5.json`; the page
  generator's hard-coded v3 invariants become v5 invariants; task 011 copy added; the
  narrative is derived from the data, not hand-written; v3/v4 history with errata;
  scrubbed artifacts (no local paths, no secrets) published beside the frozen SHA.
- **D10 pass@1, no retries.** Quality failures are terminal; infrastructure failures
  are stopped, classified and preserved; any rerun needs new explicit authorization.

## Tooling changes before launch (tracking-dir scripts, pinned by sha256 in the manifest)

1. `cell_driver_v5.py`: `--max-turns` from `manifest.execution.max_turns`; pass
   `--sanka-bin` for any config starting with `with-sanka`; scope string
   `132-cell-v5`; otherwise the v4 driver.
2. `rolling_coordinator.py`: configs `["alone", "with-sanka-readiness-aware"]` flow
   through `build_cells`; verify candidate ids and stage plans; boot gate on the first
   readiness-aware cell (target_boot must pass).
3. `build_matrix_v5.py`: config labels; readiness fields from `sanka-readiness.json`
   (readiness %, scaffold emitted or refused) as row columns; turn distribution
   summary; v0.3 diagnostics; catch-all diagnostic counts.
4. Manifest template + `PRELAUNCH.md` gates (SHA/worktree validated, env pins, six
   exact model probes, `.env` mode, memory/disk, no competing broad runs, explicit
   paid-run authorization with ceiling, unique run id).
5. sanka-public: `scripts/bench/build-developer-bench-data.mjs` v5 invariants and
   task 011 copy; `developer-bench-page.tsx` narrative from data; history + errata
   section; land or close PR #437 first.

## Timeline

Prep half a day (after #29 lands) · boot gate + calibration ≈ 2 h · rolling remainder
≈ 9–10 h · aggregate, scrub and page PR half a day. v3 stays live until the v5 page PR
lands and sanka-public is deployed (deploy requires your explicit approval).

## Launch gates (all must be true)

1. PR #29 merged; frozen worktree at the exact merge SHA passes
   `uv run --frozen sanka-bench validate`; baselines CI green at that SHA.
2. Engine pins resolve; six exact model ids re-probed without substitution; Claude
   and Codex CLI versions recorded.
3. `.env` symlink and mode verified without printing secrets; no terminal v5 rows or
   coordinator lock in the mirror.
4. Memory pressure and disk healthy; no competing pytest, coordinator, or agent runs.
5. D6 and D8 decided; explicit paid-run authorization for the 132-cell v5 matrix and
   its ceiling recorded in the manifest.
