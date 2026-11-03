# Quorivio 0.1.0-dev — RC144 — Independent portrait editor, participant parity and ten-step ratings

## Baseline and release status

RC143 cumulative from 3 November 2026, including RC142 TypeScript hotfix, result top-five wrapping/ranking and closeable formatting ribbon. RC144 is a complete local cumulative, NOT a release candidate promotion. **Certified completion stays 85.25%**, 43 accepted and 17 partial external gates. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag/publish.

## Changes implemented

1. Rating widget now has precisely **10 choices, scores 0–9** across shared editor, participant, presenter and rehearsal controls, demo statistics and the public API. New SQL inserts and updates are additionally blocked by an idempotent PostgreSQL `NOT VALID` constraint enforcing 0..9. The constraint intentionally leaves historical records with score 10 readable: no votes are silently deleted or rewritten. Historic aggregate rows can therefore still contain legacy scores. Production data and migration must be acceptance-tested before release.
2. Authored mobile layout uses a true **390 logical-pixel portrait stage**, with a minimum 720px scrollable document, independent normalized widget geometry and optional per-page mobile background. Unconfigured phone positions receive a deterministic stacked portrait layout; the desktop layout, which still drives projector and desktop preview, is not modified. Editor switch: **Desktop 16:9 / Smartphone 390px**. Right-click empty phone canvas to choose a solid mobile background, select/upload a mobile background asset, or clear it; phone never inherits desktop background.
3. Editing a phone widget's placement writes to `page_design.mobile.positions`, not `page_design.widgets[].position`. Shared text, assets and appearance remain shared. Additional/removed widgets are reconciled, deleted positions are pruned from persisted drafts. The mobile draft is included in save, dirty detection, restore, exported backup, validated import, conflict-safe rebase and saved-server-readback comparison. `validPageDesign` rejects unknown phone geometry properties, invalid bounds, extraneous widget IDs, malformed colors and IDs. Mobile assets are checked for presenter ownership before setting them, protected from deletion while in use and available through active-slide-only public media routing.
4. Phone rehearsal and real participant page use the phone-specific positions and background; phone content no longer gets globally shrunk from 1280×720, and inner controls can scroll instead of being reduced to tiny type. Desktop projector/presenter modes remain authored 16:9. Browser CSS preflight covers the 390px stage and the ribbon/cloud checks.
5. Arial is explicitly selected as the default common widget family in the authored typography style and the editor rich text surface; per-widget font overrides are retained.

## Local verification

- `node --experimental-strip-types --test apps/web/test/*.test.ts apps/api/test/*.test.ts` — **821 passed / 0 failed**.
- `python3 -m unittest tools.tests.test_rc139_rating_text_selection tools.tests.test_rc140_widget_format_scope tools.tests.test_rc141_stage_result_rating_contract tools.tests.test_rc142_editor_clipboard_mobile_footer tools.tests.test_rc143_phone_result_ribbon -q` — **22 passed / 0 failed**.
- `python3 tools/ci_rc143_format_phone_chromium.py` — Chromium CSS preflight **passed at 1225 and 390 px**; HTML fixture only, not a full live frontend integration.
- Global TypeScript 5.8.3 syntax transpilation of touched TS/TSX modules — passed with zero syntax diagnostics; isolated strict TypeScript typecheck of the six pure shared model/draft modules — passed.
- Full Python sweep was started but exceeded the container execution timeout; not represented as a pass.
- Offline `apps/web` `tsc --noEmit` was blocked immediately by missing `vite/client` type package; complete production Vite compilation and authenticated browser flows still require CI with dependencies installed.

## Remaining RC acceptance

Require green GitHub standard and extended CI on the new commit; live PostgreSQL 18 checks for migration/legacy ratings; authenticated editor-save, reload, collaborative-rebase, image upload and spectator mobile tests on iOS Safari, Android Chrome, Firefox and desktop projector; independent gate approvals. Verify accessible reading mode as a deliberate alternative to authored phone layout. In this cycle, the phone-only layout does not yet have a dedicated independent Undo/Redo history stack; shared desktop undo remains unchanged. No external gate has been signed off by these local changes.

**Suggested cumulative commit message after the latest confirmed RC140 commit:**

`Complete rating and results parity, formatting ribbon and independent mobile editing [full-ci]`
