# Release Candidate gate-closure strategy — 2026-10-24

**Baseline**: 0.1.0-dev; do not rename or tag. The RC gate matrix is the sole acceptance score. Unit test success is not a substitute for end-to-end evidence.

## New execution rule: vertical slices, not isolated helpers

1. **B1–B4: live session acceptance**. Exercise owner/presenter/participant in at least two independent browsers, with two API replicas and PostgreSQL 18. Cover start/open/submit/close/revoke, latency, score and attendance. Attach WebSocket logs, DB checks, timestamps and observed vs expected results. Complete a 500-participant same-session load run with independently reconciled telemetry. Fix issues until this gate cluster is accepted.
2. **A1–A4: editor acceptance**. Run real touch/keyboard/mouse browser scenarios: resize, rotate, drag, undo/save/reload, page reorder, widget property edits, tablet/smartphone, screen reader and thumbnails. Attach screenshot/video evidence and fix regressions before closing.
3. **C1–C4: account/security acceptance**. Test independent email MFA/TOTP enroll, reset, revoke, SMTP delivery and error paths. Exercise real Google, Facebook, GitHub, INFN OIDC in staging with test credentials; admin profile photo on RWX volume, AV, concurrency and settings persistence.
4. **D2–D4/D6: deployment/security**. Execute PostgreSQL 18 migration/backup/restore, Docker AMD64/ARM64, rootless Podman, Helm with NGINX and HAProxy, security scan, dependency license review, GDPR retention/export/deletion and penetration review. Preserve auditable evidence.
5. **PowerPoint**: track OOXML fidelity independently (not explicitly represented by a dedicated RC gate). Validate round-trip by feature class, record unavoidable unsupported structures. Never claim SmartArt/chart fidelity without actual comparisons.
6. **D5: manuals**. Cross-check IT/EN manuals against verified UI and deployed flows after acceptance.

## Gate ownership and external dependencies

- Software work remains on every partial/open gate. No gate is auto-accepted merely because test scaffolding exists.
- External acceptance is needed for mobile hardware, production-like PostgreSQL/Kubernetes, real OAuth/SMTP providers, 500 concurrent clients and human editorial/security review.
- Evidence required for each closure: test command or manual procedure, environment/version, observed outcome, artifact/log path, and dated reviewer decision. Update RC_GATE_MATRIX.json only when all gate-specific criteria are met.

## This cycle's vertical-slice progress

Live WebSocket audits now validate the **session lifecycle for every connected socket**, recheck presenter membership/role/revocation, and recheck participant membership across replicas. Missing/expired sessions, deleted participants, revoked presenters, and DB outages fail closed at the next periodic audit (currently 10 seconds). The initial upgrade authorization remains in place. These are implementation hardening and unit-tested policy changes, **not** browser or multi-replica E2E acceptance.

Local checks: backend TypeScript PASS; frontend TypeScript/Vite PASS; Node.js 138/138 PASS; Python 235/235 PASS. PostgreSQL runtime and multi-replica WebSocket tests NOT executed. Score remains 40/100.
