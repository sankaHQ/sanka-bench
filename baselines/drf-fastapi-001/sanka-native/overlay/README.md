# Generated native FastAPI application

Sanka generated this application from plan `sha256:9b90ffb455265a3369ee41f74ff5292bd695e7b251c47c75a713682e83a6b2cd`.

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
