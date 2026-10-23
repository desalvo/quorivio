
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
- RC gate audit still **37.5%** (37.5/100), with no gate advanced absent acceptance evidence. This is deliberately not a code-completion percentage.
- All developments since the maintainer-confirmed `presenter-results-canvas` commit remain uncommitted. No commit, push, tag or release performed.


## 2026-10-23 — Email MFA flow
Email MFA: login challenge endpoint, single-use PostgreSQL digest, UI and setting added; builds and code-contract tests pass; production E2E still pending.
RC weighted gate score unchanged at 37.5%; email MFA is partial until PostgreSQL/SMTP/browser integration passes.


### 2026-10-23 – Email MFA issuance hardening
Rate limit shared across replicas (3/account/minute), atomic single active challenge, migration cleanup and unique index. Build and regression evidence in `docs/EMAIL_MFA_ISSUANCE_HARDENING.en.md`. RC acceptance unchanged pending integration tests.
