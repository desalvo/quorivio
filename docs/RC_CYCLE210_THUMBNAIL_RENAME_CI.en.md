# RC210 — Reconcile selection-aware thumbnail renaming with historical CI

## Evidence and root cause
The maintainer's RC209 full-CI run `42138018546`, production-quality job `127630992928`, fails at the early RC197 Python reconciliation step in `tools.tests.test_page_rename_preview_contract_20261027`. That historic source contract still required the literal `void renameCanvasPage(a)` in the thumbnail context menu. Since RC206, the menu intentionally invokes `void renameSelectedPages(a.id)` so Ctrl/Cmd-multiselection and the **R** keyboard shortcut use one ordered, authenticated title-only pathway; the batch delegates to `await renameCanvasPage(page)`. The single-page canvas action still invokes `renameCanvasPage` directly.

## Change
- Reconcile the stale historic assertion with the current selection-aware call path, retaining explicit checks for both menu and canvas entry points, persisted page order and local snapshot title updates.
- Add `test_rc210_thumbnail_rename_ci.py` with a negative mutation regression that fails if the selection handler stops delegating to `renameCanvasPage`.
- Run the new preflight before npm, browser or Kubernetes tests; retain the complete original RC197 preflight and all historical inventory receipts.
- Leave application runtime and data schemas unchanged; preserve `0.1.0-dev`, `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Validation and release status
The formerly failing seven-module grouped CI command now passes locally: **35 Python tests**. The new RC210 source test passes **3 tests** (8 including the historical rename module). This proves the CI contract is reconciled, not that the RC209 full release is accepted: full TypeScript, Chromium, PostgreSQL, Kubernetes and publishing acceptance remain dependent on a new maintainer-triggered GitHub run. The RC209 campaign summary failed as a downstream consequence, and other downstream gates were skipped. Last independent full green: RC203 `42110429701`. Certified completion remains **85.25%** (43 accepted, 17 partial). Do not commit, push, tag or publish automatically.
