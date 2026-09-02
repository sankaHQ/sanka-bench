# Native-gate re-evaluation of frozen candidates (labelled; originals unchanged)

Evaluator: sanka-bench `d6c10fa` (evaluator 0.0.3: the serving guard resolves FastAPI 0.141 `_IncludedRouter` entries to the underlying route, and any `fastapi.routing.APIRoute` subclass with a workspace endpoint is native; catch-all serving of non-404 scenarios is reported under diagnostics.catch_all_served_scenarios). Candidates are the frozen v4 / erratum-study directories, read-only; task fixtures identical to the frozen v4 SHA.

| Cell | Source | Routes | Original verdict | Original failed gates | Re-evaluated verdict | Re-evaluated failed gates | Route classes seen | Catch-all served (non-404) | Digest unchanged |
|---|---|---:|---|---|---|---|---|---:|---|
| GLM-5.3-Flash 003 alone | v4 | 14 | False | native_target | True | — | fastapi.routing.APIRoute | 0 | True |
| GLM-5.3-Flash 004 alone (also failed other gates) | v4 | 26 | False | behavior_parity, database_parity, deterministic, native_target, side_effect_parity, target_boot | False | behavior_parity, database_parity, deterministic, native_target, side_effect_parity, target_boot | None, fastapi.routing.APIRoute | 0 | True |
| GLM-5.3-Flash 008 alone | v4 | 36 | False | native_target | True | — | target_app.AnyMethodAPIRoute | 0 | True |
| GLM-5.3-Flash 008 with-sanka | v4 | 36 | False | native_target | True | — | fastapi.routing.APIRoute | 0 | True |
| Claude Sonnet 5 011 with-sanka | erratum-study | 5 | False | native_target | True | — | fastapi.routing.APIRoute | 0 | True |
| GLM-5.3-Flash 002 with-sanka (UniversalAPIRoute subclass) | v4 | 14 | False | native_target | True | — | target_app.UniversalAPIRoute | 0 | True |
| DeepSeek V4 Pro 008 alone (CaptureAllAPIRoute subclass) | v4 | 36 | False | native_target | True | — | target_app.CaptureAllAPIRoute | 0 | True |
