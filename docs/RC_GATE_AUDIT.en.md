# RC acceptance ledger — 25 October 2026

**Version 0.1.0-dev. Auditable weighted score: 45.5/100. NOT a release candidate.**

This score is a conservative gate-management convention, not percent of source written, code coverage or a production SLA. `accepted` earns 100% of weight, `partial` earns 50%, `open`/`blocked` earn zero. See `docs/RC_GATE_MATRIX.json`; reproduce with `python3 tools/rc_gate_audit.py`.

| Area | Earned / total | Percentage |
| --- | ---: | ---: |
| A-editor | 9 / 24 | 37.5% |
| B-sessions | 11.5 / 23 | 50.0% |
| C-admin | 11 / 22 | 50.0% |
| D-validation | 14 / 31 | 45.2% |
| **Total** | **45.5 / 100** | **45.5%** |

**Confirmed green CI:** GitHub Actions workflow `40141894130` (quality and container build), opt-in Chromium PASS, 500 independent participants PASS (presenter peak >=475, zero errors), two-replica PostgreSQL 18 WebSocket PASS and PostgreSQL 18 DR PASS. D4 moves from open to partial on this evidence; 43.0 -> 45.5 points.

**New editor work:** 20-intervention batch has 205 Node and 277 Python tests PASS and API/web build PASS; its expanded Chromium browser test is not yet executed in CI. The browser save/reload fixture does not constitute real PostgreSQL acceptance.

**Still open:** real device/screen-reader acceptance, full PPTX corpus, live latency/fairness, staging DR RPO/RTO, ARM64 and rootless Podman, Kubernetes HA, SMTP/SSO providers, AV/pentest, GDPR/license sign-off.


## 2026-10-28 — Full CI 40638652838 audited subgate reconciliation

Full CI verified original multi-question PostgreSQL migration, real Chromium editor, timed fairness and bounded 500 participant tests. Separate A3-AUTO, B2-DB, B4-LOAD were accepted with a total weight of 6 redistributed from three partial gates; scoring formula unchanged, score 53.0 -> 56.0. The independent remainder stays partial, strict RC remains blocked, and the uncommitted topic-linked results receive no RC credit.
