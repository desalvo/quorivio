# RC CI MFA shared-IP throttle hotfix

### 2026-10-26 — GitHub CI MFA shared-IP quota hotfix (after committed opt-in publication)

**Committed baseline**: SHA `723dda022eedb6412bb305f58f6ddab48be0e8ef` from the opt-in Docker publication and TLS SMTP MFA acceptance batch; GitHub Actions run `40349577790`, quality job `121675471288` FAILED at `tools/ci_email_mfa_postgres.py` (final `GET /api/auth/me`: expected 200, got **429**). All **433 Node tests**, production frontend/backend build and PostgreSQL profile lifecycle passed; container build was SKIPPED; importantly, Docker publication was SKIPPED as intended.

**Root cause**: the older portable/profile HTTP E2E and the new MFA E2E share the same loopback IP and PostgreSQL-backed fixed window of **100 API requests/minute**. The MFA scenario reached that quota before its final assertion; it did not demonstrate an OTP verification failure. The existing ephemeral `LOAD_TEST_TOKEN` exception is already restricted to `NODE_ENV != production`, requires at least 32 characters and is compared with `timingSafeEqual`. The MFA script now requires this token for **explicitly local disposable CI only**, sends it in both its HTTP request helpers (including parallel OTP checks), and the workflow explicitly supplies it. The generic production limiter and MFA OTP-specific attempt counters/expiry/replay controls remain unchanged.

**Adjacent CI log hardening**: both generated test tokens are registered with GitHub `::add-mask::` before being exported; the disposable SMTP startup reads its password from the runner environment instead of expanding a GitHub expression into visible script text. Secrets are test-only, never committed. Added a 5-case Python regression covering both request paths, invalid OTP status, loopback/token guards and fail-closed production policy.

**Not yet verified on GitHub**: run standard CI after this hotfix commit, requiring MFA PostgreSQL + TLS SMTP acceptance, retention, live concurrency, container build PASS and publication SKIPPED. The RC matrix remains **48.0%** (1 accepted / 15 partial / 2 open); no gate promoted on local tests. No commit/push/tag/release performed by the assistant.
