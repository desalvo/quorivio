# Quorivio 0.1.0-dev — RC cycle 9: 71.0% (+3.0 pp), 28 October 2026

**Baseline:** cumulative cycle-8 ZIP (RC 68.0%); all previous implementation preserved. **Version:** `0.1.0-dev`, license EUPL-1.2.

## Verified gate reconciliation (not speculative)

The complete GitHub Actions [run 40717525524](https://github.com/desalvo/quorivio/actions/runs/40717525524), attempt 2, commit `f6738592c648bc620e01b92d2bbaa6b90b459287`, production quality job `123073117101`, has already passed. The original matrix still bundled these independently exercised **bounded technical** areas into broad partial gates. Each parent retains independent/hardware acceptance obligations, and exactly 2 weight points are moved from it to one accepted subgate:

- **A2-ORDER** (2): desktop/mobile Chromium editor thumbnail filmstrip, pointer controls and keyboard reorder contracts. Parent A2 remains partial (4): pixel fidelity, cross-browser native DnD and real device review outstanding.
- **A4-FOCUS** (2): real TypeScript/React Chromium modal accessible focus trap at 1440/390, dynamic portal `inert`/ARIA isolation and focus restore. Parent A4 remains partial (4): NVDA/VoiceOver/TalkBack, actual touch/keyboard and WCAG/AGID review outstanding.
- **B3-QUESTION-STATS** (2): real PostgreSQL 18 three independent questions, scoped presenter-only statistics, revisions and two-participant idempotency. Parent B3 remains partial (2): independent browser/device and assistive-technology acceptance outstanding.

This evidence is **separate** from the earlier A3-AUTO editor persistence, B3-AUDIENCE QR/ballot/moderation and other accepted subgates. All weights still sum to 100. 33 → 36 gates, 16 → 19 accepted, 17 partial unchanged. **68.0 → 71.0 (+3.0 percentage points)**. The strict RC readiness gate remains false.

## Implemented in this uncommitted batch — no scoring credit yet

Password reset now requires matching password and confirmation fields, enforces at least 12 characters, prevents a second submit during the first in-flight POST and preserves retry after a failed/expired token without restoring the bearer to the URL. The existing browser no-referrer and history sanitation remain. The real compiled React Chromium fixture at 1440/390 validates mismatch rejection, synchronously duplicated clicks (one request), error/retry, success, and non-persistence of the token. It is wired to the opt-in CI but **not yet verified by a new GitHub run**.

**Local tests:** backend/frontend TypeScript + Vite build PASS; 474/474 backend Node; 62/62 frontend Node; 979/979 Python; Chromium at 1440/390 PASS. No local PostgreSQL server, physical device tests or Firefox/WebKit checks were claimed.

**Next:** maintainer commit, full GitHub opt-in `browser_test=true`, `capacity_test=true`, `publish_image=false`, `publish_latest=false`; then operator-independent cross-browser/device/AT, production Kubernetes/RWX/ClamAV and legal/GDPR reviews. No automated commit/push/tag/image publication.

**Evidence:** `docs/validation/RC_CYCLE9_VERIFIED_GATE_HARDENING_20261028.json`, `docs/RC_GATE_MATRIX.json`.
