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
5. SSO: Google, Facebook, GitHub, OIDC/SAML 2.0 and authorized INFN AAI validation.
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
