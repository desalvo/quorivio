# PostgreSQL 18 live HTTP acceptance smoke

The CI workflow boots disposable PostgreSQL 18 and an API instance, changes the bootstrap password through `tools/ci_portable_http.py`, then runs `tools/ci_live_http.py`. CI credentials are disposable and must never be reused on a real deployment.

The smoke uses 24 independent cookie jars and concurrent submissions, checks duplicate idempotency, report privacy, closed-state rejection, and a five-second timed quiz. It uses only the Python standard library. For manual execution use an isolated disposable instance with `QUORIVIO_CI_ADMIN_EMAIL`, `QUORIVIO_CI_NEW_PASSWORD`, and optionally `QUORIVIO_CI_BASE_URL`.

**Limitations:** no cross-replica WebSocket, browser/UI, perceived timing fairness, accessibility, or 500-user load acceptance. B1–B4 must remain partial until additional runtime evidence exists.
