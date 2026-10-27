# Quorivio — Widget inspector, page rename and rehearsal follow-up (2026-10-27)

**Committed baseline:** `67a7be939a5930e2f9a49ce3932a4b7f29a682ac`, Full CI 40553571012 SUCCESS. The present cumulative is **uncommitted** and includes autosave recovery/geometry plus the user's subsequent live editor reports.

## Completed changes

- Floating portal-based widget tooltip instead of a tooltip clipped by the widget rail. Only one accessible hint per icon; no duplicate mobile status toast.
- The integrated editor now displays only its authoritative widget inspector drawer; contextual widget duplicates are suppressed. Inspector and page settings drawers offer a visible, accessible Close (×) button.
- Full question/timed-quiz choice editor: explicit option labels, single/multiple selection, add/remove answer rows up to 12, mark correct answer, and quiz duration. The editing canvas and projection display answer options with the selection marker to the **left** of the label.
- Autosave resilience (network failure before/after commit, recovery readback), shared percent geometry for canvas/audience/projection, and tests from the in-progress preceding batch.
- Dedicated `PATCH /api/sessions/:id/pages/:aid/title` endpoint. Validates length and controls, checks authorized owner/collaborator and closed-session guard, increments activity revision, broadcasts title; does **not** rewrite options, votes, design revision, or media. Rename available in the thumbnail contextual menu and blank-canvas contextual menu. In-memory draft preserved.
- Participant rehearsal removes redundant slide number/title and the purple left-hand page selector. Rehearsal-only navigation remains in the footer, with clear non-submission warning. The real audience continues to receive only the server-selected active activity; redundant page headings are suppressed when designed widgets already render the title.
- Added five new rename/rehearsal contracts and a real-PostgreSQL Chromium step: rename through the thumbnail, read back the title/options/design revision/geometry, and continue concurrency acceptance.

## Verification and acceptance limitations

- Local complete Python suite: **851/851 PASS**; backend Node: **447/447 PASS**; frontend/API TypeScript syntax transpilation PASS; Python browser script syntax PASS.
- Browser/PostgreSQL end-to-end of the **new** changes, React/Vite build and physical device/reader review **PENDING** on new commit/CI. No independent accessibility or pixel-accurate acceptance claimed.
- This batch does **not** change the formal RC ledger: **53.0%**. `release_candidate_ready` remains false. Promote relevant gates only on evidence, not from local contracts.
- Manual Docker publication is opt-in; do not publish this build automatically and do not commit/push/tag via assistant.
