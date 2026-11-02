# RC137 — Presenter answer privacy and background upload error handling (2 November 2026)

**Based on RC136** (uncommitted status not confirmed) and the last confirmed full-CI-green RC135 commit `6c1118e93076c5d2eb8d60e96a43f8c663178053`, run `41437489546`. No commit, push, Docker publication or formal RC approval is performed here.

## Functional changes

- The real presenter screen keeps each authored question/quiz/text answer field **empty, disabled and non-interactive**, independently of incoming audience responses.
- A linked `results-button` on the real presenter canvas is an **explicit action**, not an auto-updating chart. Real live aggregates, per-widget results, leaderboard and moderated question collections are instantiated **only inside** the presenter results panel after its button is pressed. On activity changes the results panel closes.
- In the editable session rehearsal and side-by-side view, presenter questions never read the participant's local draft, checked options or submitted indicators. The simulator's linked results are visible only after an explicit presenter-side click, in a distinct results region. The participant pane remains interactive. No rehearsal submits to the server.
- Canvas context background uploads no longer swallow server errors behind “check the message and retry”. Rejections now show actionable HTTP/status detail (size, type, authentication, closed session or server/scanner availability); raw server HTML and secrets are never displayed. The same rejection reaches the dashboard error display for the other two upload entrypoints. A valid JPG from a browser reporting `image/jpg`, `image/pjpeg` or `application/x-jpeg` is normalized/fallback-resolved, while `text/html`-declared files remain forbidden. The server still verifies bytes and requires antivirus scanning; there is no fail-open or bypass.

## Verification and outstanding prerequisites

- `tools/tests/test_rc137_presenter_privacy_background.py` checks projection isolation, deliberate results opening, private rehearsal controls, and failure reporting.
- Frontend Node tests include MIME whitelist and safe HTTP errors. Older source-contract tests are updated only for the newly intended presenter interaction; no tests are disabled.
- The real API/Chromium background library/persistence path is already covered by `tools/ci_browser_media_picker_postgres.py` and `tools/ci_background_library_postgres.py`; rerun them via full CI after commit. Configuration failures on a real operator installation need their exact HTTP status and server scan/storage logs for further diagnosis; no unverified server-specific fix is claimed.
- **Certified completion remains 85.25% (43 accepted/17 partial)**; independent external evidence is still required. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
