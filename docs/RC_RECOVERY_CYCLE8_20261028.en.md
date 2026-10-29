# RC cycle 8 — verified recovery lifecycle and safer browser handoff

**Baseline**: cumulative `quorivio-0.1.0-dev-rc-ci-40709447219-gitguardian-checksum-hotfix-cumulative.zip`, 753 files; source version 0.1.0-dev, EUPL-1.2. No existing capability removed.

## Reviewed, independent existing GitHub evidence

The maintainer-supplied [GitHub run 40717525524, attempt 2](https://github.com/desalvo/quorivio/actions/runs/40717525524) at `f6738592c648bc620e01b92d2bbaa6b90b459287` has SUCCESS conclusions for quality job `123073117101`, container build, and manual publication. Crucially the real PostgreSQL 18 / TLS SMTP password-recovery step passed in the quality job. The [CI fixture](../tools/ci_password_recovery_postgres.py) asserts account enumeration resistance, private delivery, digest-only storage, throttling, atomic exactly-once consumption under concurrent replay, expiration, weak-password rejection, multi-session revocation and deletion of stale MFA enrollment/challenges. These controls were NOT credited in the previously accepted C1-AUTH, whose scope is login, ordinary password change and MFA.

The existing C1 weight (4) was divided into residual C1 weight (2, still partial) and a **new non-overlapping bounded C1-RECOVERY weight (2, accepted against that specific existing green GitHub run)**. Prior C1-AUTH weight 2 stays accepted. Both before and after, total gate weights equal 100. Thus the formal score changes 67.0% -> **68.0% (+1.0 pp)**, 33 gates: 16 accepted and 17 partial. This is a documentation/evidence reconciliation of an actually tested capability, not a claim that current uncommitted code has passed GitHub.

## New code (local-only evidence, no extra RC credit)

- `apps/web/src/password-recovery-url.ts`: consume the one-time reset bearer on React mount, remove all `reset_token` query parameters using `history.replaceState`, keep only the in-memory React state, and preserve unrelated navigation state.
- `apps/web/index.html`: opt out of referrer forwarding with `meta name="referrer" content="no-referrer"` before loading the app bundle.
- `apps/web/test/password-recovery-url.test.ts`: prevent reintroduction of query/history/token handling bugs, including empty/duplicate parameters and Unicode.
- `tools/ci_recovery_url_chromium.py`: real built React in isolated Chromium desktop (1440 px) and mobile (390 px); password reset error then retry, confirm request, URL preservation and non-persistence in browser storage. The test fixture does not connect to real PostgreSQL/SMTP.
- `.github/workflows/ci.yml`: this new Chromium regression is opt-in and runs with the existing browser acceptance chain. It requires a fresh GitHub run to count as remote evidence.

## Validation boundaries

Local checks: backend/frontend TypeScript + Vite build passed; backend 474/474 Node tests; frontend 62/62 Node tests; Python 975/975 tests; desktop and mobile built-React Chromium recovery test both passed. No local Docker, Podman or PostgreSQL 18 server was available, so live integration results are the *previously verified* GitHub run only.

Still open: independent browser recovery against real SMTP and PostgreSQL after this code, external mailbox deliverability, long-lived cross-replica auth/security, Firefox/WebKit, assistive technology, physical touchscreen, legal/privacy, and production operator sign-off. Strict RC readiness remains FALSE. No assistant commit, push, tag, release, or Docker publication.
