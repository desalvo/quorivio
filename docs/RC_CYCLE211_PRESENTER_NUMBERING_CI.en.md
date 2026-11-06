# RC211 — Presenter/audience footer numbering CI reconciliation

## Evidence and root cause
RC210 full CI run `42139200296`, quality job `127634916707`, failed in the RC195 Python preflight because two assertions still demanded `viewPageNumber=slidePageNumber(activities,viewActivity.id)`. Since RC206, the approved expression is `slidePageNumber(activities,activity.id)`: even when the audience sees a different activity, its footer shows the presenter's current visible-page ordinal and skips pages hidden from the presenter. The RC91 historical test contained the same outdated literal and would otherwise fail later in CI.

## Corrections and safeguards
- Reconciled the historic RC91 and RC195 tests, retaining the typography and page-footer safeguards.
- Added RC211 negative-mutation preflight covering audience-specific numbering, raw page indices, and accidental removal of independent audience content routing.
- Added the preflight and an actual Node page-numbering unit test to GitHub Actions. Historic inventory receipts remain immutable.
- No app-runtime or DB-schema changes. Version `0.1.0-dev`; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Evidence and certification
The previously failing preflight and the targeted RC91/RC195/RC211 checks pass locally. Full GitHub CI for RC211 remains pending. Last fully green independent campaign: RC203 `42110429701`. Certified completion remains 85.25% (43 accepted, 17 partial). No commit, push, tag, or release was performed.
