# Run 40549836288 — canvas context click hit target

- Commit baseline: `b6736aaab6b7dc11e33bedecd4ceb9954d7e8ed3` (user-confirmed).
- Quality gate: FAILURE, step Chromium editor UI acceptance. Container/publisher: SKIPPED.
- Preflights passed: mock layout, fixed CSS, mobile overlay, autosave/Exit, real Chromium browser start.
- First failure: `tools/ci_browser_editor.py` -> `click_canvas_tool` -> `ensure_canvas_tools_open` -> fixed `canvas.click(button='right', position={'x':7,'y':7})`. Playwright correctly reported the `.editor-mock-brand` header intercepting pointer events.
- Cause: a locator-relative fixed corner is not guaranteed to remain exposed after scrolling the editor's accessible-control disclosure into view.
- Fix: `canvas_background_point` reads the real visual viewport, central stage bounds, actual `document.elementFromPoint`, and excludes widget/media/button targets; `open_canvas_context` clicks at those coordinates with the genuine mouse. Used by the shared helper, initial mock canvas menu, toolbar dismissal and touch-long-press target.
- Regression: mandatory independent `tools/ci_canvas_context_hit_target_chromium.py` reproduces covered old corner and requires real context menu open, selection tool use, dismissal, and reentry at desktop and touch viewport. No Playwright force click or synthetic DOM click.
- Verification: local Python 836/836, Node 447/447, Chromium desktop/touch smoke PASS, YAML parsed, package intact. GitHub Full CI & PostgreSQL editor E2E **not verified** after this patch.
- Release gate: A1/A2/A3/A4 remain partial, 53.0% weighted RC; no publication or Git actions.
