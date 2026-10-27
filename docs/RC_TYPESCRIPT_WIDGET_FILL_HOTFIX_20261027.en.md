# 2026-10-27 — Production compile hotfix and rich-widget consistency (post-6395b0b)

## Scope and baseline
- Source: the user-provided committed cumulative archive of Quorivio 0.1.0-dev; baseline commit: `6395b0b9982bbcd898d921eab836d3ee63b305eb`. EUPL-1.2, original deployment manifests and package contents preserved.
- Incident: GitHub Actions run `40574076999` failed `Production quality gate` at frontend `apps/web/src/main.tsx:939` (three TS2339 errors for `fillMode` / `fillImageAssetId`). The preceding green run is `40553571012`. No later CI success is claimed.

## Code corrections (all post-baseline)
1. Editor history widgets now use the backend's exported `WidgetTextStyle` type instead of the stale inline style subset. The visual style helper derives its fields from this same API contract. No `any` or `@ts-ignore` workarounds have been added to fix typing. Explicit narrow values for text/vertical alignment and animation comply with the API union rather than weakening it.
2. A compile-time `widget-style-contract.ts` asserts equality of API/UI shape, fill-mode, fill asset and opacity types and exercises a real image-fill style. New regressions cover API validation and renderer alpha/shape/image semantics.
3. Corrected the API `PageDesign` TypeScript widget union to include `participant-count` (already accepted by its runtime validator), plus typed `durationSeconds`, answer keys and `resultsView`. Results view values are now validated explicitly instead of accepting arbitrary strings.
4. The widget inspector's Remove button now requires explicit confirmation, consistent with canvas/context/keyboard removal. Transparent image fills no longer accidentally render an image behind otherwise transparent widget backgrounds; foreground text and borders remain independent.
5. Closed-session duplication and its media-ID remapping logic remain intact; existing API unit checks for image remapping and Python contract checks were rerun. No claim of real database copy isolation is made pending PostgreSQL integration.

## Reproducible local verification
- Recovered user-owned `quorivio-node-modules-full.tar.gz` from Library; npm registry DNS was unavailable in the execution container. Dependencies were extracted **only for testing**, and are excluded from the cumulative ZIP.
- `npm run build` **PASS** (backend `tsc -p tsconfig.json`, frontend `tsc --noEmit`, Vite production build, 1594 transformed modules).
- `npm test` **PASS 450/450** backend Node tests; frontend `node --experimental-strip-types --test apps/web/test/*.test.ts` **PASS 23/23**; combined post-change focused Node suite **PASS 26/26**.
- Python focused editor / autosave / closed-duplication tests **PASS 26/26**.
- Chromium isolated preflights **PASS 7/7 scripts** (desktop/mobile responsive controls, context toolbar, Save/Exit state, mock fidelity, obscured hit target, tooltip and input placement); see evidence manifest.
- Full Python `unittest discover` and broad RC-only discovery **TIMED OUT** in this environment. Do not claim those suites passed.
- `npm run build` originally failed in this environment **before** recovering dependencies, with missing type-definition packages. That initial environment-only failure was resolved by recovering the supplied npm archive; the subsequent actual complete build passed.

## Release gates and remaining work
- `docs/RC_GATE_MATRIX.json` A1/A2/A3/A4 retain `partial`; **0 accepted gate promotions** from this batch. Weighted global RC completion stays **53.0%**. Candidate remains blocked by all unaccepted required gates; no invented completion.
- CI GH run 40574076999 remains failed. After the maintainer commits this cumulative package, verify normal quality and container jobs, **without enabling `publish_image` / `publish_latest`**. Subsequently dispatch the manual `browser_test=true` workflow with PostgreSQL 18 and test closed-session copy in both owner and collaborator roles, rich widget persistence, real editor/preview/presentation parity, touch and network-loss recovery.
- Pending independent Firefox/WebKit, NVDA/VoiceOver/TalkBack, physical touch devices, PostgreSQL isolation under concurrent autosave, representative visual pixel comparisons and legal/AGID sign-off. No commit/push/tag/release or Docker publication performed here.
