# Quorivio RC276 — Presenter cross-page truth-toggle contract recovery

- Baseline: cumulative RC275, CI 42565597725, job 128991308978.
- Root cause: `rc191-cross-page-preview.test.ts` required `showCorrectLive` and live-only R-toggle wiring in `PresenterLinkedResult`. These are no longer present because `LinkedResultChart` owns the R state.
- Verified source path: `PresenterLinkedResult` obtains source-page `sourceWidgets` through `linkedStatisticContext`, passes them to the same `LinkedResultChart` used by the editor/rehearsal. Its local `truthVisible` state is guarded by `resultHasAnswerKey` and applies to the source question and chart rows via `viewWidget`.
- Fix: update the outdated RC191 assertion, add five positive and negative regression tests for cross-page source routing, R interactivity, shared answer copy, and fail-closed key gating, and wire an early CI step. No application runtime changes.
- Keep RC275 immutable, promote RC276 inventory. GitHub full CI and browser acceptance still required; no automatic commit/push/tag or image publishing. Certified progress remains 85.25%.
