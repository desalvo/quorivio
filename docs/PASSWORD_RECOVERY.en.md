# Secure password recovery — Quorivio 0.1.0-dev

- The “Forgot password?” control requests an email without disclosing whether an account exists.
- SMTPS (implicit TLS) is mandatory. An unconfigured mail service returns `recovery_not_configured`.
- Links contain random 256-bit single-use tokens, expire in 20 minutes and are stored in PostgreSQL only as SHA-256 digests.
- Repeated requests for an IP/email pair are limited to one per minute; general API throttling also applies.
- Password changes clear the current browser cookie and prior signed cookies are rejected by protected API middleware.
- TOTP remains enabled and continues to be required at login.
- HTTP responses and server logs never expose reset tokens.

## Open production checks
- PostgreSQL, SMTP delivery and multi-browser integration tests have not been executed.
- HTTPS and PUBLIC_BASE_URL must be configured correctly before production use.
- Rate limiting is currently in-process, not distributed. A shared backend is required for clusters.
- Audit logging, CSRF protections for requests without Origin headers and further anti-abuse controls need evaluation.
- Google/GitHub/Facebook and generic OIDC SSO are not implemented yet.
