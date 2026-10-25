## 2026-10-25 — Chromium full-gate cookie notice layering hotfix
- Maintainer confirmed standard GitHub run 40213703957: quality, container and publication jobs SUCCESS. Full opt-in run 40214402565 failed only at Chromium's functional cookie notice acknowledgement: Playwright located the enabled button, but the dashboard `.welcome` subtree intercepted its pointer events.
- Render the existing accessible cookie notice through React `createPortal(..., document.body)` so its fixed, high-z-index layer is outside the editor/dashboard stacking context. Preserve real pointer-based acceptance (no `force=True`, injected cookies or increased timeout), functional cookie semantics and existing user action.
- Three focused regressions cover portal placement, accessible real-user acknowledgement and single portal usage. Full Chromium, PostgreSQL integration and RC gate acceptance remain pending the next `browser_test=true` CI; weighted RC score remains 45.5%.

## 2026-10-25 — Chromium cookie notice acceptance hotfix (uncommitted)
- Workflow 40212671162 quality gate failed at `tools/ci_browser_editor.py:125`: Playwright found the enabled `Salva layout` button but the real fixed `Informativa cookie funzionali` dialog intercepted pointer events; retry timed out after 10 seconds. The Vite WebSocket `ECONNREFUSED` lines are separate non-fatal proxy warnings, not the click timeout cause.
- Both mocked editor Chromium and real PostgreSQL editor Chromium tests now explicitly acknowledge the functional-cookie notice via its accessible `Ho capito` button after the UI is ready; the mock test also covers its independent mobile context and verifies the banner remains dismissed after reload. No forced click, cookie pre-seeding or production behavior change. Added four Python regression contracts. Local full Python 627/627 and Node 314/314 PASS. Local npm build unavailable due to incomplete preexisting @types installation; previous GitHub CI had compiled frontend successfully. Real Chromium must rerun in CI. RC 45.5%, A1 partial.

## 2026-10-25 — CI integration hotfix after workflow 40212436677 (uncommitted)
- Production quality gate passed Node tests and frontend build, then failed at `tools/ci_editor_postgres.py:67`: creating a `slide` via `/api/sessions/:id/activities` returns HTTP 400 `invalid_activity` because that endpoint accepts poll/quiz/timed_quiz.
- Fixed the mandatory PostgreSQL smoke to create the independent canvas slide via the supported `/api/sessions/:id/pages` endpoint. Added a regression contract to guard the route. Local: 623/623 Python and 314/314 Node PASS; npm build blocked by missing local @types dependencies, while the preceding CI already passed frontend compilation. The test's per-page revision assertions and concurrent-writer checks remain unchanged. PostgreSQL and Chromium acceptance must rerun in CI. Container build/publication were skipped due to the quality gate failure. RC 45.5%, A1 partial. This hotfix is the only new change since the user-confirmed commit of the 90 editor items and the previous JSX hotfix.

## 2026-10-25 — Eleventh editor batch: 30 manual JSON recovery implementation/acceptance items (uncommitted)
- Third uncommitted editor batch since committed workflow 40192172978: **90 cumulative items**. Added v2 user-initiated JSON backup with base snapshot, validated import, same-revision local restoration, stale-backup three-way conflict recovery, safe v1 legacy handling, explicit confirmation and server freshness checks. No automatic storage or publishing.
- Node **314/314**, Python **621/621** PASS; isolated TS module typecheck and TSX syntax check PASS. Full API/web build not rerun because local npm dependencies unavailable; PostgreSQL/Chromium browser_test acceptance extended but not yet run. RC 45.5%, A1 partial. See `docs/RC_EDITOR_ELEVENTH_30_CYCLES.en.md` / `.it.md`. No commit/push.

## 2026-10-25 — Tenth editor batch, 30 three-way conflict-reconciliation interventions (uncommitted)
- Ninth PostgreSQL CAS/concurrent-editor batch remains uncommitted since green committed baseline workflow 40192172978; tenth batch is cumulative (**60 new implementation/acceptance items since that commit**). Added lossless, conservative three-way page-draft merge for independent fields, per-widget nested properties, insertions/deletions and layer ordering, with explicit choices for same-field, delete/edit, same-ID and incompatible reorder conflicts.
- Browser recovery UI now previews local/remote values, supports per-conflict and bulk choices, JSON draft export, refreshes server revision immediately before applying, detects mid-request local edits, and **never auto-publishes**. Existing PostgreSQL CAS remains authoritative; opt-in real PostgreSQL+Chromium test extended. Full inventory `docs/RC_EDITOR_TENTH_30_CYCLES.en.md` / `.it.md`.
- Local Node unit suite and API/web build PASS; 40 new merge unit tests and 12 Python source contracts PASS. Full Python suite stalled in local converter HTTP tests; real PostgreSQL and Chromium acceptance still pending CI. Weighted RC **45.5%**, A1 partial; no commit/push/tag/release.

## 2026-10-25 — Ninth batch, 30 substantial editor concurrency/persistence interventions (uncommitted)
- Maintainer confirmed **commit and all three GitHub CI jobs SUCCESS** for preceding eight conversion batches: workflow 40192172978, jobs 121165302477 (quality), 121165774432 (container), 121166223063 (publication). This is the **new committed baseline**; the 240 previous interventions/scenarios must NOT appear in the next commit summary.
- New batch: PostgreSQL `design_revision` CAS with row lock and atomic increment, 409 stale-write rejection, browser conflict notice/draft preservation/explicit recovery, corrected dirty-state signatures for both slide background colors, mandatory real PostgreSQL concurrent-writer smoke and opt-in Chromium acceptance against real production frontend/API (no mocks). Detailed 30-item inventory in `docs/RC_EDITOR_NINTH_30_CYCLES.en.md` and `.it.md`.
- Local: **244/244 Node**, API/frontend production builds PASS, 18 new Python source contracts PASS. Full Python suite and PostgreSQL/Chromium acceptance pending; CI not yet run for this new batch. A1 partial, RC score **45.5%**. No commit/push/tag/release.

## 2026-10-25 — Eighth uncommitted 30-case conversion batch: editable native PowerPoint shape paints
- Added native editable shape outline widths (0.25–12 pt), solid/dashed/dotted patterns, no-fill and no-outline across import/export, canvas inspector, projection, rehearsal and thumbnails. API/export input validation rejects malformed shape paint. 12 real LibreOffice+Poppler visual roundtrip comparisons, 18 native behavior/validation cases, 7 Node and 5 UI contract regressions.
- New 30-case suite PASS; **232/232 Node PASS; API/web production builds PASS**. **583/583 Python PASS**; GitHub CI pending. All eight conversion batches (240 acceptance/intervention items) remain **uncommitted** since green Audience 20 Cycles workflow 40144692900. Weighted RC **45.5%**, A3/D4 partial; not a release candidate. See `docs/RC_CONVERSION_EIGHTH_30_CYCLES.en.md`. No commit/push.

## 2026-10-25 — Sixth uncommitted 30-case conversion batch: real LibreOffice+Poppler 12-slide native PPTX→portable→PPTX raster comparisons, whitespace/Unicode import fixes, presenter typography and non-duplicated text, honest fidelity flags for mixed runs/theme colors/gradients/crops. Local Python 512/512, Node 221/221, API/web build PASS; CI pending. Conversion batches 1–6 (180 cases) uncommitted since green Audience 20 Cycles 40144692900; weighted RC remains 45.5%, not RC. See `docs/RC_CONVERSION_SIXTH_30_CYCLES.en.md`. No commit/push.

## 2026-10-25 — Audience journey, 20 substantial interventions (after green CI 40143475939)
- User confirmed commit of `editor-20-cycle-rc-evidence` and green quality/container jobs `121019855513`/`121020208222`. This is the new baseline; no changes from that commit are included in the suggested new commit message.
- Delivered a cohesive 20-intervention participant workflow: robust code/QR join, HttpOnly cookie participation recovery with boolean-only no-store API, loading/unavailable/retry states, join/vote concurrency guards, accessible choices and feedback, keyboard skip link, responsive mobile widget reflow, bounded WebSocket reconnection and server-authoritative result privacy.
- New opt-in Chromium test runs against the built frontend served by a disposable PostgreSQL-backed API (not a Vite mock): two isolated participants, QR and typed code, real votes, reload/idempotency, admin-report privacy, mobile, session closure and failure artifacts. Extended existing PostgreSQL HTTP smoke and Node/Python regression contracts. See `docs/RC_AUDIENCE_20_CYCLES.en.md` and `.it.md` for the 20-item inventory.
- Local validation: **215/215 Node, 282/282 Python, backend/frontend builds PASS**. Browser launch succeeds locally, but localhost navigation is blocked by `net::ERR_BLOCKED_BY_ADMINISTRATOR`; new browser acceptance is **not yet verified in CI**. Existing 500-user PASS remains from 40141894130.
- Weighted RC gate remains **45.5/100**; A1/B4 partial, A4 open. Not a release candidate. No remote commit/push/tag/release.

## 2026-10-25 — 20-intervention editor completion batch, CI evidence reconciled
- Baseline: maintainer committed the Chromium selection-state hotfix; GitHub Actions run `40141894130`, quality job `121015403855` and container build SUCCESS. Chromium PASS, 500 independent participants PASS (presenter peak >=475, zero errors), PostgreSQL two-replica WebSocket PASS, PostgreSQL 18 DR PASS. Production publication SKIPPED as intended.
- One 20-intervention cumulative batch: selected-ID sanitation, group deletion/duplication/ID collision checks, bounded group nudging and keyboard group movement/deletion, four stable group layer commands, horizontal/vertical equal-gap distribution and canvas centering, cascading group paste, expanded Chromium E2E (layer operations, keyboard, mocked PATCH/reload, 390px touch viewport), new unit/source-contract tests and bilingual status/RC reconciliation. Full inventory: `docs/RC_EDITOR_20_CYCLES.en.md` / `.it.md`.
- Local: **205/205 Node tests, 277/277 Python tests, backend/frontend TypeScript/Vite builds PASS**. New Chromium script compiles but browser navigation is blocked by local administrator policy; **expanded browser acceptance is NOT YET VERIFIED in CI**. Browser PATCH fixture is not PostgreSQL persistence; no new 500-user load run locally.
- Weighted RC gate score **45.5/100** (43.0 -> 45.5), solely because D4 becomes partial with actual 500-user and security scan evidence. A1/A4/B4/D2 remain partial/open as recorded in `docs/RC_GATE_MATRIX.json`; NOT a release candidate. No remote commit/push/release performed.

## 2026-10-25 — Chromium acceptance selection-state fix after workflow 40141207000
- The opt-in Chromium CI progressed through editor navigation, multi-selection, alignment, undo/redo, group paste and undo, but failed on a disabled `Deseleziona` button (`tools/ci_browser_editor.py:60`): the pasted widget IDs were correctly removed by undo and selection became empty; the test incorrectly attempted to click a disabled control.
- The browser script now asserts the orphaned selection is cleared and the button disabled, reselects two existing widgets using the accessible checkbox list, then checks enabled clear-selection, zero selection, and unchecked boxes. Default locator timeout is reduced to 10s; failures capture a disposable fixture screenshot, HTML and URL/JS-error diagnostics. GitHub Actions uploads the diagnostic artifact only when Chromium acceptance fails.
- CI standard was reported green by maintainer for `editor-group-operations-browser-gate` baseline; this subsequent Chromium run failed and its 500-participant test was not reached. Chromium acceptance must be rerun; browser cannot navigate to localhost in the current development environment (`ERR_BLOCKED_BY_ADMINISTRATOR`). RC weighted score remains **43.0%**; A1/B4 are not accepted. No production code behavior was changed.

## 2026-10-25 — Group editing and opt-in Chromium acceptance (after last confirmed CI-green baseline)
- Added page-local multi-widget drag with shared clamped translation (relative spacing retained), group copy/cut/paste with fresh widget IDs and deep copies, preservation of existing multi-selection on pointer-down, group gesture cancellation rollback and single undo/redo history entry per drag.
- Added eight Node regressions for group bounds, copy identity, immutability and malformed geometry; adjusted three Python source contracts to verify restoration of the *whole group* after pointer cancellation.
- Added opt-in `browser_test` GitHub Actions workflow-dispatch path for Chromium editor UI acceptance. It installs Playwright Chromium and starts a disposable Vite server. The browser script now covers group paste/undo. **Not yet executed in CI.** Local Chromium navigation was blocked by this environment's administrator policy; browser acceptance remains open.
- Local verification: **179/179 Node tests, 272/272 Python tests, backend TypeScript build and frontend TypeScript/Vite build PASS**. No PostgreSQL or actual 500-participant load test was executed in this cycle.
- This package is cumulative after the last confirmed commit `quorivio-0.1.0-dev-ci-pg18-client-hotfix-cumulative.zip`; DR preflight, PPTX security/fidelity, editor history/clipboard and multiselect/arrange are included. RC gate score remains **43.0%**; A1/A3/A4 and B4 are not accepted.

## 2026-10-24 — Editable PowerPoint import/export security and fidelity consolidation (post DR preflight)
- One consolidated cycle of **11 PowerPoint regression scenarios**: require real OOXML presentation part; reject oversized/high-ratio ZIP members, ZIP symlinks, external OOXML relationships and embedded scripts; enforce nonzero widget geometry; validate image UUIDs, private media directory and PNG/JPEG bytes on export; prevent duplicated text when UI labels are truncated; flag text over 500 characters as lossy in fidelity reporting.
- Python tests **272/272 PASS** (261 baseline + 11 new), Node **154/154 PASS**, API TypeScript and web Vite builds **PASS**. No PostgreSQL, browser, or real PPTX corpus acceptance was performed in this cycle.
- The previous DR preflight changes remain cumulative. Latest user-confirmed CI green baseline is `quorivio-0.1.0-dev-ci-pg18-client-hotfix-cumulative.zip`; the newer DR preflight package has not been confirmed committed. **43.0% RC gate score remains unchanged**; no unverified acceptance gate was promoted. Full editable OOXML fidelity and browser acceptance remain open.

## 2026-10-24 — Live widget identity and result-data guardrails
- Reject duplicate or missing widget IDs before comparing an open timed quiz definition: a Map previously silently overwrote duplicate IDs, creating ambiguous answer attribution in live edits.
- Word-cloud result projection now drops blank and oversized labels, rather than returning malformed historical data.
- Verification: API and web production builds PASS, 154/154 Node PASS, 252/252 Python PASS (plus 10 subtests). Two additional Node regression tests added.
- No live PostgreSQL/browser/500-participant run. B1–B4 remain partial, RC weighted score 40.0%; NOT a release candidate.

## 2026-10-24 — Shared PostgreSQL timed-quiz deadline policy (post live delivery)
- Legacy timed-quiz responses and independent timed widgets now use the same PostgreSQL `clock_timestamp()` deadline calculation. Previously the legacy route used API host `Date.now()` and could diverge across replicas, with inaccurate leaderboard elapsed times. The shared helper rejects missing/future start times and invalid durations and includes the exact deadline millisecond.
- Tests: 146/146 Node PASS; full backend TypeScript and frontend TypeScript/Vite production build PASS. Python suite PASS after updating source-contract checks for the refactor.
- PostgreSQL HTTP, browser, multi-replica, and 500-client E2E remain unexecuted. B2 remains partial and RC remains 40.0%; no new gate accepted.

## 2026-10-24 — Portable archive defensive validation follow-up (after RC load audit)
- Strict canonical UUID-shape validation now rejects malformed asset identifiers both on manifest export/import and during fresh-ID remapping.
- Manifest is limited to 2 MiB **before compression on export** and before ZIP deflate inflation on import; this prevents a disproportionate allocation from a forged central directory uncompressed-length field. Existing ZIP archive and total-media quotas remain unchanged.
- Added three Node.js regressions: malformed asset UUID, oversized manifest during encode, and forged ZIP central-directory manifest length.
- Verification: 129/129 Node.js tests PASS, 232/232 Python tests PASS. Backend TypeScript compilation PASS; frontend TypeScript checking PASS. The full Vite bundling in this cycle is BLOCKED by mismatched esbuild binary versions/platform in the reused npm dependency archive (nested esbuild JS 0.25.12, root available native binary 0.28.2); this is an environment blocker, not a verified product build failure. Earlier CI-green baseline is not invalidated by this local issue.
- No real PostgreSQL, SMTP/SSO, browser/mobile, 500-client load or Kubernetes tests were run. RC gate statuses and weighted progress remain 40.0%. The product is NOT release-candidate complete.

## 2026-10-24 — 500-user shard validation follow-up (after previous local cycle)
- Offline 500-user load report reconciliation added with eight tests and strict topology/concurrency checks. No live load performed; D4 remains open.
- Local verification: backend/frontend build PASS (Vite esbuild 0.25.12 platform binary), Node 126/126 PASS, Python 232/232 PASS. RC score unchanged at 40.0%; PostgreSQL, actual load, browser and cluster tests not performed.

## 2026-10-24 — Integrated portability, verified email MFA and administration cycle (post-confirmed CI baseline)
- Fresh UUID and media cloning for portable imports and session duplication; revalidation/AV and rollback; email MFA verified enrollment independent of TOTP; atomic admin settings and profile photo locking/cleanup.
- Local API/frontend builds PASS; 126 Node tests PASS; 224 Python tests PASS. Added PostgreSQL HTTP CI smoke (NOT yet executed), and regenerated six bilingual role PDF manuals.
- RC 40.0% weighted (C2 partial, not accepted), all external/browser/cluster gates still pending; **not RC**. Details: `docs/RC_CYCLE_2026-10-24.en.md` and `docs/RC_GATE_MATRIX.json`.

## 2026-10-24 — CI repair after confirmed commit (local verification)
- GitHub Actions log `logs_108675600015.zip` failed exclusively at `apps/web/src/main.tsx:394` with TS2657 (adjacent JSX buttons without a parent element). Wrapped them in a React fragment; no feature or API changes.
- Using user-provided complete Node 22 dependencies: `npm run build` PASS (API TypeScript and web TypeScript/Vite); `npm test` PASS (121 tests); Python tools unittest PASS (224 tests).
- CI PostgreSQL/integration, Kubernetes, browser, deployment and security gates have **not** been executed for this revision. RC weighted gate remains 37.5%; this package is **not** a release candidate.
- The user confirmed a commit of the previous cumulative, so this package commit scope is strictly the post-commit JSX CI fix and verification notes.

