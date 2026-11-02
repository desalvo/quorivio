# RC134 — True presenter-screen question/submit parity

2 November 2026. **Last CI-green committed baseline:** RC130, workflow `41420021082`, commit `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d`. **Uncommitted cumulative:** RC131–RC134. No commit, release, tag or push performed.

## Functional changes

- **Real presenter projection** no longer substitutes an italic “Risposta testuale” label for an authored free-answer field. Every top-level and nested question/quiz part presents an appropriately sized, disabled/read-only text area and the disabled **Invia risposta** control; choice answers display accessible, disabled radio/checkbox controls with their authored answer font. File answers display a non-interactive attachment placeholder and the disabled submit button.
- **Topic questions** now show the same read-only question text area and disabled **Invia domanda** control on the presenter projection instead of an unrelated “questions will appear here” placeholder. Live statistics and submitted content remain separate in their authorized widgets; no audience inputs or responses are revealed to the projector.
- **Presenter rehearsal** reuses the identical topic-question presenter component rather than appending a duplicate free-text area. Participant rehearsal remains interactive and simulated as before.
- **CSS parity:** align question/quiz shell inset, title inheritance, option label/control ordering and sizes across projection and presenter rehearsal. In the fixed 16:9 preview, remove the old mobile minimum 100px textarea height only for read-only controls; actual participant inputs retain the accessible mobile reading-mode constraints. Font, answer field width/height, button sizing and answer colors still derive from persisted widget style.
- **Safety:** disabled/read-only controls cannot submit, accept keyboard focus or leak answers. Existing multi-question and per-question scoring privacy, session ownership, GDPR, autosave, Kubernetes and Docker release rules are unchanged.

## Verification

- RC134 source security/UI contracts and historical projection/WYSIWYG contracts locally PASS.
- Real local Chromium synthetic CSS/layout parity: PASS at 1440px and 390px, checking authored readonly field and choice geometry, disabled submit, and both presenter surfaces.
- Existing frontend Node regression suite: 209/209 PASS; global TypeScript TSX parser: 0 syntax errors.
- Full `npm ci`/Vite build is **not verified locally**: `npm ci --offline` reports uncached `yargs-parser` package; full GitHub CI required.
- This is a CSS fixture plus source-contract test, **not a completed full authenticated PostgreSQL browser rehearsal**. CI and operator visual signoff remain required.

**Certified gate score:** unchanged 85.25%, 43/60 accepted, 17 partial (independent external evidence remains outstanding). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
