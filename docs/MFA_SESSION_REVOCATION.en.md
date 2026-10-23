# Session invalidation following an administrative MFA reset

The privileged MFA reset now sets `users.auth_revoked_at` within the same transaction as the TOTP and recovery-code removal. The existing eight-hour signed authentication cookie is rejected by `requireAuth` when its derived issuance time predates this timestamp. Presenter WebSocket upgrades enforce the same timestamp and password-change cutoff; existing WebSocket connections on this instance are actively closed by the reset workflow. The SQL migration is additive and idempotent.

**Limits:** WebSocket connections hosted by another replica are not proactively disconnected by the instance-local close; authorization must be rechecked on reconnection. Live PostgreSQL migration and multi-replica behavior are not validated in this cycle. Cookie issuance is derived from the legacy eight-hour expiry timestamp; this is compatible with existing tokens, but a dedicated server-side session table would improve auditability.