## 2026-10-24 — Unified macroarea pass: editable PPTX table-cell recovery (local)
- Native PPTX table contents now import as individually editable text widgets with proportional cell geometry instead of being silently discarded. The same 16-widget page limit applies to all shapes, including table cells.
- Fidelity diagnostics now distinguish imported table cells from dropped overflow cells, and ALWAYS flag original native table semantics as lossy (table borders, styles, merged cells and OOXML structure are not preserved).
- Regression tests cover a normal 2x3 table and a 5x4 table exceeding capacity. Local execution: **220/220 Python unittest and 120/120 API Node tests pass**.
- Full TypeScript/Vite build ATTEMPTED on this revision, blocked by missing local `@types/node` and other dependency typings; no claim of clean build or complete integration. Earlier user-confirmed GitHub CI does not certify this cumulative revision.
- **UNFINISHED SOFTWARE:** editable grouped shapes, native charts/SmartArt, full OOXML fidelity, MFA/SSO end-to-end, live/browser integration, cross-instance portable import and clean build evidence. RC gate remains 37.5% pending verified gate closure. This package is NOT a final RC.

## 2026-10-24 — Native PPTX media verification and fidelity audit consistency (local)
- Native PPTX import now checks actual PNG/JPEG file signature as well as OOXML content type and size, preventing mislabelled media from being registered as editable images.
- The fidelity report now follows the importer's actual shape iteration order, 16-widgets-per-page limit, 200-media ceiling, unique-asset byte budget and media deduplication behavior; unsupported entries contribute to the lossy flag.
- Regression coverage checks signature mismatch and 18-text-box conversion/report agreement. Local verification: Python unittest 218 passed; Node 116 passed. Earlier GitHub CI was confirmed green by the user, but this new revision has not been built in full or deployed.
- **NOT COMPLETE:** this cycle does not implement PPTX groups/charts/SmartArt/complex themes, finalize MFA enrollment, or certify responsive browser rendering. RC weighted status remains 37.5%; no new acceptance gates were closed.

## 2026-10-24 — Accessibility and fidelity-copy consolidation (local verification)
- Improved keyboard focus, reduced-motion/forced-colors support, mobile touch targets and corrected PPTX import guidance. Python 216/216, Node 116/116. Full build/browser/Kubernetes remain unverified; RC remains 37.5%. See docs/LOCAL_COMPLETION_AUDIT.md.

## 2026-10-24 — Mobile canvas pointer semantics (local verification)
- Fixed a CSS cascade regression: the mobile layout applied `touch-action: manipulation` to editable canvas widgets, allowing browser gestures to interrupt pointer-captured drag, resize and rotation. An editor-scoped mobile override now restores `touch-action: none` without changing audience form controls.
- Removed a competing `min-height: 420px`/internal overflow from the mobile editor canvas (the 16:9 artboard and outer scroll container remain authoritative).
- Regression: 213 Python tests and 116 Node tests passed. Full production frontend build, actual touch devices and Kubernetes E2E remain unverified. Weighted RC stays 37.5%.
- Open: full editor/mobile browser acceptance, extended PPTX OOXML fidelity, MFA polish, widget live E2E, build reproducibility and security audit.

## 2026-10-24 — Editor page isolation (local verification)
- WidgetCanvas is now keyed to session and selected page, preventing canvas selection, editing mode and context menus from leaking across page changes. Orphan references are cleared when widgets are removed externally.
- Tests: 211 Python unittest tests and 116 Node.js tests passed. Browser and full production build not certified; RC remains 37.5%.

## 2026-10-24 — Editor keyboard accessibility and deletion safety
- Added Delete/Backspace on focused widget and Escape to clear selection; protected nested form controls from keyboard interception. Removed widget clears inspector and context menu.
- Local suites: 207/207 Python unittest, 116/116 Node.js. Browser/TypeScript build and Kubernetes E2E not validated; weighted RC stays 37.5%. Other feature areas remain open.

## 2026-10-24 — Independent widget duplication and quiz answer inspector fix
- Widget duplication deep-clones nested option arrays and position, selects the new copy and prevents negative position for widgets at canvas edges.
- Quiz inspector honors the legacy correctOptionId when correctOptionIds is empty, consistently with backend scoring semantics.
- Three targeted regression checks added. Full TypeScript/Vite and browser/Kubernetes validation not claimed; weighted RC remains 37.5%.

## 2026-10-24 — Canvas selection and activity inspector persistence
- Fixed selection being cleared on pointer release, which made the question/timed-quiz property inspector disappear during normal editing. Widget selection now persists after pointerup, supports keyboard focus and click, and clears when the selected widget is deleted.
- Local checks: 198/198 Python, 116/116 Node.js. Production build/browser and Kubernetes acceptance remain pending; weighted RC stays 37.5%.

## 2026-10-24 — Mobile authoring geometry stabilization (local verification)
- Removed the <480px CSS reflow that overwrote all widget positions, sizes and rotations inside the editor, despite the pointer engine using absolute canvas coordinates.
- The mobile editor now uses a horizontally scrollable 16:9 artboard (minimum 600px) while keeping persisted geometry intact. The separate participant-facing view may still reflow.
- Added two mobile-geometry regressions: **195/195 Python** and **116/116 Node.js** tests pass locally.
- Attempted offline `npm install --ignore-scripts`: **blocked** by uncached `@types/bcryptjs`; no clean TypeScript/Vite build or browser validation is claimed.
- **Still open**: full mobile/device accessibility testing, PowerPoint complex-object fidelity, widget live E2E, full MFA acceptance, dependency lockfile, and Kubernetes performance/security acceptance. RC matrix remains 37.5%; software completion cannot be claimed.

## 2026-10-24 — Async editor save consistency (local verification)
- Guarded the editor against overlapping asynchronous saves and navigation while a save is pending.
- The saved baseline is now the exact draft submitted to the API, not a later in-memory edit. Subsequent edits remain marked unsaved even if an older request finishes later.
- Added Ctrl/Cmd+S inside the editor, with browser default suppressed only when editor is active; Save button is disabled during pending requests.
- Regression: Python unittest 190/190, Node.js 113/113. Full TypeScript/Vite build and real browser/Kubernetes acceptance not performed. RC matrix unchanged (37.5%).
- **Still open:** complete PowerPoint complex-object fidelity, asset-inclusive session portability, mobile E2E, integration acceptance, reproducible clean npm dependency installation, real 500-user benchmark. No claim of release-candidate completeness.

## 2026-10-23 — Page editor selection and closed-session UX hardening
- After duplication the editor selects the new page using snapshot identity comparison; keyboard navigation on page thumbnails supports arrows/Home/End; destructive/editor page controls are disabled for closed sessions.
- Added 3 targeted regression tests. Browser/full production build and Kubernetes acceptance are pending. RC remains 37.5%.

## 2026-10-23 — Dedicated full-page session editor and page lifecycle repair
- Fixed blank page creation: SQL statement had five parameter placeholders but the code supplied four values, causing `internal_error`.
- Added authorized transactional DELETE endpoint for pages, resetting the currently published page when needed, compacting positions safely, notifying connected clients. **Deletion is destructive and removes associated responses**.
- Added a fullscreen-style editor workspace, vertical page thumbnails with drag-and-drop and keyboard/button reordering, page creation, duplication and deletion, and a horizontal widget toolbar; main “Edit pages” now opens this workspace.
- Regression checks: 177 Python tests passed; 113 Node tests passed in this cycle. Production frontend compilation and browser/Kubernetes acceptance have not been rerun. RC gate remains 37.5%.

## 2026-10-23 — Native PPTX decorative shape round-trip
- Empty rectangle, rounded rectangle, ellipse and isosceles triangle auto-shapes now import as editable `postit` widgets even without text, retaining supported RGB fills and outlines, geometry and rotation. Export reconstructs native PowerPoint shapes. The fidelity report counts decorative shapes separately.
- Verified locally with Python unittest 174/174 and Node.js 113/113; browser and Kubernetes acceptance not performed. Unsupported vector shapes, charts and themes remain open. Weighted RC unchanged at 37.5%.


## CI hotfix — 2026-10-23

GitHub Actions run 108461560295: backend/frontend compiled successfully; Python integration suite failed because the CI dependency setup installed reportlab but omitted python-pptx and aiohttp (16 import errors, 3 load-test CLI failures). CI now installs and imports both dependencies before tests; the load tool validates CLI arguments before importing aiohttp. Local Python suite: 171/171 passed. Real rerun of GitHub Actions remains pending; RC gate 37.5% unchanged.

## 2026-10-23 — Native PowerPoint rectangular shape round-trip (local tests)
- Imported PowerPoint rectangle/rounded-rectangle auto-shapes with text are mapped to editable Quorivio `postit` widgets instead of generic text widgets. Standard text boxes remain `text`.
- Export of `postit` widgets now creates a native editable PPTX rectangle rather than a text box. Text, position, text style and rotation follow the existing converter path.
- Fidelity limitation: PowerPoint fills, outlines, original corner radius, grouped shapes and unlabelled vector shapes are **not** preserved. Rounded rectangles export as standard rectangles. This is a partial native shape authoring step, not full vector fidelity.
- Local verification: Python unittest **171/171**, Node.js **113/113**, including a new native auto-shape round-trip regression. Full TypeScript/Vite build and browser/Kubernetes acceptance not validated. Weighted RC stays **37.5%**.

## 2026-10-23 — PPTX image export round-trip (local validation only)
- Completed image/logo PPTX export from the browser worker: the authenticated API stages only session-owned, explicitly referenced PNG/JPEG assets, enforcing 200 files, 10 MiB/file, 50 MiB total, matching DB byte size and SHA-256 before passing them to the private conversion workspace.
- The isolated Python converter restores editable picture geometry and rotation into PPTX; missing/private media is rejected rather than silently omitted. Existing text, quiz and question static-export behavior is preserved.
- Local checks: Python unittest 165/165, Node tests 112/112. Full TypeScript/Vite build, browser execution and actual PostgreSQL/Kubernetes E2E are NOT verified; RC remains 37.5%. Unsupported vector formats, charts, SmartArt, themes and animations remain open.

## 2026-10-23 — PPTX embedded pictures as session image widgets (local validation)
- Editable PPTX browser imports now extract supported embedded PNG/JPEG pictures in the isolated worker as separate widget images, with original editable geometry and rotation. Media is placed in conversion scratch space, never exposed through portable JSON as binary data.
- During new-session creation the API checks declared asset IDs, MIME types, per-file and aggregate size bounds, count, SHA-256 and widget references; stores files under the new session and registers corresponding session_assets in the same PostgreSQL transaction. Failed imports roll back the database and remove the new session directory.
- The worker limit is 200 imported images / 50 MiB in total, each image <=10 MiB. Unsupported formats, images beyond the supported widget cap, grouped graphics, SmartArt and PPTX image export remain open. JSON Quorivio export still needs an asset-inclusive portable bundle for full media portability; static PPTX export currently omits image widgets.
- Local tests: 158 Python unittest and 111 Node.js tests passed, including new embedded picture extraction and updated fidelity report regression. Production TypeScript build and browser/PostgreSQL/Kubernetes integration NOT validated. RC 37.5% unchanged pending acceptance.

## 2026-10-23 — Widget statistics defensive aggregation (local verification)
- Hardened per-revision widget aggregation for invalid historical revision values and malformed answer payloads. Only positive safe integer revisions are emitted; answer statistics count validated unique option IDs with safe own-properties (including reserved JavaScript names). Malformed text and attachment values are ignored. No API shape or schema changes.
- Added Node regression covering invalid revisions, malformed option IDs and null/non-string payload values. Local verification: **147/147 Python unittest**, **111/111 Node.js** passed.
- **Build blocker clarified:** the supplied archive has no `package-lock.json` / shrinkwrap file, so `npm ci --offline` cannot execute; no installed frontend/backend build dependencies were present in this runtime. Production build and real browser/PostgreSQL/Kubernetes E2E remain **not validated**. Regenerate and commit a lockfile in a trusted connected build environment, then run clean `npm ci && npm run build`.
- Weighted RC gate remains **37.5%**, pending acceptance evidence. Remaining: full widget E2E, multi-replica live, MFA/photo profile and non-PDF documents.

## 2026-10-23 — Safe widget answer aggregation (local)
- Hardened per-revision widget result aggregation against JavaScript reserved object keys (`__proto__`, `constructor`) and duplicate option IDs in historical payloads. Count each unique choice at most once per submission; avoid polluted or miscounted result objects. No API or database migration.
- Verification: 147 Python unittest tests passed, 110 Node.js tests passed (one additional aggregation regression). npm install could not complete in the available environment; full build, real PostgreSQL, browser and Kubernetes end-to-end tests are **not validated**.
- RC weighted progress remains **37.5%** until acceptance gates are verified.

## 2026-10-23 — Timed widget submission deadline final validation (local)
- Fixed expiry enforcement using a fresh PostgreSQL `clock_timestamp()` sample immediately before response insertion, after attachment and revision checks; elapsed-time ranking uses this same sample. This avoids accepting an answer based on an earlier clock sample when checks take time. API/schema unchanged.
- Verification: Python unittest **147/147 passed**; Node.js **109/109 passed**. npm dependency installation timed out; production TypeScript/Vite build **not validated**. No live PostgreSQL, browser, or Kubernetes end-to-end acceptance performed.
- Weighted RC **37.5% unchanged**; outstanding: confirm deadline behavior with a real PostgreSQL instance including slow attachment check and multi-replica exercise, plus complete existing RC gates.

## 2026-10-23 — Timed widget answer-key compatibility (local validation)
- Fixed disagreement between timed-quiz validation and grading: single-choice widgets with legacy `correctOptionId` and empty `correctOptionIds` now consistently use the legacy key. Multiple-choice widgets still require `correctOptionIds`; duplicate keys are rejected before accepting a submission.
- Uses one resolver in validation and grading; no database/API migration. Regression tests added for fallback and consistent scoring.
- Local checks: Python pytest **160 passed + 7 subtests**, Node.js **107 passed**. Production `npm run build` attempted but blocked by missing Node type declarations (TS2580). Browser, PostgreSQL and Kubernetes acceptance not run. **Weighted RC 37.5% unchanged.**
- Remaining: browser E2E for widget authoring and submissions, multi-replica live, MFA, profile photo, and other RC acceptance gates.

## 2026-10-23 — Widget-first dashboard authoring
- Consolidated dashboard page creation into the Pages widget-first commands; removed the duplicate legacy creation form from the visible UI while retaining its API and existing edit route for historical activities. Clarified widget editor handoff and button labels. Local regression only; browser E2E pending.
- Verification: 158 pytest passed (+7 subtests), 107 Node tests passed; production build blocked by absent Node typings (TS2580). No browser/PostgreSQL/Kubernetes E2E run.
- RC: 37.5% unchanged pending production and Kubernetes acceptance.

## 2026-10-23 — Transactional live widget submission guard (local verification)
- Fixed a race between the initial participant identity check and widget response insertion: the handler now locks and rechecks the active, unexpired session, current published page, anonymous access and open activity inside the response transaction, before saving any answer.
- Session row lock precedes activity row lock to align with presenter page transitions. No API or database migration; historical responses remain intact.
- Verified: pytest 156 passed (+7 subtests), Node 107 passed. `npm run build` attempted but blocked by missing installed @types/node (TS2580 Buffer). Browser, live PostgreSQL, Kubernetes and multi-replica validation not run. RC unchanged at 37.5%.
- Remaining: full widget-first activity creation and acceptance, live rendering/browser checks, profile/MFA checks, non-PDF documents and other outstanding RC gates.

## 2026-10-23 — Projected media widget rendering (local verification)
- Replaced label-only projection placeholders for image, logo, video and PDF widgets with actual session-owned asset rendering (image, controlled video, PDF viewer/open link). Empty assets display a safe placeholder. Kept existing projection geometry, timed widgets and live lifecycle behavior; no API or database migration.
- Added responsive media containment styles and regression checks for asset URL encoding, supported media and safe external link attributes.
- Verification: Python unittest **142 passed**, Node **107 passed**; `npm run build` **blocked** by missing installed TypeScript Node typings (`TS2580 Buffer`). Browser, PostgreSQL and Kubernetes E2E **not run**. Weighted RC **37.5%** unchanged.
- Remaining: verify media authorization/visibility in actual browser and presenter/participant pages, widget-only activity authoring, non-PDF documents, multi-replica live sync, MFA and profile photo acceptance.

## 2026-10-23 — Canvas-first blank page creation (local verification)
- Added authenticated `POST /api/sessions/:id/pages` to create a blank slide directly in the page sequence, with title validation, presenter permissions, session closure checks, transaction and sequential positioning. Reuses existing JSONB layout; no migration.
- The Pages section has a **New blank page · Widget editor** button; the newly created page is selected and its canvas editor opens immediately. Existing poll/quiz form remains explicitly marked compatibility; full widget-only poll/quiz authoring is NOT complete.
- Verification: Python **144 passed** (+7 subtests), Node.js **107 passed**. Browser/PostgreSQL/Kubernetes E2E pending. Weighted RC remains **37.5%** pending verified acceptance.
- Remaining: fully widget-only poll and timed quiz creation, production build, live E2E, MFA/profile-photo acceptance, documents beyond PDF.

## 2026-10-23 — Page creation to widget editor handoff (local verification)
- Creating an interactive page now retains the returned activity identity, refreshes the session snapshot, selects the Pages tab and loads the newly created page directly into widget-layout editing. This removes the extra manual selection step and makes widget editing discoverable.
- The existing create-activity API remains unchanged for compatibility. The initial poll/quiz form is **not yet fully replaced** by a widget-only creation workflow; activity migration/creation from widgets is still open. No migration was added.
- Validation: pytest **141 passed** (plus 7 subtests); Node **107/107 passed**. Production build **blocked** by missing Node TypeScript declarations/dependencies; browser, PostgreSQL and Kubernetes E2E not tested. Weighted RC **37.5%** unchanged.
- Remaining: design and implement widget-only creation with full API validation, verify live presenter/participant workflow on Kubernetes, and complete remaining acceptance gates.

## 2026-10-23 — Live page unpublish and audience snapshot safety (local verification)
- Closing a published activity now atomically clears `sessions.current_activity_id` with a session row lock and broadcasts the updated snapshot. This prevents a closed page from remaining selected on the public presenter display.
- Participant WebSocket snapshots now expose an activity/results only while the session is active and that activity is explicitly open; paused, closed or unpublished pages return empty public activity/results arrays. Owner snapshots retain their editing information. No database migration is required.
- Validation: Python pytest **139 passed** (plus 7 subtests), Node **107/107 passed**, including three regression checks. Build and Kubernetes/browser/PostgreSQL E2E not validated. RC matrix stays **37.5%**.
- Outstanding: exercise open/close/resume with two live browsers and test multi-instance broadcasts on Kubernetes; widget-only activities, documents beyond PDF, MFA and profile image acceptance are pending.

