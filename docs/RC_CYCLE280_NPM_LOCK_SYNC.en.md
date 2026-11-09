# RC280 — Deterministic npm lockfile repair

The GitHub CI #42605580476 stopped at `npm ci`: `apps/api/package.json` required `ldapts@^9.2.0`, while the workspace lockfile omitted both `ldapts@9.2.0` and `strict-event-emitter-types@2.0.0`.

Both registry packages are now represented in the v2 `packages` and `dependencies` lockfile sections, with cross-checked SHA-512 subresource integrity and the API workspace requirement. Keep `npm ci`, not `npm install`, so CI does not mutate source-integrity evidence.

The `tools/tests/test_rc280_npm_lock.py` gate checks direct/transitive versions, workspace synchronization, SRI, and pre-install test ordering in both affected CI jobs. Historical RC279 receipts remain immutable.

Local verification covers static metadata, `npm ci --dry-run --offline` without EUSAGE, and Python tests. The actual dependency download, full API/web build and real manual screenshots still require the next full GitHub CI.
