# RC cycle — participant rehearsal submission parity and bounded acceptance audit

Date: 2026-10-28. Version remains **0.1.0-dev**, EUPL-1.2.

## Baseline and commit boundary

Input: `quorivio-0.1.0-dev-rc-accessible-rehearsal-profile-gate-61-cumulative.zip` (711 files). Last user-confirmed commit: `a32ef78902a656262d346a0fa622604a4deda405`; this output includes **all** previous uncommitted features and the current batch. The assistant has not committed, pushed, tagged or published images.

## User-visible improvements

1. **Participant rehearsals now have distinct draft and submitted states.** Selecting an answer does not change presenter's charts; only the explicit **Invia risposta di prova** action updates them. Each independent question is tracked separately.
2. **One-shot interactions match live restrictions:** repeated answers to a question and ratings are blocked; a page accepts only one reaction even when multiple reaction widgets appear. The same lock applies to both preview panes.
3. **File-question rehearsal** uses an actual file picker but holds **only the filename in memory**, never file contents. No API calls or uploads are made by the rehearsal path.
4. **Restart** clears draft, submitted answers, reaction locks, simulated audience question counts and seeded statistics. The footer now counts *submitted* interactions, not unsent input drafts.
5. **Race guard:** topic-question rehearsal enforces the ten-question limit inside the state update, including rapid repeated clicks.
6. **Full CI:** the optional Chromium phase now runs `tools/ci_rehearsal_submission_chromium.py`, which executes the actual TypeScript submission module with real browser pointer events at 1440 and 390 pixels. This remains a *module-level offline* acceptance, not authenticated production UI acceptance.

## Tests completed locally

- Backend: `npm test` **468/468 PASS**.
- Frontend: `node --experimental-strip-types --test apps/web/test/*.test.ts` **55/55 PASS** (including five new submission-state tests).
- Python: `python -m unittest discover -s tools/tests -p 'test_*.py'` **934/934 PASS**.
- Full API/Web TypeScript and Vite build: **PASS**, 1599 Vite modules transformed.
- Chromium 1440/390: keyboard/inert rehearsal, new real submission-state module, 16:9 dual-layout, editor/preview/audience geometry, and actual WYSIWYG component: **all five offline scripts PASS**.

**Not completed:** authenticated end-to-end rehearsals against PostgreSQL after these changes, new GitHub standard/full CI, Firefox/WebKit/physical devices, independent screen readers, real GDPR/legal/AGID assessments. Browser HTTP navigation in this local environment is blocked. The strict RC gate must remain blocked.

## Evidence-scoped RC bookkeeping

- **61.0% -> 63.0%** via retrospective independent review of **two specific technical subgates** already proven by the completed GitHub Full CI [40638652838](https://github.com/desalvo/quorivio/actions/runs/40638652838) on `a32ef78902a656262d346a0fa622604a4deda405`:
  - `B3-AUDIENCE` (weight 2, accepted): real Chromium + PostgreSQL participant join/answer/Q&A moderation and privacy lifecycle. Remaining B3 weight 4 stays partial for Firefox/WebKit, physical devices and screen-reader acceptance.
  - `D6-ERASURE` (weight 2, accepted): PostgreSQL retention and durable physical asset erasure outbox, retries, lease fencing and scoped privacy acceptance. Remaining D6 weight 3 stays partial for independent legal/AGID review, encrypted backups/key rotation and storage audit.
- Gate weights still total exactly 100; accepted=100% of weight, partial=50%. **28 gates: 11 accepted / 17 partial. RC NOT READY**.
- **Zero additional points** for the new locally implemented submission parity; GitHub Full CI must validate it after user commit. The score does not imply WCAG certification, production capacity SLO or GDPR certification.

## Next validated work

After maintainer's commit: run standard CI and opt-in Full CI with `browser_test=true` and `publish_image=false`. Prioritize manual presenter/participant dual-viewport parity, screen readers, Firefox/WebKit, Kubernetes RWX/ClamAV, actual social provider acceptance and independent operator/legal sign-off. Do not promote broad parent gates on local test evidence alone.
