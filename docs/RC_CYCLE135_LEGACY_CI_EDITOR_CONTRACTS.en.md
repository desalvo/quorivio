# RC135 — Early CI editor contract reconciliation

2 November 2026. Based on the committed RC134 cumulative at `3c75a548b277d179db49f1293fef3d5da5926f8b`. The full-CI GitHub run `41435798792` stopped at `Validate RC89 editor review regressions before npm`: 7/8 tests passed, the remaining test asserted the historical ASCII-apostrophe label `Casella di risposta libera nell'editor`, which RC132 replaced with an accessible typographic label. The same test had a second obsolete presenter-topic label removed by RC134. No frontend compilation or production browser acceptance ran in that workflow.

## Fix

- RC89 now tests the actual `EditorAnswerFieldPreview` control, accessible labels for both free-answer and topic-question fields, keyboard resize slider and the non-interactive presenter submit button.
- Old pointer safety contract now explicitly verifies `role=slider` in the exclusion from widget dragging and pointer-stop behavior.
- RC109 checks the current projection component's authored `answerInputStyle(widget.style)`, the safe first-contact resize helper and its `autoFit:false` transition; the user can still re-enable auto-fit.
- Legacy projected-options acceptance checks disabled native radio/checkbox controls, author styles and the current CSS rather than a removed decorative list.
- Run these source contracts in the early CI preflight. Previous historical inventory receipts remain immutable; new verifier/receipt RC135 validates the exact cumulative files.

**Application source and release policy unchanged.** No force-click, no weakened collision or access control, no Docker publication behavior change. Local source tests must be verified again after inventory regeneration. Real GitHub build, Chromium/PostgreSQL and full acceptance remain unverified for RC135.

Certified readiness **85.25%**, 43 accepted/17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Last fully green baseline RC130 (`41420021082`). No assistant commit/push/release.

## Verified locally

- Python suite: **1,689 tests**, 1,688 passed, 1 skipped, 0 failed.
- Frontend Node: **209/209** passed.
- TypeScript parser: no syntax errors in the active TSX and placement modules.
- Current source and cumulative ZIP: SHA-256 inventory verified.
- Complete npm/Vite build and real GitHub Actions RC135 remain unverified.
