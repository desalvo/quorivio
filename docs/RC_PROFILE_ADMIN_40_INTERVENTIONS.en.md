# Quorivio 0.1.0-dev — 40-item cumulative profile, media and administration batch

**Committed baseline:** GitHub Actions extended run `40304413948` passed. **Subsequent baseline:** the `presenter-profile-atomic-save-public-avatar` package; its commit has not been confirmed. This archive also contains that earlier profile cycle.

The 40 numbered items in the Italian inventory are **implementation and verification checkpoints delivered in one consolidated batch**, not 40 releases, independent CI executions or completed product macroareas. The new real PostgreSQL/Chromium checks are wired into CI but have **not yet run** for this revision.

## Workstreams

**1–20 — Image validation:** enforce a 5 MiB upload limit, verify PNG IHDR metadata, scan JPEG SOF markers, support all three WebP dimension headers (VP8, VP8L, VP8X), reject zero/oversized pixel dimensions (4096 px per side, 16 MP), mismatched MIME and corrupt headers, validate on upload and serving, and cover actual PNG/JPEG/WebP encoded fixtures.

**21–35 — Profile, privacy and UX:** authenticated role-neutral profile read with private no-store caching; automatic UI load, serialized photo/save/delete operations, disabled unavailable delete, image preview cache refresh and size guidance. Add real PostgreSQL HTTP acceptance for anonymous session-scoped avatar retrieval, private endpoint denial, replacement/deletion revocation and closed-session access denial.

**36–40 — Admin atomicity and acceptance:** one row-locked PostgreSQL transaction for nickname, role and approval, explicit uniqueness conflicts and rollback, primary-admin/self-demotion protections, conditional WebSocket permission revocation. UI has one Save User action, approval is draft-only until saved, moderator is selectable and duplicate saves are blocked. Add opt-in Chromium browser acceptance for real photo upload and anonymous retrieval.

## Local evidence and remaining gates
- Node.js **375/375 PASS** (58 additional tests beyond the previous 317).
- Python **692/692 PASS** (32 additional source-contract tests beyond the previous 660).
- Backend TypeScript and frontend TypeScript/Vite production builds **PASS**.
- New real PostgreSQL HTTP and Chromium UI integration **NOT YET EXECUTED** for this package; run workflow_dispatch with `browser_test=true`.
- Conservative weighted RC audit **45.5%**, unchanged. **Not RC-certified**.

Suggested commit if the preceding profile package has separately been committed: `feat: unify presenter profiles, secure avatar lifecycle and atomic admin user management`.

No commit, push, tag or release was performed.
