# Quorivio — linked results and dual rehearsal (2026-10-28)

## RC batch 2026-10-28 — linked presenter results, dual interactive rehearsal and formatting toolbar

**Version:** 0.1.0-dev (unchanged). **Last verified complete GitHub CI:** run 40595463258 on e2dc3a97bd15d82a50c23a98b1fb83c2bd1841c9 (earlier baseline, not this batch). **This batch:** local checks only; new GitHub Full CI pending. Overall conservative RC readiness remains **53.0%**; A1–A4 remain partial.

Delivered:
- Each Results widget is now an on-canvas presenter-only chart, independently bound via `targetWidgetId` to an eligible statistical widget already on the same page (question, timed quiz, rating or reactions). Source selection is available in the editor property drawer, new results default to the first eligible source, invalid/deleted sources are unlinked, and API validation rejects self-reference, invalid or non-statistical targets and foreign-page references. Older unlinked widgets remain loadable and show a configuration prompt.
- Live presenter results poll source-specific private endpoints (answer revisions, timed leaderboard, rating aggregates and page reactions) without publishing statistics in the participant widget tree. Topic-question visual statistics are still deferred until a dedicated backed aggregation is implemented; no fabricated live counts are claimed.
- Dashboard and editor expose presenter, participant and side-by-side rehearsal. They use one 16:9 draft page geometry per pane, synchronized local responses/reactions, sample statistics seeded afresh per rehearsal, and native full screen; no rehearsal write APIs are called. Participant rehearsal does not render presenter-only results.
- Participant reaction controls already submitted in real sessions; rehearsal controls now work locally and update simulated presenter results; the redundant page-level reaction bar is suppressed when a reactions widget is present.
- Copying a Results widget with its source rewires the duplicate to the duplicate source; copying only Results keeps its existing source. Editor quick palette retains font family, font size, color, and inline range styles, with improved focus handling and rounded rectangle container.

Evidence: local backend TypeScript build PASS; frontend `tsc --noEmit` and Vite build PASS; **455/455 API Node tests, 44/44 frontend Node tests, 58/58 focused Python tests PASS**; existing geometry Chromium offline PASS at 1440px and 390px, new dual-preview CSS and actual reaction pointer Chromium offline PASS at the same widths. **Local authenticated browser test blocked** by `net::ERR_BLOCKED_BY_ADMINISTRATOR` on localhost. Global Python suite TIMED OUT; it is not marked as passed. PostgreSQL 18, multi-user real browser and GitHub CI for this specific batch remain UNVERIFIED. The opt-in workflow now invokes `tools/ci_preview_layout_offline.py` before full editor Chromium acceptance.

Outstanding: end-to-end browser and PostgreSQL user/presenter synchronization, real visual compare of all widgets, independent accessibility on physical devices/assistive tech and Firefox/WebKit, true WYSIWYG during typing, multiple separately editable questions per widget, topic-question linked live statistics. No auto commit/push/tag/release or Docker publication.

Detailed notes: `docs/RC_LINKED_RESULTS_DUAL_PREVIEW_20261028.en.md` and `.it.md`.
