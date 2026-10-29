# Quorivio 0.1.0-dev — RC cycle 14: independently verified browser-engine evidence

**Formal result: 74.0% → 75.0% (+1.0 percentage point).** Matrix weights total 100; 42 gates, 25 accepted, **17 partial**; strict RC gate remains blocked. No artificial credit for this cycle's uncommitted tests.

## GitHub evidence reviewed, not guessed

GitHub Standard run [40846201940](https://github.com/desalvo/quorivio/actions/runs/40846201940) and manually dispatched Full run [40847463104](https://github.com/desalvo/quorivio/actions/runs/40847463104), both on commit `cf49c3e1d3e58d4ec4d65862a92b742348a11435`, completed **SUCCESS**. The full run's independent native Firefox/WebKit job **123360950163** passed on the actual TypeScript modal and public-stage CSS: Firefox 1440/390 px and WebKit 1440/390 px. Native engine binaries were Firefox 157.0 / WebKit 27.2 on Linux. The same full run also passed Chromium, PostgreSQL 18, multi-replica/capacity and container gates; Docker publication was skipped.

After reviewing the exact automated scope, **A3-NATIVE-STAGE (1)** covers actual native-engine 16:9 geometry, rotation and reading-mode target size; **A4-NATIVE-MODAL (1)** covers actual native-engine keyboard/contenteditable/modal/inert/portal/focus restoration. Each weight-1 accepted subgate was moved from a *partial* parent (A3 2→1; A4 4→3). The newly accepted tests are genuinely different from existing Chromium A3-GEOMETRY and A4-FOCUS. Net improvement: 1.0 pp, not 2.0. The parents **remain partial** for real devices, screen readers, pixel-by-pixel editorial and WCAG/AGID review.

## New batch — local only, no scored credit

The native cross-browser CI job now additionally runs `ci_rehearsal_singleton_offline_chromium.py --engines firefox webkit` against the *built React bundle*: dashboard/editor preview launch, exactly one dialog, portal outside inert roots, presenter/participant/both modes and invoker focus restoration, at 1440/390 px. This was already tested on local Chromium, **not yet on Firefox/WebKit on the changed source**. The CI remains manual opt-in and does not fall back to Chromium. Tests now enforce evidence-backed RC gate scoring and historical receipts without freezing old score values.

**Remaining signoffs:** real iOS/Android touch, NVDA/VoiceOver/TalkBack, independent graphical pixel fidelity, real network/provider/OAuth, ingress/storage+ClamAV/Podman/ARM64 operational trials, GDPR/AGID/security/legal and operator approval. A generated protocol is not an approval. After user commit, run GitHub `browser_test=true`, `cross_browser_test=true`, `capacity_test=true`, `publish_image=false`, `publish_latest=false`, `rc_strict=false`. Do not label RC ready while any partial gate exists.

Evidence machine record: `docs/validation/RC_CYCLE14_NATIVE_GITHUB_VERIFIED_20261029.json`. Current manifest: `docs/validation/RC_CYCLE14_PACKAGE_INVENTORY_20261029.json`.
