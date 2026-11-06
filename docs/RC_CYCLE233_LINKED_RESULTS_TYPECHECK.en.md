# RC233 — Restore strict frontend TypeScript contract for linked results

## GitHub finding

Full CI GitHub Actions run `42241665883` for RC232 commit `68391862f85036cf0327e511afbfd5ff0db5da2e` reached `RC196 strict frontend TypeScript typecheck before extended CI`. At `apps/web/src/main.tsx:2686`, seven TS2339 diagnostics reported that the editor's `widgetHistory` element type omitted `showSourceTitle`, `showSourceAnswers`, and `showCorrectAnswers`, which the linked-results configuration UI already reads and writes.

The canonical `PageDesign['widgets']` schema in `apps/api/src/domain.ts` already contains all three fields as optional booleans. The cause was a locally narrowed `EditorWidgetPermissionFields = Pick<...>` list that omitted them, not an invalid configuration or missing backend persistence.

## Correction and safeguards

- Add all three typed keys to the editor's existing `Pick<NonNullable<PageDesign['widgets']>[number], ...>` without `any`, unsafe casts, behavioural rewrites or additional public exposure of answer keys.
- Keep linked-results switches functional and retain truth highlighting as presenter-only, off by default. API/domain schema remains unchanged.
- Add the RC233 dependency-free contract test **before** npm in the CI quality gate, checking the typed keys and user-facing switch wiring, plus negative mutation tests for each missing field.
- Keep strict `tsc --noEmit -p apps/web/tsconfig.json` after npm, preserving its fail-closed behavior.
- Promote RC233 as current release inventory; retain RC232 and every prior inventory as immutable historical evidence. The RC232 historical gate is made forward-compatible with later inventory promotions.

### Release constraints

Version remains `0.1.0-dev`. No changes to authentication, privacy/retention, user roles, PostgreSQL, deployment or publication permissions. Last confirmed full-green CI: RC219 `42197607753`. Local preflight, TypeScript and inventory checks are separated from GitHub full CI acceptance. Certified completion remains 85.25% (43 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