## 2026-10-23 — Projection lifecycle states and session controls (local validation)
- Corrected public presenter projection to explicitly distinguish **not started**, **active with no published page**, **paused**, and **closed** sessions. Previously active sessions with no selected page could render a blank area, and paused sessions continued rendering the last page without explanation.
- Added dashboard guidance that changing session status to active does not itself publish a page; the presenter must open the desired page in Pages and contents. Paused controls explain that new participant answers are disabled by the API. Retained existing status and page-open endpoints without migrations.
- Verification: Python **136/136**, Node.js **107/107** PASS, including three new projection lifecycle regression checks. No live browser, PostgreSQL or Kubernetes end-to-end validation; full production build not certified in this environment.
- Still open: end-to-end state synchronization on live deployment, participant reconnect/pause UX, pointer-positioned canvas menus, other document formats and widget-only activities. RC gate **37.5%** unchanged.

## 2026-10-23 — Native empty-canvas background context menu (local validation)
- Added a right-click background menu on **empty canvas** only, with existing session image-library selection, authenticated image upload, clearing the uploaded background and explicit save guidance. Existing widget right-click menus remain independent. Keyboard-accessible expandable page/result background controls remain available.
- Existing `questionBackgroundAsset` state, upload handler, and design PATCH are reused; no API or database changes. The contextual menu is anchored inside the canvas rather than at precise pointer coordinates.
- Verification: Python 133/133 PASS; Node.js 107/107 PASS. Production build attempted and BLOCKED by unavailable Node typings / workspace dependencies. No browser, PostgreSQL or Kubernetes E2E. RC gate **37.5%** unchanged.
- Still open: contextual menu for results backdrop itself, other document formats, widget-only activity workflow, live presenter/audience end-to-end checks and real browser validation.

## 2026-10-23 — Context-accessible page/result backgrounds (local validation)
- Added separate keyboard-accessible expandable background menus in the page editor, offering library selection, authenticated image upload and explicit removal for question pages and results independently. Original editor controls remain for compatibility.
- Fixed persisted design clearing: blanking either background URL now explicitly clears the previously stored URL instead of preserving stale values on PATCH merge. Uploaded asset IDs can also be cleared. Saving remains explicit.
- Verification: Python 130/130, Node.js 107/107 PASS. Full production build attempted but BLOCKED by missing installed Node typings/dependencies. No real browser, PostgreSQL or Kubernetes E2E; weighted RC still 37.5%.
- NOT COMPLETE: true right-click on an empty canvas (current controls are accessible expanded menus), other document formats, live presentation synchronization and widget-only activity workflow. No backend schema modifications.

## 2026-10-23 — Contextual media selection for canvas widgets (local verification only)
- Canvas widget context menus now expose stored-asset selection and authenticated file upload for Image, Logo, Video and PDF. Selection changes `assetId` via the same layout state and requires explicit Save layout; no new public upload endpoint or asset privileges.
- MIME options are filtered by widget type, existing `uploadWidgetMedia` is reused, and input is disabled during uploads. Legacy widget properties and layer commands are preserved.
- Python 127/127 and Node.js 107/107 PASS. Full build attempted but BLOCKED by missing workspace dependencies and Node typings; no browser or Kubernetes integration acceptance. Weighted RC remains 37.5%.
- OPEN: document types beyond PDF, page-background context control, presenter's live rendering and synchronization, widget-only activities, comprehensive editor/UI E2E; validate selectors and uploads on deployed instance.

## 2026-10-23 — Canvas widget contextual actions (local verification; RC pending)
- Added right-click and touch/keyboard button menus for duplicate, front/back layer ordering, title editing and deletion; underlying widget geometry and saved schema unchanged.
- Python 126/126 and Node.js 107/107 pass. Full frontend build blocked by unavailable `vite/client` dependencies. Live browser/Kubernetes acceptance is outstanding; per-widget contextual media picker is still pending. RC 37.5% unchanged.

## 2026-10-23 — Session media widget extension (local, Kubernetes acceptance pending)
- Extended the graphical editor palette with separate Logo and PDF widgets, in addition to Image and Video; existing private session uploads and media library are reused. Asset selection and direct upload support images for logo and PDF for document widgets.
- Extended page-design validation to require a stored UUID asset for every media widget, and design-save API now checks ownership by the same session, presenter-owned origin and MIME/widget compatibility. Public media access remains limited to the currently opened page in an active session. PDF uses a direct download/open link; arbitrary documents are not yet accepted (the strict asset allowlist remains unchanged).
- Tests: Python 124/124 and Node 107/107 locally. Full TypeScript/Vite build unavailable (vite/client type definitions not installed), and browser/PostgreSQL/Kubernetes end-to-end acceptance remains pending.
- Remaining: per-slide uploaded background asset with audience-safe delivery, document formats beyond PDF, contextual asset choice on canvas, final presenter multimedia rendering and end-to-end checks. Do not promote the media macroarea or RC gate. Weighted RC remains 37.5%.

## 2026-10-23 — Session scheduling UI consolidation (local, pending live acceptance)
- Unified session-date editing around date, start time, duration and explicit IANA timezone; added timezone validation, duplicate prevention, sorted entries, and an opt-in import of old date-only entries. Legacy API and stored data remain intact; its parallel editing form is removed.
- Regression contracts in `tools/tests/test_session_dates_consolidation.py`. Browser/PostgreSQL/Kubernetes acceptance pending. RC weighted 37.5% unchanged.

## 2026-10-23 — Full-page session navigation and dashboard layout (partial acceptance)
- Separate New/Open/Calendar main views and selected session control room, explicit page-editor entry, session date naming, improved labels/responsive grid, and corrected Terminate control.
- Python 118/118 and Node 107/107 PASS locally; full build, browser and K8s tests not confirmed. Media widget overhaul and legacy schedule consolidation remain open. RC 37.5% unchanged. Details: `SESSION_NAVIGATION_REWORK.en.md`.

## 2026-10-23 — Multi-method MFA / calendar / Kubernetes asset-volume cycle (local, uncommitted)
- Login now returns a five-minute database-backed MFA challenge after valid primary credentials, with independently selectable TOTP or email verification. Email OTP is delivered only on explicit method selection; TOTP or a recovery code consumes the same single-use challenge under row lock, with bounded attempts. Both methods are not required sequentially. Existing email challenge verification remains compatible.
- Updated second-factor screen; primary login no longer asks for recovery/TOTP. Profile email MFA activation no longer depends on supplying an active TOTP code.
- Consolidated user save action for nickname/role/approval fields (approval-state button still has its existing immediate semantics). Modern day/week/month calendar uses existing appointments, timezone metadata and session navigation; no schema migrations.
- Kubernetes Kustomize and Helm pod fsGroup=1000 and OnRootMismatch for non-root persistent asset write access, a likely cause of upload failures; runtime volume permissions and ClamAV must still be tested on the real cluster. Profile photo upload now removes the superseded private file.
- OIDC provider inventory confirmed to be environment-driven via OIDC_PROVIDERS_JSON / OIDC_GOOGLE_* and optional social provider configuration. Empty list alone does not imply an application fault. Real provider credentials and callback testing not performed.
- Verification: Python unittest 115/115 PASS and Node (experimental TypeScript stripping) 107/107 PASS. Full production build BLOCKED: npm dependency installation stalled / npm idealTree error; global compiler parser showed no TS1xxx syntax errors but lacks installed React/Node dependencies. No Kubernetes/browser/PostgreSQL E2E. Weighted RC remains 37.5% as no new gate has sufficient end-to-end evidence.
- OPEN: unified overall MFA switch and independent email ownership confirmation, avatar runtime acceptance with volume/AV diagnostics, mobile visual acceptance, admin-save transaction atomicity and complete browser e2e. The package is NOT RC.


## 2026-10-23 — CI Kubernetes credential-generation acceptance hotfix (uncommitted)
- CI run 108303599236: 115 Python tests and PDF conversion passed, but the previous `diff -ru /tmp/q-a /tmp/q-b` step failed because independent new wizard outputs correctly generate different credentials.
- Replaced the unsafe comparison with `tools/check_k8s_generation.py`: regenerate the *same* directory and compare all file SHA-256 digests; verify independent installations have distinct admin/database/application secrets; check generated credential files' POSIX permissions. Never print secret contents in CI.
- Local verification: new acceptance check PASS and Python suite 115/115 PASS. CI must be rerun by maintainer. Build/image jobs after the failed gate were not proven successful.
- Baseline: maintainer confirmed a commit of the generated-credentials cumulative package before this change; suggested commit covers this hotfix alone. Version remains 0.1.0-dev.

## K8s wizard credentials — 2026-10-23
2026-10-23: Kubernetes wizard creates stable internal DB/admin/auth credentials and an application Secret (base64, not encrypted), with 0600 overrides, reuse on repeat generation and protected external-DB password input. See K8S_SECRETS.en.md. Real cluster acceptance pending.

## 2026-10-23 — Kubernetes test deployment and image correction (uncommitted after latest confirmed green CI)
- Default application image corrected to `desalvo/quorivio:latest` in Compose/Kustomize/Helm/CI; Helm converter image reference renamed to `desalvo/quorivio-converter:0.1.0-dev` (registry availability not confirmed).
- Wizard supports TLS termination without a named ingress TLS secret (controller default certificate required), explicit TLS disable, and independent app/PostgreSQL pod node selectors. Helm supports optional TLS secret and shared pod nodeSelector.
- Verification: 111/111 Python, 107/107 Node.js and backend/frontend production build PASS; generated Kustomize YAML parsed. No Helm binary, real Kubernetes cluster or registry publication validation. See `K8S_TEST_DEPLOYMENT.en.md` / `.it.md`. GitHub not changed; new maintainer commit and CI required before deploying. Version unchanged 0.1.0-dev.


## 2026-10-23 — Chromium editor validation: local-server access blocked
- Chromium 144 and Python Playwright are installed and launch successfully, but the managed browser blocks navigation to the local Vite server at 127.0.0.1 (`ERR_BLOCKED_BY_ADMINISTRATOR`). No browser E2E or PostgreSQL acceptance was performed (PostgreSQL server unavailable).
- Fixed accidental drag gestures when interacting with widget input fields; lost pointer capture now cancels the active gesture and restores the previous geometry. Regression tests were updated.
- Backend/frontend builds passed; Node 107/107 and Python 104/104. RC gate score remains 37.5% under the existing matrix; source tests are not counted as real browser acceptance.

## 2026-10-23 — Editor gesture stabilization (cycle 3, partial)
Delta-based rotation preserving stored orientation, cancellation rollback of geometry, pointer capture cleanup and touch gesture isolation. Backend/frontend builds passed; Node suite and 102 Python tests passed. Browser/touch, PostgreSQL and assistive-technology acceptance not executed. RC gate score remains 37.5% per matrix; editor is not E2E accepted. See EDITOR_STABILIZATION.en.md.


## 2026-10-23 — Responsive editor and accessible controls (cycle 2)
- Added a gesture-free widget management panel with 5%-step position controls, duplication and layer ordering, 44px touch targets and accessible names.
- Responsive layout and visible keyboard focus; existing widget persistence path and database schema remain unchanged.
- Backend/frontend builds passed, 107 Node and 99 Python tests passed. Real devices, screen readers and PostgreSQL E2E are not validated. RC gate remains 37.5%; editor acceptance is still open.

## 2026-10-23 — Editor composition grouped cycle (after latest cumulative; uncommitted)
- Added optional 5% drag/resize snap, widget duplication with fresh IDs and widget stacking front/back controls in the 16:9 composer; existing page persistence and keyboard geometry retained.
- Node 107/107, Python 99/99 including 3 static composition contracts, TypeScript/Vite production build PASS; no live browser/DB E2E. No RC gate closed; weighted matrix **37.5%** unchanged. See `EDITOR_COMPOSITION.en.md`.
- Last confirmed maintainer commit remains the green-CI baseline before configurable results and timed-quiz changes. No git write operations.

## 2026-10-23 — Audience slide synchronization correction (partial)
Participant WebSocket snapshots now resolve the active page by server `current_activity_id` and open state, replacing the previous incorrect first-activity fallback. Both production builds PASS, Node 107/107 and Python 96/96. Browser/PostgreSQL E2E remains open. RC acceptance stays 37.5% as no gate has been accepted end-to-end. See `AUDIENCE_PAGE_SYNC.en.md`.

## 2026-10-23 — Per-widget result word cloud (partial)

Added option-frequency word cloud for individual question widgets, with explicit counts and revision isolation; this is not a free-text word extraction cloud. Backend/frontend builds and Node tests PASS. Browser/PostgreSQL E2E not run. RC gate score **37.5%** unchanged; see `RESULT_WORD_CLOUD.en.md`.

## 2026-10-23 — Email MFA cryptographic and SMTP groundwork (NOT ENABLED)

Six-digit CSPRNG OTP, domain-separated per-user/per-challenge HMAC and constant-time validation, TLS SMTP delivery helper, three tests. Login and activation deliberately unchanged until persisted challenge, atomic use, rate limiting and UI are implemented. **Email second factor remains OPEN**, no RC gate change. See `EMAIL_MFA_FOUNDATION.en.md`.

## 2026-10-23 — Strict write Origin policy

Full scheme/host/port Origin comparison for write APIs; preserves existing no-Origin client behavior. 97/97 Node and 95/95 Python tests PASS; backend TypeScript and Vite frontend production build PASS. No reverse-proxy/browser E2E. See `docs/ORIGIN_POLICY_HARDENING.en.md`. Weighted RC acceptance remains **37.5%**, see `docs/RC_GATE_MATRIX.json`.

## 2026-10-23 — RC acceptance gate re-baseline (authoritative)

**RC 37.5% weighted evidence, not 67%.** See `docs/RC_GATE_AUDIT.en.md` and `docs/RC_GATE_MATRIX.json`. All earlier 67% entries below are historical, superseded estimates. No new end-to-end acceptance is claimed.

## 2026-10-23 — Established presenter WebSocket revocation audit

Implemented per-replica ten-second PostgreSQL authorization checks for existing authenticated presenter WebSockets, closing revoked or unapproved connections and failing closed when the database is unavailable. Build API + Vite PASS, Node tests 95/95, Python tests 93/93. Multi-replica/PostgreSQL end-to-end NOT run; email MFA and other RC gates remain open. RC gate baseline remains 67%; no new complete gate accepted. See `docs/LIVE_WEBSOCKET_REVOCATION.en.md`.

## 2026-10-23 — Live timed-widget answer protection (partial)
- Reject live timed-quiz answer/duration/removal edits with HTTP 409; preserve geometry edits, version later semantic changes for historical response separation. 91/91 Node tests PASS. Vite production build attempted but not confirmed (environment timeout). PostgreSQL/browser E2E outstanding. RC 67% unchanged. See `TIMED_WIDGET_LIVE_LOCK.en.md`.

## 2026-10-23 — Independent timed quiz widgets (partial)
- Separate widget-scoped submissions and rankings, configurable answers/duration, presenter pagination. Local builds PASS; no PostgreSQL/browser E2E. RC **67%** unchanged. See `TIMED_WIDGET_INDEPENDENCE.en.md`.

## 2026-10-23 — Per-question-widget Results (partial)
- Presenter Results: independent aggregates for each question widget and revision with a per-widget editor selection (bars/pie/table). TypeScript/Vite build and 90 Node tests PASS. Multiple independent timed quizzes remain unimplemented. RC gates **67% unchanged**. See `WIDGET_RESULTS_PER_WIDGET.en.md`.

## 2026-10-23 — Timed quiz and presenter Results (partial)
- See `TIMED_QUIZ_RESULTS.en.md`: distinct timed activity, authoritative server start and score timing, protected rankings, palette markers, presenter-only Results overlay, passing API/frontend production build and 90 Node tests. **Not RC complete.** 67% unchanged. Previous entry and earlier uncommitted features remain part of the cumulative baseline.

## 2026-10-23 — Administrative user MFA recovery
- Implemented privileged per-user TOTP MFA reset with password/TOTP step-up, primary-admin/self-reset protection, transactional credential and recovery-code deletion, websocket closure, directory status flag and administrator UI. Existing stateless login cookies are **not revoked**: production security gate remains open.
- Source, TypeScript and Vite production build validated locally; 87 Node and 91 Python checks after change. No PostgreSQL/browser E2E. See `ADMIN_MFA_RESET.en.md`. RC gate closure remains **67%**, pending live acceptance.

## Current gate snapshot — 2026-10-23 (latest cumulative package)
- **RC acceptance gate closure: 67% (unchanged).** The previous estimate is retained because source-level preview/keyboard features have not passed build/browser acceptance. This is not functional test coverage or production readiness.
- Newly implemented: geometry-backed slide filmstrip with up to 24 widget boxes, preserved placement and rotation, optional background; keyboard Alt+Arrow reordering uses the existing transactional API. Thumbnails are approximate (media glyphs, not actual image/video frames).
- Local tests: 85/85 Node.js and 88/88 Python; the latter includes 2 new static feature regressions. Full `npm install --offline` fails due to absent cached `@types/bcryptjs`; TypeScript/Vite build **not executed**, no claim of CI green on these changes.
- Still open: all live PostgreSQL/browser/container/Kubernetes/SSO/email MFA/admin MFA/accessibility/security/HA acceptance gates in prior status; PDF manuals are older editions and are **not** authoritative for recently added UI. See `SLIDE_THUMBNAILS_KEYBOARD.en.md`.
- No repository mutations; last confirmed CI predates the user-specified uncommitted changes.


## RC editor grouped cycle 2026-10-23 — see docs/RC_EDITOR_BATCH.en.md and .it.md
## 2026-10-23 — Phase 2 field-validation follow-up

See `docs/VALIDATION_PHASE2_ISSUES.it.md` / `.en.md` for completed work, unverified UI, and pending calendar/editor work.

## 2026-10-22 — Streaming asset upload hardening

- Replaced 100 MB whole-body buffering for presenter and participant raw uploads with bounded streaming to private temporary files, incremental SHA-256 and signature checks, atomic file placement and cleanup on error.
- Added three streaming regression tests (normal upload, fake media signature, excessive/truncated body). Local: **46/46 Node and 23/23 Python tests passed**. No container/PG/browser E2E verification; antivirus, distributed object storage, atomic participant quota and durable orphan cleanup are still open.
- Prior functional estimate 87%; new estimate **88%**, production readiness **35%** unchanged. Requested +10 points not achieved.

