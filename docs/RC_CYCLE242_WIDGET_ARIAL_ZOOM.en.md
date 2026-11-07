# Quorivio RC242 — Arial defaults, compact master and global zoom

## Changes
- Canvas widgets in both the page editor and master editor now inherit Arial, including all nested labels, inputs, buttons, headings and display elements. Their authored inline typefaces remain authoritative (no migration or forced rewrite of saved content).
- Scheme commands share a single non-wrapping, compact ribbon. The **Save scheme** button and dirty-state text remain visible as a sticky one-line group while the other controls scroll horizontally when necessary. Buttons retain captions, icons and full tooltips.
- A new fixed global zoom controller on every application route supplies minus, current percent, plus and a 100% reset. Range 70–150% in steps of 10%; value is stored only in local browser preferences and has a usable fallback in storage-restricted private mode. Document-root zoom also reaches portal windows.

## Acceptance
- `node --experimental-strip-types --test apps/web/test/rc242-global-zoom.test.ts`
- `python3 -m unittest tools.tests.test_rc242_arial_master_zoom -q`
- `python3 tools/ci_rc242_arial_zoom_chromium.py` — real Chromium 390/760/1440px across all 20 widget kinds in both editors with default/custom typefaces, toolbar geometry, zoom and reset.
- The full frontend/API Node suites, Python discovery and the complete GitHub CI remain the independent regression gates.

## Safety and release status
- Retain custom typefaces and all previously authored records; no migration or server-side user data changes.
- RC241 inventory becomes immutable historical; RC242 is current. No CI tests or safety checks removed.
- Certified progress stays **85.25%** until independent signoffs. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
