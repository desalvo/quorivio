# RC218 — Real Chromium/PostgreSQL thumbnail rename selector reconciliation

## GitHub failure and root cause
The RC217 full campaign (GitHub Actions run `42191917542`, production job `127805753403`) failed late in **Chromium editor PostgreSQL persistence and conflict acceptance**, at `tools/ci_browser_editor_postgres.py:151`. The browser waited 12 seconds for `get_by_role('button', name='Rinomina pagina', exact=True)` after opening the page-one thumbnail menu. Since RC206, the accessible name is **`Rinomina pagina (R)`** (or **`Rinomina pagine selezionate (R)`** for a multi-selection). That exact-name mismatch caused the timeout. Earlier preflights, TypeScript and other browser checks passed; ClamAV passed; downstream acceptance was skipped due to dependency failure.

## Change
The PostgreSQL browser test now locates the **portaled** group `Azioni pagina 1` and matches only `Rinomina pagina (R)` or `Rinomina pagine selezionate (R)` with an anchored accessible-name expression, verifies a single visible match and clicks it. This deliberately excludes the unrelated canvas-background `Rinomina pagina` button. The test retains its genuine authenticated PostgreSQL readback checks: page title changed, design revision unchanged, answer options and widget coordinates preserved, plus subsequent conflict-merge/JSON-export acceptance.

Added `tools/tests/test_rc218_browser_postgres_thumbnail_rename.py` before npm to reject obsolete selectors, missing menu scoping, broken click paths, missing database assertions, or removal of the authorized thumbnail delegation. Local real Chromium accessibility-locator smoke tests cover single and multi-selection labels. Only browser acceptance tests, CI preflight, release documentation and source-inventory metadata changed; no application runtime, schema, styling, configuration or permissions were changed.

## Verification, release constraints
Focused Python contracts passed; real Chromium locator smoke passed for both labels; integrated PostgreSQL browser acceptance and full GitHub CI **must still run** on the new commit. Version `0.1.0-dev`; latest fully green campaign remains RC203 (`42110429701`). Certified readiness **85.25%** (43 accepted, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, tag or release.
