# RC86 — Chromium palette test recovery

Source: uploaded `logs_111780102568(1).zip`, Production quality gate / Chromium editor UI acceptance. `tools/ci_browser_editor.py:273` failed after real widget context acceptance because it incorrectly required exactly 17 palette buttons. The current app exposes 19 types including `title` and `footer`.

The live Chromium contract now verifies all required kinds, unique `data-widget-kind` values, meaningful and unique accessible button names, unique SVG icons and no native `title` tooltips. It continues to add a real text widget, autosave to the API and verify reload. Four pre-install Python tests validate this contract. RC gate score unchanged 84.75%; extended GitHub run pending; no strict or publishing.
