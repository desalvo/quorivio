
### Latest development cycle — Concurrent authoring

After green CI 40192172978 (quality, container build and publication), this batch introduces PostgreSQL protection against concurrent page saves, explicit conflict recovery without silent draft loss, corrected background dirty tracking, and new real PostgreSQL/Chromium acceptance. This new batch is **not yet CI-verified**; see `docs/RC_EDITOR_NINTH_30_CYCLES.en.md`.

**Development checkpoint (2026-10-25):** Eight uncommitted conversion batches, 240 cumulative acceptance/intervention cases since Audience 20 Cycles CI-green commit; new editable PowerPoint shape fill/outline fidelity. Local: 583 Python + 232 Node PASS, API/web build PASS. GitHub CI not yet rerun; RC 45.5%. See `docs/RC_CONVERSION_EIGHTH_30_CYCLES.en.md`.

> **Latest development cycle (2026-10-22):** Transactional session page ordering and definition-only page duplication are implemented in source. See `docs/PAGE_SEQUENCE.en.md` / `docs/PAGE_SEQUENCE.it.md`. Local unit tests passed; browser/PostgreSQL integration and production validation remain pending. Functional estimate **80%**, readiness **35%**.

# Quorivio — 0.1.0-dev

**Author:** Alessandro De Salvo <braket71@gmail.com>  
**Source:** https://github.com/desalvo/quorivio  
**License:** EUPL-1.2 (see LICENSE; official full-text inclusion pending)  
**Docker:** `desalvo/quorivio`

[Italian README](README.it.md) · [CI / Docker Hub setup](docs/GITHUB_DOCKERHUB.en.md) · [User manual](docs/manuals/user-guide.en.pdf) · [Administrator manual](docs/manuals/admin-guide.en.pdf) · [Kubernetes wizard](docs/KUBERNETES.en.md)

## Project overview · 0.1.0-dev

Self-hosted interactive polls and quizzes, built with React/TypeScript, Express, PostgreSQL and WebSockets. **Early development prototype, not production-ready.** Source code license has **not** yet been decided; no license grant is implied.

## First run (Docker Compose)

1. `cp .env.compose.example .env`
2. Replace **every** placeholder with long random values. `AUTH_SECRET` must be at least 32 characters; `ADMIN_PASSWORD` at least 12.
3. `docker compose up --build -d`
4. Open `http://localhost:8080` and log in with `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
5. Create a session, add a poll or quiz, click **Avvia**, download QR as PNG/SVG, and open the URL with a different browser or mobile device. Present the independent PowerPoint/PDF however you like; the QR points to Quorivio.
6. Open **Schermo pubblico** in an authenticated presenter's second browser tab.

**Note:** `PUBLIC_BASE_URL=http://localhost:8080` QR codes work only on the host itself. Set the URL to the real HTTPS hostname when participants use their own phones. A TLS reverse proxy is required for external deployment. The Compose ports deliberately bind to loopback only; expose through your reverse proxy. Do not expose the app directly to the Internet as-is.

Podman (Compose provider required): `podman compose up --build -d`. Podman rootless, the Kubernetes chart and all deployment variants are **not yet validated**.

## Local development

Node 22+, PostgreSQL 17+: `npm install`, set `DATABASE_URL`, `AUTH_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `PUBLIC_BASE_URL=http://localhost:5173` and run `npm run dev:api` and `npm run dev:web` in separate terminals. If using Vite port 5173, set the API's base URL accordingly to allow browser Origin validation. Local DB schema is initialized automatically on API startup.

Run `npm test` for pure-domain tests and `npm run build` to compile. Environment-sensitive tests require working database and application containers; these are outstanding.

## Current capabilities

- Password login for one bootstrap administrator; HTTP-only SameSite cookies; data scoped by session owner for presenter routes.
- Session creation, permanent join URL for configured expiry (currently one day), join code, downloadable PNG/SVG QR.
- Polls and quizzes with single-answer options; quizzes have optional 30-second server clock; one answer per participant per activity, persisted in PostgreSQL.
- Presenter's live results, separate full-screen results, CSV export, WebSocket re-synchronization.
- Anonymous participant identity stored in a secure cookie; participants never receive correct quiz choices from live event snapshots.
- UI includes Italian/English language toggle for some labels; full locale coverage remains open.

## Security and known limitations

This is a working-code **candidate**; container startup and end-to-end behavior have not yet been independently verified. It is not an AgID-conformity statement. The in-memory IP throttling is unsuitable for multi-replica deployments and login guessing protection needs stronger controls; administrative IAM/RBAC and federation are not yet implemented. QR/session links are shareable by design. Organizer roles and organizations exist only as an initial schema; true multi-tenant onboarding is pending. Persistent participants' browser identities can be erased by clearing cookies. Polls accept only single choices. Timer and scoring logic are basic (correct/incorrect only); leaderboard not yet available. Current WebSocket snapshots are pushed by a single Node instance; horizontal scaling requires PostgreSQL LISTEN/NOTIFY or Redis/pubsub. CSV is per session, not anonymous guarantees against server admin access. Session expiration is fixed to one day, configurable duration and revocation are pending. No full presenter/public screen anonymous sharing yet. At this stage production deployment, governance, and external SSO should not be assumed.

