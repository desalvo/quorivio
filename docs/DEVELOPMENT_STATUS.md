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
- Default container reference changed to `desalvo/quorivo:latest` in Compose and Kubernetes wizard; publish target updated to Docker Hub `desalvo/quorivo` without renaming the GitHub source repository.
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
