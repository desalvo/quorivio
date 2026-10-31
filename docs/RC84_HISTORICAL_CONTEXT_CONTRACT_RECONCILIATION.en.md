# RC84 — historical widget context-menu test contract

**Failing CI:** `41234368553` / `124636106637`; commit `112d3c2a99b44b743bfc56f5137cd9781323f9fd`. Python full suite ran 1,466 tests; only RC37's old inline-handler literal check failed.

**Fix:** validate RC83's actual canvas capture routing (`handleCanvasContext`, DOM/geometry widget hit detection, `openWidgetContextMenu`, `positionMenu`) while preserving its external body portal and keyboard/touch behavior. The early CI preflight now runs the RC37 test and new RC84 guards before dependency installation; no browser test is skipped. Historical inventory checksums remain unchanged.

**Release status:** `rc_strict=false`, `publish_image=false`, `publish_latest=false`; 84.75% certified, pending fresh GitHub CI.
