# Why with-sanka scores dropped for Opus 4.8 and gpt-5.6-sol — forensic root cause (2026-08-31)

Four parallel investigations over the frozen v3 artifacts (agent logs, frozen candidates,
evaluator reports, engine v0.1.0a8 source, bench SHA ed6bad6). Every claim below was
verified against artifacts; several failures were re-executed to confirm the diffs.

## Verdict in one paragraph

**The scaffold did not ship bad code — on 6 of 10 tasks it shipped almost no code at all,
and the regression is a posture effect amplified by scoring geometry.** At engine
v0.1.0a8, `sanka apply` refused outright on 005/009/010 (0% readiness) and emitted only
the API root on 006/007/008 (14%/14%/3%). Not one line of overlay code appears in any
failing Opus candidate, and Sol's kept overlay files are byte-identical and uninvolved in
its flips. What changed in the with-sanka condition is the *workflow the prompt mandates*
("the complete generated deliverable is the overlay… copy every file… then verify and
adjust"): the failing runs consistently did shallower source reconnaissance and
differential verification, then exited confident at "public suite green" — and every
single regressed scenario lives in the hidden evaluation superset the public suite never
exercises. Task-level all-or-nothing scoring × route weights then converted near-misses
(28–31 of 32 behaviors) into cliff losses; task 008 alone is 36/165 = 21.8 points.

## Verified facts

Raw per-scenario parity (denominator 240 = hidden eval scenarios × 10 tasks), reproduced
exactly from `reports/`:

| Cell | behavior | database | native |
|---|---|---|---|
| Opus alone | 227/240 = 94.6% | 97.9% | 86.7% |
| Opus with-sanka | **234/240 = 97.5%** | 99.6% | 87.1% |
| Sol alone | 228/240 = 95.0% | 99.2% | 99.6% |
| Sol with-sanka | 216/240 = 90.0% | 96.7% | 97.5% |

Opus with-sanka produced *more behaviorally accurate* migrations overall while its
official score fell 84.2→60.0. Sol's decline is real but concentrated: −21.9 of its
−21.9-point drop is task 008 (31/32 behaviors, 4 hidden redirect scenarios).

Per-task passes across all 6 models (alone → with-sanka):
001–004, 010 unchanged (ceiling); 005: 2→3 (helps); 006: 1→0; **007: 0→2 (helps)**;
**008: 4→1 (Opus, Sol, DeepSeek all lost it — systematic, not noise)**; 009: 2→1
(gates degraded for Sonnet 8/8→5/8, DeepSeek 8/8→2/8, Sol 5/8→2/8, while Opus was
rescued 2/8→8/8).

`used_sanka_candidate` = presence of `overlay/sanka-manifest.json` only
(`build_matrix_v3.py:277`): 43/60 with-sanka cells (opus 4, sonnet 4, sol 10, dsv4 7,
glm 10, luna 8). Sol's 009 flag is True because it *hand-wrote* a manifest after apply
refused — the flag measures prompt compliance, not code adoption.

Effort: with-sanka did **not** shorten Claude verification structurally (−6..−9% duration)
and Fireworks models spent +32–37% more. Sol with-sanka cells finished *earlier*
(87–91s vs 100–119s on 007–009), stopping at public-green. No cell hit limits except
Sonnet-007-with-sanka (see bug B3).

## Root cause per regressed cell

Every regression is a **confidently-written wrong assumption in an otherwise ~97%-correct
port, committed as a code comment and never tested against the oracle**, always on
hidden-eval-only scenarios:

- **Opus 005** (behavior 30/31, native 0/31): wrote "the test client bypasses CSRF … we
  match that" — false; the eval driver uses `Client(enforce_csrf_checks=True)`. Its own
  verification harness used `enforce_csrf_checks=False`, manufacturing confirming
  evidence for the bug. Also registered raw `starlette.routing.Route` objects → native
  gate 0/31 (evaluator requires `fastapi.routing.APIRoute` with endpoint in-workspace).
  Ran 90 probes, all "passing". Alone-005 read DRF/Django CSRF source and ported
  `_CSRFCheck`.
- **Opus 006** (31/32): missed DRF's field-level null check ordering — `{"items": null}`
  must yield `["This field may not be null."]` before the list-type check. 29 probes vs
  alone's 58; alone's matrix included the null case. Notably this run **never invoked the
  sanka CLI at all** — pure condition/prompt effect.
- **Opus 008** (28/32): returned `Response(status_code=307)` with *no Location header*
  under the comment "only the status code and (empty) body are contractually
  significant" — the four hidden redirect scenarios capture `Location`. Its differential
  harness compared status+body+DB, never headers. Alone-008's harness printed headers
  from minute 1 and reproduced `http://testserver/...` absolute Locations byte-for-byte.
- **Sol 008** (31/32 behavior, 29/32 native): agent-written redirects — one relative
  `Location` (source uses `build_absolute_uri` → absolute), three paths left to
  Starlette's implicit slash redirect (correct behavior but no workspace APIRoute →
  native fail). Engine had emitted 1/29 non-alias routes; Sol rewrote everything
  (sanka_native.py 424→118 lines). Alone-Sol read `urls.py` on command 2 and mirrored the
  mechanism (`redirect_slashes=False` + explicit absolute 307s).
