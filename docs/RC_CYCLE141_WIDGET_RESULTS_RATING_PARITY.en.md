# RC141 — One-vote revision, results fit and four-surface visual parity

Baseline: RC140 TypeScript build hotfix cumulative, after committed RC140 (`2612d704ac9ea886a3770e7eab9148a3f2186876`). RC140 full build fix is included in RC141. No assistant commit/push/release. Strict RC acceptance is unchanged.

## Changes

- **Rating**: one stored score per `(activity_id, participant_id, widget_id)`; while the page is current/open and the session active, a new deliberate choice updates that row. Idempotent identical votes do not duplicate counts. UI highlights the current submitted choice, persists it across rehearsal page navigation and prevents concurrent duplicate submissions. Rehearsal permits replacement of a previous rating (not automatic double-counting). The authoritative API restricts updates to the current open activity.
- **Result widget**: optional `resultsOnly=true` (off by default) hides the widget heading and source/question header, but keeps anonymized aggregated values. Editable from widget properties. No result data is added to a participant slide.
- **Live results and word cloud**: render answer and `[count]` as one indivisible visual group. In default automatic fit mode, avoid nested scroll and measure intrinsic overflow for proportional scaling whenever new results arrive. User-controlled manual no-scale mode (`autoFit=false`) still permits scrolling/cropping by design. Very large tables may scale down significantly; a manual larger widget is preferable for readability.
- **Reactions**: one eight-emoji accessible button component in editor, presenter projection, side-by-side rehearsal and real audience. The reaction widget's `showTitle=false` applies in the editor and all previews; disabled presenter/editor controls retain the same appearance.
- **Multiple-choice widgets**: editor uses actual disabled native checkbox/radio markup and matches choice alignment, size and typography of presenter and participant surfaces. Control behaviour remains view-specific; authored appearance is shared.

## Verification and release limits

- Node test suite and RC141 regression tests; real Chromium CSS parity at 1440/390 px on four synthetic slide shells; strict TypeScript parsing and the RC141 source/ZIP inventory. Full Vite build, authenticated full-session browser flows and any external RC sign-offs still require GitHub CI/independent review.
- Screenshots from the user's installed Quorivio cluster are visual bug evidence; the synthetic CSS check does **not** certify full DOM/pixel identity of every real session. Compare on the user's deployment after CI.
- No changes to secrets, storage, networking, Kubernetes deployment or release authorization. Preserve the ledger value **85.25% (43 accepted / 17 partial)**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
