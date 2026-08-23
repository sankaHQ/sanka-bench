# Sanka native converter baseline provenance

Generated from Sanka commit `f4716d1599b9bef027d5efbe38bbcadba71e50d2`
(PR #15, native-strategy default) against the `drf-fastapi-001` fixture with:

```bash
sanka scan .
sanka plan --to fastapi
sanka apply --root . --bench-candidate <dir>
```

The candidate is the untouched `--bench-candidate` output: `sanka apply`
emits the overlay (entrypoint `target_app.py`, `source_root: "."`) and
`candidate.yaml` itself. Nothing was edited after generation.
