# RC222 — Compact widget formatting and editor answer parity (2026-11-06)

## Changes
- Reduced height of the **Widget format** floating window; former oversized minimum label heights removed. Accessible group names remain while redundant visual group captions are hidden.
- On narrow viewports, horizontal swipe and keyboard focus make every group reachable, rather than stacking a tall dialog. Per-element result typography appears in an expandable **Independent texts…** section.
- Editor-only single/multiple choice labels and independent subquestions now wrap long rich-text spans instead of inheriting legacy `nowrap`, clipping and ellipsis. No change to preview, presenter or participant rendering.
- Answer choice default font is **Arial**, respecting full-widget font changes (including authored inline formatting overrides and independent subquestions). Explicit text selections still support individual formatting.

## Files, tests and limitations
- `apps/web/src/main.tsx`: normalized editor answer styles, whole-widget scope behavior, expandable result controls.
- `apps/web/src/style.css`: compact ribbon and editor-only choice text wrapping and font-family overrides.
- `tools/ci_rc222_format_widget_chromium.py`: actual Chromium computed CSS at 1440/390px on a static editor DOM fixture; checks multiline layout, default Arial, font override, full text and panel height. This does not replace the compiled React application acceptance.
- Pre-npm Python/Node guards, real Chromium in opt-in browser CI, historical SHA-256 receipts and full Node suites.

## Release state
Latest integrated green RC219 run `42197607753`; RC220/221/222 require new GitHub CI and in-app acceptance. Certified **85.25%**, 43 accepted / 17 partial; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag.
