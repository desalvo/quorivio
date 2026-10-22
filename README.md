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
