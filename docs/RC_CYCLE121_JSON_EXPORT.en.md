# Quorivio 0.1.0-dev — RC121 — Safe page-draft JSON export (1 November 2026)

**Previous full CI:** GitHub Actions `41341765759` at commit `494416c3cc3c20db6c3da6330ba69d42df51196c` passed the React/TypeScript build, early Chromium editor acceptance, PostgreSQL audience tests, and the real editor's autosave/conflict/merge flow, then failed on `page.expect_download()` in `tools/ci_browser_editor_postgres.py`. The downloaded failure artifact reported `JS errors: ['invalid_draft_value']`; the page-thumbnail context menu remained open with no export. Downstream RC jobs were skipped.

**RC121 fix:** the export path now removes `undefined` *optional object properties* from in-memory widget models before strict validation and JSON serialization, for both the draft and its baseline. Required page fields are still validated; array holes, non-finite numbers, unsupported values, cyclic objects, duplicate widget IDs and prototype pollution remain rejected. Exports do not mutate live editor state and keep the v2 format and revision/merge invariants. A failed export leaves the menu open with an accessible error instead of a silent click. Five API Node regressions and five Python preflight contracts were added. The full PostgreSQL browser test still requires an actual downloaded JSON file and its original `format` and `base_revision` assertions.

**Certified completion:** **85.25%**, 43 accepted and 17 partial gates out of 60, unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. RC121 full GitHub CI is pending; no assistant commit, push or publication.

**Suggested commit since RC120:** `Handle optional widget props safely in page draft JSON exports and preserve strict backup validation [full-ci]`.
