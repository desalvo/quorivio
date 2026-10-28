# Quorivio 0.1.0-dev — Password recovery hardening and scoped auth acceptance

Date: 2026-10-28. Last maintainer-confirmed commit: `a32ef78902a656262d346a0fa622604a4deda405`. All previously uncommitted changes remain in this cumulative package. The assistant has not committed, tagged or published anything.

## New integration coverage (not yet GitHub verified)

`tools/ci_password_recovery_postgres.py` exercises the **real** backend with a fresh disposable user, PostgreSQL 18, and a temporary TLS-authenticated SMTP capture. It verifies:

- Generic 202 response for absent/present email (no account disclosure), SMTP delivery only for the present account, and single issuance per account/minute.
- A 43-character bearer token carried by the received recovery link, with only the SHA-256 digest in PostgreSQL; no bearer values in logs.
- Short-password rejection, atomic concurrent redemption (exactly one success), database-backed one-use state, and refusal to reuse a token.
- Invalid token and manually expired token refusal, two previously authenticated sessions revoked, the old password rejected, and the new password accepted.
- Mandatory loopback API and PostgreSQL, explicit CI opt-in, ephemeral run ID, private mode-0600 SMTP capture and nonproduction test token.

A related security fix also makes **both password-reset confirmation and authenticated password changes atomically revoke outstanding MFA login and enrollment challenges**; the new E2E seeds stale challenge rows and proves removal after reset.

The GitHub workflow runs the new test after the existing PostgreSQL + TLS SMTP MFA test and before retention/erasure checks. This test is **pending maintainer commit + new full CI**; its success and real multi-replica/browser recovery acceptance must not be presumed.

## Conservative gate reconciliation

The previously successful GitHub full CI [40638652838](https://github.com/desalvo/quorivio/actions/runs/40638652838) verified PostgreSQL account/login/profile lifecycle, password change/session invalidation, and TLS SMTP MFA with revocation. The former partial C1 (6 weight) is split into a 2-weight **C1-AUTH accepted automated subgate** and a 4-weight **C1 partial remaining gate**. The weighted ledger stays at 100 and progresses from 65.0% to **66.0%**, 31 gates: 14 accepted, 17 partial. No credit is claimed for the new recovery test.

**Strict RC remains NOT READY.** Still pending are password-reset browser/CI acceptance, long-lived multi-replica revocation, external mail-provider deliverability, social SSO providers, physical-device and screen-reader accessibility, visual/presentation parity, Kubernetes RWX/ClamAV, independent security/AGID/GDPR/operational review.

Suggested next GitHub validation after maintainer commit: manual `workflow_dispatch` with `browser_test=true`, `publish_image=false`, `rc_strict=false`. Do not publish images as part of acceptance.

**Local validation after security fix:** TypeScript API/Web and Vite build PASS; Node backend 468/468, Node frontend 58/58, Python 944/944 PASS. PostgreSQL/SMTPS acceptance remains pending: local runtime has no PostgreSQL/psql/Docker.
