# RC graphical editor issue batch — 27 October 2026 (English)

Baseline: the maintainer committed Quorivio on `551396cdaafb8765140355557eae8f8ceb59c8d4`; the immediately preceding cumulative archive is `quorivio-0.1.0-dev-rc-53-dynamic-gate-score-ci-hotfix-cumulative.zip`. No automated git commit or publication has been performed.

## Reported issues and changes

- Central canvas: the editor now allocates the full flexible central column and uses a responsive 16:9 artboard; it no longer retains its previous max-width.
- Thumbnail menus: elevate the active thumbnail rail and row above the stage, and open popups outside the thumbnail card; preserve the narrow-screen fixed popover.
- Widget tooltip: remove duplicate browser-native `title` from icon tools, retaining ARIA names and the authored hover/focus/touch tooltip.
- Multiple canvas menus: background/page options and arrangement tools are now mutually exclusive; the page menu exposes an explicit entry for selection/alignment tools. Shared Chromium helper follows the same real-pointer path.
- Resize and rotation: expose all eight resize handles and rotate handles at high stacking priority, while preserving existing pointer and keyboard geometry behavior. These gestures still require full-device acceptance.
- Interactive widgets: double-clicking a question, topic-question, or timed quiz opens its context/properties path, and the editor displays choice labels for supported widget types. Projection uses the same saved percent geometry. Further widget-by-widget visual fidelity work is still open.
- Canvas/projection persistence mismatch: palette-created and drag/drop widgets now carry explicit, bounded percent `position` including rotation instead of relying on editor-only fallback geometry.
- **Critical save error identified:** the API permits widget IDs of at most 48 characters, but `topic-question-<UUID>`, `results-button-<UUID>`, and `participant-count-<UUID>` previously exceeded this limit (51/51/54 characters). All create, copy, paste and duplicate paths now use valid UUIDs (36 characters). API validator smoke verified this directly.
- The editor blocks blank media placeholders with a precise message, checks the 16-widget quota, shows save errors inside the full-screen editor, and reads back the authoritative activity after a successful PATCH; it does not mark the local draft saved if the revision or serialized widgets differ.

## Verification

- Python project suite: 824/824 PASS locally.
- Node API tests: 447/447 PASS locally.
- TypeScript/TSX syntactic transpilation: PASS; full `npm run build` cannot be certified from the archived dependency stubs, which omit Node/React type declarations.
- Direct API `validPageDesign` smoke for all six widget ID kinds: PASS with UUIDs. Old long type-prefixed IDs exceed the limit.
- No new deployed PostgreSQL+Chromium acceptance run has been performed on this batch. Save/restore, real viewport, pointer rotation, and cross-browser testing remain mandatory, as does an operator check of the screenshot-specific issues.

**RC readiness remains 53.0% (historical evidence baseline only), release_candidate_ready=false.** Do not promote A1/A2/A3 before real frontend build, PostgreSQL save/reload, and visual acceptance. If the runner fails, preserve the first failing test log and avoid treating this static batch as final sign-off.
