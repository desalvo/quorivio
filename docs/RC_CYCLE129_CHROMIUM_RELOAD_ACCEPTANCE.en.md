# RC129 — Chromium editor reload acceptance

- GitHub run `41389141345` failed in `Chromium editor UI acceptance` after the frontend had built.
- The historical browser test autosaved four widgets, reloaded the page, and tried to reopen the session manually. RC128 intentionally restores the authenticated session and editor page on reload.
- `.page-editor-thumb-row.is-active` intercepted the background sidebar click by design; this does not prove broken CSS layering.
- Browser acceptance now waits for the restored editor, visible Exit button, active page thumbnail, four persisted widgets, and matching persisted tab-local session/page identifiers.
- No `force=True`, UI/runtime changes, weaker gates, or automatic publishing.
- Local static tests passed; live Chromium and full GitHub CI must still run on the new commit.
- RC certification: 43 accepted, 17 partial, **85.25%**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
