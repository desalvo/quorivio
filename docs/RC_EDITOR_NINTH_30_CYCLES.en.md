# Batch 9 — 30 substantial changes: concurrent editing and real persistence

**Confirmed baseline:** maintainer committed the previous eight batches and GitHub Actions 40192172978 passed quality, container build, and publication. The previous 240 items are excluded from the next commit message.

## Thirty traceable implementation and acceptance items

1. Separate PostgreSQL `design_revision` per activity.
2. Independent versioning from live activity revision.
3. Idempotent database migration.
4. Row-level lock before version comparison.
5. Backwards-compatible optional expected revision field.
6. Strict safe-positive-integer validation.
7. HTTP 409 for stale authoring.
8. Conflict response includes only current revision, no private page data.
9. Transaction rollback before mutating content on conflict.
10. Atomic revision increment with the layout update.
11. Return committed revision to client.
12. Include revision in normal activity snapshot.
13. Capture revision on editor open.
14. Send expected revision on each browser save.
15. Advance local revision only on successful save.
16. Accessible and actionable conflict feedback.
17. Preserve unsaved draft after a conflict.
18. Disable subsequent writes until conflict recovery.
19. Dedicated reload-from-server action.
20. Explicit confirmation before discarding local changes.
21. Restore full layout, background, widgets, headers and version.
22. Fix dirty tracking for question background color.
23. Fix dirty tracking for result background color.
24. Shared deterministic draft signature for loaded and edited content.
25. Unit regressions for every draft field and malformed versions.
26. Mandatory real PostgreSQL HTTP smoke with two authenticated cookie jars.
27. Concurrent writers acceptance: exactly one wins a shared revision.
28. HTTP checks for invalid revisions, geometry, native shape paints, independent pages and closed sessions.
29. Opt-in real Chromium + PostgreSQL UI acceptance with no intercepted routes.
30. CI integration, failure artifacts, bilingual inventory and updated RC matrix.

## Verification status

- API TypeScript and web Vite builds: local PASS.
- Node.js **244/244 PASS**; new Python source contracts **18/18 PASS**.
- Real PostgreSQL concurrency and real Chromium acceptance are **authored but not executed locally**; GitHub CI still required. The PostgreSQL smoke is mandatory; Chromium runs with `browser_test=true`.
- RC A1 remains **partial**, score unchanged **45.5%**. No commit/push/tag performed.
