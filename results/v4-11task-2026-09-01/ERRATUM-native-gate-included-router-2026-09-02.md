# Erratum 2 — the native-serving gate rejected every FastAPI `include_router` candidate

Date: **2026-09-02**  
Scope: all matrix runs at FastAPI 0.141.1 (pinned since the first commit); observed in
v4 and in the erratum study. v3 had no candidate using `include_router`.  
Status of v4 numbers: **unchanged**. Corrected verdicts are published as a labelled
re-evaluation beside the originals (`../v4-native-gate-reevaluation-a-2026-09-02/`).

## Mechanism

FastAPI 0.141 keeps `app.include_router(router)` targets as lazy
`fastapi.routing._IncludedRouter` entries in `app.routes` instead of copying the
router's `APIRoute` objects. The serving guard matched the request against
`app.routes`, got a full match on that wrapper, and recorded it as the serving route.
The wrapper carries no endpoint, so the evidence read
`route_class = fastapi.routing._IncludedRouter`, `endpoint_in_workspace = false`, and
the evaluator failed `native_target` on every scenario — while behaviour, database,
determinism and side-effect gates passed. A candidate built the ordinary FastAPI way
(a router module plus `include_router`) could not pass the native gate at all.
Reproduced on the frozen v4 environment with a three-line app.

Fix: sanka-bench PR #28 (`e3e875b`, branch `native-gate-included-router`). The guard now
walks the wrapper's effective candidates with the request scope and records the
underlying route, recursing through nested and prefixed includes; raw Starlette
routes, mounts and bridges are recorded as themselves and still fail. Evaluator
version is `0.0.2` from this change so re-evaluated reports are distinguishable.

## Blast radius

Every native-gate failure in v4 and the erratum study whose recorded route class was
`_IncludedRouter`:

| Cell | Routes | Other gates | Re-evaluated with the fixed guard |
| --- | ---: | --- | --- |
| GLM-5.3-Flash 003 alone | 14 | all passed | **passed 8/8** |
| GLM-5.3-Flash 008 with-sanka | 36 | all passed | **passed 8/8** |
| GLM-5.3-Flash 008 alone | 36 | all passed | still fails native: underlying route is `target_app.AnyMethodAPIRoute`, an `APIRoute` subclass (see policy question) |
| GLM-5.3-Flash 004 alone | 26 | boot, behaviour, database, determinism failed | still fails (genuine) |
| Claude Sonnet 5 011 with-sanka (erratum study) | 5 | all passed | **passed 8/8** |

Candidate digests are unchanged between the original and re-evaluated reports; only
the evaluator changed (`0.0.1` → `0.0.2`).

## Derived view (labelled; the official v4 rows are unchanged)

Official v4, then v4 with the erratum-study cells substituted for the discarded rows
and the include_router false negatives replaced by their re-evaluated verdicts:

| Model | Config | v4 official | Derived under both errata |
| --- | --- | ---: | ---: |
| Claude Opus 4.8 | alone | 100.0% | 100.0% |
| Claude Opus 4.8 | with-sanka | 92.9% | 100.0% |
| Claude Sonnet 5 | alone | 78.8% | 91.8% |
| Claude Sonnet 5 | with-sanka | 57.1% | 91.8% |
| gpt-5.6-sol | alone | 48.2% | 48.2% |
| gpt-5.6-sol | with-sanka | 84.7% | 84.7% |
| DeepSeek V4 Pro | alone | 63.5% | 63.5% |
| DeepSeek V4 Pro | with-sanka | 84.7% | 84.7% |
| GLM-5.3-Flash | alone | 22.4% | 30.6% |
| GLM-5.3-Flash | with-sanka | 44.1% | 65.3% |
| gpt-5.6-luna | alone | 45.9% | 45.9% |
| gpt-5.6-luna | with-sanka | 48.8% | 48.8% |
| **All six** | alone | 59.8% | 63.3% |
| **All six** | with-sanka | 68.7% | 79.2% |

Under both errata the Claude with-sanka deltas are 0.0 for Opus and 0.0 for Sonnet,
the GLM delta widens to +34.7, and the six-model route-weighted improvement becomes
+15.9 points (610 → 646 alone, 701 → 808 with-sanka out of 1020).

## Decision: `APIRoute` subclasses are native (evaluator 0.0.3)

Three further native-only failures were rejected only because the serving route was
an `APIRoute` *subclass* and the evaluator compared the class name with
`fastapi.routing.APIRoute` exactly:

| Cell | Routes | Subclass | What it does |
| --- | ---: | --- | --- |
| GLM-5.3-Flash 008 alone | 36 | `AnyMethodAPIRoute` | `matches()` returns FULL on a path match regardless of method, so the workspace endpoint reproduces DRF's 405 handling; plus a `/{not_found_path:path}` 404 route |
| GLM-5.3-Flash 002 with-sanka | 14 | `UniversalAPIRoute` | promotes PARTIAL (path matched, method not) to FULL for the same reason; plus a `/{full_path:path}` 404 route |
| DeepSeek V4 Pro 008 alone | 36 | `CaptureAllAPIRoute` | same pattern, documented in its docstring as preserving DRF's resolve-path-then-check-method order; plus a `/{path:path}` 404 route |

