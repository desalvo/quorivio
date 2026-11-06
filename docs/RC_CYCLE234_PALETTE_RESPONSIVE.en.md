# RC234 — Chromium phone editor palette overflow correction

## Verified cause

GitHub Actions full CI run `42245983528`, commit `d744de0eac508c5e6196e97315c09aa388c55985` (RC233), failed at the real browser gate `ci_rc171_editor_palette_chromium.py` while checking viewport width **620 px**. The widget palette measured scrollWidth **1198 px** with clientWidth **608 px**, although the earlier 1440 and 960 px cases passed. The RC226 one-column mobile override in `apps/web/src/style.css` applied a stronger `body .editor-ux-v2 .editor-widget-grid` rule with `flex-wrap:nowrap` and `overflow-x:auto`, which superseded RC171's intended wrapped, vertically scrolling palette.

## Implemented repair and acceptance

- Maintain RC226's single-column phone editor layout and all widget controls, without any horizontal palette scrolling. The mobile widget rail uses `min-width:0`, `max-width:100%`, `box-sizing:border-box`, and a bounded height of `min(30dvh,198px)`; the grid uses wrapping with vertical scrolling and no horizontal overflow.
- Keep all 19 fixture widget/graphic triggers at compact sizes. No widget types, access rights, QR behavior, database model, user data or desktop editor rendering are changed.
- Retain the original RC171 Chromium gate. Add independent `tools/ci_rc234_palette_chromium.py` with real Chromium coverage at 320, 390, 440, 620, 740, 760, 761, 960 and 1440 px. Verify all 19 tools, bounded icon sizes, no horizontal overflow, and reachability of the final graphic tool after scrolling.
- Add `tools/tests/test_rc234_palette_responsive.py` with negative CSS mutation checks and explicit fail-closed GitHub workflow integration. Do not bypass browser acceptance or soften prior assertions.
- Promote RC234 as the only current source inventory; preserve RC233 and every preceding receipt as historical immutable evidence, with all four active handoff/status headers updated.

The two browser cases preceding the failure, the new Chromium suite and the three source contract tests pass locally. The full CI for RC234 is **not yet certified**. Certified completion stays at **85.25%** (43 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Version remains `0.1.0-dev` and commit/push/tag remain the user's action.