- **Sol 009** (2/8 gates): `sanka apply` refused (0 routes, no overlay); everything
  agent-written. Unhandled `sqlite3.IntegrityError` on duplicate key crashes the guarded
  serving process → target_boot + deterministic + parity cascade; plus blank-vs-required
  wording. Alone-009 had all of it right (explicit duplicate 400, IntegrityError catch).
  Agent closed on "All 8 public scenarios match."
- **Sol 007** (db_parity flip): never registered PATCH/PUT/DELETE routes (405s, rows
  unchanged) despite a dead `DETAIL_ALLOW` constant showing the intent.

Reverse flips cap the attribution: **the tool contributed no code to the wins either**.
Opus-007-with-sanka passed via harness discipline (diffed captured headers, deferred to
observation); alone-007 overrode its own observation with a transport theory.
Alone-009 was the rushed sample (verified only the public 8; crashed on missing-file).
With n=1 per cell, which micro-assumption a run chooses to verify is substantially
stochastic — but the with-sanka tilt toward earlier confidence recurs across models and
tasks, and 008's 4→1 across three independent models is systematic.

## The engine's actual role (v0.1.0a8)

Honest, but the honesty doesn't travel:

- Readiness **is** computed and machine-readable — `FrameworkPlan.readiness`,
  per-route `adaptation_reasons`, persisted to `.sanka/plan-fastapi.json` and
  `sanka plan --json` — but **none of it ships in the overlay/manifest the agent (and
  bench) consume**. `apply` prints "generated N native routes" with no denominator.
- At 0% readiness apply refuses (correct — protected 005/009/010 from facade traps). In
  the 1–54% band it emits a **healthy-booting app that silently 404s every unsupported
  route** — the harmful shape (006/007/008: agents receive an api-root-only app with zero
  in-artifact trace of the 6–28 missing routes).
- The scanner **silently skips non-DRF views**: 008's four trailing-slash-redirect routes
  (plain Django view) are absent from scan, plan, and every disclosure — precisely the
  family that killed 008 in both Opus and Sol sanka runs.
- `sanka verify` (exit-1 on any needs-adaptation, differential probes via
  `.sanka/verify-cases.json`) exists but nothing in the apply/bench flow invokes it.