## 2026-10-22 — Page sequence and safe page duplication

- Added an authenticated presenter-only transactional `PUT /api/sessions/:id/pages/order` endpoint for exact activity-ID permutations, and `POST /api/sessions/:id/activities/:aid/duplicate` for page-definition-only copies. Both reject closed sessions and broadcast updates on success.
- Added up/down ordering buttons and per-page duplication in presenter UI, with accessible labels. These controls do not yet offer a freeform drag-and-drop page canvas.
- Added dedicated unit tests and bilingual `docs/PAGE_SEQUENCE.*.md`. PostgreSQL/browser integration and full frontend build remain unverified. Prior functional estimate 78%; revised estimate 80% (+2 points), production readiness 35% unchanged; requested +10 is not achieved.

## 2026-10-22 — Session binary asset API (new cycle)

Implemented: authenticated raw binary upload/download for session presenters, signature and size validation, PostgreSQL metadata and SHA-256, Compose persistent asset volume, tests and bilingual `docs/ASSET_UPLOADS.*.md`. Local verification: 11/11 Node tests and 14/14 wizard tests passed. Unverified: TypeScript full build, CI, browser, Docker, PostgreSQL integration, antivirus, cleanup and shared Kubernetes object storage. **Not production ready.**

# Quorivio · Development status

Version: **0.1.0-dev** · 2026-10-22

## Implemented in source

- NPM workspace; React/TypeScript application and TypeScript Node/Express backend.
- PostgreSQL schema and startup bootstrap of one local admin.
- Login/logout, owner-scoped presenter session management, single-answer poll and quiz creation.
- Session join code/URL, anonymous participant token, downloadable QR PNG/SVG.
- Start/close session; open/close activities; server-validated answers, duplicate suppression with database unique key, optional quiz timer.
- WebSocket session snapshots, participant-only redaction, projector view, simple live bar charts, CSV export.
- Container build, local Compose draft, experimental Helm chart, initial security and architecture documents.
- Pure-domain automated test files.

## Verification status

- Local Node.js 22/npm toolchain available.
- Docker and Podman executables **not available** in this execution environment; container start **not tested**.
- PostgreSQL execution and multi-user end-to-end verification **not yet tested**.
- `npm install` **BLOCKED**: npm registry not reachable from this runtime (offline cache lacks @types/bcryptjs; online attempt timed out).
- 4 pure-domain tests **PASSED** with Node 22 TypeScript stripping (2026-10-22).
- Backend and frontend entry files **PASSED** TypeScript transpilation syntax diagnostics (no dependency typecheck); full `tsc`/Vite build **BLOCKED**, not verified.
- Helm chart templates written but `helm template` **BLOCKED**: Helm CLI unavailable.

## Open / backlog

1. Finish multi-user E2E tests and robust auth/session security; CSRF, distributed throttling and audit logs.
2. Kubernetes Helm chart, rootless Podman verification, OCI image scans, health metrics and CI matrix.
3. Full i18n, WCAG keyboard/screenreader assessment, aesthetic refinements and offline font bundling.
4. Session duration settings/revocation; role-based and organization-based authorization.
5. SSO: Google, Facebook, GitHub, OIDC/SAML 2.0 and authorized generic OIDC validation.
6. Word clouds, open responses, multiple-choice, rating, ranking, Q&A/moderation, leaderboards and fair-time scoring.
7. Integrated presentation builder, document conversion sandbox and previews.
8. PDF/XLSX export, templates, history/reporting, collaboration.
9. Durable multi-replica events and replay, load tests and operational observability.
10. AgID guideline mapping, privacy policy, consent/retention, SBOM, vulnerability processes and penetration tests.

## Risks

Current implementation is a prototype and **must not be described as fully end-to-end validated, AgID certified, SSO-enabled or production-ready**. Project license selected: EUPL-1.2; full verified official license text inclusion and external/transitive dependency license review are pending.

## Second delivery — documentation, CI and Kubernetes (2026-10-22)

- Added repository metadata (Alessandro De Salvo, `braket71@gmail.com`, `github.com/desalvo/quorivio`), EUPL-1.2 SPDX notice, bilingual root READMEs, bilingual operations/release/architecture/security/versioning and CI setup documents. **Official full EUPL-1.2 legal text still needs vendoring before public release.**
- Added GitHub Actions workflows with test/build/npm audit/gitleaks/Trivy gates and Docker Hub publication from main -> `latest`, release tags -> exact tag; production environment approval rules must be set manually in GitHub. No CI execution in this environment.
- Added original SVG application logo/icon, photographic/artistic cover asset and four PDF manuals (administrator and user, IT and EN). Copied the assets to Vite `public/docs` and added manual links to the web navigation. PDF creation and rendering checked locally, but in-app link and frontend build unverified.
- Added standalone Python 3 Kubernetes wizard, interactive/unattended, reuses stored delta overrides, deterministic Kustomize manifests. Four Python tests **PASSED**, repeatable output **PASSED** (2026-10-22). It does not deploy or create secrets.
- `npm install --package-lock-only --offline` **BLOCKED** (missing cached @types/bcryptjs); dependency lockfile and fully reproducible installation are still open. GitHub CI currently uses npm install rather than npm ci for this reason; convert to a committed lockfile + npm ci as a release hardening requirement.
- Production posture remains **NOT VALIDATED**: running CI and release security gates, browser E2E, PostgreSQL integration, image signing/digest, multi-replica WebSockets, full EUPL licence text and real Kubernetes deployment remain pending.

## Third delivery — PostgreSQL variants, ingress and GDPR (2026-10-22)

- Updated Compose DB image from PostgreSQL 17 to `postgres:18.6-alpine` and volume target to `/var/lib/postgresql`. **Major upgrades require migration**, not image replacement.
- Kubernetes wizard can generate internal PostgreSQL StatefulSet/PVC/service or use external PostgreSQL without generating database resources; stale database manifests are removed on regeneration.
- Added ingress choices NGINX / HAProxy community / HAProxy Technologies and implementation-specific legacy class annotations; ingressClassName also provided.
- Added secret reference for DATABASE_URL and PostgreSQL connection metadata. Secrets and TLS certificates are **operator-supplied**; TLS enforcement in actual application DB URL and PostgreSQL HA/backup are not validated.
- Added GDPR IT/EN implementation registers with data inventory, known gaps, required external legal/operational decisions. Added automated check for presence of both registers.
- Python wizard suite expanded to **11 passing tests** (confirm with command output); PostgreSQL, ingress, CI, Kubernetes and complete app tests are **not validated in runtime**. Existing PDF manuals remain the previous edition and need regeneration when runtime behavior is verified.
- No git commit, tag, release or production deployment performed.

## CI hotfix — missing npm lockfile (2026-10-22)

- Inspected GitHub Actions run logs `logs_107772108116.zip`: `actions/setup-node@v4` failed before package installation because `cache: npm` requires an npm lockfile, which is absent.
- Removed npm cache configuration from setup-node, preserving the remaining production quality gate, image build gate and publication gate. This unblocks the *setup-node* failure only, not a guarantee of overall CI success.
- Attempt to generate a real lockfile via `npm install --package-lock-only` timed out due unavailable npm registry access in the build environment. Do NOT fabricate a lockfile. Next release-hardening step: generate and commit `package-lock.json`, change installation to `npm ci`, restore npm caching and rerun the full CI.
- `python3 -m unittest discover -s tools/tests -q`: 11 tests passed; npm build/tests and GitHub CI not executed locally.

## CI hotfix — Trivy Action tag resolution (2026-10-22)

- Inspected `logs_107774225598.zip`: production quality gate passed (four domain tests, frontend/backend build, audit 0 findings, Kubernetes validation and secret scan). Container build job failed **during action resolution** before image build: `aquasecurity/trivy-action@0.33.1` is not an available tag.
- Fixed `.github/workflows/ci.yml` to use the published release `aquasecurity/trivy-action@v0.36.0` (note the `v` prefix), keeping the blocking HIGH/CRITICAL scan.
- GitHub CI must be rerun to verify image build and scanning. Container scanning and deployment are not yet validated.

## CI runtime image vulnerability remediation (2026-10-22)

- Examined GitHub Actions `logs_107776665722.zip`: all quality checks and Docker build passed, but Trivy correctly blocked publication due to **10 HIGH CVEs** reported against bundled npm tooling in the Node 22 Alpine runtime image (`brace-expansion`, `ip-address`, `pacote`, `picomatch`, `sigstore`).
- Updated `Dockerfile` to delete npm, npx and corepack from the runtime stage **after** installing production dependencies, including explicit assertions verifying removal. Node.js itself and application dependencies remain. The build stage retains npm.
- The HIGH/CRITICAL Trivy exit-code 1 gate remains in place, unchanged. No suppressions or ignore rules added.
- Verified Dockerfile configuration and archive integrity locally. **Docker/Podman not installed here**; rebuilt image and Trivy scan must run in GitHub CI. A clean scan is not claimed before that run.
- Remaining production work: implement committed `package-lock.json` and `npm ci`, verify end-to-end deployment and GDPR technical controls.

## Data lifecycle and participant safety cycle (2026-10-22)

- User confirms prior GitHub CI was entirely green and the previous cumulative package has been committed; current changes are **not committed**.
- Implemented owner-authorized session deletion, access revocation with rotated join credentials and WebSocket disconnection, and configurable retention (1–3650 days, default 90).
- Added hourly purge of closed/expired sessions past retention, backed by PostgreSQL cascading deletes. Added idempotent participant rejoin with an existing valid cookie.
- Hardened CSV exports against spreadsheet formula injection. Added domain tests for retention and CSV escaping.
- Verification: **6/6 Node domain tests passed**, **11/11 Kubernetes wizard tests passed**. Runtime API integration, Postgres migrations, CI, Docker and GDPR effectiveness remain **unverified** on this cycle.
- Next: automated PostgreSQL API integration tests, secure TLS/CSRF/session checks, backup expiration policy, multi-replica event delivery, SSO and new activity types.
- Archive retention: library inspected; 6 Quorivio ZIP packages exist, below the requested 10-package cap; no old packages eligible for removal at that time.

## Delivery progress — evidence-based estimates (2026-10-22)

These are **engineering estimates**, NOT CI pass percentages or certifications. Each category counts toward a fixed equal-weight functional rubric (10 items) or operational-readiness rubric (10 items). Recalculate every cycle from verified functionality; do not silently promote source implementation to tested release capability.

**Functional completion: 34%** (scores / 10). Rubric: core architecture 80, session lifecycle 65, participant UX 40, polls/quizzes 30, results and exports 25, advanced activity types 0, integrated presentations 0, IAM/SSO/tenancy 45, documentation 35, operations tooling 20 = 340 / 10. Documentation 35 refers to completeness across all required deliverables, not quality of the new manuals alone.

**Production readiness: 36%** (355 / 10, rounded). Rubric: baseline CI 80, basic Docker runtime 70, database integration 30, Kubernetes deployment 40, auth hardening 30, GDPR controls 20, multi-replica 0, operational docs 55, disaster-recovery verification 10, production E2E/load/security verification 20. CI success was reported by the user for the **previous** cumulative archive; this new artifact has not run in GitHub Actions.

Progress bars (10 blocks):

- Features: **34%** `███░░░░░░░`
- Production readiness: **36%** `████░░░░░░`

## Current delivery — UI GDPR controls and illustrated manuals

- Added presenter UI for editing session retention (on blur), revoking access and deleting a session with confirmation. The backend handlers already existed. UI/browser integration **not tested**.
- Added third documentation navigation link for the dedicated presenter manual (IT/EN).
- Added reproducible `tools/generate_manuals.py` PDF generator: six role-specific PDF manuals (participant, presenter, administrator × IT/EN), cover imagery, navigable table of contents, total page numbering, illustrated UI/workflow diagrams, results chart, procedures, troubleshooting, and appendices. Contents distinguish implemented vs planned features.
- Copied manuals to `apps/web/public/docs/manuals/` for delivery by web UI; frontend build not run locally (npm packages unavailable).
- Local automated regressions: 6/6 Node domain tests and 11/11 Kubernetes wizard tests passed. PDF generation and PDF page geometry inspected. User-reported previous CI green remains separate.
- Next priorities: executable CI for current package, PostgreSQL integration and frontend E2E, GDPR audit/rights workflows, SSO, activity breadth, load and Kubernetes cluster verification.


## Identity, content and governance cycle (2026-10-22)

- Added PostgreSQL additive migrations: user approval, compulsory bootstrap password rotation, `user` role, named anonymous participants, session access policy, page design JSON, admin settings and session closure timestamp.
- Implemented preliminary account self-registration API, admin role/approval/list/deletion API, administrator URL/retention settings, mandatory password-change endpoint and access middleware. The admin UI provides listing, approval and editing of roles/settings; user creation UI remains pending.
- Anonymous participants are prompted for pseudonym and necessary functional-cookie acknowledgment in UI. Rejoin continues using an HttpOnly random token; pseudonym is saved locally for convenience. Implemented per-session `allow_anonymous` API. **Authenticated participation is not yet implemented.**
- Added typed HTTPS media/layout model (background, logos, image/video/PDF references) and a simple presenter form for session theme and current activity media; per-page WYSIWYG and content upload are pending.
- Configurable public external URL for QR; session closure retention uses `closed_at` or expiry plus global admin setting (default 60 days).
- Requested demo admin password `000000` is explicitly restricted to opt-in non-production setups and forced rotation. Production refuses weak bootstrap passwords.
- Validation: **8/8 Node domain tests**, **11/11 wizard tests** locally. Frontend/backend builds, DB migrations on a populated PostgreSQL instance and CI for this package **not tested**. This is not a production release.
- Remaining: SSO, MFA, SMTP and test emails, media upload/security, cookie policy, registered-user join, result layout and full editor, spreadsheet export, GDPR and E2E.
- Estimates: functional **39%**, production readiness **34%**. Operational readiness decreases because new auth/migration surfaces are untested; prior CI green applies only to user's earlier commit.

Progress: Features `████░░░░░░` 39%; readiness `███░░░░░░░` 34%.

Additional source changes: registration page, admin account creation/deletion UI, websocket owner-role checks, opt-in publishing of aggregate participant results, and session theme display. Requires real PostgreSQL/API/browser integration tests.

## 2026-10-22 — Collaboration, portable sessions and ingress sizes
Partial API implementation: collaborators, definition-only JSON import/export, draft duplication, audit-preserving invalidation, live option edits and configurable ingress upload size. 8/8 Node tests, 14/14 Kubernetes wizard tests passed. Full database backup/import, file uploads and UI remain pending. New CI build unverified. Functional estimate 43%; production readiness 33%.


## 2026-10-22 — Expanded professional manuals

- Expanded and regenerated six bilingual PDF manuals for participants, presenters and administrators. Added full event walkthroughs, preflight checklists, troubleshooting decision paths, privacy explanations, backup/restore safety practices, Kubernetes configuration, API-vs-UI capability boundaries and detailed collaboration/export limitations.
- Source: `tools/generate_manuals.py` + `tools/manuals_extra.py`; generated PDFs stored in `docs/manuals/` and mirrored to the web static manuals directory. Tables of contents and page counts are generated by ReportLab. Illustrations are conceptual; actual screenshots remain pending browser verification.
- Manual counts: 11+ pages participant, 14+ presenter, 15+ administrator, per language; verify individually in PDF info. This cycle updates documentation only; functional completion remains **43%**, production readiness remains **33%**; these are estimates, not CI results.
- Browser build and current CI not rerun. No software behavior was newly validated.

## Presenter workflow UI cycle (2026-10-22)
- Added browser controls for session duplication, definition-only JSON import/export, collaborator management, live activity edit and explicit response invalidation.
- Regenerated six bilingual PDF manuals with workflow sections. Browser diagrams remain illustrative.
- Node domain tests: 8/8 passed; Kubernetes wizard: 14/14 passed. Full TypeScript/Vite build and real PostgreSQL/browser integration NOT executed here.
- Full instance backup/restore, file uploads, SSO, MFA, SMTP and full rich media editors remain open.
- Estimated functional completion 46%; production readiness 33% (unverified new UI).

## 2026-10-22 — Asset UI and aggregate reporting cycle

Implemented in source: authenticated presenter asset list/delete operations scoped to session, upload/list/open/remove controls in presenter UI, platform administrator upload-size setting, and one-way session report export with activity totals, invalidation audit and asset hashes. Report deliberately excludes participant identifiers and is not a portable archive or an instance backup. Local verification: 11/11 Node tests and 14/14 Kubernetes wizard tests passed. Open: dependency-enabled TypeScript build, actual PostgreSQL/browser integration, distributed asset storage, malware scanning, GDPR purging of orphaned disk files, complete admin backup/restore, SSO/MFA and production tests.

Estimated functional coverage: 53% (previous 48%, engineering estimate reflecting completed API+UI workflows; not an acceptance-test percentage). Production readiness: 33% unchanged pending integration and security validation. Suggested commit must cover uncommitted work since the user's last confirmed actual commit (runtime npm security hotfix); later package commits have not been confirmed by the user.

Additional deletion hook: session deletion and retention-based purging now attempt to remove the session's private on-disk asset directory after successful database deletion. Cleanup failure is logged for operator remediation; there is no durable retry queue yet, so GDPR deletion assurance remains open.

## 2026-10-22 — Offline backup tooling and persistent Kubernetes assets

- Added `tools/instance_backup.py`: offline database/asset archive, per-file SHA-256 manifest, archive verification and guarded restore to empty targets.
- Added bilingual operational documentation `INSTANCE_BACKUP.it.md` and `INSTANCE_BACKUP.en.md`.
- Kubernetes wizard now generates asset PVC and mounts `/app/assets`, with validated size, access mode and StorageClass overrides.
- Local checks: 11/11 Node tests, 19/19 Python wizard/backup tests. No live PostgreSQL backup/restore, container CI, browser or Kubernetes deployment was tested in this cycle.
- **Open**: administrative UI backup/restore, encrypted/scheduled offsite backups, real PostgreSQL restore drills, shared object storage, comprehensive production security validation. Do not treat offline backup tooling as complete production disaster recovery.
- Previous completion estimates of 53% functional and 33% readiness are historical estimates. This cycle adds useful capabilities but does **not** substantiate +10 percentage points of fully validated functionality.

