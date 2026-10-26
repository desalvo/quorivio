# Quorivio 0.1.0-dev — post-commit RC erasure recovery batch

Date: 2026-10-26. **Committed baseline:** `quorivio-0.1.0-dev-rc-acceleration-retention-erasure-preflight-cumulative.zip` (maintainer confirmed commit). Baseline GitHub Actions `40322399238`: production quality `121570698068` and container build `121572390069` **SUCCESS**; publication **SKIPPED intentionally**. This batch is **not committed** and contains only subsequent changes.

## What changed (22 engineering / operational changes across 3 related areas)

### A. Per-file private attachment lifecycle
1. Atomic SQL CTE deletes the session asset metadata and queues physical erasure in the same transaction.
2. A rejected, absent, or differently scoped asset never queues a deletion job.
3. The existing widget/slide reference checks remain in place before deleting an attachment.
4. New durable, session-independent `session_asset_file_cleanup_jobs` with composite `(session_id,asset_id)` key and due-time index.
5. Multi-replica claims use PostgreSQL `FOR UPDATE SKIP LOCKED` and bounded batches of 50.
6. Claims carry a 5-minute lease and are acknowledged only by their matching lease.
7. Failed I/O returns the job to a bounded exponential retry schedule (maximum one hour).
8. The physical erase refuses noncanonical IDs and symlinked session folders, and treats missing files/folders as successful idempotent deletion.
9. Files are deleted with `unlink`, not recursive directory deletion; unrelated files are not touched.
10. A minute-cadence retry worker operates independently of the hourly session purge; a newly deleted attachment also prompts immediate best-effort draining.

### B. Profile and account lifecycle
11. Separate, durable `profile_photo_cleanup_jobs` with due-time index and no FK to a potentially deleted user.
12. Replacing/removing a profile photo atomically queues the previous file **inside the existing user row-lock transaction**, before committing the new photo URL.
13. Administrator account deletion now queues any profile photo before committing user deletion; existing self-deletion/primary administrator/dependent-data protections remain.
14. A deleted user's authenticated WebSocket connections are explicitly closed after commit.
15. Profile cleanup uses its own leased, replica-safe, bounded (50) worker with max-one-hour retry backoff.
16. Profile deletion restricts IDs to canonical UUIDs, refuses redirected symlink folders, and never deletes a newly published photo by enumerating directories.
17. A startup drain and minute-cadence worker retry outstanding profile-photo jobs. Any new profile photo is retained if its transaction fails.

### C. Operational assurance and privacy controls
18. The previous session-directory queue now receives a minute-cadence retry worker, avoiding an hour-long backlog for batches beyond 50.
19. Session-directory cleanup errors are persisted as bounded OS error codes, not full file paths; UUID path validation is strict.
20. New platform-admin-only `GET /api/admin/privacy/erasure-status` returns aggregated backlog/due/age counters, `private, no-store`, with no user IDs, image IDs or paths.
21. Mandatory PostgreSQL CI acceptance was extended with scoped metadata deletion, transactional queues, real temporary filesystem file erasure, avatar erase, due-time backoff and stale-lease reclaim; run only with disposable DB opt-in.
22. RC fail-closed preflight includes the new module and PostgreSQL acceptance tool as required release artifacts; bilateral IT/EN readiness, inventory and GDPR documentation updated.

**Regression tests authored:** 44 new Node cases across `asset-erasure.test.ts` and `profile-erasure.test.ts`, plus 10 new Python integration-source contracts. The 54 cases are independently counted tests, *not* 54 production features or CI executions. Automated unit tests exercise real private temp files, symlink targets, worker failures, retries, no-op queues, CAS acknowledgement behavior and path traversal. CI SQL/file tests were authored but **not executed on real PostgreSQL here**.

## Status and release evidence

- Full local Node: **430/430 PASS** (baseline 386/386; +44 cases).
- Full local Python: **707/707 PASS** (baseline 697/697; +10 cases).
- New TS sources and CI JavaScript: syntax accepted by Node 22 native type stripping / JS syntax check.
- **TypeScript API and Vite production builds: NOT VERIFIED locally** because the supplied archive contains no `node_modules` and the dependency installation cannot complete in this environment; the previous committed baseline's CI builds are not evidence for these edits.
- New PostgreSQL transactional/replica file deletion acceptance: **PENDING CI**; no live browser acceptance claimed.
- Weighted RC audit: **45.5%**, unchanged: no gate was promoted on the basis of local tests or authored future checks. `D1` retains accepted status for the **previous committed baseline only**. `C4` partial and `D6` open.

## Operator instructions / production limitations

Run standard GitHub CI on the user's next commit and verify the mandatory PostgreSQL retention-erasure step and container gate. Escalate to full opt-in browser/capacity CI on the next 2–3 significant batches, before RC approval, or sooner if subsequent changes touch identity/session authorization.

For an authenticated platform administrator: `GET /api/admin/privacy/erasure-status` supplies only counts. For DB-level inspection, query `session_asset_cleanup_jobs`, `session_asset_file_cleanup_jobs` and `profile_photo_cleanup_jobs` for `count(*)`, `min(queued_at)` and due timestamps; **do not dump private file paths or individual identifiers into support tickets**. A missing file counts as erased; queued failures retry. Verify shared RWX mounts are identical across replicas and deletion is not blocked by permissions. A persistent backlog needs an operator alert; no alert integration is claimed.

**Important:** these jobs erase only live private media. They do **not** erase backups, exported copies, snapshots, third-party mail/SSO data or access logs. A controller-approved retention/backup schedule and legal GDPR/AGID/security accessibility sign-off remain required; this is not GDPR certification or RC acceptance.

Suggested next focus: (1) run DB erasure and real-browser profile/attachment lifecycle CI, (2) close real-browser presenter/poll/quiz acceptance where possible, (3) independent mobile/AGID accessibility and operational backup/rootless/ARM64 sign-off. No commit/push/tag/release done.