- 008 unsupported constructs: `re_path` regex routes + `@api_view` function views +
  custom-dispatch APIViews (18× VIEW_KIND), `lookup_field="code"` (6× LOOKUP_FIELD),
  dynamic format-built patterns (4× ROUTE_PATTERN). 009: FileField/validator/create
  overrides (SERIALIZER_SEMANTICS ×9) + `@action` (×3). 010: `@transaction.atomic`
  overrides + `@action`. 005's blanket `SANKA_DRF_MIDDLEWARE_UNSUPPORTED` is already
  fixed by the post-run middleware allowlist (sanka #35, 2026-08-29, not in 0.1.0a8).
- Baseline provenance is mixed: 001–003 generated at older engine commits, 004–010 at
  PyPI a8 (disclosed in GENERATED.md, but regenerate for determinism claims).

## Bench measurement findings

Sound overall — raw parity reproduces exactly, budgets are config-symmetric, and
with-sanka got no hidden handicap in time/turn budgets. Real issues:

- **B1** `side_effect_parity` is vacuous on 9/10 tasks (drivers hardcode
  `side_effects=[]`; only 009 emits evidence) — "8 hard gates" is effectively 7.
- **B2** the 60-turn cap only reaches Claude (`_codex_command` passes no turn limit;
  codex is bounded only by the 3600s timeout) — cross-agent effort comparability caveat.
- **B3** turn-cap/error exhaustion zeroes a cell **without evaluation**:
  Sonnet-007-with-sanka hit `error_max_turns` at 61 turns and was scored 0 (weight 14)
  with its workspace never frozen or evaluated. One-sided against with-sanka this run.
- **B4** silent provider death charged as model quality: GLM-006-alone ended after 61s
  with no new files and no error event; terminal-failed but absent from the
  infrastructure-reruns ledger.
- **B5** PROMPT_SANKA's mandated `cp -R overlay/. .` contradicts PROMPT_CORE's "add new
  files only" on `README.md` (present in every task source); adapter silently drops the
  modified file (11 with-sanka cells). Inert here (README), but a distortion channel.
- **B6** the prompt tells agents they're graded on `public-tests/scenarios.json`; tasks
  004–010 actually evaluate a hidden ~4× superset (e.g. 8 public vs 32 eval). Deliberate
  and config-symmetric — but it interacts with the sanka prompt's "verify and adjust"
  framing: an agent that does exactly what the prompt asks still fails unseen criteria.
- **B7** (latent) no oracle-stability check; no nondeterminism sources found in drivers.
- Scoring confirmed: score = Σ route_weight(fully-migrated)/165, pass@1 n=1; 008 = 21.8
  points on one all-or-nothing gate over 32 scenarios; Opus with-sanka's 28/32 on 008
  scores identically to producing nothing.

## Recommendations

**Track 1 — bench validity (cheap, before any rerun):**
1. Rewrite PROMPT_SANKA from mandate to readiness-aware availability: run scan/plan,
   read the readiness report, adopt the overlay only for covered routes, and state that
   the source app — not the overlay — remains the specification to verify against.
   (Optionally keep three arms: alone / sanka-available / sanka-mandated; the current
   condition measures "our instructions", not "our tool".)
2. Publish per-route/per-scenario diagnostics beside the official v0.2 score (the data
   already exists in `reports/`) — this is the v0.3 per-endpoint effort. Keep v0.2 as the
   comparable headline; never let raw parity replace it in public claims.
3. Fix B3 (freeze+evaluate on cap exhaustion), B4 (classify empty transcripts as infra),
   B1 (real side-effect evidence or drop the gate name), B6 (tell agents a hidden
   superset with header/redirect/edge coverage exists — without revealing it).
4. n=3 on decisive pairs before model-level conclusions (008/009 × Opus/Sol at minimum);
   single-sample task flips of 31/32-quality candidates are coin flips at the cliff edge.

**Track 2 — engine (the real product work; first four are small):**
1. Ship the gap inventory in the emitted artifacts: readiness, `native_eligible_routes`,
   `unsupported_routes: [{method, path, reasons}]` in sanka-manifest.json + copy
   `plan-fastapi.json` into the bench candidate. (Data already exists; it just doesn't
   travel.)
2. Fail-loud 501 stubs for unsupported non-alias routes (default in bench projection) —
   turns silent 404s into self-diagnosing TODOs. This alone flips 006/007/008 from
   "silently wrong" to "checklist".
3. Readiness-aware apply: print readiness + gap count at apply; `--min-readiness` /
   gap-report-only mode emitting a migration checklist instead of a "deliverable".
4. Wire the existing verifier into apply (`verify-cases.json`, scenario ingestion,
   `verify-report.json` in the candidate) — the "finisher" seam already exists unwired.
5. Disclose scanner skips (non-DRF callbacks → `skipped_routes`) — 008's redirect family
   must stop being invisible.
6. Envelope expansion, ordered by observed damage: 008-class (regex routes, function
   views, APIView, lookup_field, trailing-slash redirect parity) → 009-class (serializer
   semantics: file upload validation, custom actions, IntegrityError→400 mapping) →
   010-class (transactional overrides). Middleware allowlist (#35) already landed.
7. Strategic: emit per-route **semantic parity notes** from the scan (CSRF enforcement,
   absolute-Location redirects, null-vs-blank wording, Allow/WWW-Authenticate/
   Content-Length behavior, unique-constraint 400s). Alone-winners won by discovering
   exactly these in source; the scanner already visits these constructs. This converts
   the anchoring effect into a verification amplifier — Sanka as finisher.

**Track 3 — replication (proof, ~$60–70):** tasks 008+009 × Opus+Sol × 3 arms
(alone / current mandate / readiness-aware prompt+artifacts) × n=3, pass@1 each,
disclosed as a diagnostic side-study, not an official-score rerun.

## Where the earlier internal analysis stands

Confirmed: raw parity direction and magnitudes (exact); Sol's drop = task 008 hidden
redirect family; native readiness 0–14% on 005–010; anchoring concern on 008; cliff
sensitivity; "measures availability+instructions, not generated-code quality"; 43/60
manifest retention (with the caveat that the flag is file-presence, and endogenous to
engine coverage). Corrected/nuanced: the harm is **not** agents adopting an unsuitable
generated architecture (no overlay code survived into any failing Opus candidate; Sol
rewrote it) — it is the mandated copy-adjust *workflow* displacing source reconnaissance
and licensing earlier confidence; and Opus's regression is within single-sample variance
at the cliff, while 008's cross-model 4→1 and 009's cross-model gate collapse are the
systematic signals worth engineering against.
