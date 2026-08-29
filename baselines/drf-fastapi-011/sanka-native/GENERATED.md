# Sanka native-converter provenance (drf-fastapi-011)

Generated once with PyPI `sanka-cli` 0.1.8 delegating to `sanka-migrate`
0.1.0a8, installed inside the fixture virtualenv with Python 3.12.13,
Django 5.2.17, Django REST Framework 3.18.0, and FastAPI 0.141.1.

The pass@1 run was executed from
`<repo>/tasks/drf-fastapi/drf-fastapi-011/source`:

```bash
sanka scan .
sanka plan . --to fastapi
sanka apply --root . --to fastapi --bench-candidate <local-path>
```

Scan reported 5 endpoints and scan hash
`sha256:67733c4559dc8fce8d14d94914932d84c712841c0335acf02fa742ff7f289a10`.
The native plan hash was
`sha256:69055f8284208722875ce972a3db2b247fc7feb987e02f74a60014bd52ecc12c`.

## Honest outcome: 0% readiness and no candidate emitted

The native plan generated 0 of 5 non-alias routes. The three transaction routes
report `SANKA_DRF_SERIALIZER_SEMANTICS_UNSUPPORTED` because their serializer's
slug-related account field requires manual adaptation. The annotated account
list and grouped summary each report `SANKA_DRF_VIEW_KIND_UNSUPPORTED` because
they are not router-bound `ModelViewSet` CRUD routes.

The apply command exited with `the native plan contains no generatable routes;
nothing to apply`, so the frozen benchmark candidate is intentionally a no-op:
there was no generated overlay to package. It fails the boot, behavior,
database, side-effect, native, and determinism gates while source qualification
and source regression still pass. Nothing was retried or hand-fixed.
