# Full Chromium editor header interception: regression and repair

**Date:** 2026-10-27 · **Project:** Quorivio `0.1.0-dev` (unchanged) · **Committed baseline:** `0bb8fb7856727699384dfe51aea6ee6d961ea022` · **License:** EUPL-1.2

## GitHub evidence

- Standard push CI: https://github.com/desalvo/quorivio/actions/runs/40588408394 — SUCCESS: Production quality gate and Container build gate. Production publication skipped.
- Manual Full CI: https://github.com/desalvo/quorivio/actions/runs/40589103128 — FAILURE: Production quality gate, step `Chromium editor UI acceptance (opt-in)`; `tools/ci_browser_editor.py:106` → `click_canvas_tool` → `ensure_canvas_tools_open` → button `Strumenti di selezione e allineamento`. Playwright: `Timeout 12000ms exceeded`; `<header class="editor-mock-header">` intercepts pointer events. Existing six preliminary Chromium scripts completed successfully; subsequent PostgreSQL browser tests were not reached.

## Fix

`apps/web/src/style.css` anchors the canvas background contextual menu and grouped arrangement overlays at viewport-safe positions below the fixed editor header, sized for desktop and mobile touch. This removes the overlapping hit target without hiding controls, weakening pointer checking, or using force clicks. `tools/ci_editor_context_tools.py` verifies the DOM hit test at the actual menu entry and reports an explicit obstruction. The new `tools/ci_editor_context_header_overlay_chromium.py` recreates partially obscured artboard geometry, right-click opens the true menu, and desktop/mobile real clicks traverse the selection and nudge panels twice. The test **fails on the previous CSS and passes after the change**. Integrated into the opt-in job of `.github/workflows/ci.yml` before `tools/ci_browser_editor.py`, plus 5 nonbrowser regression contracts in `tools/tests/test_ci_editor_header_overlay_20261027.py`.

## Results and limits

- Local TypeScript API/frontend and Vite build PASS.
- Local 450 backend Node tests PASS; 23 frontend Node tests PASS.
- Real Chromium isolated fixture desktop and mobile PASS; existing canvas-hit-target, nested CSS and accessible disclosure Chromium preflights PASS.
- Five focused Python tests PASS; full local Python suite timed out and is not treated as passed.
- Application-level Chromium acceptance on a live localhost URL is unavailable in this environment (browser network navigation blocked); the full browser/PostgreSQL flow requires a fresh GitHub Actions run.
- Full CI after the fix **PENDING**; no Docker image published. No promotion of A1/A2 or other RC gates. Weighted overall **53.0%**, not release-candidate-ready. Additional device/accessibility acceptance still required.
