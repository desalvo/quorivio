# Quorivio 0.1.0-dev RC268 — Preview, thumbnails and phone fidelity

This cumulative revision follows maintainer-committed RC267, with green full CI
[42516844646](https://github.com/desalvo/quorivio/actions/runs/42516844646)
and successful manual multiarch publication
[42518673212](https://github.com/desalvo/quorivio/actions/runs/42518673212).

## Implemented behavior

- Native fullscreen preview scales the actual 1280×720 slide by both available
  width and height, hides preview chrome and restores the editor's global zoom
  after leaving fullscreen.
- ArrowLeft/ArrowRight and PageUp/PageDown navigate preview pages without
  stealing keyboard interaction from answers and editable controls.
- Clicking empty thumbnail rail space opens the page context menu. Drag-and-drop
  accepts insertion targets before, between and after thumbnails, including
  the trailing empty rail; the transactional page order persistence is reused.
- Automatic smartphone card layout reduces excessive blank heights in short
  questions and results; QR graphics have bounded size, and result labels wrap
  without desktop overflow.
- **Per-page static-slide policy:** a raster-imported PDF/PPTX page, or any
  `slide` with no page-authored resizeable widget, automatically displays at
  **16:9** for phone participants. The decision is recomputed for each currently
  presented page and does not persist/modify the session's authored mobile
  layout. Switching back to an interactive page restores the normal phone
  layout. Explicit manual view selection and accessible reading remain usable.
  Participant phone rehearsal uses the same page-scoped rule.

## Acceptance and limitations

`apps/web/test/rc268-preview-sidebar-mobile.test.ts` covers page insertion
slots, fullscreen, keyboard controls, responsive QR/results layout, imported
PDF pages, static-to-interactive transitions and manual overrides. CI runs this
regression before npm installation. The local full frontend/API/Python suites,
TypeScript/Vite builds and inventory checks are part of final artifact evidence.
The GitHub full RC268 CI and authenticated cluster acceptance are **pending**.

No changes to Kubernetes, database, converter, PVC or credentials. No
commit/push/tag or Docker release by the assistant. `rc_strict=false`,
`publish_image=false`, `publish_latest=false`; accepted completion remains
**85.25%**.
