# MFA recovery codes — Quorivio 0.1.0-dev

Each TOTP activation generates ten random, one-time 128-bit recovery codes, shown once in the UI. Store them securely offline. At login enter one in the alternative recovery-code field if the authenticator is unavailable. A used code is atomically deleted from PostgreSQL and cannot be reused. The MFA panel can rotate all codes (revoking previous ones) after password and TOTP verification. Disabling MFA deletes the codes.

Only HMAC-SHA256 digests keyed with AUTH_SECRET are persisted. Changing AUTH_SECRET invalidates all stored codes. Never log raw codes. A verified administrative out-of-band process for loss of both authenticator and recovery codes is not implemented. Real PostgreSQL/browser E2E verification is pending. External SSO is still outstanding.
