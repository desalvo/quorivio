# RC244 — Editor widget Arial baseline and unbiased Chromium regression

**Source run:** GitHub Actions [42377514266](https://github.com/desalvo/quorivio/actions/runs/42377514266), committed RC243 `a0e7dbcf22b6f73ce8a04caa028ef4745825698e`.

**Failed step:** Chromium editor UI acceptance, `tools/ci_rc224_thumbnail_menu_chromium.py` at 320×240. The fixture found `['Arial, sans-serif', 'Arial, sans-serif', '"DM Sans", system-ui, sans-serif', '"DM Sans", system-ui, sans-serif']` for page/scheme text and input elements. The former RC242 stylesheet rule set the `.widget-canvas-item` root to `font-family:inherit`, defeating the existing Arial baseline for the slide-master root; page's global DM Sans then leaked into the scheme canvas.

**Fix:** Set the editor widget *root* to `Arial,sans-serif` in both the `editor-ux-v2`, `slide-scheme-workspace` and `powerpoint-editor` contexts. Its children still inherit the authored face, and specific user-selected inline font declarations (e.g. Georgia/Verdana) remain authoritative. No other application typography or public route is changed.

**Regression improvements:** The RC242 real Chromium fixture previously assigned `font-family:Arial` inline to every default widget and thus obscured this bug. It now tests bare default widgets in both editors for all 20 types; custom font overrides remain asserted. The existing RC224 Chromium menu test is retained, including 320×240. Four new mandatory early Python tests verify the CSS baseline, the unbiased browser fixture, negative mutation behavior and that the historical browser/TypeScript gates remain enabled.

**RC controls:** RC243 original source inventory is immutable historical evidence; RC244 is the active inventory. Version `0.1.0-dev`; completion remains **85.25%** (43 accepted, 17 partial) pending independent signoffs; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag/publication performed by the assistant. Full GitHub CI RC244 must run after user commit.
