# Quorivio 0.1.0-dev — rehearsal keyboard focus and audited RC progress

Date: 2026-10-28. Baseline: last user-confirmed commit `a32ef78902a656262d346a0fa622604a4deda405`; **the previous topic-statistics cumulative package has NOT yet been committed** according to the user. Do not omit those changes from the next commit or cumulative ZIP.

## Implementation

- The presenter, participant and combined preview dialogs now use the **same** `activateRehearsalDialog` keyboard lifecycle.
- Opening the preview focuses its labelled Close control; Tab / Shift+Tab cycle through actually visible, enabled controls and recover escaped focus. Escape closes the modal. Closing restores focus to the control that invoked it (when still connected).
- Background page scrolling is locked while the modal is open and restored to its prior value on unmount. The handler is removed when the modal unmounts; the outer dialog no longer duplicates Escape closing.
- The exact TypeScript keyboard module is transpiled to a standalone script for a real offline Chromium acceptance on desktop 1440×900 and mobile-sized 390×844 viewports. The script checks focus, actual keyboard events, Escape, native button click, scroll restoration, and cleanup. Opt-in GitHub Full CI invokes it immediately after the existing dual 16:9 preview preflight.

## Local verification (not CI sign-off)

- `npm run build`: API `tsc`, web `tsc --noEmit`, Vite production build **PASS**.
- `npm test`: **468/468 PASS**; web `node --experimental-strip-types --test apps/web/test/*.test.ts`: **50/50 PASS**.
- `python -m unittest discover -s tools/tests -p 'test_*.py'`: **921/921 PASS**.
- Browser: `ci_rehearsal_keyboard_chromium.py`, `ci_preview_layout_offline.py`, `ci_widget_visual_geometry_20261028.py`, `ci_browser_rich_text_offline.py`: **PASS**.
- The authentic local Vite site remains inaccessible to Chromium here: `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Offline tests do NOT prove authenticated application flows, Firefox/WebKit, VoiceOver/NVDA/TalkBack, or physical devices. The next opt-in GitHub Full CI remains required.

## Audited evidence-scoped progress: 56.0% → 60.0%

`docs/RC_GATE_MATRIX.json` preserves a fixed sum of 100 weighted points, `accepted=1`, `partial=0.5`. Four bounded engineering gates are split out of previously broad partial gates using earlier verified GitHub CI, and are explicitly **not** credited for this uncommitted batch:

| Accepted narrow gate | Weight | Evidence | Unaccepted parent scope |
|---|---:|---|---|
| B1-WS | 2 | Full CI 40638652838: 2-replica PostgreSQL/WebSocket lifecycle and privacy | Long-running recovery/latency/SLO |
| C2-TLS | 2 | Full CI 40638652838: PostgreSQL + disposable TLS SMTP MFA end-to-end | Real providers and production deliverability |
| D2-DR | 2 | Full CI 40638652838: disposable PostgreSQL 18 backup/restore & integrity | Production-scale RPO/RTO, encryption and key rotation |
| D3-IMAGE | 2 | Multi-platform Buildx publication in 40595463258 and image build/scan in 40638652838 | Native ARM64 boot, rootless Podman, HA Kubernetes |

Each original parent loses 2 weighted points and remains **partial**; thus every split raises the weighted score by 1.0 point, for a total of +4.0, while the external obligations remain open. The new keyboard behavior is only local evidence and **is not accepted as a new RC gate**. The ledger now has **25 gates: 8 accepted, 17 partial**, score **60.0%**. `tools/rc_release_preflight.py --strict` must still fail: **NOT RELEASE CANDIDATE READY**.

## Next work and release requirements

Run standard CI and manual extended CI (`browser_test=true`, `publish_image=false`) after the user's next commit. Verify focus in editor and dashboard through the authenticated app; inspect live widget/linked topic statistics on PostgreSQL; conduct external operator parity and screen-reader acceptance. Independently validate real SMTP, production backup restore objectives, native ARM64/Podman, HA ingress, data protection and GDPR/AGID. No commit, push, tag or Docker publication made by this cycle.