All three keep explicit per-path routes with workspace endpoints, import no source
framework, and use the subclass only to mirror DRF's resolve-first-then-405 order and
Django's 404 body. The disclosed contract says "served by a FastAPI `APIRoute` whose
endpoint code lives inside the candidate workspace". Decision (haegwan, 2026-09-02):
read that as `isinstance` — a subclass is an `APIRoute`. Implemented on top of PR #28
(sanka-bench PR #29, head `c09d59f` after rebasing onto the merged #28; batch b below ran at the pre-rebase commit `d6c10fa`, whose evaluator files are byte-identical):
the evidence keeps the concrete class name and adds `route_is_apiroute` and the
matched `route_path`; the report lists scenarios that a catch-all route served
although the source answered something other than 404 under
`diagnostics.catch_all_served_scenarios`, as a diagnostic, never a gate; evidence
recorded before 0.0.3 keeps the exact-class reading so old reports keep their
verdicts; the agent prompt is unchanged.

### Re-evaluation batch b (evaluator 0.0.3, all seven native-only failures)

| Cell | Routes | Original | Re-evaluated | Route class seen | Catch-all served non-404 |
| --- | ---: | --- | --- | --- | ---: |
| GLM-5.3-Flash 003 alone | 14 | failed (native) | **passed 8/8** | `fastapi.routing.APIRoute` | 0 |
| GLM-5.3-Flash 008 alone | 36 | failed (native) | **passed 8/8** | `target_app.AnyMethodAPIRoute` | 0 |
| GLM-5.3-Flash 008 with-sanka | 36 | failed (native) | **passed 8/8** | `fastapi.routing.APIRoute` | 0 |
| GLM-5.3-Flash 002 with-sanka | 14 | failed (native) | **passed 8/8** | `target_app.UniversalAPIRoute` | 0 |
| DeepSeek V4 Pro 008 alone | 36 | failed (native) | **passed 8/8** | `target_app.CaptureAllAPIRoute` | 0 |
| Claude Sonnet 5 011 with-sanka (study) | 5 | failed (native) | **passed 8/8** | `fastapi.routing.APIRoute` | 0 |
| GLM-5.3-Flash 004 alone | 26 | failed (boot, behaviour, database, determinism, native) | failed (same gates) | mixed | 0 |

The catch-all routes in the three subclass candidates served only scenarios the
source application also answered with 404, so none of them acted as a dispatcher.
Candidate digests are unchanged; only the evaluator changed (`0.0.1` → `0.0.3`).

### Derived view under both errata and the subclass decision (labelled; v4 rows unchanged)

| Model | Config | v4 official | Derived |
| --- | --- | ---: | ---: |
| Claude Opus 4.8 | alone | 100.0% | 100.0% |
| Claude Opus 4.8 | with-sanka | 92.9% | 100.0% |
| Claude Sonnet 5 | alone | 78.8% | 91.8% |
| Claude Sonnet 5 | with-sanka | 57.1% | 91.8% |
| gpt-5.6-sol | alone | 48.2% | 48.2% |
| gpt-5.6-sol | with-sanka | 84.7% | 84.7% |
| DeepSeek V4 Pro | alone | 63.5% | 84.7% |
| DeepSeek V4 Pro | with-sanka | 84.7% | 84.7% |
| GLM-5.3-Flash | alone | 22.4% | 51.8% |
| GLM-5.3-Flash | with-sanka | 44.1% | 73.5% |
| gpt-5.6-luna | alone | 45.9% | 45.9% |
| gpt-5.6-luna | with-sanka | 48.8% | 48.8% |
| **All six** | alone | 59.8% | 70.4% |
| **All six** | with-sanka | 68.7% | 80.6% |

Verified routes: alone 610 → 718, with-sanka 701 → 822 of 1020. The six-model
improvement is +10.2 points under the corrected evaluator (official v4: +8.9). Sanka
improves four cohorts (sol +36.5, GLM +21.7, luna +2.9, and no longer regresses Opus
or Sonnet, both 0.0) and leaves DeepSeek unchanged at 84.7 in both arms. The earlier
"derived under both errata" table above (63.3% → 79.2%) predates the subclass
decision and is superseded by this one.

## Artifacts

- `../v4-native-gate-reevaluation-a-2026-09-02/` — `run-manifest.json` (evaluator
  revision and file digests, candidate paths, selection rule), `reevaluate.py`
  (read-only over frozen candidates; writes only new reports), `reports/`, `logs/`,
  `reevaluation.json`, `REPORT.md`.
- `../v4-native-gate-reevaluation-b-2026-09-02/` — batch b under evaluator
  0.0.3 (all seven native-only failures; manifest pins evaluator file digests).
- Fix and tests: sanka-bench PR #28 (include_router) and PR #29 (subclass rule,
  catch-all diagnostic), `docs/design.md`.
