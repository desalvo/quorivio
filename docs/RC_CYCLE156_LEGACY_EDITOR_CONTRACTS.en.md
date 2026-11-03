# RC156 — Full-suite legacy editor contract reconciliation

GitHub Actions run [41720825704](https://github.com/desalvo/quorivio/actions/runs/41720825704) on committed RC155 passed early preflights, 833 Node tests, frontend TypeScript/Vite build, real Chromium and PostgreSQL integration phases; in the final 1,798-test Python suite, three literal assertions failed (three failures total): `test_canvas_background_native_context`, `test_editor_page_isolation`, and `test_rc_rehearsal_unique_mount_20261028`.

The runtime remains unchanged. Updated those historical tests to assert the current behavior instead of outdated source snippets:

- Desktop vs smartphone uploads use the same background upload handler with a device flag, storage target isolation, and per-device preview binding.
- WidgetCanvas remount identity includes account/session, current page, and `canvasDevice`; smartphone widgets and mode are passed separately.
- Editor rehearsal consumes the unsaved editor widget draft, the separate mobile layout and current desktop background, rather than reusing the stale persisted session snapshot.

Added `tools/tests/test_rc156_editor_contracts.py` with positive and deliberate negative mutation cases, and moved all four suites to an early CI preflight before npm/PostgreSQL, preventing 10-minute CI runs from failing on obsolete assertions. Historical RC155 inventory is immutable and checked as `--historical`; RC156 is the sole current manifest. No application runtime changes, release publishing, commit or deployment by assistant.

**Acceptance before release:** run the full GitHub `[full-ci]` workflow and verify all browser, live-server and Kubernetes checks. The 500-user exercise requires a separate explicitly authorized deployment/command. Certified development gate score remains **85.25%** (43 accepted / 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
