# RC250 — Fix real CSS-zoom thumbnail dropdown pointer interception

Baseline: RC249 committed `cf0a1e45048ad49e6d320eddf610f205e4d4bc53`, GitHub workflow `42410387603`, quality job `128517050772`. Strict TypeScript and earlier browser checks passed; the real compiled-editor Chromium test timed out at `ci_browser_editor.py:266` after expanding both native disclosure sections, because the menu overlay intercepted the same thumbnail menu toggle.

## Root cause and correction

The browser's `getBoundingClientRect()` returns visual CSS pixels after `html { zoom: 80%; }`, while fixed-position style offsets in a body portal are *again scaled by the root zoom*. RC249's anchor calculations assumed both units were identical, which was true only without CSS zoom. `thumbnailMenuPosition` now calculates viewport clipping and avoidance in visual coordinates, then returns CSS layout positions/sizes divided by the effective root CSS zoom. Both opening and scroll/resize repositioning pass `getComputedStyle(document.documentElement).zoom`, and a root-style observer handles live UI zoom changes.

## Validation and limits

- Existing RC249 pointer geometry remains required.
- New negative Node test reproduces overlap with the old result at 80% zoom and verifies the fix at 64%, 80%, 100%, 120%.
- Eight real Chromium cases use actual root zoom and the expanded native submenus; actual pointer clicks close the menu, no `force=True` or DOM-triggered bypass.
- The original `tools/ci_browser_editor.py` remains active against compiled React and PostgreSQL test workflows; passing isolated tests does not guarantee the new full GitHub campaign.
- No DB/Kubernetes/API/schema changes, no image publication. Gate matrix still **85.25%**, RC strict blocked by 17 independent external approvals.

Release flags: `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag by the assistant.
