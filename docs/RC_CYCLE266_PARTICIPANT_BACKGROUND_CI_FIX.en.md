# Quorivio 0.1.0-dev RC266 — Participant background CI contract compatibility

## Failure
Committed RC265 [full CI 42506410487](https://github.com/desalvo/quorivio/actions/runs/42506410487) failed during the `RC227 schema backgrounds and mobile participant mode before npm` preflight. Legacy RC173 test `participant page paints the authored background once` matched the obsolete literal `:slideBackgroundCss(entry.activity.page_design`, while RC265 correctly composes the stage background via `...slideBackgroundCss(...)` to accommodate full-bleed imported pages and the participant phone layout.

## Scope
- Update the historical RC173 contract to require exactly one background composition on the participant stage, never its outer wrapper.
- Add RC266 preflight coverage for full-canvas imported backgrounds, accessible reading mode, and master overlay suppression on audience/presenter.
- Gate this prior to RC227 without disabling RC227. Application runtime, converter, Kubernetes manifests, secrets and wizard remain unchanged.
- Keep all previous RC265 import modes, thumbnails and historical checks intact.

## Release validation
Run the affected early CI gate and the complete GitHub full CI after commit. Do not publish or deploy until validated.

## Additional RC266 editor floating-window fix
Dragging the widget formatting palette and page/widget-properties drawers previously stopped prematurely because the full panel was clamped inside the viewport, even when it was too wide/tall to leave room for a useful docking position. A reachability-preserving clamp now leaves a 112 px horizontal / 44 px vertical graspable title-bar strip visible while allowing full docking at right/bottom screen edges. A lower-right resize handle supports mouse, pen and touch; keyboard arrows resize by 16 px, Shift+arrows by 48 px. Adaptive minimum sizes and viewport maxima keep resizes usable on small screens. CSS variables override legacy `!important` fixed widths. Source, Node, RC105 historical and real Chromium computed-style tests cover the changes at desktop, phone and compact sizes. No changes to database, converter, Kubernetes or Secret content.

### Global CSS zoom correction
Quorivio zooms `<html>` (80% by default). `window.innerWidth` remains in physical pixels whereas fixed-position offsets are logical coordinates; root `clientWidth` can also vary with overflow styles. The floating window now uses `innerWidth/computedZoom` and `innerHeight/computedZoom` for consistent placement, and observes the root with ResizeObserver for zoom changes. Tested at 70%, 80%, 120% and across desktop/phone/compact viewport sizes in real Chromium.
