# Generated native FastAPI application

Sanka generated this application from plan `sha256:388d0716cb5019591711c529391edbe57648e251bbad4385b32eba78df0c6f51`.

Routes are declared with FastAPI decorators in `target_app.py` (`@app.get`,
`@app.post`, ...). Shared DRF-parity validation lives in `sanka_native.py`.
Persistence uses the retained Django ORM through the async facade in `sanka_store.py`. Generated `sanka_settings.py` removes DRF apps; Django is loaded for ORM access only, never as the request server.

Set `SANKA_DATABASE_URL` for PostgreSQL (the scan never stores a password).
SQLite uses the captured database path, overridable with `SANKA_DATABASE_URL`
or `SANKA_TEST_DB`.

`sanka test` writes `test_generated.py` here and runs it. SQLite write tests
use an isolated copy of the database.

Format-suffix alias routes from the source router are dropped as a disclosed
contract change; clients negotiate content types with headers instead.

```bash
python -m pip install -r requirements.txt
python target_app.py
```