## 2026-10-22 — Image defaults, page layout editor and re-voting
- Default container reference changed to `desalvo/quorivio:latest` in Compose and Kubernetes wizard; publish target updated to Docker Hub `desalvo/quorivio` without renaming the GitHub source repository.
- Fixed session creation to persist the reference date and added authorized live metadata editing.
- Added presenter page-specific editor for question/result headings and backgrounds.
- Changed response uniqueness to partial unique active vote; invalidated history is retained and same participant may submit again after invalidation. Requires PostgreSQL schema migration before backend deployment.
- Local regression: 11 Node tests and 19 Python tests passed. No integration PostgreSQL or browser tests.
- Prior estimate 55% functional/35% production readiness. Given incomplete acceptance tests, do not claim the requested additional 10 percentage points.


## Quiz modes and reactions (2026-10-22)
Implemented answer-mode schema and validation, required flags, reaction persistence and presenter statistics, basic web controls. Local tests: 17 Node and 23 Python passed. No PostgreSQL or full browser E2E; file-upload from participants remains pending. Estimated functionality 63%, readiness 35%.

2026-10-22: widget composer question-page ordering, rating 0–10 endpoints, PostgreSQL uniqueness and aggregate stats; no full browser/DB CI yet. Timer/QR placeholders. Docs build dev-20261022.

Progress estimate: functional 66% (previous 63%); readiness 35% unchanged. Browser, TypeScript full build, DB integration and actual container release not yet verified. Note: 10% increase requested but not substantiated.

## Runtime widget and portable quiz fix — 2026-10-22
- Export/import of session definitions now includes quiz answer modes, required flags, and multiple correct option IDs; duplicate definitions preserve these fields.
- Participant timer widget now displays a countdown using server-side opening timestamp and configured duration; scoring deadlines remain server-side.
- Participant QR widget now displays a locally served SVG for the session's public invitation (with no presenter credential).
- Unit tests: 20/20 Node; 23/23 Python. Runtime integration and browser build **not verified**. These improvements do not warrant +10 percentage points of verified functional completion.

## Audience Q&A and word cloud — 2026-10-22
- Implemented normalized single word/short-phrase contribution per participant per active page (max 48 characters), durable in PostgreSQL and scoped to its session.
- Added Q&A: up to three questions per participant per page, moderation states pending/approved/rejected, protected presenter moderation endpoints, public approved-only listings and idempotent upvotes.
- Added presenter management panel (word-frequency visualization, pending questions, approvals and counts) and participant contribution/upvote panel.
- Added `apps/api/src/audience-tools.ts` with focused validation and unit regression tests.
- **Local verification:** 25/25 Node domain tests, 23/23 Python operational tests. Real database migrations, TypeScript full build, browser flow and multiplayer authorization still not validated.
- User requested +10 percentage points from 68%. **Not achieved by this cycle**: no defensible evidence to assign +10 points from two new modules without full integration. Engineering estimate functional 72%; production readiness remains 35%.

## Presenter profiles and multi-target rating widgets (2026-10-22)
- Implemented: owned vs invited collaboration labels; approved presenter public profile name/photo URL; selectable profile widgets; multiple widget-scoped 0–10 ratings with question/quiz/session/presenter target kinds; per-target rating aggregates; independent widget removal.
- Unit tests: 29/29 Node.js with `--experimental-strip-types`; 23/23 Python.
- Limitations: profile photo uses remote HTTPS URL, no direct photo upload; quiz target is activity scoped; multi-question quiz grouping, all-page rendering, PostgreSQL migration and browser E2E remain unverified.
- Overall functional estimate: 75% (previous 72%); operational readiness: 35% (unchanged). Estimates, not production acceptance.

## Page widgets cycle (2026-10-22)
- Added backend validated text styles, optional descriptions and obligatory rating titles.
- Added question widget configuration and rich text controls in presenter editing panel.
- Added tests for rich widget schema and validation.
- LIMITATION: independent question-widget submissions, per-rating audience comments, freeform page canvas and graphical page sequence are not completed.
- Pending: browser build, database integration, UI screenshot verification.

**Cycle assessment:** estimated functional scope 78% (previous 75%); production readiness 35% unchanged, pending database/browser/CI verification. The requested +10 percentage points are not verified.

### 2026-10-22 — Independent question widgets
Implemented: standalone widget-specific response endpoint, PostgreSQL `widget_answers` table and aggregate presenter endpoint; question widget UI with single/multiple/text/file inputs, independent choices and required flag; validation and tests. Node tests must be rerun in CI. Not completed: browser/PostgreSQL integration, participant upload, widget editing with historical revisions, all question widget analytics. Functional baseline 80%; provisional 83%, production readiness unchanged 35% pending integration validation.


## Question-widget revision cycle — 2026-10-22
- Added row-locked page design updates with numbered historical definitions of question widgets when their answer semantics change.
- Each widget submission stores the definition revision, with uniqueness per participant/widget/revision.
- Presenter-only aggregate/detail endpoints break down counts by revision, options and response type; text responses are not returned.
- Tests: 43/43 Node and 23/23 Python locally. PostgreSQL migrations, real browser build, multi-client concurrency and CI not yet verified.
- Engineering coverage estimate: 85% (was 83%); operational production readiness 35% unchanged. Requested +10 points not achieved.

## 2026-10-22 — Participant file widget uploads
- Added participant-scoped upload endpoint and file picker for independently submitted file widgets.
- Added participant ownership tracking to assets and enforced authorization when submitting file-widget and primary file answers.
- Enforced a provisional ten-asset upload limit per participant/session.
- Known gaps: in-memory buffering, malware scanning, orphan cleanup, concurrency-safe quotas, PostgreSQL/browser tests and production validation.

## 2026-10-22 — Offline presentation import staging
- Implemented `tools/import_presentation.py` for bounded PDF/PPTX-to-PNG conversion and SHA-256 manifest generation, without changing application version.
- Repaired invalid TypeScript SQL string quoting in session listing route; a full TypeScript build is pending dependency installation.
- Verification: 46 Node tests and 27 Python tests passed (including 4 presentation import tests). PDF page rendering tested locally; real PPTX fidelity remains unverified.
- Not complete: web upload/import API, database persistence for presentation slides, sandboxed worker deployment, slide previews, interactive editing, animation/video fidelity, browser end-to-end testing, PostgreSQL integration, CI execution.
- Functional coverage assessment: 89% (previous 88%, +1 approximate point). Production readiness remains 35%. Do not interpret as end-to-end certification.


## Ciclo pagine slide — 2026-10-22

Integrated slide pages: the web workspace creates slide activities from already uploaded or batch-uploaded PNG/JPEG/WebP images. Public media endpoint limited to current page of active session. Offline PDF/PPTX conversion exists, but direct web conversion and isolated worker are still pending. PostgreSQL/browser tests and production readiness are pending. Functional estimate 90% (previous 89%); readiness 35% unchanged.

## 2026-10-22 — Experimental direct PDF/PPTX import
- Implemented presenter-only upload endpoint, 100 MiB ceiling, conversion subprocess timeout, validation of page checksums, transactional slide insertion, file cleanup on error, and browser file picker.
- Default OFF via QUORIVIO_ENABLE_CONVERTER; separate sandboxed conversion worker NOT implemented. Docker runtime does not include converter tools.
- Verified 46 Node and 27 Python existing regression tests, TypeScript/TSX parser, and real two-page PDF offline conversion. No API PostgreSQL integration or production safety validation.
- Functional estimate 91% from 90% (not +10); readiness remains 35%.

## 2026-10-22 — Authentication foundation (TOTP MFA + SMTPS)
- Implemented: TOTP enrollment, confirmation, password+TOTP login enforcement, disabling with both factors, AES-256-GCM encryption of pending and enabled secrets, and the browser-side TOTP controls.
- Implemented: SMTPS environment validation, non-secret administrative status view, authenticated test-email endpoint, TLS certificate validation and SMTP test UI; nodemailer declared as runtime dependency.
- Added tests for RFC 6238 vector, Base32, time windows, encryption/authentication, configuration validation and SMTP credential redaction.
- Verified locally: Node unit tests and Python project tests; complete npm build, delivery with a real mail server, PostgreSQL migration and browser flow have NOT been run.
- Open: social/generic OIDC SSO, OIDC/SAML provider callbacks, verified SMTP delivery, MFA backup codes/recovery, per-account/distributed brute-force controls, replay prevention, secure administrator-configured SMTP credentials, all production integration tests.

## 2026-10-22 — Password recovery
Implemented short-lived SHA-256 hashed single-use password reset tokens, generic account enumeration-resistant responses, SMTPS delivery, account/IP throttling, reset UI and password-change revocation check for protected API routes. TOTP remains required. Unit tests 57/57 Node and 27/27 Python pass. Not tested against a live SMTP server, PostgreSQL migrations, browser flows, or multiple nodes. SSO remains open.

## MFA recovery codes — 2026-10-22
Implemented: 10 one-time 128-bit recovery codes at MFA confirmation, keyed HMAC hashes stored in `mfa_recovery_codes`, atomic consumption on login, password+TOTP-protected rotation, web setup/entry interface, invalidation upon MFA disable. Verified: Node tests 60/60, Python 27/27. Pending: live PostgreSQL migration and browser integration, SSO, distributed rate limiting, production security review.

## 2026-10-22 — OIDC federation foundation
- Added configurable Google/generic OIDC/custom OIDC Authorization Code + PKCE provider support, explicit linking to an already signed-in account, RS256 JWKS verification, state/nonce checks, UI login/link controls, and `oidc_identities` schema.
- Existing accounts are not automatically linked by email; enabled local TOTP is not bypassed by OIDC login.
- Tests: 64/64 Node and 27/27 Python pass; includes new crypto and claim verification tests. Full npm build, real OIDC callback/browser, and PostgreSQL migrations remain **untested**.
- BLOCKED/OPEN: real Google and generic OIDC credentials/federation validation, GitHub/Facebook OAuth (or broker), SAML, distributed state persistence, OIDC MFA step-up, unlink controls and security review. Do not claim SSO production-ready.
- Functional estimate: 96% (from 95%, +1), production readiness: 35% (unchanged); estimates are not deployment certification.

## 2026-10-22 — GitHub/Facebook OAuth2
**Implemented:** OAuth2 start/callback, strict state cookie, immutable identity lookup, explicit approved-user linking, TOTP-bypass prevention, UI links, 5 helper tests. **Verified:** 69 Node tests, 27 Python tests. **Pending:** live provider tests, multi-replica state, PostgreSQL integration, frontend full build and end-to-end tests.

## 2026-10-22 — Page drag-and-drop cycle
- Implemented native HTML5 drag and drop of page rows in the presenter workspace, backed by the existing transactional page sequence endpoint. Stable page IDs preserve existing answers; keyboard-friendly Up/Down controls remain.
- Added pure page ordering helper and four new automated regression tests.
- Corrected an obsolete presenter help note about direct PDF/PPTX import; it is experimental and config-gated, rather than altogether unavailable.
- New docs: `PAGE_STORYBOARD.it.md`, `PAGE_STORYBOARD.en.md`. Six role/language PDF manuals regenerated with page-sequence instructions.
- Not verified: full npm build and TypeScript type checking, actual browsers/PostgreSQL, multi-user race conditions, OAuth IdPs, conversion-worker isolation.
- Feature completion estimate 98% (previous 97%); production readiness still estimated 35%. These are project planning estimates, not certification or E2E validation.


## 2026-10-22 — Freeform widget canvas (experimental)
- Implemented visual percent-based widget positioning, pointer dragging, in-canvas title editing, width controls, individual removal and persistence in page designs. Existing list/keyboard controls remain available.
- Added strict server-side coordinate validation and two tests; full regression: 71/71 Node and 27/27 Python.
- Parsed modified TSX/TS files with TypeScript parser: zero syntax diagnostics. Browser and PostgreSQL integration, full frontend build, collision avoidance and accessibility verification remain open.
- Functional coverage estimate: 98% unchanged (experimental addition within an already-counted macroarea). Production readiness: 35% unchanged. **Do not claim 100% complete**; worker isolation and distributed storage remain pending.

## Antivirus upload scanning cycle — 2026-10-22
- Added optional streaming ClamAV `INSTREAM` client (`apps/api/src/malware-scan.ts`), with fail-closed `QUORIVIO_AV_REQUIRED=true` configuration, bounded scan size and timeout.
- Integrated scans ahead of PostgreSQL asset insertion for presenter and participant uploads, and ahead of conversion for PDF/PPTX web imports. Failed presenter/participant scan removes the received asset.
- Added four local scanner protocol/validation tests and bilingual operations guides `docs/ANTIVIRUS_UPLOADS.*.md`.
- Requires operator action: deploy private ClamAV service, maintain signatures, configure host and required policy, and test using the real deployment. Scanner not bundled in default Compose/Kubernetes manifests. No assertion of complete production readiness.

**Current handoff:** Antivirus source is locally verified (75/75 Node, 27/27 Python); production readiness **35% estimated** and overall functional coverage **98% estimated** remain unchanged because infrastructure integration is not deployed or validated. User action is required only for provider credentials and actual production acceptance tests; all other features below remain open for autonomous work.

**Still incomplete (do not mark complete):** isolated document converter worker; cross-replica socket, OAuth state and rate-limit coordination; real shared-object media storage; complete canvas collision/accessibility behavior; comprehensive browser+PostgreSQL tests; actual SSO/SMTPS/ClamAV and Kubernetes production validation.

## Generic OIDC provider configuration (2026-10-22)
Removed the former institution-specific provider preset and all branded references. Additional OIDC providers are supported via OIDC_PROVIDERS_JSON (up to 32); strict validation and two focused unit tests. No externally hosted provider has been tested. Remaining independent engineering work includes isolated document conversion, distributed WebSocket/auth state, shared media storage and E2E validation. Do not claim full feature completion or production readiness.


## Managed antivirus and SSO defaults (2026-10-22)

Docker/Podman Compose now bundles a private ClamAV service and persists its signatures. Helm includes a ClamAV sidecar with fail-closed scanning. Public provider endpoints are documented for Google, GitHub and Facebook; client registrations and secrets remain operator tasks. Offline source-level tests do not constitute deployment validation. Multi-replica synchronization and isolated document conversion are still outstanding.

## 2026-10-22 — Cross-replica WebSocket synchronization and persistent Helm assets

**Implemented:** dedicated PostgreSQL LISTEN/NOTIFY fan-out for session snapshots, UUID-only notification payloads, reconnecting listener, persistent Helm assets PVC with optional existing claim, Kustomize wizard multi-replica option gated on RWX storage, and focused Node/Python tests. Bilingual operator guides: `MULTI_REPLICA_SYNC.*.md`.

**Verified locally:** 79 Node tests and 33 Python tests; static Helm configuration checks. **Not verified:** PostgreSQL integration, network split recovery in a real cluster, browser load-balancing, full frontend build. OAuth/OIDC temporary login state and rate limiting remain per-process, therefore production multi-replica remains incomplete. No claims of total functional or production completion. Functional estimate **98%**, production readiness **35%** unchanged pending integrated evidence.

**Remaining autonomous work:** isolated PDF/PPTX worker container; shared OAuth login state and distributed rate limiting; browser/SQL integration test harness, responsive canvas refinements. **External acceptance:** OAuth provider credentials, SMTP delivery, deployment on actual Kubernetes/Docker environment and security/privacy validation.

## 2026-10-22 — PostgreSQL-backed federated authorization and distributed API throttling

**Implemented in this package:** Replaced instance-local OIDC and GitHub/Facebook authorization-state Maps with short-lived `auth_flows` rows. Each callback consumes its SHA-256 state key using atomic `DELETE ... RETURNING` and checks the browser state cookie, provider, and expiry. Added database-backed minute-window API request throttling keyed by the hash of the incoming IP address, with an atomic UPSERT and fail-closed 503 on database errors. Added periodic cleanup and regression/contract tests. SQL is included in the idempotent schema bootstrap.

**Validation:** 82/82 Node domain/contract tests and 33/33 Python tests passed. **Not performed:** TypeScript/npm full build, real PostgreSQL migrations, multi-replica browser/SSO provider integration, Kubernetes container startup and load testing. The tests do not demonstrate these integrations.

**Remaining autonomous work:** isolated document-conversion worker and queue; full end-to-end automated application tests; comprehensive canvas responsiveness/accessibility; cleanup and lifecycle of shared uploads; observability and review of SQL migration compatibility. **Requires user infrastructure/provider setup later:** OAuth application registrations, real SMTP credentials, actual PostgreSQL, clustered storage/Ingress and Kubernetes smoke/load testing. Avoid claiming 100% readiness until validated.

## 2026-10-22 — Isolated presentation conversion worker
- Added dedicated non-root Python conversion service, authenticated HTTP job dispatch using opaque IDs, private temporary shared volume, Compose service and Kubernetes Helm sidecar. API no longer executes document conversion subprocesses.
- Verification: 82 Node tests; 37 Python tests, including new worker path and deployment tests.
- Unverified: real worker container builds/runs, production DB/browser and multi-replica runtime, full build and security review. Other backlog items remain open; functional coverage and production readiness not increased without E2E proof.

## 2026-10-22 — CI PostgreSQL boot and converter build gate
- Replaced the remaining instance-local password recovery request throttle with a PostgreSQL atomic UPSERT fixed-window limiter, preventing cross-replica bypass.
- Added GitHub Actions temporary PostgreSQL 18 integration service, application boot from compiled artifact, live/readiness and public homepage checks, explicit bootstrap-user and selected schema assertions, plus a denial check for unauthenticated account access.
- Added a separate Docker build of the converter image to the container gate; retained the blocking Trivy scan of the main app image. Dedicated converter CVE scanning is **still required**.
- Added Python CI contract tests and bilingual handoff instructions (`CI_INTEGRATION.it.md`, `.en.md`).
- Local Node/Python suite passes; **not verified in this container:** npm install/build, actual PostgreSQL startup, Docker/Podman image build, GitHub CI execution, real-cluster deployments. The repository owner can now run the CI gate and return first failing logs. Do not claim 100% product completion or production acceptance.
- Estimates unchanged pending live evidence: **98% functional coverage**, **35% production readiness**.


## CI run 107927415489: dependency security fix (2026-10-22)
- Confirmed PASS: unit tests (82), frontend/backend compilation, live PostgreSQL 18 bootstrap, health probes, initial authorization checks.
- Confirmed FAIL: npm production dependency audit. Nodemailer 6 flagged HIGH.
- Code change: `apps/api/package.json` now requires `nodemailer: ^10.2.1` and removes `@types/nodemailer` (bundled TypeScript declarations).
- PENDING: updated npm install, full build/audit on GitHub Actions, and container gates. **Do not claim CI green before the rerun.**
- Commit baseline: the user confirmed committing the prior CI integration gate package; the suggested next commit only contains this security dependency remediation plus docs.

