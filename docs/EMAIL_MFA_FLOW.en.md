# Email second factor — implementation status

Optional email verification can now be enabled in the account security page, provided an administrator has configured SMTP. Activation and deactivation require the current password and TOTP code when TOTP is active, and force reauthentication.

After a successful password/TOTP check, the API creates a random UUID challenge with an HMAC-SHA256 code digest, a five-minute expiry and a maximum of five attempts in PostgreSQL. No login cookie is sent until the verification endpoint consumes the challenge in a transaction. SSO connections are rejected for accounts with TOTP or email MFA enabled rather than bypassing the factor.

**Verification boundary:** TypeScript/frontend production builds and code-contract tests pass. SMTP delivery, concurrent challenge consumption, PostgreSQL migration, real browser flows, anti-enumeration and multi-replica behavior require integration tests. Email OTP is not phishing resistant; TOTP is still available. Avoid enabling in production before these tests.
