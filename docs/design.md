# Implemented slices

## Coding-agent baselines

Frozen, fully disclosed agent candidates for every task: Claude Code run
headlessly with a fixed migration contract and the public scenarios, one
unattended attempt (infrastructure failures may be retried once, disclosed
verbatim in the candidate's provenance), same model and budget across the
alone/with-Sanka pair. Candidate schema v0.2 adds an optional ``stats`` block
(turns, wall time, reported cost) that the evaluator copies into result
provenance and the report renders beside the tally — the honest comparison
axis once capable agents pass the synthetic fixtures outright.

## drf-fastapi-006: deep writable graphs and atomic replacement

The sixth fixture extends nested writes from one child level to a graph with
two independently constrained lists: `Order -> OrderItem -> Adjustment`.

- `POST`, `PUT`, and `PATCH` all accept the three-level graph. A supplied
  `items` list is a complete replacement, including on PATCH; a PATCH that
  omits `items` updates only root fields and preserves the existing nested
  graph, including every primary key;
- item SKUs are unique per order and adjustment codes are unique per item.
  These constraints are exercised during persistence rather than reduced to
  preflight-only validation, so a duplicate at the second item or second
  adjustment proves the surrounding `transaction.atomic()` rolls back the
  changed parent, deleted old graph, and already-created siblings;
- DRF 3.18's sparse string-index format is part of the HTTP contract. A bad
  second adjustment under the second item is returned as
  `{"items":{"1":{"adjustments":{"1":{...}}}}}`, with no placeholder
  entries for valid siblings;
- candidates see 7 scenarios and the evaluator grades a 32-scenario strict
  superset. The 25 hidden scenarios cover empty/default branches, errors at
  both list depths, mid-graph uniqueness, Nth-child rollback, PUT replacement,
  PATCH preservation, PATCH replacement, and rejected partial graphs. A
  visible-only scratch probe passes all 7 public scenarios and fails 25 of the
  25 hidden scenarios;
- the DRF-free reference reproduces all 32 response and database results. The
  compatibility bridge does the same through Django and therefore fails the
  native serving-evidence gate. With `sanka-cli` 0.1.8 and `sanka-migrate`
  0.1.0a8, the native plan reports 14% readiness: one API-root route emitted,
  seven format-suffix aliases dropped, and all six order routes marked
  `SANKA_DRF_SERIALIZER_SEMANTICS_UNSUPPORTED`. The untouched candidate boots
  but matches 0/32 responses and 22/32 database states.

## drf-fastapi-005: authentication and permission matrix

The fifth fixture turns the single-scheme auth surface from 002 into a
hard-tier ordering matrix with a visible/hidden split.

- one `ModelViewSet` runs an expiring database-token authenticator before
  `SessionAuthentication`; malformed, invalid, inactive, and expired token
  branches are distinct, and a bad token must stop evaluation before an
  otherwise valid session can authenticate;
- session-backed unsafe writes retain CSRF enforcement. The oracle pins a
  valid session+CSRF create and a missing-cookie 403 independently from token
  401 responses;
- `get_permissions()` selects `AllowAny` for list, `IsAuthenticated` for
  create, `IsAdminUser` for destroy and the custom `review` action, and
  `IsAuthenticated` plus an owner object permission for ordinary detail
  routes. Staff may destroy or review somebody else's object; owners who are
  not staff may not;
- the 401/403/404 cases prove evaluation order: authentication still runs on
  an `AllowAny` list; anonymous detail access fails before lookup; an
  authenticated missing detail reaches 404; and object permission failures
  happen only after a real detail object is loaded. Every case compares exact
  response bodies plus declared `WWW-Authenticate` and `Allow` headers;
- candidates see 7 scenarios while the graded evaluator runs a 31-scenario
  strict superset. The 24 hidden cases carry the malformed/expired/inactive
  variants, token-before-session traps, CSRF failure, missing-object ordering,
  owner denial without mutation, and token/session staff-action branches. A
  scratch candidate implementing only the seven public cases passes all seven
  and fails 16 of the 24 hidden scenarios.

All response formats were captured from the source application before the
native reference was written. The DRF-free reference reads the retained token
and session tables through Django's model layer, validates session hashes and
CSRF tokens natively, and passes all 31 scenarios. The compatibility bridge
also preserves all behavior but fails recorded serving evidence. The pinned
converter reports 0% native readiness because both configured Django
middleware classes are unsupported, emits no candidate, and is recorded as
the honest empty/no-boot outcome rather than repaired.

## drf-fastapi-004: signal-driven side effects, hidden scenario split

The fourth fixture is the first hard-tier task: its observable behavior
lives partly outside the views, in Django signals, and its graded scenario
set is deliberately wider than the public one.

- `post_save(LedgerEntry, created=True)` and `post_delete` receivers —
  connected in `AppConfig.ready` — keep an API-read-only `Account.balance`
  (via `F()` expressions) and an append-only `AuditLog` in step; the audit
  table has no writing endpoint but a read-only list endpoint;
- a custom `POST /accounts/{pk}/transfer/` action locks both accounts in pk
  order inside `transaction.atomic`, validates amount and funds, and writes
  two ledger entries plus one `transfer` audit row on success; insufficient
  funds must leave all three tables untouched (proven by database parity);
- deleting an account cascades its entries and fires the receivers per
  cascaded row in Django's descending-pk deletion order — the surviving
  audit rows pin that order;
- the driver supports request chains (`setup` requests before the graded
  request, each served in a fresh guarded process against the shared
  scenario database), which also forces real persistence between serving
  processes;
- the split: `public-tests/scenarios.json` carries 5 scenarios, the graded
  `evaluation/scenarios.json` a 17-scenario superset. The 12 hidden
  scenarios cover balance read-only enforcement, multi-entry `F()`
  composition, reverse postings on delete, rollback, transfer error shapes,
  audit ordering, cascade audit, and Decimal string forms. A visible-only
  probe passes all 5 public scenarios and fails 10 of the 12 hidden ones,
  so saturating the public surface no longer saturates the task.

All response formats were captured empirically from the live source
application before the native reference was written. The reference serves
through settings that install the ledger app via a plain `AppConfig`
(source receivers never connected) and reapplies every side effect
explicitly in the same transaction as its cause. The shipped converter
(`sanka-cli` 0.1.8 / `sanka-migrate` 0.1.0a8) honestly reports 54% native
readiness — mixin-composed viewsets and custom actions are outside the
envelope — and its frozen output fails at 5/17 behavior parity, so 004
ships without a passing converter baseline.

## drf-fastapi-003: nested writes, transactions, validation edges

The third fixture covers the validation and transaction surface:

- writable nested serializers with DRF's index-keyed nested error format
  (`{"items": {"1": {"quantity": [...]}}}` — failing indices only), the
  list-type error, and combined order-level plus item-level errors;
- a transactional nested create: parent and children written inside
  `transaction.atomic`, then a business rule raises — the observable
  contract (400 plus an unchanged database) is enforced by the database
  parity gate, so a candidate that half-writes fails;
- `unique=True` model-message validation ("order with this reference already
  exists."), decimal digit/precision errors and string representation,
  choice-field errors, and cascade deletion.

All response formats were captured empirically from the live source
application before the native reference was written. Native plan readiness
for the current Sanka converter is 57% (nested serializers are outside the
envelope), so 003 ships without a converter baseline.

## drf-fastapi-002: authentication and object permissions

The second fixture (`drf-fastapi-002`) covers the auth surface:

- database-backed `TokenAuthentication` (`rest_framework.authtoken`);
- `IsAuthenticated` plus the canonical author-or-read-only object permission;
- `perform_create` author injection;
- 401 variants (missing, invalid, malformed credentials), 403 on
  foreign-object writes, and `WWW-Authenticate`/`Allow` header parity via the
  scenario-level `capture_headers` contract (drivers and the serving guard
  capture a declared header subset into the compared response).

A native candidate must reimplement token authentication without loading DRF:
the token table stays, owned by the retained Django half, and the reference
implementation reads it through an unmanaged model mirror. Baselines are
noop, the Sanka compatibility bridge generated from merged Sanka main
(behavior passes — auth included — native gate fails on evidence), and the
human native reference. The Sanka converter's native envelope does not cover
authentication yet, so 002 intentionally has no passing converter baseline.

Baselines are laid out per task: `baselines/<task-id>/<candidate>/`.

# Implemented v0.1 slice

This slice establishes the evaluator boundary before a converter or hosted API
is allowed to claim a successful DRF-to-FastAPI migration.

## Implemented

- JSON Schemas for tasks, candidates, and results.
- One pinned CRUD fixture with deterministic scenarios.
- Local and network-disabled, read-only Docker evaluation runners.
- Existing-test regression checks.
- Differential HTTP and SQLite row-state comparison.
- Runtime native-target compliance: every candidate scenario is served in a
  fresh guarded child process that arms a PEP 578 audit hook before candidate
  code loads. The hook cannot be removed once installed. It records imports of
  forbidden module prefixes (DRF and Django request-serving machinery),
  process creation, and socket connections. The guard also records whether the
  scenario was matched by a `fastapi.routing.APIRoute` whose endpoint code
  lives inside the candidate workspace. The guard observes and records rather
  than blocking, so facade candidates still demonstrate behavioral parity
  while failing the gate on evidence.
- Textual pattern checks demoted to result diagnostics over every
  candidate-contributed file (they previously gated on the entrypoint file
  only, which a helper-module facade trivially bypassed; the
  `tests/fixtures/obfuscated-bridge` control pins that bypass as caught).
- The native reference serves through DRF-free settings, proving the DRF
  request layer is genuinely absent from a native serving process while the
  retained Django test suite still exercises the source application.
- Two clean evaluation repetitions and variance detection; recorded serving
  evidence participates in the determinism fingerprint.
- No-op, Sanka PR #13 compatibility-bridge, and native human-reference
  baselines.

## Deliberate limits

- The fixture covers one model and CRUD behavior only.
- Scenarios are served through an in-process ASGI test client, not through
  independently booted server processes.
- The serving guard defends against converters that Goodhart the visible
  checks, not against deliberate audit-hook evasion; adversarial custody
  belongs to the future hidden evaluator.
- Side-effect ledgers are represented in the result contract but the first
  fixture has no Celery, email, file, signal, or webhook scenario.
- The public evaluator material is visible to candidates. A future Verified set
  must mount hidden tests only after the candidate is frozen.
- Docker build dependency resolution is pinned by `uv.lock`; the evaluation run
  itself has no network.
- No hosted execution, repository upload, leaderboard, API route, or product
  integration is included.

## Next implementation gates

1. Add transaction-rollback, nested-write, and side-effect fixtures
   (authentication and object permissions landed as `drf-fastapi-002`);
   extend the Sanka converter's native envelope to pass 002.
2. Replace public-only task execution with a private hidden-evaluator mount and
   signed result manifest.
3. Integrate the shared result schema into `sanka verify` without letting Sanka
   select or bypass evaluator assertions.
4. Design the separately reviewed `/v2/migrate/code-projects` and
   `/v2/migrate/code-migrations` API resources.
