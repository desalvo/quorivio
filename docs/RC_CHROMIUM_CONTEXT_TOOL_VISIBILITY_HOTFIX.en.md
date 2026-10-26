# RC Chromium contextual-toolbar acceptance correction — 2026-10-26

**Baseline committed:** `a415b2655d4d0e648777c3a65efbc28e011663f0`.
**Evidence:** GitHub Actions manual `40385480205`, `Production quality gate` failed in its opt-in `Chromium editor UI acceptance`; container build depended on quality and was skipped; Docker publishing skipped under opt-in policy.

## Failure

`tools/ci_browser_editor.py` searched for `get_by_role("button", name="Porta selezione davanti")` after editing, undo/redo and checkbox selection. Playwright's call log showed only a ten-second wait for that name, with no pointer interception and no page JavaScript exception. The redesigned editor deliberately hides the entire `.canvas-editor-tools` panel using `.editor-ux-v2 .canvas-editor-tools{display:none!important}` until the user opens the canvas menu (`data-tools-open={backgroundMenu}`). The test assumed the contextual panel stayed open across operations. The previous thumbnail menu overlap was no longer the failing assertion.

## Correction

- One shared `tools/ci_editor_context_tools.py` contains `ensure_canvas_tools_open`, `click_canvas_tool` and `close_canvas_tools`. The helpers verify actual visibility/enablement and use ordinary Playwright pointer clicks; no force clicks, JavaScript state mutation, disabled controls, or production shortcuts.
- The mocked Chromium editor fixture exercises arrangement, clipboard, layer movement, duplication and removal **through a genuinely open contextual menu** and explicitly verifies that controls disappear on menu close and return on reopening.
- The *real PostgreSQL* Chromium editor acceptance shares the same helpers and closes the context drawer before Save and conflict resolution, avoiding another latent unguarded context-toolbar test failure.
- Updated the existing twenty-cycle editor test contract and added four structural regressions that require guarded contextual operations on both desktop and touch.
- No production source, schema, CSS, authentication, persistence, Docker opt-in publication logic or participant APIs were changed in this correction.

## Verification and boundaries

Python syntax/compilation and focused editor/canvas/browser regression suites pass locally. The previously committed Node suite remains unchanged; Node tests are run again for the packaging gate. The complete real application Chromium workflow (including PostgreSQL editor acceptance, mobile and touch) **cannot be claimed passing until GitHub reruns it**. No RC gate is promoted: weighted evidence score stays **48.0%**. The CI history documents a test flow mismatch with intentionally contextual UI, not evidence that the layer-order operation itself is broken.

Next: maintainer applies cumulative ZIP, commits, and runs manual `browser_test=true`, `publish_image=false`, `publish_latest=false`. Inspect the first failing Chromium step if another issue surfaces; do not add arbitrary sleeps or force clicks.
