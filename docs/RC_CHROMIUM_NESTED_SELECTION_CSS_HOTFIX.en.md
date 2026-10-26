# RC Chromium nested selection CSS hotfix — 2026-10-26

- Committed baseline: `b8b08fd1fd61fcf15ff49c98ed530df7693c7e38`.
- Failing manual run: https://github.com/desalvo/quorivio/actions/runs/40392423273/job/121816969728. The alignment panel was present but the nested layer/nudge group was absent from the Chromium accessibility snapshot. Chromium correctly could not locate `Porta selezione davanti` even after reopening the canvas context.
- Root cause: global `display:none!important` on `.editor-ux-v2 .canvas-editor-tools` combined with an open-state selector matching only the direct child. Nested layer controls remained CSS-hidden indefinitely.
- Production fix: restore `display:flex!important` for the *descendant* `.canvas-editor-tools` only when `data-tools-open=true`. Do not expose permanent toolbar or weaken context-menu restrictions.
- Acceptance: `tools/ci_nested_context_css_chromium.py` uses real Chromium and production stylesheet, checking closed/open/real click/closed on both desktop and touch. Main Chromium test and shared helper assert the layer group and front button visibly reachable. This is now a preflight only in the existing opt-in Chromium job.
- Run standard CI then manual `browser_test=true`, `publish_image=false`, `publish_latest=false` without changing the latter's default.
- RC score stays 48.0% until full acceptance. No commit, push, tag or publication carried out.
