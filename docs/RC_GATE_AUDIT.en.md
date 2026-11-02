# RC acceptance ledger — 2 November 2026

**0.1.0-dev, RC135 full-CI-green baseline. Certified weighted score: 85.25/100; 17 independent gates remain partial. Formal release candidate NOT approved.**

Scoring convention: accepted=100% of weight, partial=50%, open/blocked=0. This is **not** code completeness or independent legal/accessibility certification.

| Area | Earned / total | % |
| --- | ---: | ---: |
| A-editor | 20.5 / 24 | 85.4% |
| B-sessions | 18.5 / 21.0 | 88.1% |
| C-admin | 16.5 / 20 | 82.5% |
| C-security | 2.0 / 2 | 100.0% |
| D-validation | 25.75 / 31.0 | 83.1% |
| B-live | 2.0 / 2 | 100.0% |
| **Total** | **85.25 / 100** | **85.25%** |

**Verified production CI:** run [41437489546](https://github.com/desalvo/quorivio/actions/runs/41437489546), commit `6c1118e93076c5d2eb8d60e96a43f8c663178053`: quality, native browsers, PostgreSQL, Podman, Kubernetes NGINX/HAProxy, real ClamAV, multiarch AMD64/ARM64 and Docker publication succeeded. **External evidence missing:** see `docs/RC136_EXTERNAL_ACCEPTANCE_EN.md` and `docs/validation/RC136_OPERATOR_EVIDENCE_REQUIREMENTS_20261102.json`. No extra RC points are attributed to the RC136 packet tool.

---

## Historical acceptance log (October 2026)

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
