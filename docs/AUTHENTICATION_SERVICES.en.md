# TOTP authentication and SMTP service — 0.1.0-dev

## TOTP MFA

Quorivio now supports local-password authentication with a second TOTP factor (6 digits, 30-second steps, ±1 time step). After login, select **Configure MFA**, import the provisioning link or secret into an authenticator app, and confirm a valid code. TOTP protection applies to future logins only after confirmation. Deactivation requires both the account password and a current TOTP code.

Pending and active secrets are encrypted at rest with AES-256-GCM using a key derived from `AUTH_SECRET`. Protect and retain this value; rotating it without migration makes existing secrets inaccessible. Backup recovery codes, per-account lockout, protected administrative recovery and TOTP replay rejection remain open, so do not mandate MFA in production before establishing a tested recovery process.

## SMTPS

Configure `SMTP_HOST`, `SMTP_PORT` (defaults to 465), `SMTP_SECURE=true`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_FROM` via environment/secret management. In **Administration → SMTP/SMTPS**, check non-secret configuration and send a test message. The service uses implicit TLS with certificate validation. Plaintext SMTP and opportunistic STARTTLS are not supported here. The API does not disclose stored credentials.

Actual delivery requires the `nodemailer` runtime dependency declared in the API package. No real mail server delivery has been tested. Account approvals, password resets and notification emails are not automatically sent. Credential management is environment-only for now.

## Still open

Provider integrations for Google, GitHub, Facebook and generic OIDC are not implemented; OIDC/SAML callbacks, PKCE/state/nonce, tenant mapping, password reset emails, MFA recovery, distributed per-account rate limiting and end-to-end tests remain. No AgID or GDPR certification is implied.
