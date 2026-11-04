# RC172 — Safe mixed manual and automatic smartphone authoring

Cumulative changes after RC171 without discarding existing mobile edits.

- Manual phone widgets reserve their vertical areas before other automatic widgets are laid out. The stage can grow to accommodate the remaining interactive widgets; desktop coordinates and explicit phone coordinates are not rewritten.
- Editor and public/participant layouts now calculate stage height using the exact same phone overrides as their automatic widget positions, preventing inconsistent height in mixed layouts.
- The **Compact automatically** action resets only phone positions, preserving user-customized phone fonts and colours.
- A manual placement occupying the full phone page has no overlap-free arrangement; the iterative solver is bounded rather than running indefinitely.

**Local evidence:** 296 web Node tests pass including five new RC172 tests; new Python structural/negative preflight and updated historical compatibility checks. npm install timed out in this environment, so the full Vite build, authenticated Chromium/PostgreSQL and actual device comparisons remain pending; do not describe them as passed.

**Certified completion 85.25%** (43 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit, push, tag, image publication or deployment.
