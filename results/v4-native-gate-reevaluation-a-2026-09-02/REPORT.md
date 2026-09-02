# Native-gate re-evaluation of frozen candidates (labelled; originals unchanged)

Evaluator: sanka-bench `e3e875b` (serving guard resolves FastAPI 0.141 `_IncludedRouter` entries to the underlying route). Candidates are the frozen v4 / erratum-study directories, read-only; task fixtures identical to the frozen v4 SHA.

| Cell | Source | Routes | Original verdict | Original failed gates | Re-evaluated verdict | Re-evaluated failed gates | Route classes seen | Digest unchanged |
|---|---|---:|---|---|---|---|---|---|
| GLM-5.3-Flash 003 alone | v4 | 14 | False | native_target | True | — | fastapi.routing.APIRoute | True |
| GLM-5.3-Flash 004 alone (also failed other gates) | v4 | 26 | False | behavior_parity, database_parity, deterministic, native_target, side_effect_parity, target_boot | False | behavior_parity, database_parity, deterministic, native_target, side_effect_parity, target_boot | None, fastapi.routing.APIRoute | True |
| GLM-5.3-Flash 008 alone | v4 | 36 | False | native_target | False | native_target | target_app.AnyMethodAPIRoute | True |
| GLM-5.3-Flash 008 with-sanka | v4 | 36 | False | native_target | True | — | fastapi.routing.APIRoute | True |
| Claude Sonnet 5 011 with-sanka | erratum-study | 5 | False | native_target | True | — | fastapi.routing.APIRoute | True |
