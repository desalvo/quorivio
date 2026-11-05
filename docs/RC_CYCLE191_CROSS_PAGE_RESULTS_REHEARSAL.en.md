# Quorivio 0.1.0-dev — RC191: cross-page live results and split-screen rehearsal parity

**Published baseline:** RC190, commit `bb80a3ce28cafa437da4903fef3fb84a4fc54b25`; full green CI run `42027634427` and successful Docker Hub multiarch publication run `42032833536` (`sha-bb80a3ce28ca` and `latest`). Version stays `0.1.0-dev`.

## Fixes

1. **Cross-page Results source was blank in rehearsal.** The old rehearsal resolved `linkedStatisticSource(widget,widgets)` from only the results slide, ignoring `targetActivityId`. RC191 uses shared `linkedStatisticContext()` in presenter projection and rehearsal, resolving the source activity, widget, option labels, and chart mode within the current session.
2. **Live charts could remain empty under frequent voting.** `PresenterLinkedResult` depended on the full live `snapshot` object, which changed on every WebSocket update and cancelled outstanding authenticated statistics requests. RC191 loads immediately and polls every 3 seconds without invalidating requests on snapshot changes. Network errors and truly empty datasets are displayed separately; there is no fabricated live data.
3. **Side-by-side rehearsal ignored presenter exclusions/audience mapping.** Presenter navigation now skips `presenterHidden` slides, while the participant panel resolves the selected presenter's `audiencePageId` and uses that page's desktop/phone geometry, background and widgets. Starting on a presenter-hidden audience slide selects its linked presenter page when available. Audience countdowns do not reset when the presenter changes slides without changing the audience page.

## Required scenario

Page **A** contains a question and has `presenterHidden=true`. Page **B** displays a Results widget with `targetActivityId=A`, `targetWidgetId=<question widget>` and `audiencePageId=A`. Rehearsal "Affiancate" displays **B** to the presenter and **A** to participants, and a simulated answer in A updates the result chart on B. Production reads authenticated, source-scoped aggregates only on the presenter screen. Forward navigation skips A for the presenter.

## Checks and limitations

- **326/326 frontend Node** and **599/599 API Node** tests pass.
- **30 historical Python** checks and **6 new RC191 Python** checks pass.
- Strict TypeScript for standalone routing/results modules passes; `main.tsx` has no parser errors. Full React/Vite compilation requires installed npm dependencies and must be confirmed by the next GitHub CI.
- Early Python + Node RC191 preflight added to GitHub Actions. Original fail-closed privacy/authorization, package integrity, and other gates retained.
- Post-commit full GitHub CI, authenticated PostgreSQL two-page browser test and visual acceptance remain pending. Certified completion **85.25%**, 43 accepted gates / 17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag/publish.
