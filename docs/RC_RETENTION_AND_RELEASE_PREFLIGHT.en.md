# RC acceleration batch — retention, erasure outbox and release preflight

Date: 2026-10-26. Baseline: maintainer-committed profile/media/admin 40-intervention package is **not** confirmed; this cumulative package includes it. Last maintainer-confirmed commit was the Chromium context-menu hotfix.

## Delivered code (not release sign-off)

1. Per-session `retention_days` is now actually used by the hourly PostgreSQL purge; changing the global setting no longer silently overrides session owners' choices.
2. New regular and portable-import sessions inherit the current administrator default; later global changes affect only future sessions.
3. Only the session owner may change retention; collaborators get HTTP 403.
4. Sessions are never purged while active and unexpired, and expiry/closure timestamps anchor retention. Legacy closed rows without `closed_at` conservatively use expiry.
5. Manual and automatic database deletion atomically enqueue asset directory cleanup in a durable PostgreSQL outbox. A failed filesystem deletion no longer permanently loses its retry intent.
6. Cleanup claims use `FOR UPDATE SKIP LOCKED` and a five-minute lease, so multiple API replicas do not concurrently process the same job; stale claims can be retried.
7. Successful filesystem deletion acknowledges only the matching lease; failed jobs remain recorded with bounded error text and retry after lease expiry.
8. CI adds a transaction-rolled-back real PostgreSQL retention/outbox test; the existing authenticated HTTP acceptance checks defaults and overrides.
9. The editor's retention control now falls back to the actual 60-day default, not the obsolete 90-day text.
10. `tools/rc_release_preflight.py` emits deterministic, human-reviewable gate blockers and returns code 2 with `--strict` until **every** gate is accepted. It does not infer compliance from passing unit tests.

## Evidence and limitations

Local checks: Node 386/386, Python 697/697 (to be rechecked after packaging), backend/frontend builds pass. PostgreSQL 18 integration and multi-replica filesystem cleanup have **not** been executed in this environment. The next GitHub CI must validate the added PostgreSQL test before any release claim.

**RC is not yet approved.** The gate matrix remains 45.5%. Production-like DR drills, ARM64/rootless Podman/Kubernetes acceptance, accessibility with independent devices and assistive technologies, real OIDC providers, independent security review, AGID/GDPR legal/operational sign-off and representative PowerPoint fidelity acceptance remain open.

## Operator runbook

- Inspect pending cleanup without revealing credentials: `SELECT session_id, queued_at, attempts, claimed_until, left(last_error,120) FROM session_asset_cleanup_jobs ORDER BY queued_at;`
- Confirm the `QUORIVIO_ASSET_DIR` is shared across API replicas and writable for deletion; filesystem cleanup is asynchronous and eventually retried.
- Verify backup retention separately: removing live PostgreSQL rows/media does **not** remove historical backup copies.
- Run `python3 tools/rc_release_preflight.py --strict` before proposing an RC tag; nonzero means blocked.
- Run GitHub Actions with `browser_test=true` and `capacity_test=true` on a disposable environment, and independently verify the remaining gates before marking them accepted.
- Do not commit, push, tag, or publish automatically.
