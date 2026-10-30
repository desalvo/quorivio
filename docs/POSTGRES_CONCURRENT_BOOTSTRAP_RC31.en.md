# RC cycle 31 — PostgreSQL 18 concurrent API startup

## Closed code-level gap
Before cycle 31, each Quorivio API replica independently replayed `schema.sql` and tested for an empty `users` table before creating an initial administrator. Two pods becoming ready together could race on non-idempotent schema upgrades, first-admin uniqueness, and a partially inserted organization/user if tutorial provisioning failed.

The actual application startup now holds a **session-scoped PostgreSQL advisory lock** on a *dedicated* pool connection while executing schema upgrades and first-account provisioning. All queries within the critical phase use the same connection. The initial organization, admin, and tutorial session/activities are created in **one SQL transaction**; failure rolls everything back. The lock has a **120-second acquisition timeout** (followers fail/restart instead of waiting indefinitely), is always released, and the connection is destroyed if unlock status is uncertain. The server starts listening only after the guarded phase completes. Runtime requests, websocket subscription, and periodic workers are outside this lock.

## CI evidence (pending maintainer commit)
The standard production quality job now creates an **entirely separate disposable PostgreSQL 18 database** (`quorivio_bootstrap_ci`), simultaneously starts two real compiled API processes on different local ports, waits for both readiness endpoints, and verifies precisely one admin, one organization and one user. The database and processes are removed even after a failure. Secrets, session identifiers and raw runtime logs are not published. Both existing single-replica integration and later two-replica WebSocket tests remain mandatory.

Local evidence: Node unit tests for lock acquisition/failure/uncertain unlock/concurrent critical-section entry, Python CI source contracts and whole available suites. The actual two-process PostgreSQL acceptance **has not been run locally**; it must PASS in fresh GitHub Actions on the next commit. This cycle does **not** change the 79.25% formal RC score; 17 partial independent/operator gates remain. The opt-in multi-worker NGINX CI introduced in cycle 29 also remains pending the maintainer's commit. No Kubernetes/HAProxy/CSI RWX production assertions are implied.

## Operator cautions
- On a heavily loaded database, the 120s advisory-lock wait can fail startup; Kubernetes will restart the follower. Inspect database migrations and deployment sequencing, **never** disable the lock to bypass the failure.
- Use an independently managed PostgreSQL HA service for actual database availability: serializing schema upgrades is **not** a PostgreSQL failover mechanism.
- Run the existing strict RC gate only after all residual manual, real-device, storage, accessibility and legal reviews have passed.
