# RC155 — Editor conflict toolbar CI regression correction

The GitHub run [41719228484](https://github.com/desalvo/quorivio/actions/runs/41719228484) on committed RC154 stopped in step **Editor autosave recovery and shared geometry unit tests**. The failing unit test `closing format widget does not clear active widget selection` in `apps/web/test/rc139-rating-editor-selection.test.ts` required the obsolete selection-only `&&widgets.some(...)` condition.

The current editor deliberately includes `!suspendFormattingRibbon`: the parent canvas passes `suspendFormattingRibbon={pageConflict}` to hide the floating formatting toolbar while the revision conflict panel is open. This prevents pointer-event interception of the compare/reconcile button, without losing the current widget selection or draft. The production behavior remains unchanged.

## Regression acceptance

- Node: `node --experimental-strip-types --test apps/web/test/rc139-rating-editor-selection.test.ts apps/web/test/rc155-conflict-ribbon.test.ts`.
- Python source guard: `python3 -m unittest tools.tests.test_rc155_conflict_ribbon -q`.
- Each negative mutation removing suspension, disconnecting `pageConflict`, or clearing active selection must fail.
- Test on a real authenticated Chromium/PostgreSQL environment: save concurrent edits from two presenter sessions; trigger revision conflict, verify the compare button is physically clickable, reconcile, verify the draft persists and the toolbar returns afterward. This is **not** certified until GitHub CI passes.
- Full CI and the separate authorized 500-user load test (see RC154 administrator guide) remain pending. Never run load tests automatically or against an unapproved host.

**Release safety:** RC154 manifest kept historical, current manifest RC155 only; no CI publishing without successful gating.