**Database recovery:** in an isolated maintenance environment use `pg_dump -Fc -U quorivio quorivio > quorivio.dump`; restore with `pg_restore` in a fresh database; test restore routinely. Formal automated backup/restore tests pending.

See `docs/DEVELOPMENT_STATUS.md`, `docs/SECURITY.md`, and `docs/ARCHITECTURE.md`.

## Kubernetes (experimental, not verified)

Use the draft chart at `helm/quorivio`. Provision a PostgreSQL database and a Kubernetes secret named `quorivio-secret` with keys `DATABASE_URL`, `AUTH_SECRET`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD`. Build/push an image under a registry you control and set `--set image.repository=...`; set HTTPS `publicBaseUrl` and configure ingress and TLS. Run `helm template quorivio ./helm/quorivio` to inspect manifests prior to install. The chart is **not tested**; replicas must remain **1** until cross-replica events and shared rate limiting are implemented.

### Kubernetes and GDPR (work in progress)

The standalone wizard now supports NGINX and two HAProxy legacy annotations, internal PostgreSQL 18 or external TLS PostgreSQL. See [Kubernetes](docs/KUBERNETES.en.md) and [GDPR register](docs/GDPR.en.md). These changes are not cluster-tested or certified GDPR compliant.

### Data lifecycle APIs (development)

Authenticated session owners can revoke a session (`POST /api/sessions/:id/revoke`), erase it and its dependent rows (`DELETE /api/sessions/:id`), or set retention (`PATCH /api/sessions/:id/retention`, JSON `{ "retention_days": 90 }`). A periodic cleanup deletes closed/expired sessions after the retention window. These features require PostgreSQL integration and privacy review before production use; see `docs/GDPR.en.md`.


## Development progress

Feature completion **34%** (`███░░░░░░░`), production readiness **36%** (`████░░░░░░`). These are estimates, not certification or deployment approval. See `docs/DEVELOPMENT_STATUS.md`.

Updated participant, presenter and administrator manuals (IT/EN) are available in `docs/manuals/` and from the web UI. Regenerate with `python3 tools/generate_manuals.py`.

### Identity and rich-media development (0.1.0-dev)

This cumulative introduces pending-approval registration, basic admin user CRUD and role approval, mandatory bootstrap password rotation, named anonymous participation with necessary cookies, a configurable external URL, page design references and a participant-results visibility toggle. These are development features, **not production-validated**. SSO, TOTP/email MFA, SMTP/SMTPS, secure file uploads, result page editor and XLSX export are not complete; see `docs/REQUIREMENTS_IDENTITY_MEDIA.en.md`. Demo `000000` admin bootstrap requires explicit `ALLOW_INSECURE_DEV_BOOTSTRAP=true` outside production.

### Collaborative sessions and upload settings
See [documentation](docs/COLLABORATION_BACKUPS_UPLOADS.en.md). Wizard `--set max_upload_mb=100` emits the ingress limit; changing admin setting does not automatically redeploy Kubernetes. File ingestion and complete admin backup/restore are not implemented yet.

Detailed bilingual role manuals are generated using `python3 tools/generate_manuals.py` (requires reportlab and Pillow). Each manual includes an operational walkthrough, troubleshooting and feature-status caveats.


Session raw binary upload development notes: [docs/ASSET_UPLOADS.en.md](docs/ASSET_UPLOADS.en.md).

### Session asset workflows (development)

Presenter-side upload, inventory, authenticated opening and removal plus aggregate JSON session reports are documented in [Asset workflows](docs/ASSET_WORKFLOWS.en.md). Platform admins can configure the upload maximum (default 100 MB), and must regenerate Kubernetes Ingress resources if the limit changes. This is not a complete session export or database backup.

### Offline instance maintenance

For PostgreSQL + private-asset backup/verify/restore use `tools/instance_backup.py`, following `docs/INSTANCE_BACKUP.en.md`. A Kubernetes asset PVC can be configured through `asset_storage_size`, `asset_storage_class`, and `asset_access_mode` in the standalone wizard. This is **not** yet an administrator UI workflow or production-validated disaster recovery process.

Quiz and reactions: [English guide](docs/QUIZ_REACTIONS.en.md).

Widget composer: rating 0–10, reactions, text, divider, timer/QR placeholders; reorder drag & drop. See docs/WIDGETS.en.md.

## Audience tools (development)
The 0.1.0-dev application includes session-scoped word frequency contributions and moderated Q&A with unique audience upvotes. See `docs/AUDIENCE_TOOLS.en.md`. Real database and browser integration tests are pending.

### Rich page widgets (development)
Rating titles are required; ratings support optional participant comments (up to 1,000 characters). Question widgets, per-widget formatting and limited animations are available in the page editor. Full canvas/page-sequence editing and independent per-widget answers are not complete. See `docs/PAGE_WIDGET_EDITOR.en.md`.

### Independent question widgets
Presenters can place multiple independent question widgets on an activity page. Each collects a distinct response (single/multiple choice, text or existing file reference). See `docs/INDEPENDENT_QUESTION_WIDGETS.en.md` for API and validation details. PostgreSQL/browser integration is pending.

Independent question widget revision tracking and per-revision presenter aggregates: see [guide](docs/WIDGET_REVISIONS.en.md).

Participant file-widget upload: see `docs/PARTICIPANT_UPLOADS.en.md`; not yet production-validated.

Streaming uploads: presenter and participant binary uploads use bounded private temporary files; see `docs/STREAMING_UPLOADS.en.md`. Not yet production validated.

### Offline presentation conversion (development preview)

`python3 tools/import_presentation.py slides.pdf ./slides-rendered` converts PDF and PPTX sources into PNG pages and a verified manifest. See [English presentation import guide](docs/PRESENTATION_IMPORT.en.md). This is **not yet integrated** with session UI/API. Render external documents only inside a properly isolated worker in production.


### Integrated slide pages / Pagine slide integrate

Integrated slides: upload a batch of PNG/JPEG/WebP images in the presenter workspace to append slide pages; PDF/PPTX must first be converted offline using tools/import_presentation.py. Direct browser conversion is pending.

### MFA and SMTP (0.1.0-dev)

Local login now supports optional TOTP MFA with confirmation, and environment-configured SMTPS provides an administrator-only configuration check and test message. See `docs/AUTHENTICATION_SERVICES.en.md` for requirements and restrictions. Social and generic OIDC SSO integrations remain open.

### Password recovery (development)
The login screen supports SMTPS-delivered, one-time password reset links. Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` and HTTPS `PUBLIC_BASE_URL`. See `docs/PASSWORD_RECOVERY.en.md`. MFA stays enabled after a reset. This workflow requires production integration and security testing.

