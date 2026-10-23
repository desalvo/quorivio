# Email MFA: issuance and concurrency hardening

The login flow now limits challenge issuance to three attempts per user per UTC-minute bucket via the PostgreSQL-backed rate-window table. The challenge is replaced with a single atomic `INSERT ... ON CONFLICT(user_id) DO UPDATE`. An incremental unique index ensures a single outstanding challenge per user; a migration cleanup retains only the latest historic row before creating the index.

Checks: TypeScript backend build, Vite frontend production build, Node tests, Python regression tests where available. **Not yet validated:** real SMTP delivery, concurrent PostgreSQL connections, live multi-replica scenarios, browser flow, and network fairness. Do not mark these RC gates accepted.
