# Eleventh editor batch — 30 recovery implementation/acceptance items

Baseline: committed workflow 40192172978; previous ninth and tenth editor batches are still uncommitted. This third batch makes **90 cumulative implementation/acceptance items** since that commit.

Items include functional behaviors and distinct acceptance criteria; they are **not** 30 independent major features.

1. Versioned JSON draft backup v2.
2. Embed authoritative baseline snapshot in backups.
3. Keep original session identity in backup.
4. Keep original page identity in backup.
5. Preserve design revision for optimistic concurrency.
6. Preserve all page header and background fields.
7. Preserve editable widget payloads.
8. Explicit manual export from the editor.
9. Explicit file-picker import with no automatic storage.
10. Bound import file size to 2 MB.
11. Reject malformed JSON.
12. Reject unsupported backup formats.
13. Reject session mismatches.
14. Reject page mismatches.
15. Reject invalid revision values.
16. Validate all eight page text fields.
17. Validate widget list size and unique identifiers.
18. Validate widget types before editor application.
19. Reject prototype-pollution object keys.
20. Bound JSON nesting, object sizes and node counts.
21. Reject invalid numeric and oversized text payloads.
22. Fetch latest server snapshot before recovery.
23. Refuse import when local page changes during upload.
24. Require explicit user confirmation before replacing a draft.
25. Restore same-revision drafts locally without publishing.
26. Require three-way merge for stale v2 drafts.
27. Block unsafe stale v1 backup restore.
28. Require explicit choice for conflicting imported fields.
29. Recheck server revision before applying merged recovery.
30. Extend real Chromium/PostgreSQL acceptance and regression contracts.

Evidence: Node 314/314, Python 621/621, isolated TypeScript module typecheck and TSX syntax transpilation PASS. Full frontend/backend build unavailable because npm ci did not finish in the local environment. Real Chromium/PostgreSQL recovery acceptance added to browser_test opt-in; **not run locally**. RC remains 45.5%, A1 partial.

Security/privacy: manual JSON backups contain slide layouts and asset identifiers; protect the downloaded file. No browser localStorage/sessionStorage is used and importing does not send a PATCH.

Pending: commit all three editor batches, run CI with browser_test=true, inspect PostgreSQL CAS and recovery, and perform independent browser/device accessibility acceptance.
