# Combined MFA and calendar acceptance — 2026-10-23

Baseline: `quorivio-0.1.0-dev-ci-k8s-credentials-hotfix-cumulative.zip`. The hotfix and this cycle are uncommitted unless the maintainer confirms otherwise. Login uses a single-use, DB-backed challenge after password verification. For a TOTP-enabled account choose Authenticator; for email choose Email to request delivery. Either successful method establishes the session, never both in sequence. A recovery code is exposed only in the second step. Rate limit is 3 email sends/minute/account and 5 verification failures/challenge. Email enrollment currently relies on already-authenticated account and password, not separate email-possession proof; this remains open.

Persistent profile uploads require a writable `/app/assets` claim owned or group-writable by uid/gid 1000. New `fsGroup` setting may be insufficient with some CSI drivers: inspect `kubectl describe pod`, PVC ownership and antivirus connectivity. Profile image downloads use authenticated URLs. Do not disable mandatory AV in production to work around an upload failure.

SSO provider list is populated on startup from `OIDC_PROVIDERS_JSON` and `OIDC_GOOGLE_*` plus social variables. With no configured credentials it is expected to be empty. Do not invent credentials. Configure redirect URIs matching deployed `PUBLIC_BASE_URL` and test provider callbacks.

Acceptance still required: MFA switching, replay/expiry, SMTP absence, recovery, concurrent requests, file upload/reload on cluster, calendar timezone/date edge cases, accessibility and full build. No release qualification.
