# RC acceptance re-baseline — 23 October 2026

**Version:** 0.1.0-dev. **Weighted acceptance evidence: 37.5 / 100 points.** This replaces the previously repeated 67% estimate, which was not derived from a maintained acceptance matrix. **It does not mean 37.5% of source code has been written**, nor is it a statistically measured quality score.

The auditable source of truth is `docs/RC_GATE_MATRIX.json`. Run `python3 tools/rc_gate_audit.py` to reproduce overall and per-area values. Each required gate has a fixed positive weight (all weights total 100), a state, evidence, and an unmet acceptance condition. `accepted` earns its whole weight, `partial` earns half, and `open`/`blocked` earns zero. These values are a deliberately conservative **project-management convention**, not measured automated-test coverage. The weights and statuses must be human-reviewed against actual deployment evidence.

| Area | Weighted earned / possible | Acceptance % |
| --- | ---: | ---: |
| A: graphical editor | 9 / 24 | 37.5% |
| B: sessions and results | 11.5 / 23 | 50.0% |
| C: administration, MFA, SSO | 8.5 / 22 | 38.6% |
| D: release verification | 8.5 / 31 | 27.4% |
| **Total** | **37.5 / 100** | **37.5%** |

Existing source has substantial functionality: editor, session sync APIs, timed-widget submission, presenter results, TOTP and session revocation. None of these should be labeled end-to-end accepted without PostgreSQL, multi-browser and (where relevant) multi-replica tests. The last documented successful backend/frontend builds, 95 Node tests and 93 Python checks refer to the previous package, not an independently certified deployment.

**Mandatory external acceptance:** PostgreSQL 18 transactional/migration tests, simultaneous presenter/participant latency and fairness, browser accessibility on phone/tablet/desktop, SMTP and real OAuth/OIDC identity providers, PDF/PPTX + AV processing, ARM64/AMD64 container CI, rootless Podman, Kubernetes multi-replica and recovery, GDPR/security/license audit. Email second factor remains unimplemented; existing SMTP mail is not equivalent to email MFA.

**State changes:** Update evidence and status only after a corresponding check is actually run; preserve failure reports. CI green validates the configured CI gates, not the entire RC. The matrix can change score when acceptance evidence is collected without source changes. Do not declare RC until every mandatory gate is accepted.
