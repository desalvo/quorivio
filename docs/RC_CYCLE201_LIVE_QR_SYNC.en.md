# Quorivio 0.1.0-dev — RC201 — Live QR synchronization after URL rotation

**Baseline:** RC200 cumulative (not yet confirmed by full GitHub CI); RC199 last verified green run `42096705867`. This cycle changes runtime QR delivery only, keeps `0.1.0-dev`, and preserves the safe flags `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Behavior

- The signed-in dashboard and all participant QR widgets in the editor, rehearsal, presenter projection and audience view fetch their canonical URL from the same server QR policy; they never infer URLs from `join_code` or `window.location.origin`.
- Changing a session access code through reset immediately hides the old QR in authenticated views before requesting a new image and link. Presenter WebSockets remain connected and receive the rotated session snapshot; invalidated participant sockets are disconnected without disclosing the new secret.
- Each QR watches for canonical URL changes every 12 seconds and also refreshes on window focus, resumed network connection and page visibility. This covers public-origin changes and missed events without reloading the browser. Pending requests are abortable and stale images disappear on unavailable/revoked links.
- The dashboard QR, invitation hyperlink, PNG/SVG download URLs and presenter QR use the URL revision as an image-cache key, so browsers cannot preserve the previous bitmap. The display URL and QR are always derived from the same canonical server target.
- QR origin resolution reads the shared `public_base_url` platform setting for each endpoint request (including PowerPoint QR export), rather than a pod-local copy, so multiple Kubernetes replicas agree after administrator updates. Database lookup failure fails closed.

## Acceptance and limitations

Local executable QR state tests: 4/4 passed. Python QR/lifecycle source contracts: 21/21 passed. Previous RC71 disposable PostgreSQL acceptance is extended to check the actual QR URL rotation; this end-to-end PostgreSQL check and full React/TypeScript/Vite build require GitHub CI in the dependency-complete environment. The local `npm run build -w @quorivio/web` was blocked by missing cached `vite/client`, not a reported source error. The JavaScript/TypeScript parser check is clean for both modified app entry points. The RC200 integrated pipeline remains unconfirmed.

Old public participant tokens remain invalid after a reset. A public view using a revoked token shows an unavailable QR, rather than learning the new private token automatically. Previously downloaded PDF/PPTX files and static images cannot update after export.

Certified project readiness remains **85.25%** (43 accepted and 17 partially accepted gates), without promoting any release gate. No assistant commit, push, tag or production publication.
