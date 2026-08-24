# Sanka native converter baseline provenance (drf-fastapi-003)

Generated from Sanka commit `86dea33d90b4693c4e26d0b765713353c98ef7de`
(PR #21, nested-writes envelope) against the `drf-fastapi-003` fixture with:

```bash
sanka scan .
sanka plan --to fastapi
sanka apply --root . --bench-candidate <dir>
```

The candidate is the untouched `--bench-candidate` output. The author's
`create()` — including its `transaction.atomic` boundary and the
business-rule rollback — is carried over verbatim in the generated
`sanka_user_logic.py`, with `serializers.ValidationError` swapped for the
native shim. DRF is never imported by the serving process.
