# RC237 — Scoped thumbnail rename CI contract

**Baseline:** Quorivio 0.1.0-dev RC236, user-committed as `910c60216d9e18c7602a47070a5d822588f1194f`.
Full CI https://github.com/desalvo/quorivio/actions/runs/42256926397 failed in the pre-npm RC218 negative mutation guard, not in browser runtime.

## Root cause

`verify_contract()` searched for `actions=page.get_by_role(...)` as an unanchored substring. RC236 added `export_actions=page.get_by_role(...)`. After mutating the rename-group assignment, the export locator still contained the searched substring; the test mistakenly accepted a wrong rename locator, and CI correctly failed the negative test with `AssertionError not raised`.

## Fix

Require the complete `actions=page.get_by_role(...)` assignment on its own line (not a suffix inside `export_actions`). Preserve the real browser + PostgreSQL acceptance, title-only persistence assertions, and the RC236 export disclosure. Add independent RC237 regression tests and mandatory pre-npm execution. No application CSS, TypeScript, API, database, privacy, or publishing changes. No tests disabled.

## Validation

- Run `python3 -m unittest tools.tests.test_rc237_rename_scope_guard tools.tests.test_rc218_browser_postgres_thumbnail_rename tools.tests.test_rc236_page_menu_disclosures -q` without `PYTHONPATH`.
- Deliberate rename-action mutations must fail even with `export_actions` present.
- RC236 inventory is historical, RC237 the only current manifest. Verify four release headings, source hashes and final ZIP.
- Full GitHub CI including Chromium/PostgreSQL still pending after maintainer commit.

**Certified 85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag.
