# RC196 — React compilation and cross-page result-widget types

## Failure evidence

GitHub Actions [run #296](https://github.com/desalvo/quorivio/actions/runs/42081815639), commit `b8d689a139d50b24724fbeb37da3d50c23e84fd1`, passed the RC195 early preflights and all 345 frontend Node tests. The production gate then failed at **Compile frontend and backend**: `apps/web/src/main.tsx` had a `TS2552` undefined `linkedResultQuestion` name and two `TS2339` errors because the editor widget type did not include `showSourceQuestion`.

## Changes

- Import `linkedResultQuestion` explicitly from `widget-results.js`, restoring the real source-question display without an undefined reference.
- Include `showSourceQuestion` in `EditorWidgetPermissionFields`, inferred from the persisted and validated `PageDesign.widgets` type.
- Add an early RC196 pre-npm contract with negative mutations against the missing import, missing type field or disconnected result rendering.
- Run **strict frontend TypeScript compilation** immediately after npm setup (in addition to the existing API typecheck), before costly browser/PostgreSQL/HA workflows.
- Preserve historic immutable inventories and create a new independent cumulative SHA-256 manifest.

## Validation and limits

Locally 345/345 frontend and 603/603 API Node tests passed, together with relevant RC192/RC195/RC196 Python regressions and an isolated strict TypeScript compilation using the *actual* `PageDesign` and `widget-results` types. A full local npm/Vite build could not complete: offline npm lacked a cached dependency, and the online installation timed out. The forthcoming GitHub run must confirm the integrated React/Vite/PostgreSQL acceptance. No commit, push, tag or publication performed.

The version remains `0.1.0-dev`. The last fully green/published baseline remains RC190 (runs `42027634427` and `42032833536`). Evidence-based completion stays **85.25%** (43 accepted, 17 partial); `rc_strict`, `publish_image`, `publish_latest` remain off absent explicit opt-in.
