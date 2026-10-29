# Quorivio 0.1.0-dev — independent release-candidate acceptance protocol

**Scope:** the 17 currently partial RC gates. Local/automated CI coverage is **not** independent operator acceptance. Neither a generated checklist nor a new test suite promotes a gate automatically.

For each gate, record the exact revision, deployed image digest, UTC time, independent reviewer, device and OS/browser versions, dataset, PASS/FAIL/BLOCKED outcome, redacted screenshots/logs, ticket and approval. Never attach raw credentials, personal information or recovery tokens. Accept a gate only when **all** residual conditions in `docs/RC_GATE_MATRIX.json` have independently reviewed evidence.

## Native browser engines

The explicit GitHub Actions input **`cross_browser_test=true`** installs native Firefox and WebKit in a separate optional job. Tests cover the compiled production modal TypeScript module, public 16:9 stage/reading controls and real built React presenter/editor preview at desktop 1440px and mobile-sized 390px viewports. Test screenshots and diagnostics are uploaded on failures. These are engine-level automated checks, **not** genuine physical-device testing, pixel accuracy certification, an accessibility screen-reader audit or legal sign-off. Native browser tests have **not** yet passed remotely on this revision.

When Playwright browsers are installed locally:

```bash
npm run build
python3 tools/ci_cross_browser_rc.py --engines firefox webkit
python3 tools/ci_rehearsal_singleton_offline_chromium.py --engines firefox webkit
```

Unavailable engines must fail closed, never silently fall back to Chromium. After committing, run `workflow_dispatch` with `browser_test=true`, `cross_browser_test=true`, `capacity_test=true`, `publish_image=false`, `publish_latest=false`, and `rc_strict=false` while any partial gate remains.

## Remaining independent sign-offs

- **A1/A2/A3/A4:** representative visuals across editor/preview/live audience including rich text, cropping, gradients, widget stacking and thumbnails; physical drag/touch, keyboard-only and multiple browsers; NVDA, VoiceOver and TalkBack; WCAG/AGID assessment and actual devices.
- **B1/B2/B3/B4:** realistic sustained concurrent sessions, multiple replicas, impaired and recovered networks, WebSocket recovery, timed fairness, scoped statistics, percentile latency and memory with explicit operational targets. The 500-participant CI fixture is bounded and is not a production SLO.
- **C1/C2/C3/C4:** real SMTP provider failure/retry, recovery links and cross-replica MFA/session invalidation, Google/GitHub/Facebook OAuth provider consent and callbacks, real ClamAV/RWX storage and independent security/privacy acceptance.
- **D2/D3/D4/D5/D6:** real DR exercise and measured recovery objectives, encryption/key rotation, ARM64, rootless Podman, NGINX/HAProxy Kubernetes deployments, RWX/ClamAV failure recovery, external pentest, third-party Office conversion fidelity, bilingual editorial/manual acceptance, GDPR/AGID and legal/operator sign-off.

Gate evidence must be linked and reviewed before editing statuses. Recompute `python3 tools/rc_gate_audit.py` and require `python3 tools/rc_release_preflight.py --strict` to pass before calling the RC ready.
