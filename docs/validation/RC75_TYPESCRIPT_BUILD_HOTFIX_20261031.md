# RC75 — Frontend TypeScript build hotfix

- Failed CI: https://github.com/desalvo/quorivio/actions/runs/41207039782/job/124554135225
- Git HEAD before fix: `77486c8f9b902d5e89f0f3f823d3cf496f00d5c3`
- `main.tsx`: TS2339 twice, `reactionIconSize` missing from the *editor-state* `Pick<PageDesign.widgets>` type, although the persisted schema already supported the property.
- `slide-master.ts`: TS18048 optional `pageNumber` comparison without a TypeScript narrowing guard.
- `widget-results.ts`: TS2339 `answerMode` missing from one branch of the source/subquestion union.
- Corrected all three with explicit structural types and stable number narrowing. No behavior or persisted schema changes.
- Node tests: 560 API; 123 web. Additional strict TS isolated-module check and unit regressions are passing locally. Full npm build not run locally (registry DNS EAI_AGAIN), and entire Python suite timed out.
- Historical inventories remain immutable; RC75 adds a new manifest and enforces it after historical verifiers in CI.
- Release configuration unchanged: `rc_strict=false`, `publish_image=false`, `publish_latest=false`; score remains **84.75%** until further verified acceptance.
