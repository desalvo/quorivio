# Chromium real PostgreSQL editor: canvas overflow intercepting Save — 2026-10-27

**Failing run:** 40513571247, job 122222001046, commit `45145d73c23b3466c2944e385decd336df129765`.

- Mandatory tests and simulated-backend Chromium editor acceptance **passed**; real PostgreSQL Chromium participant acceptance **passed**.
- The opt-in real-PostgreSQL editor browser scenario failed at `tools/ci_browser_editor_postgres.py:154` on an ordinary Playwright click of the exact `Salva layout` button. `Porta in primo piano Third` from the expanded canvas accessible controls intercepted pointer events.
- **Root cause:** the new `editor-stage` is a scrollable flex column, but `editor-canvas-slot` used `flex:1` and allowed child overflow. An expanded three-widget accessibility panel projected over the later Save area; the footer and secondary controls could also flex-shrink under pressure. Closing context panels in the test did not close this legitimate accessible disclosure, nor should it.
- **Production fix:** the canvas slot, bottom controls and secondary Save/merge area now retain their natural content height (`flex:0 0 auto`); the already scrollable stage scrolls to accommodate them. No pointer-event bypass, CSS blanket overlay, forced test click, or removal of accessible controls. Existing context menus and icon-only widget palette retained.
- **New required Chromium preflight:** `tools/ci_editor_save_flow_chromium.py` imports real production CSS and reproduces the expanded three-widget accessibility list plus both Save labels at 1440×1000 and touch 390×844. It verifies real hit-testing, clicks Save using the same helper as the PostgreSQL test, checks the output, then clicks a widget's accessible layer control. With the **prior stylesheet this test fails on both viewports**; with the new stylesheet both pass.
- `tools/tests/test_ci_editor_save_flow.py` checks the layout contract, shared Save locator and CI invocation.
- **No production API, database, secrets or billing changes.** Actual production-backed Chromium replay on GitHub remains necessary; do not claim full CI green or raise RC readiness above **48.0%** until confirmed.
