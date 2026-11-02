# RC130 — Real authenticated Chromium reentry and media picker recovery

## Failure observed

GitHub Actions run `41417000544`, job `125183202409` (commit `b6e3f2e0181478682beaa9b06e2831d9b4decaa3`) fails in the real PostgreSQL JPG background and Logo acceptance after the earlier browser reload acceptance succeeds. `tools/ci_browser_media_picker_postgres.py` calls `open_editor` after uploading the Logo; the shared helper navigates back to `/` and tries to click the old dashboard `Apri sessione` action. The current editor's thumbnail correctly intercepts the pointer event. This is a test state expectation regression, not evidence that JPG or Logo persisted incorrectly.

## Repair

The existing shared browser helper checks the original disposable authenticated session and page IDs in per-tab `sessionStorage` before attempting dashboard navigation. When the workspace was restored it validates the matching session title and page through authenticated `GET /api/sessions/{sessionId}`, waits for the actual editor, checks a single active current-page thumbnail and the canvas, and returns without a fake/forced click. Unexpected restored IDs fail closed. Fresh workspace openings retain the real dashboard click and cookie dialog checks. Both PostgreSQL browser acceptance scripts pass the fixture IDs on reopened editor access.

## Evidence and limits

Five dependency-free executable Python tests cover correct restoration, mismatched session/page rejection, and both script callsites. Existing RC129/RC123 and cookie/pointer contracts remain required. Workflow preflight is fail-closed before npm; old SHA inventory stays historically preserved. One RC125 fake-Docker test subprocess timeout increases from 5 to 15 seconds to tolerate local runner load; digest/architecture/tag checks and publisher logic remain unchanged. No application code or publisher authorization changes; GitHub's real Chromium / PostgreSQL / media-persistence and full CI remain to be verified on the new commit. Certified completion remains 85.25% (43 accepted, 17 partial), strict release not accepted.

**Final local result:** Python unittest discovery: 1,674 tests run, 1,673 passed, 1 skipped, zero failures. Full browser/PostgreSQL GitHub rerun still required.
