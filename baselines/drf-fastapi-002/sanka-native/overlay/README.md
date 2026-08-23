# Generated native FastAPI application

Sanka generated this application from plan `sha256:0cb2ae5e26a1059630b7f37f4b82fafc480d6bf031715eac5c0f7f146c2e2d85`.

FastAPI owns the request layer. Django is configured through the generated
`sanka_settings` module, which removes the DRF request layer and keeps the
original models, migrations, ORM, and synchronous transactions. Validation is
a native reimplementation of the serializer semantics captured at scan time,
including the exact error strings.

Format-suffix alias routes from the source router are dropped as a disclosed
contract change; clients negotiate content types with headers instead.

Run locally from the Django repository root:

```bash
python -m pip install -r .sanka/output/fastapi/requirements.txt
uvicorn --app-dir .sanka/output/fastapi app:app --reload
```
