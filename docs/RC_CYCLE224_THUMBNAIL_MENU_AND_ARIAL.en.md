# RC224 — Viewport-safe thumbnail menu and Arial authoring defaults

**Baseline:** RC223 cumulative source. Last independently verified all-green GitHub full CI: **RC219**, run `42197607753` (14 jobs passed). RC220–RC224 require full integrated verification. Version **0.1.0-dev** remains unchanged. **85.25%** (43 accepted, 17 partial gates). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag.

## Thumbnail menu — actual viewport containment

- The contextual menu is rendered in `document.body` and positioned by the pure `thumbnailMenuPosition(x,y,width,height)` helper, which clamps both axes and computes the available **height below the actual menu origin**. The CSS uses `--thumbnail-menu-max-height` to overcome the former `!important` fallback that silently overrode the inline maximum height (reproduced and fixed in Chromium).
- Persistent primary actions: open, rename and duplicate, plus delete with server confirmation. Details groups contain **Create and import** (new before/after, PDF/PPTX, JSON import), **Reorder** (move up/down) and **Export and data** (JSON export). Every prior action remains; disabled states, multi-selection shortcuts and owner/session permission controls remain unchanged.
- Native `<details>/<summary>` provide touch and keyboard expansion; Escape returns focus to the originating miniature menu trigger. Expanded groups scroll **within** the bounded portaled menu, including when the originating thumbnail sits near the bottom-right edge. The outside rail is not unclipped.

## Arial default audit — both editors

- Enumerated all **20 widget kinds** created from the page and master/scheme widget palettes and checked `initialWidgetTextStyle` -> `widgetTypographyStyle` -> `stageWidgetTypography` fallback to Arial, including forms, question titles and answer options, results, profile, QR and participant counter.
- Verified title and footer defaults (`newTitleWidget`, `newFooterWidget`) in *new* schemes and pages. Title text inherits the master's default Arial through `widgetDisplay` rather than forcing `fontFamily` into a local title override. This is essential: a deliberately customized master or widget must not be overwritten. The footer's font is explicitly Arial on creation.
- Graphic presets (shapes/lines) also default to Arial. Editor and scheme canvas text controls inherit the effective authored widget font, preserving saved explicit typefaces and inline formatting.

## Validations

- Local Node API suite **625/625**, web suite **390/390**, Python regression suite **54/54**, RC224 preflight **6/6** and Node focused suite **5/5**.
- Chromium with the actual stylesheet and representative portaled menu passed at **320x240**, **390x380**, **390x844**, **1440x900**; all expanded commands are reachable and new editor/scheme text resolves to Arial. A separate test verifies menu positioning at each viewport corner and rejects out-of-bounds cases.
- Syntax check for modified TypeScript successful; RC224 pre-npm regression and Chromium gate added to `.github/workflows/ci.yml`. These fixtures are not a substitute for the compiled React/browser/PostgreSQL campaign or user acceptance. Full GitHub RC224 CI remains pending; no justified increase to 85.25%.
