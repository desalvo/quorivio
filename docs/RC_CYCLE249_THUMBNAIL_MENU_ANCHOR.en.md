# RC249 — Accessible floating thumbnail menu anchored outside its trigger

## Confirmed failure

RC248 source at `9027af34f0d8182d12bda366a89e239286b63a41`, GitHub full CI [42405687692](https://github.com/desalvo/quorivio/actions/runs/42405687692), failed the real React Chromium editor (`tools/ci_browser_editor.py`). Its page-1 thumbnail menu was expanded; the portaled "Rinomina pagina (R)" item physically intercepted pointer clicks intended for the menu toggle. Playwright correctly refused a forced click. ClamAV passed, downstream campaign jobs were skipped.

## Fix

The page thumbnail menu now receives the actual toggle rectangle, places itself wholly to its right/left when space permits, and narrows within available room on phones. If neither side is usable it opens in the larger vertical space. The content remains vertically scrollable and limited to the actual viewport. Capture-phase scroll and resize listeners update placement if the thumbnail rail, viewport or UI zoom changes. The toggle remains pointer-accessible, keyboard and Escape support and focus return are unchanged. No test click is forced and the full original Chromium React/PostgreSQL acceptance stays mandatory.

## Validation and status

New pre-npm negative guard, pure TypeScript geometry tests, and live Chromium CSS pointer testing at 320×240, 390×844, 760×820, 960×760 and 1440×900. Previous RC224/RC248 browser tests retained, historical inventory remains immutable. Full GitHub RC249 CI pending. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag or cluster changes.