MFA includes ten one-time recovery codes shown upon TOTP activation; see `docs/MFA_RECOVERY_CODES.en.md`. Live PostgreSQL/browser testing remains pending.

### Federated authentication (development)

Experimental OpenID Connect login and explicit account linking are available for configured Google, generic OIDC or custom OIDC issuers (see `docs/OIDC_SSO.en.md`). This does not enable GitHub/Facebook OAuth or SAML. Real provider acceptance and multi-replica handling are pending; do not enable federation in production without testing.

### Social OAuth integrations (development)
GitHub and Facebook OAuth2 account linking and sign-in are implemented as opt-in HTTPS flows. They require registered provider clients, are not validated with live providers, and are not multi-replica ready. See `docs/SOCIAL_OAUTH.en.md`.

### Antivirus uploads (new, optional integration)

All participant/presenter uploads and web presentation sources can be scanned via a private ClamAV `INSTREAM` service. Configure `QUORIVIO_AV_REQUIRED=true`, `CLAMAV_HOST`, optionally `CLAMAV_PORT=3310`; the default is not production-safe. The bundled Compose service or Helm pod sidecar is started with Quorivio; validate it with a real container runtime. Details: [Antivirus uploads](docs/ANTIVIRUS_UPLOADS.en.md).


Custom OIDC SSO provider registration: `OIDC_PROVIDERS_JSON` (see `docs/OIDC_PROVIDERS.en.md`).


## Managed antivirus and SSO setup

The application stack automatically starts private ClamAV with fail-closed uploads. Standard Google, GitHub and Facebook endpoint defaults are built in; provide the registered client credentials and redirect URIs. See [Deployment guide](docs/MANAGED_ANTIVIRUS_AND_SSO.en.md).


Isolated presentation converter: see [deployment instructions](docs/ISOLATED_CONVERTER.en.md). Configure `QUORIVIO_WORKER_TOKEN` before enabling stack conversions.

### Development checkpoint — seventh uncommitted conversion batch (2026-10-25)

The current cumulative development package contains **seven uncommitted conversion batches (210 intervention/acceptance items)** after the last maintainer-confirmed green Audience 20 Cycles commit. The latest batch preserves editable native PowerPoint picture crops through import, canvas metadata, browser projection/rehearsal and PPTX export. Full evidence and 30-case inventory: [`docs/RC_CONVERSION_SEVENTH_30_CYCLES.en.md`](docs/RC_CONVERSION_SEVENTH_30_CYCLES.en.md). **GitHub CI has not yet been run on these seven batches**; no RC gate is promoted.
