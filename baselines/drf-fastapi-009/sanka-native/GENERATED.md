# Sanka native-converter provenance (drf-fastapi-009)

Generated once with PyPI `sanka-cli` 0.1.8 delegating to `sanka-migrate`
0.1.0a8, installed inside the fixture virtualenv with Python 3.12.13,
Django 5.2.17, Django REST Framework 3.18.0, and FastAPI 0.141.1.

The pass@1 run was executed from
`<repo>/tasks/drf-fastapi/drf-fastapi-009/source`:

```bash
sanka scan .
sanka plan . --to fastapi
sanka apply --root . --to fastapi --bench-candidate <local-path>
```

Scan reported 12 endpoints and scan hash
`sha256:2c9527862aeb49ca669da9a697ddc07de672de01a475ae9006444429f41bacc0`.
The native plan hash was
`sha256:eaaf407ffc090b288ff33c734fa807d03b381ef84c88362ef0dc26829efbc5c4`.

## Honest outcome: 0% readiness and no candidate emitted

The native plan generated 0 of 12 non-alias routes. Nine routes report
`SANKA_DRF_SERIALIZER_SEMANTICS_UNSUPPORTED` because multipart `FileField`
validation and the serializer's metadata-writing override require manual
adaptation. The three binary download routes report
`SANKA_DRF_CUSTOM_ACTION_UNSUPPORTED`.

The apply command exited with `the native plan contains no generatable routes;
nothing to apply`, so the frozen benchmark candidate is intentionally a no-op:
there was no generated overlay to package. It fails the boot, behavior,
database, side-effect, native, and determinism gates while source qualification
and source regression still pass. Nothing was retried or hand-fixed.
