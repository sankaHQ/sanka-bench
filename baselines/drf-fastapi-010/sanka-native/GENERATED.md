# Sanka native-converter provenance (drf-fastapi-010)

Generated once with PyPI `sanka-cli` 0.1.8 delegating to `sanka-migrate`
0.1.0a8, installed inside the fixture virtualenv with Python 3.12.13,
Django 5.2.17, Django REST Framework 3.18.0, and FastAPI 0.141.1.

The pass@1 run was executed from
`<repo>/tasks/drf-fastapi/drf-fastapi-010/source`:

```bash
sanka scan .
sanka plan . --to fastapi
sanka apply --root . --to fastapi --bench-candidate <local-path>
```

Scan reported 5 endpoints and scan hash
`sha256:1a04fdc293f968e80e2cb01db14c90f7bd74215f392e168606bd62942f869e53`.
The native plan hash was
`sha256:a367264ab13feae3f286ddaa15b6280920504f5894e2c18cbe131729f94e8ca9`.

## Honest outcome: 0% readiness and no candidate emitted

The native plan generated 0 of 5 non-alias routes. Four routes report
`SANKA_DRF_VIEWSET_OVERRIDES_UNSUPPORTED` because the viewset overrides create
and partial update to write versioned audit events transactionally. The custom
transition route reports `SANKA_DRF_CUSTOM_ACTION_UNSUPPORTED`.

The apply command exited with `the native plan contains no generatable routes;
nothing to apply`, so the frozen benchmark candidate is intentionally a no-op:
there was no generated overlay to package. It fails the boot, behavior,
database, side-effect, native, and determinism gates while source qualification
and source regression still pass. Nothing was retried or hand-fixed.
