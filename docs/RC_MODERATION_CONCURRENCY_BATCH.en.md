# Quorivio RC — Audience Moderation Complete-Path Batch (2026-10-26)

**Committed baseline:** `c44a3cb884b37ad20cc8c46203e16c24c6520412` (GitHub Actions `40359804334`: quality/build SUCCESS, publication SKIPPED). Changes listed here are post-commit only.

**Scope:** 40 individually auditable implementation, behavior and CI coverage items within the B3 moderated-audience workflow, **not 40 unrelated macrofeatures**. No commit, push, tag or release performed. Production publication stays manual opt-in.

## Inventory

1. Transaction-scoped session state check before accepting audience writes
2. Shared row lock on the published session prevents a page switch during the write
3. Shared row lock on the open activity prevents stale submissions after closure
4. Consistent session -> activity lock ordering avoids inversion against presenter transactions
5. Participant row lock serializes concurrent question submissions across replicas
6. The three-questions-per-participant/page cap is now atomic under concurrency
7. All rejected quota attempts explicitly roll back and return HTTP 429
8. Question submissions return pending moderation state and remaining allowance
9. Question submission emits live notifications only after the transaction commits
10. Word submission reports first-write versus duplicate and preserves the original word
11. Word submission cannot race a page switch or closure
12. Votes are idempotent with explicit already_voted feedback
13. Votes hold question row locks against simultaneous presenter moderation
14. Votes reject hidden/rejected questions without leaking content
15. Notifications failing after commit no longer turn successful writes into spurious 500s
16. Public approved-question reads additionally require the current activity to be open
17. Public approved-question order now uses a deterministic ID tie-breaker
18. Old presenter questions endpoint retained for compatibility
19. New presenter queue paginates deterministically in 20-row pages
20. Validated moderation status filter: pending, approved, rejected or all
21. Validated bounded 1..10000 pagination with integer-only encoding
22. Separate pending/approved/rejected counters and filtered totals
23. No-store cache protection on private moderator queue responses
24. Bulk moderation accepts only 1..20 unique UUIDs and approved/rejected states
25. Bulk moderator locks selected questions and fails atomically for foreign/missing IDs
26. Bulk moderation records updated timestamps and broadcasts after commit
27. Presenter supports reversing an approval or rejection
28. Presenter UI shows counters, status filters and accessible page navigation
29. Presenter refreshes moderation results and word cloud every six seconds
30. Presenter UI supports per-question checkboxes and approve/reject selected page
31. Participant question/word fields are cleared only after confirmed server submission
32. Participant submissions use disabled busy states, accessible feedback and duplicate notices
33. Approved audience questions refresh periodically without revealing unmoderated text
34. New Node policy tests cover query validity, malicious paging and bulk admission
35. New PostgreSQL HTTP CI fixture tests 12 simultaneous posts with exact quota enforcement
36. PostgreSQL CI fixture checks private pending/rejected content, paging and cross-session isolation
37. PostgreSQL CI fixture checks atomic bulk moderation and moderator reversibility
38. PostgreSQL CI fixture checks idempotent words/upvotes and rejection after session closure
39. Opt-in Chromium fixture tests real participant question approval/voting/revocation
40. Static Python delivery tests verify lock/CI/UI wiring and fail-closed publication policy

## Evidence and gate outcome

- **442/442 Node tests PASS**; **52/52 focused Python tests PASS**, encompassing audience, client, RC, integration and existing relevant regressions. New TypeScript/TSX parsing PASS. CI workflow YAML parsed.
- The **full Python discovery suite did not complete in this environment** (conversion/worker tests timed out), so it must not be described as PASS. The local full API/web TypeScript build is not executable due missing installed workspace dependencies/`@types`; GitHub build gate is required.
- Real PostgreSQL moderator load/IDOR/atomic-bulk acceptance and Chromium end-to-end tests are **written but not executed**; they will execute in the next GitHub Actions standard/opt-in workflows, respectively.
- B3 stays **partial** until verified in GitHub plus independent cross-browser/accessibility acceptance; weighted RC **48.0% unchanged**, 1 accepted / 15 partial / 2 open. Do not infer that code/test additions alone prove RC readiness.

## Next CI run

Push the cumulative package. Standard CI must show PostgreSQL Q&A concurrency and moderation PASS, 442 Node unit tests PASS, PostgreSQL MFA/DR/erasure PASS, container build SUCCESS and `Production publication: SKIPPED`. Then run manually with `browser_test=true`, `publish_image=false`; check the appended Chromium participant Q&A flow and existing editor tests. Do not run `rc_strict=true` until all formal RC criteria pass.
