# RC217 — Dynamic public phone-stage height and private-widget exclusion

## GitHub failure
RC216 run `42150766799`, production job `127673188105` failed in the Chromium participant/PostgreSQL integration step at `tools/ci_browser_participant.py:279`. Historical RC176/RC165 browser acceptance assumed **998px** for the fixture, including a 248px question with shorter choice rows. RC207 introduced a **44px minimum for touch-answer rows**, increasing the same question to 278px and the legitimate fixture height to **1028px**. The hard-coded browser check rejected the improved phone accessibility.

## Change and preserved guarantees
Rather than replacing 998 with another frozen stage height, the Chromium check calculates expected stage height from the **rendered PUBLIC-only widget bounds**, 16px outer margins and 8px gaps. It checks total compactness, no invisible gaps, minimum question height, last footer placement, exact public-widget count, and absence of presenter-only `results-button`/`participant-count` shells. Reconciled RC168/RC169/RC177 historical assertions with the new invariant and retained their negative checks.

Early fail-closed Python `tools/tests/test_rc217_public_phone_stage_ci.py` rejects fixed-height regressions, removal of the visible-layout filter, and loss of RC207 touch heights. Native Node `apps/web/test/rc217-public-phone-stage.test.ts` executes the source planner: 1028px for short answers, increased height for 255-character options, and identical height after adding extra private presenter widgets. Both execute before npm. The original real PostgreSQL+Chromium acceptance is still required after dependency/build stages.

## Verification
Local real Chromium with source CSS and TypeScript planner confirmed 1028px stage, ~16px margins and ~8px gaps at viewport widths 390 and 1440. Focused Python and Node tests pass; full integrated GitHub RC217 CI remains pending. No React, API, CSS, database, desktop-stage or permission changes. Version `0.1.0-dev`, certified readiness **85.25%** (43 accepted / 17 partial gates), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag.
