# Sanka native-converter provenance (drf-fastapi-008)

Generated once with PyPI `sanka-cli` 0.1.8 delegating to `sanka-migrate`
0.1.0a8, installed inside the fixture virtualenv with Python 3.12.13,
Django 5.2.17, Django REST Framework 3.18.0, and FastAPI 0.141.1.

The pass@1 run was executed from
`<repo>/tasks/drf-fastapi/drf-fastapi-008/source`:

```bash
sanka scan .
sanka plan . --to fastapi
sanka apply --root . --to fastapi --bench-candidate <local-path>
```

Scan reported 36 endpoints and scan hash
`sha256:69a673430c0d2cfb8f0e40337fb53dc5b1909dce08cff6d82177f84db6aba7d9`.
The native plan hash was
`sha256:828cb33d720a97dfec9e1125f49094b9dca00dfa540e5b138413b1441d315aa7`.

## Honest outcome: 3% readiness and only the API root emitted

The native plan generated 1 of 29 non-alias routes and dropped 7 format-suffix
aliases. The remaining 28 non-alias routes require manual adaptation: 18
function/APIView methods report `SANKA_DRF_VIEW_KIND_UNSUPPORTED`, 6 viewset
methods report `SANKA_DRF_LOOKUP_FIELD_UNSUPPORTED`, and 4 dynamic-regex
methods report `SANKA_DRF_ROUTE_PATTERN_UNSUPPORTED`.

The untouched candidate therefore serves only `/api/viewset/`. It boots, but
the 32-scenario evaluator records 0/32 behavior matches, 19/32 database-state
matches, 32/32 empty side-effect ledgers, and 0/32 native route checks. Nothing
was retried or hand-fixed; this fixture deliberately leads the converter on
mixed legacy view kinds, non-slug lookup semantics, and dynamic regex
adaptation.
