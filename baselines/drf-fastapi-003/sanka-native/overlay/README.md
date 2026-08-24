# Generated native FastAPI application

Sanka generated this application from plan `sha256:f18fe9b6e4706c50295f732887fd407e7124efab2606d32ae971abd61057c42d`.

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
