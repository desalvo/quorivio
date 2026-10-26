# Q&A PostgreSQL connection pool starvation — CI 40366108461

## 2026-10-26 — GitHub CI 40366108461: concurrent Q&A PostgreSQL pool-starvation fix (uncommitted)
- **Committed baseline:** GitHub commit `1d4f0e957da2a568c188279e8d8e4fa76cb6dd33`; Production quality gate FAILED during `tools/ci_audience_moderation_postgres.py:73` at `ThreadPoolExecutor(max_workers=12)`, after 25-second HTTP socket timeout. Node 442/442 and API/web compile SUCCESS; normal publication SKIPPED. Real PostgreSQL moderation acceptance not completed on this run.
- **Root cause:** the questions, words and upvote request handlers checked out one of the default 10 PostgreSQL pool connections *before* calling `audienceIdentity()`, which itself uses `db.query` to validate a session, participant and open page. Twelve concurrent requests can fill the entire pool with outer clients waiting for nested queries: connection pool starvation/deadlock. Reusing the same `urllib` opener across all threads also made the stress fixture less realistic and potentially unsafe.
- **Production fix:** defer the pool checkout until identity checks finish in all three endpoints; retain participant FOR UPDATE and session/page FOR SHARE transaction locks, per-participant 3-question cap, voting/approval restrictions, and all rate limits. Return pool clients immediately after COMMIT, *before* `notifyAudience()` triggers independent database queries; defensive optional release/rollback for pre-transaction failures.
- **CI/test fix:** twelve distinct urllib openers/cookie jars carrying copied **identical participant credentials** concurrently assert exactly 3 accepted and 9 limited. Add three Python regression contracts for identity-before-checkout, release-before-broadcast, distinct clients/same cookie. Keep this PostgreSQL integration test mandatory.
- **Local verification:** Node **442/442 PASS** (`node --experimental-strip-types --test`), **51/51 focused Python PASS** plus full focused audience suite 18/18, TypeScript syntax and Python compilation PASS. Full Python suite started but timed out in document conversion HTTP tests in this local environment; do not claim a pass. Actual PostgreSQL concurrent replay, TypeScript/Vite compilation and container build after patch remain **new GitHub CI PENDING**.
- **RC evidence:** **48.0% unchanged**, B3 partial until PostgreSQL stress and independent Chromium/cross-browser acceptance. D1 prior green baseline preserved as historical evidence; this commit's overall CI is FAILED. No commit/push/tag/release performed by assistant.

## Acceptance checklist

- [x] Never reserve a PostgreSQL connection before `audienceIdentity()` uses the shared pool.
- [x] Commit and release the connection before broadcasting a snapshot to other database users.
- [x] Preserve limits, locks, page checks, and private moderation.
- [x] Run 12 independent HTTP clients sharing one participant identity, with an exactly-three successful quota.
- [x] Local Node, focused Python, and syntax checks.
- [ ] GitHub PostgreSQL concurrency integration SUCCESS.
- [ ] GitHub build/container SUCCESS with publication SKIPPED.
- [ ] Optional Chromium participant Q&A and independent accessibility acceptance.
