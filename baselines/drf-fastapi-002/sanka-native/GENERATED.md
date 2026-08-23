# Sanka native converter baseline provenance (drf-fastapi-002)

Generated from Sanka commit `a5866d3831712fb05908b6b967bc08bb1ce031e4`
(PR #17, auth-envelope extension) against the `drf-fastapi-002` fixture with:

```bash
sanka scan .
sanka plan --to fastapi
sanka apply --root . --bench-candidate <dir>
```

The candidate is the untouched `--bench-candidate` output. Nothing was edited
after generation. Token authentication is served natively: the generated
runtime reads the retained `authtoken_token` table through a raw
quoted-identifier lookup — DRF is never imported by the serving process.
