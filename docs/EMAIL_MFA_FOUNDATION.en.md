# Optional email MFA — implementation foundation (NOT ENABLED)

This cycle adds cryptographically generated six-digit challenges, HMAC-SHA256 digests domain-separated by user/challenge, constant-time verification, validated SMTP delivery with TLS, and unit regressions. These primitives are **not wired into the login path** and must not be represented as a working second factor.

Before activation implement PostgreSQL-bound single-use challenges, 5-minute expiration, maximum failed attempts, atomic consumption, race-safe issuance and resend limits, password-first flow with pending auth rather than login cookie, opt-in management via authenticated password/TOTP step-up, recovery handling, SMTP fail-closed behavior, browser flows and E2E verification. Never send an authentication cookie before completing required factors. SMTP remains a prerequisite and email MFA must be optional.

No new npm dependencies or database migrations; version 0.1.0-dev unchanged. CI confirmation is still external.
