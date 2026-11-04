# RC173 — Live audience slide parity, accessibility and rating

**Base:** cumulative RC172 derived from RC171. Version `0.1.0-dev` and EUPL-1.2 unchanged; no automatic commit, push, tag or publication.

- Removed the second copy of the slide background from the public page wrapper. Only the authored 16:9 stage paints that background.
- Separated public controls into **16:9 Slide**, **Smartphone layout**, and **Accessible reading**. The 16:9 mode preserves desktop stage geometry at every viewport size; smartphone customization is now opt-in. Accessible reading uses a neutral, unpainted linear document and excludes decorative shapes/lines.
- Prevented narrow-screen 44px touch rules from distorting the faithful 16:9 stage; accessible reading retains large interactive controls.
- Editor rating uses exactly one visual title at a time, switching ownership between the shared rating body and the editable text field. The shared 0–9 choices and optional comment remain unchanged.
- Presenter-only results and counts are absent from the public stage. An unlabelled shape matching a private results rectangle is also omitted as an orphaned fill; other page graphics are preserved. Removed the legacy public no-widget statistics fallback.
- Preserved authored masters and the RC171/RC172 non-overlapping phone layout calculations.

**Evidence:** 302/302 frontend Node tests passed, including six focused RC173 cases. Full TypeScript/Vite build blocked by unavailable offline npm dependencies (`vite/client`, TS2688); authenticated Chromium visual comparisons, multi-browser/mobile/accessibility runs, PostgreSQL integration and GitHub CI are pending. Readiness remains **85.25%** (43 accepted and 17 partial gates); no external gate has been promoted.

Use `rc_strict=false`, `publish_image=false`, `publish_latest=false` until CI and visual acceptance finish.
