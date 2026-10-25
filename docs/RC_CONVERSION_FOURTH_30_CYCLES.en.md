# Fourth 30-intervention batch — PPTX validation and path safety

**Committed baseline:** Audience 20 Cycles. All four conversion batches remain uncommitted; this cumulative archive covers 120 declared checks/interventions. The following 30 entries are distinct regression scenarios, not 30 independent product features.

1. Inspect OOXML relationships with uppercase .RELS extensions.
2. Reject double-percent-encoded absolute paths.
3. Reject nested percent-encoded path traversal.
4. Reject relationship traversal beyond package root.
5. Apply root-escape protection to package-root relationships.
6. Preserve legitimate internal ../media relationships.
7. Reject empty relationship targets.
8. Reject XML-normalized control characters in targets.
9. Reject percent-encoded URI schemes.
10. Reject noncanonical /./ ZIP entry segments.
11. Reject XML-encoded carriage returns and line feeds in targets.
12. Preserve valid package-root internal relationships.
13. Verify valid font-family export.
14. Reject blank font families.
15. Bound font-family length.
16. Reject invalid Unicode surrogate font names.
17. Validate text color as full hexadecimal RGB.
18. Validate shape fill color.
19. Validate shape stroke color.
20. Allowlist supported export shape types.
21. Reject negative font sizes.
22. Reject excessively large font sizes.
23. Reject boolean widget coordinates.
24. Reject numeric coordinates supplied as strings.
25. Preserve safe default geometry when position is omitted.
26. Preflight image asset IDs before PPTX construction.
27. Reject unsupported UUID versions before image processing.
28. Reject explicitly null page designs.
29. Reject explicitly null widget lists.
30. Reject symlink ancestors of private media directories and serialize the verified in-memory image bytes without reopening the path.

**Local results:** 448/448 Python tests, 30 new; no TypeScript changes. Node and frontend/backend builds not rerun because npm dependencies are unavailable in this container. GitHub CI and container build pending. **D4 remains partial, 45.5% unchanged.** No commit/push/tag/release.
