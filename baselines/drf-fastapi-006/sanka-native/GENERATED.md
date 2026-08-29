# Sanka native converter baseline provenance (drf-fastapi-006)

Generated with the shipped engine — PyPI `sanka-cli` 0.1.8 delegating to
`sanka-migrate` 0.1.0a8 — installed into the fixture virtualenv
(`python 3.12.13`, `django 5.2.17`, `djangorestframework 3.18.0`,
`fastapi 0.141.1`) and run against the `drf-fastapi-006` fixture with:

```bash
sanka scan .
sanka plan . --to fastapi
sanka apply --root . --to fastapi --bench-candidate <dir>
```

The candidate is the untouched `--bench-candidate` output (plan hash
`sha256:388d0716cb5019591711c529391edbe57648e251bbad4385b32eba78df0c6f51`).

## Honest outcome: 14% readiness and only the API root emitted

Scan reported 14 endpoints. The native plan dropped 7 format-suffix aliases
and generated 1 of 7 non-alias routes. All 6 order CRUD routes require manual
adaptation with `SANKA_DRF_SERIALIZER_SEMANTICS_UNSUPPORTED`: the three-level
nested fields plus the serializer's transactional create/update overrides are
outside the current native envelope.

The frozen application therefore serves only `/api/`. Across the 32 graded
order scenarios it boots and responds deterministically, but matches 0
responses, 22 database states, 32 side-effect ledgers, and 0 native route
checks; unrouted scenarios record `no FastAPI route matched`. Nothing was
hand-fixed. The benchmark leads the converter on deep writable replacement,
depth-two index errors, mid-graph uniqueness, and rollback after partial graph
writes.
