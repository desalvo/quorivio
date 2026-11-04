# Quorivio RC174 — Single participant stage and measured 16:9 scaling

**Cumulative base:** RC173. Product version `0.1.0-dev` and EUPL-1.2 unchanged. No automatic commit, push, tag or deployment.

1. **Duplicate outer session branding:** Organization logos and the oversized session heading used to remain visible *above* the actual active participant slide. They now render only on join, consent and status views; the active stage keeps the semantic `h1` for screen readers but visually presents a single authored slide. The public wrapper has no slide-like painting or opaque card around it.
2. **Legacy media duplication:** `page_design.media` is only displayed outside the widget stage if no authored widgets exist; older widget-free activities remain supported.
3. **Unscaled form fields on faithful phone 16:9:** An actual Chromium/CSS reproduction measured the same two-line textarea at **57.2 px** high at both desktop (stage width 1229 px) and phone (374 px). Narrow-screen faithful-stage label text, padding, border and input/button dimensions now use container units. The textarea becomes **18.0 px** at stage width 374 px and **15.0 px** at 304 px. Accessible reading preserves controls at least 44 px tall.
4. **Historical contract updates:** A handful of old static tests were coupled to the previous JSX className string; extraction now uses the stable route marker, while unrelated stale Python negative-test anchors were updated to current RC172 structure.

**Local evidence:** 307/307 web Node tests; 588/588 API Node tests; 18/18 targeted historical Python tests and 5/5 RC174 Python preflight tests. Real Chromium *DOM/CSS fixture* passes at viewport widths 1280, 390 and 320 px, checking 16:9 dimensions, widget positions, no extra heading box, scaled form height, no horizontal overflow and background-free accessible reading. The optional Chromium CI phase now runs this fixture. **Full Vite/TypeScript build** cannot run offline without npm dependencies. Authenticated React/PostgreSQL browser acceptance, real-device validation and full GitHub CI are still pending.

**Readiness remains 85.25%** (43 accepted, 17 partial gates). Keep `rc_strict=false`, `publish_image=false`, `publish_latest=false` and do not publish without further validation.