## GitGuardian TOTP fixture follow-up (2026-10-22)
- Replaced the literal public RFC 6238 Base32 vector in `apps/api/test/totp.test.ts` with a runtime-generated key from RFC byte data; generated non-RFC test secrets at runtime.
- Verified Node test suite 82/82 and Python test suite 40/40.
- Source: `docs/CI_TOTP_SECRET_SCANNER.en.md`; original report should be triaged in GitGuardian. No actual production credential was identified in this fixture.
- Other CI errors have **not** been diagnosed; requires the latest failed job logs.
- No git commit/push/tag performed.


## Python cache cleanup (2026-10-22)
- Added root .gitignore patterns for Python bytecode and tool caches: __pycache__/, *.py[cod], .pytest_cache/, .mypy_cache/, .ruff_cache/.
- Excluded all Python cache directories and compiled bytecode from the cumulative source ZIP; Python source/tests remain intact.
- Note: caches already committed to Git remain tracked until the maintainer explicitly untracks them with `git rm --cached`; no Git history rewrite is required.
- Latest confirmed commit is the Nodemailer security hotfix. Changes since that commit include the TOTP test-fixture fix and this Python cache cleanup; commit only at user discretion.
- Functional coverage and production readiness estimates remain 98% / 35%; pending live CI validation.

## CI-green baseline and converter concurrency hardening (2026-10-22)
- Maintainer confirmed committing the Python-cache cleanup and reported green CI. This supersedes earlier historical CI-pending/failed status above; the latest user-confirmed commit is the baseline for future commit descriptions.
- Hardened private conversion worker: reject pre-existing output directories and symlink outputs, prevent simultaneous conversion of the same job in a worker instance, release reservation on success/failure, and return HTTP 413 for oversized requests.
- Added high/critical Trivy image scan for `quorivio-converter:gate` to CI without relaxing the runtime-image security gate.
- Added 3 regression tests. Current local verification: 82/82 Node and 43/43 Python PASS, Python executed with bytecode generation disabled.
- Still requires CI rerun for the new converter image scan; live multi-pod/multi-process and browser conversion checks are not yet demonstrated. In-process duplicate-job protection is not a distributed lock; separate converter replicas must coordinate via storage/queue in a production HA design.
- No commit, push, release or tag performed.

## 2026-10-22 — Cross-process conversion reservation (uncommitted)
- Extended private PDF/PPTX conversion worker with an atomic per-job `.conversion-lock` directory on its shared conversion volume. Protects against duplicate conversions across worker processes or pods mounting the same filesystem, in addition to the in-process reservation.
- Preserve lock on abrupt process termination to fail closed; operator must investigate abandoned jobs before manually clearing such a reservation. Do not automatically delete a lock whose owner status is unknown.
- New regression tests cover pre-existing shared reservations, lock lifecycle during conversion, and cleanup on conversion failure. Local tests: Node 82/82, Python 46/46 pass.
- Baseline is the last maintainer-confirmed CI-green Python-cache cleanup commit. No subsequent commit confirmed; package cumulatively includes earlier converter hardening and converter-image Trivy gate.
- Pending: rerun CI for these changes; live multi-worker shared-volume and crash-recovery tests, end-to-end browser and real deployment acceptance. No commit/push/tag performed.

## Manual recovery of crashed shared conversion jobs (2026-10-22, uncommitted)

- Added `tools/recover_conversion_lock.py`, an operator-only, offline lock inspection and recovery utility. Read-only by default; removal requires `--recover --workers-stopped` after **all** workers on the shared conversion volume have been stopped.
- The recovery tool refuses invalid IDs, unsafe or symlinked lock paths, nonempty reservations, ambiguous source files, and jobs with existing output. It intentionally does **not** attempt to infer that an active worker has stopped or automatically steal a lock.
- Added `docs/CONVERSION_RECOVERY.en.md` and `.it.md` with safety steps, plus seven tests for safe recovery behavior.
- Local verification: Node **82/82**, Python **53/53** passed. Full container, concurrent worker, PostgreSQL and browser end-to-end verification remain pending. Keep version `0.1.0-dev` and preserve uncommitted status. Commit summary must include all changes since the last user-confirmed commit: converter hardening, Trivy gate, cross-worker locking, and manual recovery.

## 2026-10-22 — Conversion publish integrity and source ambiguity (uncommitted)
- Reject ambiguous PDF/PPTX jobs with two valid sources; require exactly one.
- Generate page manifest in private staging before atomically renaming the completed page directory into place, avoiding partially published output.
- Unit tests: 82/82 Node, 55/55 Python pass. Real image builds, multi-worker NFS/PVC semantics and browser import remain to be confirmed in CI/deployment.
- Last confirmed commit: Python cache cleanup with green CI. All converter/Trivy/recovery changes since then remain uncommitted. Version unchanged: 0.1.0-dev.

## 2026-10-22 — RC readiness integration batch (uncommitted)
- Added private HTTP worker integration tests: authenticated conversion, malformed requests, 413 size limits, 503 not-ready response and safe lock release.
- Strengthened API validation of converted slide manifests: expected format/version, exact source type and SHA-256, sequential page names/positions and PNG magic bytes in addition to existing per-file SHA-256 and size checks.
- CI now explicitly installs and checks PDF rendering test prerequisites; runs actual Poppler/ReportLab conversion rather than silently permitting the optional rendering test to skip.
- Added `docs/RELEASE_CANDIDATE_READINESS.{en,it}.md` to distinguish offline checks from required operational and GitHub acceptance.
- Local: 82/82 Node, 60/60 Python. Last maintainer-confirmed commit is the Python-cache-cleanup CI-green baseline. All converter hardening, Trivy, shared locking, manual recovery, atomic publishing and this batch are uncommitted cumulatively.
- **RC status: BLOCKED** until fresh CI (with image scans) and real Docker/Podman/browser/HA acceptance. Preserve version 0.1.0-dev. No commits, tags or releases by assistant. Historical status sections above reflect their time, not the current latest gate.

## 2026-10-22 — Field validation (phases 1–2) corrections, pending CI (uncommitted)
- ARM64 Compose: managed ClamAV default changed to `clamav/clamav:stable-debian` based on maintainer deployment feedback; image existence/build must still be validated in CI or real deployment.
- Authentication: the mandatory initial password change now signs out client-side and shows the login screen rather than attempting to reuse a revoked cookie. Login accepts either email or the optional globally unique, case-insensitive nickname. Primary administrator has the reserved, immutable nickname `admin` but may change email via a separate audited-by-API administration action. Existing databases migrate primary identity at startup when absent.
- User administration: principal administrator can never be demoted, unapproved or deleted; current-user self-demotion protection remains. User approval toggles immediately and visibly between red and green states. Admin account identity may change its email without changing the stable login identifier.
- Web UI: functional navigation routes to main-area panels for Users, Server Settings, SSO, MFA, Presenter Profile and Workspace. Workspace distinguishes owner/collaborator roles by color. Each session may have zero or several explicit schedule dates via new API and date-selection controls. Session creation still retains legacy reference_date defaults for compatibility.
- Server SMTP/SMTPS settings: admin configuration can now persist with AES-256-GCM encryption under `AUTH_SECRET` and never returns the password. Existing environment configuration remains as fallback. MFA enrollment requires a configured SMTP transport. MFA provides both otpauth URI and authenticated, no-store PNG QR code; actual notification/email fallback behavior is not yet implemented or validated.
- Added additive SQL migrations for primary admin identity, nickname uniqueness, session schedule dates, encrypted SMTP settings. For production, back up the database and test migrations on a clone; avoid changing `AUTH_SECRET` without migrating encrypted settings.
- Validation: Node and Python offline suites, TypeScript/TSX syntax checks; full npm CI, PostgreSQL migration, browser interactions and real SMTPS connectivity remain **unverified** for this cycle. Version remains `0.1.0-dev`, RC acceptance blocked.
- Last user-confirmed commit: RC-readiness-integration cumulative with green CI. All the changes above are subsequent, uncommitted work.
- Next priorities: operational end-to-end verification, UX polishing, MFA notification path, SSO configuration UI, full calendar presentation, and validation that the database migration works against existing installations.

## CI TypeScript navigation hotfix (2026-10-23)
- **Observed CI failure:** `apps/web/src/main.tsx` TS2345 in admin navigation: the conditional administrator entries were inferred as `string[][]`, widening `key` beyond the dashboard page union.
- **Fix:** preserve literal tuple types on the conditional entries (`as const`), so `setDashboardPage(key)` remains statically checked without casts or widening the state type.
- **Regression:** `tools/tests/test_dashboard_navigation_types.py` asserts literal typing and state setter usage. A fresh full npm build in GitHub Actions is still required to confirm compilation.
- **Scope:** all previous field-validation changes remain included; no version bump, commit, push or release.

## Cycle 2026-10-23 — server pagination, scheduling and session lifecycle (uncommitted)
- Added authenticated, owner/collaborator-scoped server-side search and paginated listings for users and sessions (1–100 entries per page); legacy unpaginated array responses retained to avoid breaking existing clients.
- Introduced `session_appointments` with explicit date, HH:MM start time, duration (5–1440 minutes), and IANA timezone. Added session-specific CRUD and a scoped global calendar API, plus monthly calendar and appointment editor UI.
- Added `paused` session state with pause/resume transitions and UI controls; responses remain restricted to active sessions.
- Introduced initial editor section tabs and responsive calendar styling.
- Local checks: Node test suite 82 passed; Python suite 75 passed. A complete TypeScript frontend build, database migration against an existing DB, real browser testing, and multi-container verification were not available in this cycle and remain release gates.
- **Still open**: full administrative MFA enforcement flow, email second-factor, full web management of configurable SSO providers, accessibility/responsive audit, broad UI toggles, and end-to-end tests with seeded PostgreSQL and external services. Do not call RC validated yet.

## Post-validation UI and profile update (23 October 2026)
- Added private streamed profile-image uploads (PNG/JPEG/WebP, 5 MB), antivirus scanning, replacement and deletion via authenticated API; presenter public image delivery is scoped to session and membership.
- Profile nickname now initializes from the authenticated account; profile images no longer accept externally hosted URLs.
- Added drag-and-drop from existing widget toolbox into the graphic canvas; positioned widgets remain draggable and removable.
- Notifications support click to dismiss, explicit close and Escape, with improved stacking.
- Added regression contract tests. **Remaining**: full PowerPoint-like page editing (dedicated image/video widgets, complete widget types, slide thumbnails, advanced management), responsive browser QA, full CI compilation and deployment testing.


### 2026-10-23: Browser-only session rehearsal and sticky-note widgets
Added a dashboard-launched participant rehearsal dialog with local-only mock responses, per-page navigation and reset. No submissions reach the API; this is not a full networked participant end-to-end test. Added sticky notes to the page canvas and shared validation. Local Node and Python tests pass. Still pending: production image/video widget asset delivery, full presentation-grade canvas ergonomics, admin-managed MFA, full web SSO configuration, and real browser/CI integration tests.

Media widgets, filmstrip navigation and binary controls implemented in source; RC gate estimate 63%, not E2E approved.

## 2026-10-23 — Fullscreen slide canvas and graphical page ordering
- The slide composer uses a 16:9 editing surface, with inside-body pointer dragging and eight edge/corner resize handles. Width and height are persisted as percentages, with a backward-compatible optional `height` in the validated page schema.
- Removed the old embedded width `+`/`−` buttons. A small dismiss control remains on the widget border; the widget fits its explicit rectangle.
- Added the browser fullscreen editor control; direct drag-to-reorder is available on the slide filmstrip as well as the existing slide list, using the transactional order API.
- Updated the rehearsal display to respect stored widget heights; added geometry regression coverage.
- Verification performed: Node unit tests and Python tests. Browser rendering/fullscreen behavior and complete TypeScript build await CI and field testing. The full RC remains gated on SSO/MFA completion and operational E2E checks.

## 2026-10-23 — Widescreen slide rulers, rotation, mobile reflow, topic Q&A and presenter preview

- White 16:9 editor canvas with percent rulers; draggable interior, edge resizing, dedicated arbitrary-angle rotation handle and stored `position.rotation` (-360..360). The earlier fullscreen and slide reordering controls remain.
- Reflow live widgets into readable stacked blocks on small screens; desktop layout retains stored rotation, mobile presentation does not rotate controls.
- Presenter dashboard previews projection/results in an iframe and links to a separate presentation screen.
- Added independent `topic-question` widgets, topic-specific PostgreSQL submissions, anonymous-by-default presenter listings with optional pseudonyms, ten questions per page, ten submissions per participant/widget, and periodic refresh. Presenter rehearsal remains browser-local.
- New focused Node rotation validation regression, migration and contract tests; see `docs/SLIDE_RULERS_ROTATION_TOPICS.en.md`. **Not yet E2E validated:** frontend npm build, browser gestures, real DB migration, mobile devices, historical live-results preview.
- Estimated RC gate closure **67%** (prior 65%); this is not production certification.

## 2026-10-23 — Accessible keyboard geometry on slide canvas (uncommitted)
- Focusable widget canvas items now provide arrow-key positioning (1 percentage point), Shift+arrows width/height resizing, and Alt+arrows rotation (5 degrees). Ctrl permits finer changes (0.1 position/size points, 1 degree rotation). All changes use existing widget position state and persistence pathways, and remain bounded by canvas dimensions. Interactive form controls are excluded from keyboard geometry handling. Visible keyboard focus styling and accessible instructions were added.
- Verification in this cycle: production backend TypeScript compilation and frontend TypeScript/Vite build **PASS** (1,579 transformed modules); Node tests **85/85 PASS**; Python tests **91/91 PASS**, including three new source/contract regressions. Keyboard interactions have **not** been exercised in a real browser with assistive technology; this is not a closed accessibility acceptance gate.
- Overall RC gate estimate remains **67%** pending real browser, database, CI, multi-replica and deployment checks. Last maintainer-confirmed CI green remains the prior baseline; all subsequent changes are uncommitted. No commit, push, tag or release performed.

## 2026-10-23 — Presenter results canvas placement and topic questions (uncommitted)
- The `results-button` on the projection screen now uses its saved complete rectangle and rotation; a legacy fallback remains available. Results stay presenter-only and use an accessible toggle region.
- The presenter Results panel includes the current activity aggregates, the timed-quiz leaderboard when applicable, and one paginated (10/page) topic-question list per topic widget.
- Local validation: backend TypeScript and frontend Vite production builds PASS; Node 90/90 PASS; Python 93/93 PASS, including two new presenter-results contract tests. No browser or PostgreSQL E2E validation in this cycle.
- **RC gate closure estimate remains 67%**. Remaining widget-specific graph settings, fully independent timed quiz widgets, and real synchronization/deployment tests are not completed. No maintainer-confirmed new CI, commit or release.

## Current cycle (2026-10-23)
2026-10-23 — Presenter `results-button` persists page aggregate visualization bars/pie/table. Backend/frontend builds and 90 Node + 93 Python tests PASS. **Still open:** per-widget configuration, multiple independent timed quizzes on a single page, browser/PostgreSQL E2E and PDF manual updates. Previous baseline CI green confirmed by user; this cycle not committed. RC gates remain 67%.

## 2026-10-23 — Timed leaderboard pagination (post-commit, pending user CI)
- Maintainer confirmed **commit and green CI** for `quorivio-0.1.0-dev-presenter-results-canvas-cumulative.zip`. This is the current commit boundary; the results-visualization cycle and this pagination cycle remain uncommitted. Older notes describing pre-boundary work as uncommitted are historical.
- The authorized presenter timed-quiz leaderboard now paginates at 20 correct responses per page with stable ordering by server-recorded elapsed time, submission timestamp and response ID. Rank numbering remains global across pages; page navigation is present in the presenter results screen and refreshes every two seconds.
- Backend and frontend production builds **PASS**; Node tests **90/90 PASS**, Python tests **93/93 PASS**. Database/browser E2E for this pagination remains outstanding.
- **RC closure remains 67%**. Independently scored concurrent timed widgets, per-widget chart settings, email MFA, cookie invalidation after MFA reset and infrastructure acceptance remain OPEN. This increment is not a release candidate.

## 2026-10-23 — MFA session revocation (uncommitted)
- Administrative MFA reset now transactionally sets `users.auth_revoked_at`, invalidating previously issued signed cookies on protected API calls and preventing revoked presenter cookies from authenticating new WebSocket connections. Existing instance-local sockets are closed as before.
- An additive SQL migration, two focused regression checks, and IT/EN technical notes were added. This addresses the previously identified stale-cookie risk, but **multi-replica socket termination and real PostgreSQL validation remain open**.
- Last user-confirmed commit/green CI was `presenter-results-canvas`; all subsequent changes remain uncommitted. RC closure estimate stays **67%** until integration gates are verified.

## 2026-10-23 — Batch security hardening (after last confirmed commit)
- WebSocket upgrade Origin now uses exact public URL origin comparison (scheme/hostname/port) instead of hostname-only comparison, matching mutating HTTP API protection; browsers from other schemes or ports cannot use a signed cookie for cross-origin live socket access. Origin-free authenticated non-browser clients retain existing behavior.
- Both presenter leaderboard endpoints reject invalid/fractional/overlarge page values with HTTP 400 instead of silently clamping or coercing. Response ranking order and page size are unchanged.
- Verified: backend TypeScript build PASS; frontend Vite production build PASS (1579 modules); Node tests 99/99 PASS; Python tests 95/95 PASS. No PostgreSQL, full browser, SSO-provider or Kubernetes E2E acceptance performed.
- RC gate audit still **37.5%** (40.0/100), with no gate advanced absent acceptance evidence. This is deliberately not a code-completion percentage.
- All developments since the maintainer-confirmed `presenter-results-canvas` commit remain uncommitted. No commit, push, tag or release performed.


## 2026-10-23 — Email MFA flow
Email MFA: login challenge endpoint, single-use PostgreSQL digest, UI and setting added; builds and code-contract tests pass; production E2E still pending.
RC weighted gate score unchanged at 37.5%; email MFA is partial until PostgreSQL/SMTP/browser integration passes.


### 2026-10-23 – Email MFA issuance hardening
Rate limit shared across replicas (3/account/minute), atomic single active challenge, migration cleanup and unique index. Build and regression evidence in `docs/EMAIL_MFA_ISSUANCE_HARDENING.en.md`. RC acceptance unchanged pending integration tests.

