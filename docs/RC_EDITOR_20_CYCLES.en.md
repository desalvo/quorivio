# Quorivio 0.1.0-dev — 20-intervention cumulative batch (25 October 2026)

**Baseline:** last user-confirmed commit (Chromium selection-state hotfix). GitHub Actions workflow `40141894130`, job `121015403855`: production quality SUCCESS; container build SUCCESS; Chromium opt-in PASS; 500 independent PostgreSQL/WebSocket participants PASS with presenter-observed peak >=475 and zero errors. Production publication was skipped as intended.

## Twenty concrete interventions — one cumulative package

1. Reconcile actual CI evidence into the weighted RC gate matrix.
2. Filter orphan and duplicate selected widget IDs.
3. Delete selected widget groups without modifying unselected objects.
4. Duplicate groups with fresh IDs, stable layer order and deep clones.
5. Reject duplicate-ID collisions against all existing canvas widgets.
6. Nudge groups with shared clamped displacement within canvas bounds.
7. Arrow-key movement of the entire focused multi-selection.
8. Delete/Backspace for selected groups with undo support.
9. Move the whole selection to the front with stable internal order.
10. Move the whole selection to the back with stable internal order.
11. Move a potentially disjoint selection one layer forward.
12. Move a potentially disjoint selection one layer backward.
13. Equal horizontal gaps measured between widget edges.
14. Equal vertical gaps measured between widget edges.
15. Center the selected group horizontally on the full canvas.
16. Center the selected group vertically; single-widget centering supported.
17. Repeated group paste with bounded cascading offsets and fresh IDs.
18. Extend Chromium acceptance for layers, nudging, duplication, deletion and undo.
19. Extend Chromium acceptance for mock PATCH persistence, reload, keyboard commands and 390×844 touch-capable viewport.
20. Add Node/Python regressions, rebuild API/web, update bilingual documentation and reproducible RC score.

## Verified results and outstanding acceptance

- **205/205 Node.js tests PASS** (26 added since the green baseline).
- **277/277 Python tests PASS** (3 added; two old source-string tests updated to follow the refactor).
- **API TypeScript and web TypeScript/Vite production builds PASS.**
- New Chromium acceptance **not executed locally**: local Chromium navigation to `127.0.0.1:5173` fails with `ERR_BLOCKED_BY_ADMINISTRATOR`. Run the opt-in GitHub workflow.
- Browser save/reload uses an in-memory HTTP fixture, **not PostgreSQL persistence**. Physical mobile devices and screen readers remain untested.
- The 500-participant pass belongs to the previous green CI run; no new local load test was performed.
- **RC score 45.5/100** (previously 43.0): D4 promoted from `open` to `partial` based on actual CI load and security evidence. No other gate was promoted merely because new code exists.

## Remaining RC gates

Editor browser acceptance, real PostgreSQL persistence, device/accessibility testing; PPTX real-world corpus and fidelity; live latency/fairness and participant privacy; representative staging DR and RPO/RTO; ARM64, rootless Podman, Kubernetes HA; SMTP/SSO providers, malware scanning, pentest, GDPR and license sign-off.

**Not a Release Candidate.** No commit, push, tag or deployment was performed in this batch.
