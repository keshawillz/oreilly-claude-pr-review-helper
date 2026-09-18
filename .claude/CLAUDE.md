# Project context

A small shop backend in Python. The code under review lives in app/.

## Review and testing standards (read by CI runs)
- Tests live in tests/, one file per module, pytest style
- Fixtures: tests/fixtures/users.json, tests/fixtures/orders.json
- Test public functions. Do not test private helpers.
- critical: security hole, data loss, crash in normal use
- major: wrong result or unhandled error on a likely path
- minor: works today, harder to maintain or test
- Coverage already exists for: discount math, tax, order totals, password hashing, token expiry
