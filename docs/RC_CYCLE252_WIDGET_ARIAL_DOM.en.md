# RC252 — Default Arial in new question titles and answer options

## Reproduced root cause

In the **actual compiled React editor**, inserting a new question widget generated a rich-text `span` with `style="font-family: undefined"`, while the widget container correctly declared `font-family: Arial`. Assigning JavaScript `undefined` to `CSSStyleDeclaration.fontFamily` creates a literal CSS font family named `undefined` instead of removing the property. Answer choices use the same rich-text renderer. Prior CSS-only and fake DOM tests inspected the Arial parent without measuring its child glyphs.

## Minimal source fix

`inlineMarkDomCss` in `apps/web/src/widget-text-marks.ts` filters out missing properties before any imperative style assignment. `RichWidgetText` uses it in `apps/web/src/widget-rich-editor.tsx`. Unmarked titles/options inherit their intended Arial default; independently authored base faces (Verdana, Tahoma) and inline marks (Georgia, Trebuchet MS, size/color/weight) stay intact. Persisted text and marks remain in their existing plain-text format; no database migration is required.

## Fail-closed regression checks

- Node: `node --experimental-strip-types --test apps/web/test/rc252-rich-dom-aria-default.test.ts`.
- Production frontend build: `npm run build -w @quorivio/web`.
- Chromium: `python3 tools/ci_rc252_arial_rich_dom_chromium.py`, using the **actual built Vite/React bundle** at 390×844 and 1440×940. Asserts computed fonts of rendered glyph spans on titles and answers, actual new-widget insertion, authored style retention, and studio's 80% zoom.
- Both test paths are wired into full GitHub CI, with new current-cycle SHA-256 archive inventory and immutable past receipts.

## Handoff

Maintainer-committed RC251 passed full CI [42416170735](https://github.com/desalvo/quorivio/actions/runs/42416170735); application images [42417768823](https://github.com/desalvo/quorivio/actions/runs/42417768823) and isolated converter [42417918195](https://github.com/desalvo/quorivio/actions/runs/42417918195) published successfully. RC252 is **not committed or published** and requires full CI after the maintainer's commit. Product ledger unchanged: **85.25%** (43 accepted / 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
