# Quorivio RC evidence audit — 27 October 2026

## Certified weighted score: 53.0% (previously 48.0%)

This is an evidence-scored **readiness index**, not code coverage or a legal compliance certificate. The weight policy is `accepted=1.0`, `partial=0.5`, `open/blocked=0`. We promote only two gates from **open → partial** based on completed GitHub Actions evidence and explicitly retain the remaining missing validations.

| Gate | Weight | Before | After | Index delta | Verified scope |
|---|---:|---|---|---:|---|
| A4 — mobile/accessibility baseline | 6 | open | partial | +3.0 | Real Chromium desktop/mobile touch, pointer and keyboard editor/participant journeys |
| D3 — distribution/runtime platforms | 4 | open | partial | +2.0 | Manually authorized multiarch `linux/amd64` + `linux/arm64` publish, SBOM/provenance |
| **Total** | | | | **+5.0** | **53.0%** |

### Evidence receipt

- **Full CI run:** `40517573850`, commit `e372a3aec8ba6b028283e9d00f68305a39562ed8` (already committed by maintainer).
- **Quality job:** `122235650919` SUCCESS; Chromium UI, real PostgreSQL editor conflict/persistence, participant QA and moderation, timed fairness/atomic limits, two-replica WebSockets, optional 500 participants, MFA, DR.
- **Container gate:** `122238333840` SUCCESS, image scan and build.
- **Manually authorized publication job:** `122239629249` SUCCESS. Registry: `docker.io/desalvo/quorivio`, tags `latest` and `sha-e372a3aec8ba`, digest `sha256:2be79bc6ca99fa22b6f970c8bb97d9162b4943dafd27c80d3eb1b60ebc474e41`. Buildx provenance covers both CPU architectures; this **does not** demonstrate ARM64 execution.

### New post-commit changes (not yet CI-accepted)

- Editor sidebar: accessible thumbnail keyboard reorder `Alt+ArrowUp` / `Alt+ArrowDown` alongside normal arrows for navigation; page draft guard and existing serialized server ordering retained.
- `Escape` from a thumbnail context menu closes it and restores keyboard focus to its trigger.
- Reorder communicates pending/saved/failed states in an unobtrusive ARIA live region.
- Tests ensure page-switching vs page-reordering semantics, focus recovery, status announcements and concurrency fences.

### Why other gates remain partial

A1/A2/A3, B1–B4, C1–C4, D2/D4–D6 lack one or more of independent cross-browser/screen-reader tests, physical devices, production-like latency, provider validation, deployment drills, security/privacy reviews, representative Office corpus, or operator acceptance. In particular, success in Chromium and PostgreSQL does **not** by itself justify promoting B2 or B3 to accepted. A4 is *partial*, not certified WCAG/AGID. D3 is *partial*, not proof of ARM64 or rootless deployment.

The RC preflight must remain `release_candidate_ready=false`. No release, commit, tag or push is authorized by this audit. Next: CI standard + Chromium after the thumbnail changes; controlled multi-engine/device tests; ARM64, Podman and Kubernetes deployment receipts.
