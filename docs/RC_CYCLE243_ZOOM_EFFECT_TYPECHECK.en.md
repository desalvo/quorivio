# RC243 — React zoom cleanup TypeScript correction

- **Source of failure:** GitHub run [42376234500](https://github.com/desalvo/quorivio/actions/runs/42376234500), commit `f2899cc76320667a442b504d9e89f38c6f1611ff`, failed `Production quality gate` at strict frontend TypeScript: `apps/web/src/main.tsx(2768,12): TS2345`, incompatible effect destructor `() => string`.
- **Root cause:** `CSSStyleDeclaration.removeProperty` returns the previous property value as `string`. An expression-bodied arrow cleanup in `GlobalPageZoomShell` returned this value, but React's `EffectCallback` only permits void cleanup.
- **Correction:** `return()=>{root.style.removeProperty('zoom');};` returns `void` and still removes the document-level zoom on effect cleanup. No change to persisted 70–150% zoom, default 100%, or accessible controls.
- **Regression:** `tools/tests/test_rc243_global_zoom_effect_cleanup.py` validates source structure, explicitly rejects the old code, and guards the pre-npm workflow and unchanged strict `tsc --noEmit` gate. No test or mandatory job was disabled.
- **Release:** RC242 receipt remains immutable and becomes historical; RC243 current. Awaiting GitHub full CI after user commit. Progress 85.25% (43 accepted / 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
