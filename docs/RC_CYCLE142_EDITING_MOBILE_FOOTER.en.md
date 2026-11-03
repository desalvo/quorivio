# RC142 — Cross-page editing, mobile preview and independent widget typography

**Baseline:** RC141 cumulative, not confirmed committed. This RC142 ZIP contains all RC140 TypeScript fixes, RC141 stage/rendering fixes, and RC142 updates. No assistant commit, push, or release.

- Copy selected canvas widgets using Cmd/Ctrl+C and paste on another page in the **same session** with Cmd/Ctrl+V. The in-memory clipboard preserves grouped layouts and reassigns widget IDs and internal links. Native text editing and browser clipboard remain untouched; a new browser session has no saved widgets. Backspace/Delete requests confirmation before deleting selected widgets, and Undo/Redo continues through existing canvas history.
- Format widget remains dismissible without clearing selection. Added top/middle/bottom vertical text alignment to the format ribbon. Independently set the Footer page number's face, point size, color, and right/bottom padding. Its default edge padding is now **5 logical pixels** instead of 10.
- Reaction emoji sizes (16–96) and Rating control sizes (10–64) are editable through the ribbon and validated server-side. Reaction sizing now uses relative font units so it participates in content fitting, like rating controls.
- The rehearsal dialog supports a separate **Smartphone** mode and the desktop/smartphone participant toggle in side-by-side rehearsal. Both dashboard and page editor expose the same option. This is a responsive preview of a simulated 390-pixel phone, not an assertion of equivalence to every physical handset.
- The top canvas ruler receives a visible 29-pixel row and is no longer clipped by conflicting grid styles.
- Source validation is fail-closed via the RC142 inventory; original historic inventories remain untouched.

**Validation:** New Node and Python targeted regressions, full Node suite, TypeScript/TSX syntax parsing and source/ZIP SHA-256 inventory. Full Vite build, actual Chromium/Firefox/WebKit visual verification and Kubernetes deployment acceptance require the next GitHub Actions run. Formal completion stays **85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Local test evidence (3 Nov 2026):** 810/810 Node tests PASS; 30/30 targeted Python tests PASS; TypeScript/TSX parsing PASS for six touched source modules; release metadata and inventory guard PASS. Full npm/Vite build, full Python suite and native browser/device visual checks were not completed locally and must not be marked green.

**RC142 hotfix after GitHub Actions run 41624931068:** The frontend TypeScript build failed on two errors: non-standard Footer CSS variables without a typed style assertion (`TS2353`) and a stale `copiedWidgets` identifier following the shared cross-page clipboard migration (`TS2304`). Fixed the `React.CSSProperties` assertion, replaced the stale button guard with reactive session-scoped clipboard availability (also enabling Paste immediately after Copy/Cut), and added regressions. Node and Python tests pass locally; full TypeScript/Vite build and full CI still require new GitHub run. No application release gate changed.
