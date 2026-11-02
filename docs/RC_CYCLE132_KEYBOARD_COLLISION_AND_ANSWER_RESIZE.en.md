# RC132 — Keyboard/pointer collision parity and accessible free-text response geometry

2 November 2026. Baseline confirmed by maintainer: RC130 committed, GitHub run `41420021082` green. RC131 and RC132 are **uncommitted cumulative changes**; the full GitHub CI for these changes has not been executed.

## Implemented

1. **Keyboard geometry:** both single-widget Arrow-key movement and multi-selection keyboard/toolbox nudges use the same continuous first-contact swept-collision algorithm as the pointer in RC131. A translation stops at the first non-graphic obstacle instead of jumping through it or bouncing back. Multi-selection spacing, canvas bounds and intentional shape/line overlays are preserved. Rotation and size changes still use their separate bounded/collision-rejecting geometry constraints.
2. **Free-text answer editor:** the response-field resize handle is now an accessible vertical slider with explicit min/max/current logical pixel values (`48..400`), keyboard focus indication and ArrowUp/ArrowDown (8 px), Shift+Arrow (32 px), PageUp/PageDown (32 px), Home/End support. Both ordinary free-text answers and participant-submitted topic questions now use the same editor resize handle; topic questions previously displayed a fixed read-only preview. The pointer resize remains available. The slider does not activate the surrounding widget move interaction; each keyboard resize flows through the existing saved design and history, with a single Undo entry per key operation. No change to response contents or permissions.
3. **Regression protection:** ten additional Node tests cover thin-obstacle tunneling, rigid group nudge, graphics, boundaries, invalid values, keyboard resize and undo behavior. A new early Python source contract and dedicated CI step prevent future reversion of these semantics. No publication action, release flag or mandatory pre-existing test has been disabled.

## Verification and release boundary

Local frontend Node test command: `node --experimental-strip-types --test apps/web/test/*.test.ts` (RC132 result: 202/202 PASS). Targeted Python early/source tests: 27/27 PASS; full Python suite not completed under the local execution deadline (converter test phase). The 202/202 frontend Node suite and source inventory are verified locally; archive integrity is verified separately. GitHub native browser, TypeScript/Vite production builds and full CI require a new maintainer commit; no claim of successful RC132 GitHub certification is made.

**Certified RC completion remains 85.25%** (43 accepted, 17 partial of 60). Physical mobile/assistive-device acceptance, external identity provider/SMTP, independent CSI/off-site DR and security/GDPR operator approval remain outstanding. The strict gate is intentionally not promoted. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
