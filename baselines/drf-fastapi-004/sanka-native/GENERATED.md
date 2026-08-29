# Sanka native converter baseline provenance (drf-fastapi-004)

Generated with the shipped engine — PyPI `sanka-cli` 0.1.8 delegating to
`sanka-migrate` 0.1.0a8 — installed into the fixture virtualenv
(`django 5.2.17`, `djangorestframework 3.18.0`, `fastapi 0.141.1`) and run
against the `drf-fastapi-004` fixture with:

```bash
sanka scan .
sanka plan . --to fastapi
sanka apply --root . --to fastapi --bench-candidate <dir>
```

The candidate is the untouched `--bench-candidate` output
(plan hash `sha256:68162c9f7e9bf13aea681080dd22d69c526fac7a179b395a35bca7b6b2d32e91`).

## Honest outcome: the fixture is outside the current envelope

The native plan reported 54% readiness (7 of 13 non-alias routes) and six
endpoints needing manual adaptation:

- `SANKA_DRF_VIEWSET_KIND_UNSUPPORTED` — `LedgerEntryViewSet` (4 endpoints)
  and `AuditLogViewSet` (1 endpoint) are mixin-composed viewsets, not
  `ModelViewSet`;
- `SANKA_DRF_CUSTOM_ACTION_UNSUPPORTED` — the `transfer` custom action
  (1 endpoint).

The emitted application therefore serves only the `AccountViewSet` surface.
Evaluated as frozen, it fails: behavior parity 5/17, database parity 10/17,
native compliance 5/17 (unrouted scenarios record `no FastAPI route
matched`), `fully_migrated=false`. The five passing scenarios are exactly
the plain-account ones, including both balance-read-only checks — every
scenario touching entries, the audit trail, or the transfer action fails.
The engine also never generated the signal side effects; the emitted app
relies on the retained `ledger` app config, whose `ready()` still connects
the source receivers. Nothing was hand-fixed. The benchmark leads the
converter: signal-driven side effects, mixin-composed viewsets, and custom
actions are the next envelope work.
