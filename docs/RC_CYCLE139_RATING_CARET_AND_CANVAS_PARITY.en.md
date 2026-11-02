# RC139 — Rating parity, editor selection and canvas spacing (2 November 2026)

Baseline: committed RC137 (GitHub workflow 41475936282); RC138 is included in this cumulative package and remains uncommitted.

The 0–10 rating now uses one reusable, accessible UI across editor, real presenter screen, presenter/participant rehearsal and the real participant view. The editor renders the heading only once while the readonly projections show a noninteractive scale, without mirroring votes or private response values. Interactive participants select distinct large labeled buttons (or a configured select control). The same widget styling follows the authored canvas geometry.

The floating **Formato widget** close control now hides the ribbon without deselecting the widget. Inline rich-text pointer events bypass widget drag and preserve browser text-range behavior. Double-clicking an already editable field must never send focus back to its beginning; property text fields no longer force a select-all action. The 16:9 widget interiors now use the same proportional padding rather than the editor-only 23px right inset. The content fit wrapper does not force a 100%-tall invisible content box; manual widget geometry still belongs to the author and can be resized independently.

Local acceptance: source-level TypeScript parse, web Node regressions, targeted legacy Python preflights, strict SHA-256 inventory. Full browser interaction and npm/Vite CI must be verified on GitHub and the user's installation before closing this acceptance item. No admin credentials, Kubernetes resources, or live session data are changed.

**Certified score 85.25% (43 accepted / 17 partial)**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit, push or release performed by the assistant.
