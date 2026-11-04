# Quorivio 0.1.0-dev — RC168 — Participant phone geometry without phantom gaps

## Verified problem

RC167 filtered presenter-only widgets out of the participant DOM, but **after** computing automatic phone stacking and stage height. Invisible Results and Connected Participant widgets could therefore reserve space in both participant rehearsal and live presentation, leaving large blank gaps and moving the footer away from the bottom.

## Functional correction

1. `participantPhoneLayout()` is the shared visible-only layout plan for real and rehearsal phone stages. It filters presenter-only widgets **before** computing both `mobilePageWidgets` and `mobileStageHeight`.
2. Presenter-only layout, 16:9 desktop, phone backgrounds and authored per-widget mobile geometry/typography overrides are preserved.
3. Master-inherited presenter counters do not reserve participant phone space either.
4. The authenticated PostgreSQL/Chromium participant fixture now includes a footer and asserts an exact 928-pixel phone stage for six visible widgets and the footer 24 pixels above the bottom. It switches between the 16:9 slide and accessible reading modes and verifies accessible desktop ordering.
5. Browser JavaScript errors are counted, not printed raw, to avoid accidentally logging participant bearer join links.

## Verification and release criteria

- Node tests include positive/negative pre-filter vs post-filter mobile layout comparisons, master inheritance and custom phone geometry.
- Python RC168 regression protects the shared implementation and CI wiring.
- Real Chromium CSS fixture covers 390px and 1440px screen widths without silent browser skips.
- CI runs the Python preflight before npm and the browser acceptance with the built frontend; RC167 inventory is historical and RC168 is current.

Overall certified completeness remains **85.25% (43 accepted / 17 partial)** until the full GitHub TypeScript/Vite build, PostgreSQL-authenticated browser scenario and independently approved physical-device visual comparison have passed. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit, push, tag or deploy.
