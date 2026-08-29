# Sanka native-converter provenance (drf-fastapi-007)

Generated once with PyPI `sanka-cli` 0.1.8 delegating to `sanka-migrate`
0.1.0a8, installed inside the fixture virtualenv with Python 3.12.13,
Django 5.2.17, Django REST Framework 3.18.0, and FastAPI 0.141.1.

The pass@1 run was executed from
`<repo>/tasks/drf-fastapi/drf-fastapi-007/source`:

```bash
sanka scan .
sanka plan . --to fastapi
sanka apply --root . --to fastapi --bench-candidate <local-path>
```

Scan reported 14 endpoints and scan hash
`sha256:271c8c10f125fb202d7c3b875478ee3ce211450692692d55202276151a5ded0e`.
The native plan hash was
`sha256:5d6e22c669dd930e4cdcbd9e6626dfeb8064186b1daf024ce8084b116b8a9b2e`.

## Honest outcome: 14% readiness and only the API root emitted

The native plan dropped 7 format-suffix aliases and generated 1 of 7
non-alias routes. All 6 record CRUD routes require manual adaptation with
`SANKA_DRF_VIEWSET_OVERRIDES_UNSUPPORTED` because the source viewset overrides
`retrieve()` and `update()` for conditional response behavior.

The untouched candidate therefore serves only `/api/`. Across the 30 graded
record scenarios it boots deterministically but matches 0 responses, 21
database states, all 30 empty side-effect ledgers, and 0 native route checks.
Nothing was hand-fixed; the benchmark leads the converter on cursor
pagination, combined filtering, exact decimal/timezone representation, and
conditional ETag responses.
