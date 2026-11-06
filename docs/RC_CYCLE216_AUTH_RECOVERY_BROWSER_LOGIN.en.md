# RC216 — Chromium expired-auth login and workspace recovery acceptance

## Observed GitHub failure
Run `42145939288` (production job `127657299986`) passed early preflights and strict TypeScript but failed in `tools/ci_browser_editor.py` at line 402. After mock `/api/auth/me` returned 401, the app correctly rendered the anonymous landing screen and the accessible presenter login (heading, email/nickname field, password, submit). The legacy browser test still queried `main.narrow`, a CSS container no longer present. ClamAV passed, full campaign failed and downstream jobs were skipped; no new Docker Hub publication occurred.

## Reconciliation
Use accessible role/name assertions for the presenter sign-in heading, both form inputs and the submit action, and assert that the protected editor is absent during logout. Preserve the browser scenario's second half: restore mock authentication, reload without wiping cookies, and require the prior session editor to become visible. No production React, CSS, API, database, or permission changes. Add early pre-install fail-closed regression `tools/tests/test_rc216_expired_auth_browser_contract.py` with negative mutations against stale selector, missing form, broken reauthentication and cookie clearing.

## Validation and release
Targeted Python regression tests pass. End-to-end compiled Chromium acceptance must be confirmed by full GitHub RC216 CI. Historical source inventories preserved, version `0.1.0-dev`, certified **85.25%** (43 accepted / 17 partial gates), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag.
