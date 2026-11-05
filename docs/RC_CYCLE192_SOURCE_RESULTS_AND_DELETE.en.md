# Quorivio 0.1.0-dev — RC192: results source title/options and confirmed page deletion

**Baseline:** cumulative RC191; last independently GitHub-green full campaign remains RC190 run `42027634427` and verified Docker Hub multiarch publish `42032833536` (commit `bb80a3ce`). No change to application version `0.1.0-dev`.

## Changes

1. **Optional source question in a Results widget.** A new per-Results-widget checkbox “Mostra titolo e risposte della domanda sorgente” (`showSourceQuestion`) displays a read-only copy of the originating question title, description and all possible answers, with its original widget font, inline rich-text marks and answer styles, *above* the statistics. Handles a source on a different page and a specifically selected independent subquestion (`targetQuestionId`). Ratings and reactions display their available 0–9 values/icons. The option defaults off; enabling it clears “Solo risultati”, and enabling “Solo risultati” clears this option to avoid contradictory settings. Results data remain presenter-only; the source content is not a public statistics leak and no answer keys are shown. Live statistics and rehearsal use the same `LinkedResultChart` renderer. The previously reported missing results were confirmed by the user to be a **rehearsal-only issue**; do not describe production counting as broken.
2. **“Elimina pagina” now follows explicit confirmation.** Previously the authenticated API returned HTTP 409 `page_referenced_by_session` when another page routed its audience or Results widget to the page being deleted. The confirmed delete now serializes under a session row lock, locks affected pages, safely removes `audiencePageId`, `targetActivityId`, `targetWidgetId` and `targetQuestionId` links in page/result designs, bumps each changed design revision to protect concurrent editors, deletes the page and associated response records with existing FK cascade, then compacts positions in the same transaction. Its response includes `detached_pages`; the editor reloads the authoritative snapshot and shows the number of affected pages. Cancellation still performs no operation. A pending/dirty editor continues to protect against silent loss of unsaved content.

## Validations and remaining acceptance

- **603/603 Node API tests and 329/329 Node frontend tests pass**, plus **18 targeted Python tests** and strict TypeScript checks on source/result/domain modules. Historical dual-projection contracts and new source/deletion regression preflight pass.
- Static TypeScript TSX parser verification. Full npm-installed React/Vite/backend compilation and authenticated PostgreSQL/browser deletion require the post-commit GitHub Actions run; not certified from local tests alone.
- The CI adds dependency-free RC192 guards *before* npm and checks historical inventories unchanged.
- Product certified completion remains **85.25%** (43 accepted gates, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag/publish.

## Suggested interactive acceptance

Create page A with multi-choice widget Q, including styled title, options and an independent subquestion. Create page B with a Results widget linked to A/Q, enable `showSourceQuestion`; both split rehearsal and presenter live should show authored title and options above the bar/pie chart. Disable it and confirm the former layout. Check no grading keys are exposed. Then set B’s `audiencePageId=A`, confirm Delete on A, and verify A disappears, B remains, B’s saved audience destination is reset to same-page default, and B’s results source is cleared rather than silently dangling. Repeat with other viewers/editors open and ensure design revision conflict protection.
