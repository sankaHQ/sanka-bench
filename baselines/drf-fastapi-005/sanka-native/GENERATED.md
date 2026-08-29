# Sanka native converter baseline provenance (drf-fastapi-005)

Generated with the shipped engine — PyPI `sanka-cli` 0.1.8 delegating to
`sanka-migrate` 0.1.0a8 — installed into the fixture virtualenv
(`python 3.12.13`, `django 5.2.17`, `djangorestframework 3.18.0`,
`fastapi 0.141.1`) and run against the `drf-fastapi-005` fixture with:

```bash
sanka scan .
sanka plan . --to fastapi
sanka apply --root . --to fastapi --bench-candidate <dir>
```

## Honest outcome: no native candidate was emitted

Scan reported 16 endpoints. The native plan dropped 8 format-suffix aliases
and reported 0% readiness (0 of 8 non-alias routes), with all 8 routes marked
`SANKA_DRF_MIDDLEWARE_UNSUPPORTED`: the fixture configures Django session and
authentication middleware, whose behavior the current native generator does
not reproduce. Plan hash:
`sha256:058667c1568c4f354c1e74b2112c0e6e548dd79a3cf410dde96603b92a91c456`.

The apply command then refused with `error: the native plan contains no
generatable routes; nothing to apply`. The baseline therefore records the
empty generated outcome with candidate kind `noop`; no target overlay exists
and nothing was hand-written or repaired. Evaluated as frozen it fails target
boot, behavior parity, database parity, and native compliance across all 31
graded scenarios. Session middleware, multi-authentication ordering, per-action
permissions, and the custom action remain outside this engine outcome.