### 2026-10-23 — per-page uploaded backgrounds (partial multimedia cycle)
- Added `backgroundAssetId` to page/result design validation; server verifies image MIME, presenter ownership and session boundary at save time.
- Added per-page/result background asset selection and upload in the editor, and image background in presenter and participant rehearsal views.
- Public asset delivery recognizes backgrounds only on the currently open activity, preserving restricted access.
- Still open: canvas context menu, live audience visual parity, full browser/build and Kubernetes acceptance. RC weighted score held at 37.5%.

## 2026-10-23 — Canvas-first interactive page templates
- Added direct page actions for poll, quiz and timed quiz; each calls the existing authenticated activity API, uses starter options (and 30-second timed-quiz duration), refreshes the session and opens the created page in the widget editor.
- The legacy activity creation form is retained; option editing and answer-key management still use the existing activity editor. Full widget-only activity authoring is **not closed**.
- Validation: Python 146 passed (+7 subtests), Node 107 passed; production build attempted but blocked by unavailable Node typings/dependencies (`Buffer` TS2580). No browser/PostgreSQL/Kubernetes acceptance. RC remains **37.5%**.

## 2026-10-23 — canvas interactive widget configuration
- Added in-canvas configuration controls for question and timed-quiz widgets: response modes, answer options, correct answers, required responses, quiz duration.
- Preserved legacy activity APIs and editing paths. No version change.
- Local checks: 140 Python unittest cases; 107 Node tests passed. Full frontend build and browser/Kubernetes end-to-end acceptance pending.
- See `docs/CANVAS_WIDGET_ACTIVITY_EDITOR.en.md`.

## 2026-10-23 — Presenter interactive widget rendering
- Projected `question` and `timed-quiz` widgets now render their saved prompt, description, answer options, answer-mode guidance and (for timed quizzes) live countdown instead of a label-only placeholder. Correct answers are intentionally not exposed to the presenter projection.
- Text/post-it widgets also render their descriptions. Added responsive overflow handling and 3 static regression tests.
- Local validation: Python unittest discovery 145 passing (runner also prints a recover-CLI diagnostic during import), Node 107 passing. `npm run build` attempted and failed due to missing Node typings (`Buffer`, TS2580); browser, PostgreSQL and Kubernetes acceptance not performed. Weighted RC remains 37.5%.
- Open: participant/presenter end-to-end parity, full widget-only authoring, browser builds and Kubernetes verification.

## 2026-10-23 — Canonical timed-widget revision semantics
- Normalized timed-quiz answer-key comparison to match the live scorer: for single choice the nonempty legacy `correctOptionId` takes precedence; a one-element `correctOptionIds` array is equivalent when the legacy field is absent. Multiple-choice widgets use `correctOptionIds`. Default timed-quiz mode is single and duration is 30 seconds.
- Prevents spurious answer-revision increments and unnecessary rejection of live cosmetic/format-preserving edits. Genuine answer-key and duration changes remain protected.
- Added two Node regression tests; 109/109 Node tests passed and 145/145 Python unittest cases passed. Full TypeScript production build and Kubernetes/browser/PostgreSQL acceptance not validated in this cycle. RC remains 37.5%.
- Open: full widget-only authoring, live end-to-end, MFA/profile asset checks, production build and Kubernetes acceptance.

### 2026-10-23 — Timed widget database-clock consistency
- Timed widget submission checks expiry and computes elapsed milliseconds from the same PostgreSQL `clock_timestamp()` captured on the locked activity read, instead of each Node.js replica's system clock.
- Regression tests: `tools/tests/test_widget_database_clock.py`; local Python unit discovery 147 passed, Node API suite 109 passed.
- Production TypeScript build and real PostgreSQL / Kubernetes multi-replica browser validation remain pending; RC gates and baseline 37.5% unchanged.

### 2026-10-23 — PowerPoint editable portability groundwork
- Added `tools/pptx_portable.py` for PPTX text boxes -> portable Quorivio editable text widgets and portable JSON -> PPTX static text slides (opt-in `python-pptx`).
- Fixed the proprietary JSON importer to accept exported slide pages (previous export/import incompatibility).
- Added mobile editor/participant layout constraints and touch targets without altering stored canvas geometry.
- Verified standalone converter tests; full graphical format fidelity, direct in-browser PPTX editable import/export and touch-device acceptance remain OPEN. See `docs/POWERPOINT_PORTABILITY.md`.
- Release gate percentage unchanged pending full build, browser and Kubernetes acceptance.

### 2026-10-23 — Editable PPTX text-style round-trip
- Extended the optional text-box converter to retain explicit font family, point size, bold, italic and fixed RGB color on PPTX import/export. Local styled PPTX round-trip passed. Mixed formatting, master/theme semantics, in-browser export, production build and device acceptance remain OPEN. RC gate score unchanged at 37.5%.

### PPTX editable import hardening (2026-10-23)
- CLI: pre-parse OOXML ZIP size, entry-count and macro/executable checks, plus permitted-font filtering for portable import. New Python regression tests.
- Pending: editable PPTX import/export in browser, faithful rendering of non-text shapes, complete mobile E2E and acceptance gates.

### 2026-10-23 — Incremental editable PPTX + mobile interaction
- PPTX CLI: derive page headings from source text and round-trip text-box rotation; regression test added.
- Mobile: increase participant radio/checkbox touch targets and normalize response text areas without changing stored geometry.
- Validation: Python unittest discovery 153 passed; `npm test` 111 passed. Full frontend build and browser/Kubernetes acceptance not verified.
- PowerPoint fidelity, browser PPTX import/export, embedded shapes/assets and mobile device acceptance remain OPEN; weighted RC stays 37.5%.

### 2026-10-23 — Browser-integrated editable PPTX import/export
- Added authenticated `POST /api/presentations/import-editable` (creates a new editable session) and owner-authorized `GET /api/sessions/:id/export.pptx`, with Dashboard controls.
- Conversions run in the existing isolated converter service through `/portable-import` and `/portable-export`, with opaque job IDs, worker token, reservation locks, bounded input/output, malware scanning on import and temporary workspace cleanup. Converter image installs pinned python-pptx 1.0.2.
- Imports editable text boxes, positions, rotation and a subset of formatting; only supported text/interactive widget representations export to PPTX. Interactive activities become static visual content in PowerPoint. Original image-based PPTX/PDF import remains available as a separate fidelity-first option.
- Validation: 155 Python unittest cases and 111 Node.js tests passed; isolated PPTX worker round trip passed. Production TypeScript build FAILED owing to missing installed Node type definitions; no browser, cluster or database E2E run. Browser integrated fidelity and service deployment remain UNACCEPTED; RC gate unchanged at 37.5%.

### 2026-10-23 — PPTX import fidelity reporting / Rapporto di fedeltà PPTX
- Extended editable PowerPoint conversion to round-trip explicit underline formatting; added metadata-only import fidelity counts for skipped pictures, charts, tables and unsupported shapes and page overflow, returned from worker to API without including slide text or media bytes. / Estesa la conversione PPTX alla sottolineatura; aggiunto resoconto delle forme non convertite restituito dall’API senza contenuti privati.
- 157 Python and 111 Node tests passed locally. Image/shape editability, frontend build and real browser/mobile/Kubernetes testing remain open. Weighted RC unchanged at 37.5%.


## 2026-10-23 — Demo, presenza e carico
Added demo session transactional provisioning on registration/admin account creation (five activities), live cross-replica distinct participant presence widget, and authorized 500-audience staging load script. End-to-end cluster acceptance pending.

### 2026-10-23 — 500-user anonymous QR load topology
- Reworked `tools/load_500.py` to use anonymous QR invitation flow, cookie-isolated virtual participants, optional presenter and sharding across distinct load generators, optional locally bound source IPs, JSON metrics.
- Added `docs/ARCHITECTURE_500.md`, Italian counterpart, and an optional Helm staging capacity values profile; made ingress annotations configurable.
- **Open RC gate:** no actual 500-client measurement; cross-pod websocket event distribution, ingress capacity, resource sizing and synchronization require Kubernetes acceptance testing. Percentage unchanged (37.5%).


### 2026-10-23 — Fan-out reconnect hardening
Cross-pod PostgreSQL notification listener now re-synchronizes local WebSocket sessions after reconnect; tests cover recovery. Real multi-pod validation pending.

### 2026-10-23 Native PPTX geometry cycle
- Removed forced 12% × 8% minimum widget geometry from native PPTX import and API validation to preserve small objects. Added off-canvas loss reporting and round-trip geometry tests.
- RC weighted progress remains 37.5%; browser/Kubernetes acceptance and full frontend build remain unverified.

### 2026-10-23 — Native PPTX deduplicated media and OOXML validation
- Editable PPTX import now reuses a single stored asset for byte-identical PNG/JPEG objects repeated across slides; their widget instances and geometry remain independent.
- Preflight rejects unsafe/duplicate OOXML archive member names and encrypted ZIP entries.
- Regression coverage: repeated media import/export and unsafe ZIP entry rejection. Local test run: 169 Python tests and 113 Node.js tests passed.
- Browser/full TypeScript build and real PostgreSQL/Kubernetes acceptance **not validated**. Overall verified RC gate value remains **37.5%**.

### 2026-10-23 — Native PPTX import media guard
- Fixed MIME/size versus remaining media-quota precedence in `tools/pptx_portable.py`; unsupported picture formats can no longer enter staged session assets.
- Added regression coverage to `tools/tests/test_pptx_portability.py`.
- Local checks: 170 Python unittest cases passed; 113 Node tests passed. Browser, PostgreSQL, Kubernetes and production frontend build not certified in this cycle.
- PPTX native vector shape fidelity and full editing remain open. RC gate matrix unchanged pending end-to-end acceptance.


### 2026-10-23 native PPTX shape color round-trip
Post-commit development: native rectangular/rounded shape fills and strokes preserved in PPTX import/export and projection widget style. Local Python/Node checks passed; browser/K8s acceptance pending.

#### 2026-10-23 — Native PPTX ellipse and triangle shape round-trip
- Added editable shapeType support for oval and isosceles-triangle PPTX text autoshapes, including validated API styles and presenter approximations; preserved rectangle compatibility.
- Round-trip regression added, 173 Python tests and 113 Node tests passed locally. Full production build/browser/Kubernetes acceptance not claimed.
- RC gate percentage remains 37.5%; no external changes or commits performed.

### 2026-10-24 — Full-page editor unsaved edits
Added a baseline signature for widgets, headers and backgrounds; unsaved-change indicator, save-state guard, confirmation on page navigation/close and beforeunload. Full browser validation pending.

### 2026-10-24 — Full-page editor thumbnail fidelity and draft safety
- Page filmstrip previews now render the saved page's widget positions, sizes, labels, and supported background URLs instead of only the title. The preview remains read-only and is capped at 24 widgets per page.
- Reordering pages (drag-and-drop or arrow buttons) and returning to the dashboard now guard against discarding unsaved canvas edits.
- Verification: 186 Python unit tests and 113 Node tests pass locally. Full TypeScript/Vite build and actual browser/Kubernetes tests have **not** been verified in this cycle.
- RC acceptance stays **37.5%**; other features (PPTX complex elements, full mobile interaction, end-to-end multi-replica synchronization and accessibility) remain open.

## Portable Quorivio archive cycle (2026-10-24)
Implemented native self-contained `.quorivio` ZIP export/import, with asset manifest, SHA-256 verification, strict ZIP validation, fresh join credentials and a dashboard import/export flow. Legacy JSON definition-only API remains. Local checks: 190 Python and 116 Node tests passing. Real browser/database cross-instance acceptance and complete TypeScript/Vite build remain pending. RC gate stays at 37.5%.

### 2026-10-24 — Editor geometry stabilization
- Matched pointer and keyboard resize minimums to the 0.01%-sized shapes already accepted by the server and native PPTX conversion. Preserved four decimals instead of one to avoid silently enlarging tiny imported objects.
- Confirmed that keyboard geometry shortcuts ignore editable input fields.
- Local tests: 193 Python and 116 Node.js passed. No full browser/production build or Kubernetes acceptance in this cycle; RC remains 37.5%.

### 2026-10-24 — Editor ordering race hardening (post-commit cumulative)
- Serialized page-order requests while preserving unsaved-edit confirmation and full-screen editor navigation.
- Added an `aria-busy` state, disabled filmstrip dragging/reordering while a reorder persists, and ignored late order snapshots belonging to a previously selected session.
- Added targeted Python regression tests. No database migration, public API change, GitHub modification, or cluster deployment.
- This is **not** completion of the full software backlog: PPTX complex OOXML fidelity, MFA and mobile acceptance, integration/production build, security review, and Kubernetes E2E remain open. RC gate stays **37.5%**.
- Validation in this cycle: 204 Python unittest cases and 116 Node tests passed; ZIP integrity passed. Local `npm run build` did **not** pass (Node typings unavailable in this container, TS2580 in `totp.ts`); CI/browser/Kubernetes not re-run.

## 2026-10-24 — Canvas multipointer gesture ownership
- Added pointer identity to in-progress canvas gestures: secondary touches cannot start over an active drag, resize or rotate operation, and unrelated pointer moves/releases/cancels are ignored. Mouse gestures accept only the primary button.
- Updated gesture regression contracts and added two multipointer tests. Local checks: 209 Python tests and 116 Node tests passing.
- Local reproducible npm installation remains blocked: `npm install --offline` reports ENOTCACHED for `@types/bcryptjs`; TypeScript/Vite build, browser/device and Kubernetes acceptance remain unverified. This change does not close the editor or RC gates.
- Verified RC score: 37.5%, unchanged. No commits or remote mutations.

### 2026-10-24 — Unified completion audit: independent authenticator enrolment
- Removed the erroneous SMTP prerequisite from TOTP authenticator setup. TOTP is available independently of email delivery; email MFA continues to require SMTP.
- Protected the authenticator provisioning response from intermediate HTTP caching with `Cache-Control: no-store, private`; the QR endpoint already carried the same header.
- Added Node regression contracts covering independent TOTP/email enrolment and changed the older Python contract that enforced the incorrect coupling.
- Validation of this cumulative revision: Python unittest 218 PASS, API Node tests 118 PASS. Local `npm run build` FAILED because the container has no installed Node typings; this is **not** evidence of a clean production build. Integration/browser, real PostgreSQL, multi-replica, advanced OOXML, security and GDPR acceptance remain OPEN.
- RC score remains at the last validated gate level (37.5%). Do not mark the software complete.

### 2026-10-24 — Unified completion cycle / portable bundle integrity
- Hardened local/central ZIP consistency, canonical and disjoint entry layout, MIME signature checks and adversarial bundle regressions.
- Tests: 218 Python and 120 Node passing; production build and real integration are not certified here.
- See `docs/UNIFIED_COMPLETION_PROGRESS_2026-10-24.md`. RC gate remains 37.5%, not complete.

## 2026-10-24 — Native PowerPoint grouped shape recovery
- Flatten nested OOXML shape groups into independently editable widget candidates with child-coordinate transforms.
- Fidelity report explicitly marks flattened groups as lossy.
- Local verification: 223 Python, 120 Node.js API. Fresh build blocked by missing installed Node typings; not RC.
- See `docs/UNIFIED_COMPLETION_PROGRESS_2026-10-24.md` for detailed open gates.

## 2026-10-24 — Integrated macroarea continuation: chart titles and OIDC boundaries

- Native PPTX chart titles are now imported as independently editable text widgets, respecting the existing 16-widget/page limit. Chart series, axes, plot and styles remain unsupported and are explicitly counted as lossy in fidelity reports.
- OIDC ID-token claim checks reject excessively old `iat`, non-finite validity claims and validity intervals longer than 24 hours, in addition to existing issuer/audience/nonce/signature requirements. Regression tests added.
- Local evidence: 224 Python unittest tests PASS; 121 Node.js tests PASS. The full npm build was attempted but could not complete because Node TypeScript declarations are not installed in this environment (`TS2580`), not because compilation success has been established.
- **Not closed:** whole-product RC, complex PowerPoint charts/SmartArt, end-to-end MFA/SSO, PostgreSQL live participant flows, across-instance bundle import, browser/device accessibility, real 500-participant capacity, security/GDPR and reproducible CI for this revision. All require additional implementation or external validation.
- No changes to repositories, running servers or Kubernetes.

## 2026-10-24 — Cumulative integrated package handoff
- See `docs/CYCLE_DELIVERY_2026-10-24.en.md` for a verified baseline delta, performed tests, explicit blocks and acceptance next steps.
- Local compilation PASS, Node 126/126 PASS, Python 224/224 PASS; CI PostgreSQL end-to-end step added but not run locally.
- Matrix remains 40.0/100; no RC claim; no external mutations.

### 2026-10-24 integrated hardening follow-up
- `.quorivio` importer now enforces aggregate declared ZIP expansion quota before payload inflation and decodes manifest as strict UTF-8 (rejecting ill-formed bytes); exporter enforces the total compressed ZIP size bound.
- Added portable archive rejection tests. PostgreSQL, real browser/device, external SSO and 500-user live load are **not** validated in this environment.
- Local API TypeScript compilation and Node/Python suites exercised; Vite bundling blocked by archived esbuild binary platform mismatch. Do not promote RC gates solely on these tests.

## Cycle 2026-10-24 — mobile pointer gesture CSS reconciliation
- Fixed the 700px mobile breakpoint overriding canvas widget `touch-action:none` with `manipulation`, which could cancel pointer capture during drag, resize and rotation. Native form-control touch interaction retained.
- Added 3 mobile pointer regression tests (`tools/tests/test_mobile_touch_capture_contract.py`).
- Local verification: API TypeScript build PASS; frontend TypeScript noEmit PASS; Node tests 131/131 PASS; Python tests 235/235 PASS. Full Vite bundling BLOCKED by mismatched offline esbuild native binaries; retest in GitHub Actions. No browser/device or live database acceptance was performed. RC matrix unchanged: 40.0%.

### 2026-10-24 — Page reorder validation hardening
- Replaced permissive UUID-shape matching with strict UUID version/variant validation.
- Reject duplicate existing page identifiers and use linear-time set membership instead of repeated scans.
- Added three Node.js regressions; focused suite: 8/8 PASS.
- RC gate A2 remains partial pending browser and cross-device acceptance. No production infrastructure was touched.

### 2026-10-24 — Multi-gate acceleration: live authorization lifecycle
- Strategy switched to full vertical-slice acceptance; see `docs/RC_ACCELERATION_PLAN.en.md` and `.it.md`.
- Hardened the 10-second WebSocket audit to revalidate all sessions, presenter role/membership and participant membership against PostgreSQL, with fail-closed behavior on database errors. Added policy regression tests for expiration, presenter removal, role/credential revocation and participant removal.
- Local: backend TypeScript PASS; frontend TypeScript/Vite PASS; Node 138/138 PASS; Python 235/235 PASS. No PostgreSQL/multi-replica E2E evidence; B1–B4 remain partial. Matrix remains 40.0%.

