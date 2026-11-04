# RC176 — Accessible DOM reading order and three independent participant modes

**Date:** 2026-11-04. **Cumulative base:** RC175. `0.1.0-dev`, EUPL-1.2 unchanged.

## Actual code corrections

1. The live participant footer was visually moved last using CSS `order`, while DOM/keyboard and screen-reader order remained at the source position. `participantReadingWidgets()` builds a real accessible document order: top-to-bottom, left-to-right for equal rows, footer last. Decorative lines/shapes and presenter-only tools have no nodes in that document. Authored 16:9 stacking order and custom phone geometry are not changed.
2. The authenticated Chromium/PostgreSQL audience fixture incorrectly asserted `.stage-phone` after clicking "Lettura accessibile". It now tests **all three modes independently**: `.stage-fidelity`, `.stage-phone` and `.stage-reading`, including neutral white background, footer last in DOM, accessible 44px input target, 16:9 normalized desktop/phone position parity, and no phantom private-widget space in the phone layout.
3. A standalone Chromium fixture executes the **actual TypeScript visibility/reading-order policy** with the shipped CSS at 1280, 390 and 320px. CI includes this fixture and a mutation-guarded Python preflight.

## Confirmed local validation

- Frontend Node **313/313**, API Node **588/588**.
- Targeted Python **25/25**, including 5 RC176 Python and 4 RC176 Node regressions.
- Actual Chromium DOM/CSS: RC174 slide geometry, RC175 media fidelity, RC176 accessible reading order, all **PASS** at three widths.
- TypeScript syntax transpile on three changed TypeScript/TSX units: zero syntax diagnostics.

## Limitations and acceptance

The **authenticated built React + PostgreSQL journey**, TypeScript/Vite build, and current GitHub Actions run **were not executed**. `npm ci --offline` lacks cached tarballs and the registry hostname is unreachable in this environment. A standalone Chromium CSS fixture is not a WCAG/AGID sign-off or a physical-device test. A4 remains **partial** until independent assistive-technology/device/operator approval.

**Certified global completion remains 85.25% (43 accepted, 17 partial).** Do not grant extra points for unreviewed local source/tests. Keep `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No automatic commit/push/tag/deploy/publish.
