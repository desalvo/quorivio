# RC223 — Context-only widget formatting and stage geometry

**Baseline:** RC222; most recent verified entirely green GitHub CI is **RC219**, run `42197607753` (14 successful jobs). RC220–RC223 still require integrated CI. Unchanged version **0.1.0-dev**; verified completion **85.25%**, 43 accepted and 17 partial gates. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag.

## Contextual format panel

- The floating formatter no longer opens on widget selection or double-click. Open it exclusively through **widget context menu → Format**. Closing it preserves the widget selection; context menus remain keyboard/touch accessible.
- Compact, viewport-bounded tabs **Text, Borders, Effects, Content, Links** (Links only for results widgets) replace the tall control stack. Tabs scroll horizontally on narrow screens.
- Text controls include font, size, emphasis and horizontal/vertical paragraph alignment plus dedicated choice/footer controls. Borders include width, color, shape, dash and fill. Effects include theme, animation, opacity and appearance. Content includes title/main-question visibility, results source title/options, QR URL and footer toggles. Links select cross-page results source page/widget/subquestion.
- All saved properties are already validated by the server (`validWidgetTextStyle` and `validPageDesign`); no arbitrary CSS or external links introduced.

## Rendered geometry

- **Footer:** late forced-center CSS rules are overridden so authored left/center/right and top/middle/bottom alignment applies in editor, preview, presenter and audience surfaces. Slide number placement is unchanged.
- **QR:** the server-provided URL is a clickable/selectable *single-line* row reserved below the QR image. Extremely narrow widgets scroll the URL horizontally rather than making all characters illegibly small; full simultaneously visible text cannot be guaranteed in arbitrarily narrow boxes. QR image occupies the remaining space.
- **Connected participants:** title and count are sized against their own widget box (`cqw/cqh`), eliminating the old viewport-sized font and inflated padding. A hidden title takes no space; global auto-scaling is disabled for this widget.

## Validation and remaining gates

- Local Node tests: **625/625 API**, **385/385 frontend**. Targeted Python suites: **34/34**, including 7 new RC223 preflight/mutation checks.
- Real Chromium computed-style fixtures at **390 and 1440 px** verify footer, QR and count. These DOM fixtures do not replace the integrated compiled React browser/PostgreSQL CI.
- TypeScript syntax and package SHA-256 inventory validation are release preflights. GitHub full CI and manual parity on very narrow widgets remain pending. Do not increase the certified score without independent validation.