## 2026-10-24 — Live delivery reliability

- Added per-session snapshot coalescing and 2 MiB slow WebSocket consumer protection; five Node regression tests. Full frontend Vite and backend TypeScript builds PASS, Node 143/143, Python 235/235. B1 remains partial pending real PostgreSQL/multi-replica and browser acceptance. See `LIVE_DELIVERY_RELIABILITY.en.md`.

### 2026-10-24 — Session-bus reconnection hardening
- PostgreSQL LISTEN reconnects if the mandatory local snapshot resynchronization fails, instead of silently leaving stale browser clients.
- Added regressions for both failed LISTEN and failed resynchronization.
- Acceptance gate B1 remains partial: no PostgreSQL multi-replica browser validation was performed.

### 2026-10-24 — Session bus stale-listener fencing and error recovery
- Fence PostgreSQL LISTEN notifications by active listener identity and lifecycle, preventing callbacks from retired connections or after shutdown from sending obsolete updates.
- On a rejected notification handler, log and force a reconnect/resnapshot rather than silently discarding the update.
- Two additional Node regressions. Full local checks: backend TypeScript and frontend Vite PASS, Node 150/150 PASS, Python 252 passed (+10 subtests).
- Gate B1 remains partial; these are simulated listener tests, not PostgreSQL multi-replica acceptance. No live infrastructure was changed.

## 2026-10-24 — Live queue error propagation and completion semantics

Changed the per-session snapshot queue so all concurrent callers await the same final coalesced update, failed reads are reported to callers after pending refreshes drain, and queue entries are cleaned after errors. Listener resynchronization no longer discards failures. Added two regression tests. Local builds PASS, Node 152/152, Python 252/252 (10 subtests). B1 remains partial until PostgreSQL multi-replica browser acceptance.

## 2026-10-24 — PostgreSQL-backed live lifecycle acceptance gate (B1–B4)

- Added `tools/ci_live_http.py` and made it a mandatory CI step following the existing PostgreSQL-backed portable/profile smoke, reusing the changed disposable admin password.
- The test creates and activates a session, opens a poll, enrolls **24 separate participants** with independent cookie jars, submits concurrently, checks exactly-once storage and duplicate idempotency, verifies aggregate report privacy, closes the poll, and rejects late answers.
- The same smoke opens a **five-second timed quiz**, checks one accepted answer, PostgreSQL-clock expiry rejection, and the report's exact count. It then closes the session and verifies public join denial.
- Added two static CI contract tests to ensure the new real-database gate cannot silently disappear or execute before the password transition.
- **Verified locally:** backend and Vite builds PASS; Node 154/154 PASS; Python 239/239 PASS; Python script compiles. **Not executed locally:** PostgreSQL HTTP smoke, WebSocket cross-replica, browser/device, or 500-client load. The CI workflow must execute the new gate on the next authorized push; no claim of green remote CI is made.
- **RC matrix remains 40.0%**. B1–B4 remain partial until runtime evidence and browser/distributed acceptance are available. This is test infrastructure, not a closed gate.


## CI hotfix after commit 22daad0 (2026-10-24)

GitHub Actions run 40128742733, job 120975700188: the PostgreSQL-backed portable HTTP test failed on first bundle import with `invalid_bundle_definition` (HTTP 400). Root cause: `portableSession()` selected PostgreSQL `reference_date` (DATE) without casting; node-postgres returns a JavaScript Date, and bundle JSON serialized it as an ISO timestamp rather than the required `YYYY-MM-DD`. Fix: select `reference_date::text AS reference_date`. Added an HTTP assertion on `/api/sessions/:id/export.json` to catch future regressions. Local API TypeScript build PASS; 154/154 Node tests PASS; 254 Python tests PASS (10 subtests). The PostgreSQL HTTP workflow must be rerun after commit; do not mark the gate accepted before CI succeeds.


### 2026-10-24 — CI concurrent live throttle hotfix
CI hotfix: PostgreSQL HTTP portable test now passes; live concurrent smoke reached the database-backed shared IP rate limit (429). Added ephemeral, 64-hex-character CI-only load token to the existing non-production bypass, preserving production throttling. CI rerun required.

## 2026-10-24 — Mandatory PostgreSQL two-replica WebSocket acceptance (after green CI baseline)

- Added `tools/ci_live_replicas.py`, a real two-process HTTP/WebSocket integration test with both API replicas connected to the same PostgreSQL 18 service.
- CI now starts the second API on port 8081, verifies readiness, executes the two-replica test, and always terminates both processes while printing their logs.
- The test validates presenter and participant sockets on opposite replicas, cross-replica activity opening, answer aggregation, activity closing, session closing, and withholding unpublished results from participants.
- CI test uses an ephemeral, non-production-only load token; production rate limits remain enforced.
- The user confirmed the previous `ci-live-throttle-hotfix` baseline committed and CI green. This change is **after** that baseline.
- Gate B1/B4 **remain partial** pending execution of the new CI gate and independent browser/500-client acceptance; do not infer success from static tests.
- Local verification for this cycle: 154/154 Node tests PASS, 242 Python tests PASS (unittest discovery), backend TypeScript and frontend Vite builds PASS. New two-replica runtime smoke is not executable locally (no PostgreSQL daemon/container); awaiting CI.

### Ten-cycle consolidated capacity / multi-replica acceptance batch (2026-10-24)

**Single-package policy:** no intermediate archives; this batch consolidates ten focused
implementation/validation interventions before the next maintainer commit.

1. Fixed aiohttp loopback IP cookie persistence for anonymous load clients.
2. Enforced UUID session identifiers and safe QR token syntax in the load CLI.
3. Enforced participant WebSocket snapshot privacy and session identity during load.
4. Recorded measured shard elapsed time for operator reconciliation.
5. Validated finite, ordered percentile summaries in the shard aggregator.
6. Added an HTTP test proving participant cookies cannot access presenter reports.
7. Asserted unpublished results remain hidden when a cross-replica activity opens.
8. Tested cross-replica duplicate response idempotency.
9. Added a post-vote WebSocket privacy check on the second replica.
10. Added an opt-in disposable 500-participant same-session CI acceptance runner, with
    ephemeral load credentials, a single presenter observer and guaranteed cleanup.

**Gate audit correction:** D2 moves from `open` to `partial` (40.0% -> 43.0%) because
the maintainer explicitly confirmed a green PostgreSQL 18 CI baseline including the
schema bootstrap and portable/profile HTTP smoke. This is a correction to the
conservative evidence ledger, not a claim of completed backup/restore or migration.
No additional gate has been accepted. The two-replica test and the 500-client test
are **not claimed passed** until the remote CI reports their results. The capacity
run is explicitly opt-in under GitHub Actions `workflow_dispatch` / `capacity_test`;
normal commits do not generate 500 clients. PostgreSQL 18 local execution, multi-
architecture runtime, browser and production-provider acceptance remain open.

**Local validation for this batch:** 154 Node unit tests, 248 Python tests, API
TypeScript and Vite production builds PASS. No live PostgreSQL or browser run in
this environment. See `docs/RC_GATE_MATRIX.json` for the 43.0% audit.

## 2026-10-24 — consolidated functional batch: disaster recovery and replica acceptance

**Baseline:** maintainer-confirmed green `ci-live-throttle-hotfix` commit. The previous ten-cycle
archive was **not confirmed committed**, and this cumulative batch retains its changes.

**Ten substantive internal interventions, one package:**

1. **Atomic backup publication:** write a private temporary archive on the destination filesystem,
   verify it and publish with an exclusive hard link, refusing overwrites and incomplete archives.
2. **Bounded archive generation:** cap individual objects, total bytes, file count and manifest size;
   hash source files without loading whole assets into memory.
3. **Strict archive path validation:** enforce canonical two-component asset paths and reject
   traversal, absolute paths, backslashes, duplicate archive members and malformed records.
4. **Backup integrity before publication:** re-open and verify the completed archive, catching
   checksum mismatch or source mutations during capture.
5. **Restore staging:** verify and stage all assets in a temporary sibling directory before
   attempting PostgreSQL restore; publish only after database restore succeeds.
6. **Destination safety:** refuse symlink/nonempty asset destinations and re-check before publication.
7. **Adversarial regression coverage:** seven additional tests cover traversal, duplicates,
   corrupt metadata, symlink destinations, failed database restores and overwrite refusal.
8. **Real PostgreSQL 18 DR acceptance:** new `tools/ci_backup_restore.py` backs up the disposable
   CI database, restores to a separate fresh database, compares user/session/activity/answer
   row counts and verifies asset bytes and overwrite rejection.
9. **Mandatory CI integration:** run the DR acceptance against the existing PostgreSQL 18 service
   and clean up the temporary restored database even on failure.
10. **WebSocket replica acceptance accuracy:** discard queued pre-vote snapshots before requiring
    a fresh participant notification; avoid falsely passing the post-vote privacy check.

**Locally verified:** 154/154 Node tests, 255/255 Python tests, backend TypeScript and
frontend Vite production builds PASS. PostgreSQL 18 fresh-database restore and the two-replica
WebSocket scenario require the next CI run. No claims of remote execution or RPO/RTO
acceptance are made. D2 remains `partial` and the overall gate audit remains 43.0% until
its PostgreSQL acceptance evidence is available. No GitHub commit/push/tag/release was made.

### CI PostgreSQL 18 client hotfix (2026-10-24)
- GitHub Actions run 40133452409 failed during DR backup: Ubuntu supplied pg_dump 16.15 against PostgreSQL 18.6.
- CI now installs PostgreSQL client 18 explicitly and checks pg_dump/pg_restore versions before integration.
- Live HTTP and two-replica WebSocket acceptance passed in the failing run. DR acceptance remains pending until the next CI run.
- No RC gate was marked accepted solely on the basis of this fix.


### 2026-10-24 — PostgreSQL DR operational safety batch (post-green baseline)

Maintainer confirmed green CI with PostgreSQL 18 two-replica WebSocket and fresh-database disaster recovery acceptance. This batch makes restore refuse populated databases before `pg_restore`, rejects unreadable preflight output, verifies staged dump and assets against the original manifest again before database modification, checks regular files at archive creation, and expands adversarial tests. The mandatory CI DR smoke now verifies refusal to restore into its populated source database, schema parity, private asset permissions, and reports backup/restore durations as **CI samples only**, not RTO/RPO guarantees. Local Python suite: 261 tests PASS. The next CI has not run on these changes. D2 remains partial pending operational rehearsal, retention/encryption and production-like RPO/RTO validation; the overall audit remains 43.0%.

### 2026-10-24 — Editor functional batch: history and widget clipboard

Based on the latest cumulative PPTX/DR package (not yet confirmed committed). The
editor now offers page-scoped Undo/Redo with toolbar and Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z
(or Ctrl/Cmd+Y) outside text inputs. A pointer drag/resize/rotation is one undo
operation, even when it produces many intermediate updates; cancellation restores
the original geometry without adding a history entry. The bounded 60-step history
is reset on page changes, preserves unsaved-draft detection, and clears redo after
new edits. Widget Copy/Cut/Paste operates inside the canvas, assigns fresh widget
IDs, preserves editable options/media/style, and constrains placement to the slide.
Keyboard clipboard shortcuts are scoped to the canvas and never intercept form inputs.

**Ten functional checks:** undo, redo, divergent-edit invalidation, gesture grouping,
gesture cancellation, page isolation, history limit, copy independence, paste bounds,
and duplicate-ID rejection. **Verified locally:** 163/163 Node tests, 272/272
Python tests, API TypeScript and web TypeScript/Vite builds PASS. No real browser,
mobile device, 500-participant capacity, or new CI run in this batch. A1/A3 remain
partial and RC audit remains 43.0% until browser acceptance evidence is available.
No commit/push/tag/release performed.

### 2026-10-25 — Editor multi-widget layout batch (after last green CI baseline)
- Delivered shift-click multi-selection, Ctrl/Cmd+A, accessible selection checkboxes and deselection, ten alignment/size/distribution actions (left/right/top/bottom/center X/Y, same width/height, distribute X/Y).
- Geometry is constrained to the 0–100% canvas; operation updates are atomic and share existing per-page undo/redo. Selection remains page-scoped because the editor is keyed by session/page.
- Evidence: 171/171 Node tests, 272/272 Python tests, TypeScript API/web builds PASS; new arrange-widget unit suite PASS.
- Browser acceptance NOT passed: headless Chromium was available but navigation to localhost and file URLs was blocked by the execution environment (`ERR_BLOCKED_BY_ADMINISTRATOR`). Optional `tools/ci_browser_editor.py` provided for an unrestricted Playwright host. No fabricated browser sign-off.
- RC A1 remains partial and verified score unchanged at 43.0%; real-browser interaction, persistence, PPTX corpus and 500-participant capacity remain open.


### Chromium browser acceptance navigation hotfix (2026-10-25)

The GitHub Actions browser gate failed because the Playwright fixture expanded the session details but never clicked the nested Open session button. The test now opens the session dashboard before requesting the page editor. Browser rerun is pending; no A1 acceptance claimed.

### 2026-10-25 — 30-intervention conversion/atomic-publication batch

**Committed baseline:** audience 20-cycle package; GitHub run 40144692900 quality and container build SUCCESS, browser editor + real PostgreSQL participant acceptance PASS, publication SKIPPED. The earlier 500-user opt-in PASS remains valid.

Delivered 30 grouped functional/security interventions across flattened PPTX admission, PDF rendering, input identity, numeric slide order, PNG validation and quotas, private atomic import/export, strict worker HTTP and mandatory CI conversion prerequisites. See `docs/RC_CONVERSION_30_CYCLES.en.md` and `.it.md` for the exact 30-item inventory, remaining criteria and tests.

**Local:** 215 Node, 340 Python (58 new), TypeScript API and Vite web builds PASS; real 12-page Poppler PDF and LibreOffice PPTX conversion PASS. **New CI not run.** D4 remains partial; overall RC audit stays **45.5%**. No commit/push/tag/release.

### 2026-10-25 — Second 30-intervention batch, both conversion batches uncommitted

The confirmed committed baseline is Audience 20 Cycles. Both the preceding conversion 30-intervention batch and this second 30-intervention batch remain **uncommitted** and are combined in the new cumulative package. Improved full PNG/JPEG stream verification, OOXML admission and XML relationship parsing, fail-closed export preflight, media budgets, atomic exclusive PPTX/JSON publication, private permissions, SHA-256 source identity and worker-root symlink rejection. Detailed inventory: `docs/RC_CONVERSION_SECOND_30_CYCLES.en.md`. Local checks: **375 Python, 215 Node, API/web builds PASS**. New GitHub CI has not run. D4 remains partial; RC **45.5%**. No commit/push/tag/release.


### 2026-10-25 — Third 30-intervention conversion batch, still uncommitted

The cumulative package now includes **90 interventions since the confirmed Audience 20 Cycles commit**. Added full PNG chunk CRC and pixel decoding, encrypted/JavaScript PDF rejection, complete OOXML XML/DTD/URI/ActiveX/OLE/macro preflight, and strict worker HTTP Bearer/framing handling. **43 new behavioral tests** (418 Python, 215 Node); backend/frontend builds PASS. See `docs/RC_CONVERSION_THIRD_30_CYCLES.it.md` and `.en.md`. New GitHub CI and container build are still pending; D4 remains partial, **45.5%**. No commit/push/tag/release.

### 2026-10-25 — Fourth 30-case conversion hardening batch (still uncommitted)

Added OOXML relationship, encoded URI/path, traversal, numeric geometry, font, color, shape-type, media-ID and symlink safeguards. Export now serializes verified image bytes without reopening mutable media paths. 30 new behavioral regressions: **448/448 Python PASS**. Node/build not rerun because npm dependencies are absent locally. New CI and container build pending. Details in `docs/RC_CONVERSION_FOURTH_30_CYCLES.en.md`. Declared cumulative total since Audience commit: **120 interventions/checks**; **45.5%** unchanged, D4 partial. No commit/push/tag/release.


### 2026-10-25 — Fifth conversion batch: native slide backgrounds and text alignment (uncommitted)

Thirty real PPTX behavior scenarios now cover editable solid RGB backgrounds, horizontal text alignment and vertical anchoring, negative export admission and truthful fidelity warnings for gradients/mixed alignment. API validates the new style and page properties; editor, presenter projection and rehearsal expose them. Added six Node API tests. **221 Node, 478 Python, API/web production builds PASS locally**. The five conversion batches since the committed Audience 20 Cycles baseline total **150 distinct interventions/checks**, not 150 new macrofeatures. CI and independent real-world PPTX visual corpus pending; RC remains **45.5%**, no commit/push/tag/release. Inventory: `docs/RC_CONVERSION_FIFTH_30_CYCLES.en.md`.

### 2026-10-25 — Seventh 30-case conversion batch (210 uncommitted cumulative)

Native PowerPoint picture crop now survives editable import/export as fractional metadata, with deduplicated original images, crop-aware projection/rehearsal, keyboard-accessible crop editor and reset, strict API/export validation and truthful loss reporting for unsupported negative overscan. 30 acceptance scenarios include 12 actual LibreOffice/Poppler image comparisons. Local **225 Node / 548 Python PASS**, API/web builds PASS. See `docs/RC_CONVERSION_SEVENTH_30_CYCLES.en.md`. CI not yet run; A3/D4 partial, RC **45.5%**. No commit/push/tag/release.

### 2026-10-25 — CI TS17001 hotfix after committed editor 90-cycle batch

Maintainer confirmed the 90-cycle editor package was committed. GitHub run `40209267607`, quality job `121216807167`, failed at the web production build (`apps/web/src/main.tsx:568`, TS17001): the conflict-inspection button declared `disabled` twice. Fixed by combining both disable predicates into a single JSX attribute (`pageSavePending || !!mergeCandidate?.local`), preserving both guards. Added `tools/tests/test_editor_jsx_duplicate_disabled_hotfix.py` regression. GitHub quality gate stopped after 314/314 Node tests passed; container build and publication were skipped, not failed. The next commit contains **only this hotfix**; no new 30-intervention batch. The new GitHub CI and Chromium/PostgreSQL end-to-end acceptance remain pending. RC gate A1 remains partial; overall audit **45.5%** until new evidence. No commit/push/tag/release by the assistant.
