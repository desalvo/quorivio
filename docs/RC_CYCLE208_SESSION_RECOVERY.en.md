# RC208 — Nonblank presenter dashboard and session recovery

## Regression and trigger

A presenter reported that reopening a previously active session or its dashboard could leave the application completely blank until browser cookies were deleted. The exact production exception was not available; a contemporaneous investigation of RC207 code found a real bootstrapping gap: stored workspace IDs initiated session fetch and live sockets before `/auth/me` had resolved, HTTP requests had no timeout, missing session data had no visible recovery action, and React lacked a crash boundary. QR polling was already cancellation-aware but could remain pending indefinitely on a stalled response. These are addressed without asserting that QR polling was conclusively the original cause.

## Recovery policy

- Check authentication before loading an owner's saved session or connecting a presenter WebSocket. A failed session restore does **not** erase cookies, tokens, or server data.
- Bound authentication and initial session snapshot requests to 12 seconds; give transient errors a visible UI and bounded retry. The disconnected-live HTTP fallback likewise permits only one outstanding request and aborts after 10 seconds. 401 returns to login. 403/404/410 clear only the stale tab-local route and return to session list.
- Drop mismatched/corrupt session snapshots; accept older valid snapshots with omitted optional statistics by filling the missing arrays.
- If React rendering throws, discard only stale session navigation and remount once. A persistent failure shows a recovery action rather than an empty root.
- QR ownership and URL revisions remain server-authoritative; an unresponsive QR fetch aborts after 9 seconds, then retries at the existing interval/focus/visibility triggers. Revoked access must never leave stale scannable pixels.
- Existing editor and master state on the server is untouched; automatically recover the workspace only when safely possible. Avoid storing private tokens or answer data in diagnostics.

## Validation and limits

- New executable `apps/web/test/session-load-recovery.test.ts` exercises active owner sessions, changed QR codes, missing statistics fields, invalid cross-session snapshots, and 401/403/404/410/503 outcomes.
- `tools/tests/test_rc208_session_recovery.py` validates the source and CI contracts before npm.
- `tools/ci_browser_editor.py` includes browser checks after reload for an active session, rotated code, 503 with manual retry, and expired authentication followed by restoration. This browser scenario must still be executed as part of a full compiled Chromium CI job.
- CI safety settings stay `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Version stays `0.1.0-dev`.
- No claim of independently reproducing the original user cookie/environment state or full browser certification is made until a new GitHub run is green.
