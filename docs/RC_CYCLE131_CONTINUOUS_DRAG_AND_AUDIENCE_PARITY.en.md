# RC131 — Continuous collision containment and participant typography parity (2 November 2026)

## Verified baseline

Maintainer committed RC130; GitHub Actions [41420021082](https://github.com/desalvo/quorivio/actions/runs/41420021082) at `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d` completed successfully: production quality, real Chromium and PostgreSQL, ClamAV, native AMD64/ARM64 OCI runtime/build, Kubernetes NGINX/HAProxy, Podman and full RC campaign. Docker Hub was published by explicit commit authorization. This evidence belongs to RC130, not RC131.

## Implemented in RC131

1. Replaced discretized pointer sampling (max 400 steps) with **continuous swept axis-aligned collision**: the first exact collision fraction across every selected, non-graphic widget and fixed non-graphic obstacle limits group motion. A 0.05%-wide obstacle cannot be bypassed by a long pointer jump. All selected widgets retain relative offsets; canvas boundary clamping, negative/diagonal drags, finite inputs and graphic-overlay exceptions are preserved. Invalid overlapping starting layouts remain unchanged (fail closed), not silently repaired.
2. Removed forced fixed font sizing from the **16:9 participant slide** which was overriding author-selected font sizes, particularly through the legacy mobile `!important` selector. The audience stage now receives `--authored-widget-font-size` from the same typography helper as the editor and presenter rehearsal. A later scoped rule honors it on the 16:9 stage, while the accessibility **reading mode stays at 1rem** and is not forced into the scaled slide.
3. Added seven Node regression cases for fast/narrow/diagonal/vertical/group/graphic/invalid-motion geometries. Added a native Chromium CSS/geometry test comparing actual editor, single/split rehearsal, live presenter projection and participant stage at 1440px and 390px. The test asserts normalized stage geometry and authored title/footer font, weight, color and family. Real application E2E remains mandatory; this fixture supplements it, not a substitute.
4. Preserved historical tests and source checksum receipts. Updated RC124 source contract to require analytic collision enforcement, and added RC131 early preflight plus the RC131 browser check to the existing GitHub workflow. No new publication permission and no CI gate was disabled.

## RC certification boundary

The **certified completion remains 85.25%**: 43 accepted gates and 17 independent/operator gates still partial. RC131 changes address the editor fidelity scope inside partial gates A1/A3, but cannot alone close physical iOS/assistive-device, real identity-provider, independent storage/HA, security/GDPR and manual sign-off requirements. The strict candidate gate must stay blocked. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Verification

Local Node frontend suite, targeted Python tests, TypeScript syntax and real isolated Chromium CSS geometry can be run without external credentials. **GitHub Actions RC131 is not yet executed**, so compiled React/PostgreSQL live replay, multi-browser application parity and Docker build must be checked by the maintainer's next commit. Do not publish merely to test the editor changes.

## RC131 local verification receipt (before GitHub)

- Python full suite `python -m unittest discover -s tools/tests -p 'test_*.py' -q`: **1,677 tests, OK, one skipped, zero failures**. One negative CLI test intentionally emits `--recover requires --workers-stopped` to stderr; the suite itself passed.
- Frontend Node full suite: **192/192 passed**. RC131 seven new motion regressions all passed.
- Native local Chromium CSS/geometry fixture: **1440px and 390px PASS** for editor, rehearsal, projection and audience. The test compares normalized geometry and authored font/color/family for titles and footers.
- `main.tsx` TypeScript parser: **0 syntax diagnostics**. Full npm/Vite dependency build and real React/PostgreSQL acceptance on RC131 are still pending a fresh GitHub run.
- Current release headers and historical checksum references checked. No external sign-off or strict RC acceptance has been claimed.
