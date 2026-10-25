# Quorivio 0.1.0-dev — tenth editor batch: 30 implementation and acceptance items

**Committed baseline:** GitHub Actions 40192172978 (quality, container, publication SUCCESS). The ninth PostgreSQL concurrency batch is **not yet committed**; this tenth batch is cumulative with it. No automatic commit, push, tag or release.

## 30 substantive changes and acceptance criteria

1. Preserve the local editor's original base draft for three-way reconciliation.
2. Fetch a fresh authenticated remote session snapshot before reconciliation.
3. Keep the PostgreSQL compare-and-swap design revision as the only publishing authority.
4. Independently merge question headers.
5. Independently merge result headers.
6. Independently merge question/result background colors.
7. Independently merge question/result background URLs.
8. Independently merge question/result background asset identifiers.
9. Match widgets by stable IDs, not array indexes.
10. Recursively merge independent properties of the same widget.
11. Independently merge X/Y coordinates and dimensions.
12. Merge nested style properties without dropping disjoint changes.
13. Treat concurrently edited nested arrays atomically to prevent hybrid answer options.
14. Preserve non-conflicting local widget insertions.
15. Preserve non-conflicting remote widget insertions.
16. Preserve simultaneous insertions with different widget IDs.
17. Require explicit resolution for different concurrent insertions with the same ID.
18. Merge widget deletion when the other side has not edited that widget.
19. Require explicit resolution for delete-versus-edit races.
20. Preserve local layer reorder against unrelated remote content edits.
21. Preserve remote layer reorder against unrelated local content edits.
22. Require explicit resolution for incompatible simultaneous layer reorders.
23. Show local/remote values and field names for each conflict (240-character preview cap).
24. Offer per-conflict local or remote selection without defaulting to local.
25. Offer deliberate bulk local/remote conflict selection controls.
26. Export the full local draft to JSON, including page ID and base revision, before discarding it.
27. Recheck the server revision immediately before applying a merge; refresh if it changed.
28. Reject a stale application if the local draft changed during the asynchronous freshness check; never auto-publish.
29. Provide responsive, keyboard-focusable, 44px conflict controls and accessible labels/status.
30. Extend real PostgreSQL + Chromium opt-in acceptance to cover disjoint merges, no-auto-save, CAS, same-field conflict resolution and confirmed destructive reload.

## Verification and limitations

- **40 Node behavioral tests** cover insertions, deletions, nested properties, ordering, security and immutability; **12 Python UI/CI contract tests**.
- TypeScript API and Vite production builds and Node tests run locally.
- The real PostgreSQL/Chromium acceptance is **not locally verified** and requires `browser_test=true` in GitHub Actions.
- Reconciliation only edits a **local draft**; final publication is manual and still CAS-guarded. This is not real-time collaborative cursor/presence editing.
- The weighted RC score remains **45.5%** until fresh CI evidence and a formal gate review.
