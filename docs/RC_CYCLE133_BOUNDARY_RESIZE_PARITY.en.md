# RC133 — Boundary-constrained resizing in the page editor

2 November 2026. **Last committed green baseline:** RC130, GitHub Actions `41420021082`, commit `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d`. All RC131–RC133 changes are cumulative and **not yet committed**.

## Closed functional scope

- **All eight pointer resize edges/corners** now use `resizeWidgetToCollisionLimit`: a deterministic, bounded calculation from the original pointer-down rectangle, stopping at the first overlapping non-graphic widget rather than bouncing back when the requested size is too large. It prevents overshooting thin neighbours during fast mouse/touch movement and prevents successive pointer events from using an already clipped intermediate size. The opposite side of a west/north resize remains anchored.
- **Keyboard resizing (Shift+arrows)** uses the same collision algorithm as pointer resizing. Keyboard widget movement from RC132 remains unchanged; rotation retains the existing collision-rejection behavior. Graphic shapes and lines retain their intentional overlap policy.
- **Cancelled text-answer handle gestures:** a browser pointer cancellation reverts to the height at pointer-down, without recording an incomplete edit or a spurious Undo step.
- **Undo and redo:** a pointer gesture continues to be committed as a single history entry. The function fails closed on malformed, out-of-canvas or initially-overlapping geometry and checks serialized four-decimal precision before accepting an edit. Resizing does not alter responses, session ownership or remote data.
- **Regression tests:** seven Node geometry/undo tests and five Python early contracts; previous keyboard source checks reconciled with the new behavior. Dedicated CI checks execute before npm and again during runtime-independent Node acceptance. All prior release and Docker permission guards remain active.

## Evidence and limits

RC133 local frontend Node suite: 209/209 PASS. Local targeted Python (canvas keyboard, RC132 and RC133): 11/11 PASS. TypeScript source syntax and code-level behavior inspected; a complete TypeScript/Vite build and real browser input/visual acceptance are subject to full GitHub CI after commit. Certified release gate score remains **85.25%** (43 accepted / 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. External accessibility, operator, infrastructure and GDPR acceptance is still pending. No assistant commit, push or release.
