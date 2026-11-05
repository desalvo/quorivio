# RC195 — RC161 master font CI reconciliation

## GitHub evidence

GitHub Actions run `42074647393` (#295; commit `c219d4b2377af721a20fccebe52ea57a30b3114d`), Production quality gate job `127411480855`, failed in step 14, `RC161 master image, Arial and graphics presets contracts before npm`. The historic test searched an obsolete `fontFamily:'Arial'` literal in `apps/web/src/main.tsx` and stopped the workflow before npm. Real ClamAV passed; dependent jobs were skipped.

## Changes

- No application runtime or CSS changes. In the current code, `slide-master.ts` defines `DEFAULT_TITLE_STYLE`/`DEFAULT_FOOTER_STYLE`; `widgetDisplay` overlays master and authored styles, `stageWidgetTypography` resolves the same source, and `widgetTypographyStyle` retains authored fonts with Arial fallback. `widget-typography-defaults.ts` covers questions/answers.
- Updated RC161 to check these shared contracts and their override precedence, rather than requiring a duplicated inline source literal.
- Added RC195 Python negative-mutation and real Node/TypeScript behavioral tests (including phone projection, custom master title, authored widget style, footer numbering and question choice font fallback) as an **early, fail-closed preflight** ahead of RC161.
- Retained all older immutable manifests and the RC194 question/answer/rich-text implementation. Checksums and active RC195 metadata updated independently.

## Additional historical preflight reconciliations

A complete walk of all 96 pre-npm CI steps uncovered additional stale source-string checks in RC144, RC167, RC168, RC169, RC131, the timed rehearsal deadline test, and RC91. Those historical assertions now check the **actual independent page** (`viewActivity`, `viewWidgets`, `audienceActivity`) and shared resolved typography. The rehearsal timer correctly restarts only when the audience question page changes, and footer numbering follows the displayed activity ID. The underlying app runtime was not modified. RC195 negative tests guard against reintroducing a single presenter/audience page or silently losing custom typography.

## Validation and limits

Targeted RC161/RC195 regressions, historical preflights, Node API/frontend suites and cumulative SHA-256 source/ZIP verification are the local acceptance gates. Only a newly committed GitHub CI can certify full React/Chromium/PostgreSQL/Kubernetes behavior. Certified global score remains **85.25%** (43 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag or Docker publication by the assistant.
