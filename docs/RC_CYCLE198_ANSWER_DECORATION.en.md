# RC198 — Consistent underline and strikethrough in answer text

**Version:** Quorivio `0.1.0-dev` (unchanged)  
**Base:** user-committed RC197 cumulative, 5 November 2026 (`0794f02`, GitHub Actions #298 launched).  
**Scope:** rich-text formatting for questions, timed quizzes and independent subquestions.

## Fixed issue

Widget Format already distinguished answer font, size, color, bold and italic, but applying **Underline** or **Strikethrough** under the **Answers** scope instead changed the *title* style. Consequently, unmarked answer choices and subquestions did not render those decorations. The same gap affected whole-widget decoration.

## Changes

- Added optional `answerUnderline` and `answerStrikethrough` booleans to the strict API style schema. Legacy pages remain valid, with no database migration.
- Reused the shared answer renderer to apply underline, line-through, both or none to options, answer fields and presentation surfaces.
- **Whole widget** propagates both decorations to answers and inline marks, including independent subquestions; **Answers** edits only their dedicated properties.
- Exposed dedicated accessible answer underline/strikethrough controls in the formatting palette and widget properties.

## Validation and remaining evidence

- **605/605** API Node tests, **348/348** frontend Node tests passed, including **five new** positive/negative/compatibility/scope tests.
- Full TypeScript/Vite was **not runnable locally** because the source snapshot has no `node_modules` (`vite/client` missing). Do not treat this as a completed typecheck.
- Post-commit compiled React/browser/PostgreSQL/GitHub CI remains pending for this cycle. Run #298 is the earlier RC197 commit, not RC198.

**Governance:** certified **85.25%** (43 accepted, 17 partial), no unearned gate promotion; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, tag, deployment or publication.
