# Quorivio 0.1.0-dev — Mock-aligned editor, auto-save and page-scoped JSON (2026-10-27)

Baseline: last user-declared commit `551396cdaafb8765140355557eae8f8ceb59c8d4`. This is cumulative with the previously delivered *uncommitted* editor-layout/widget-persistence package. No new commit or release was performed.

## Implemented in this working package

- Editor now fills the viewport with a single branded header, slide-thumbnail rail, responsive 16:9 canvas and icon-only widget palette; only the **Exit** action remains persistently displayed. Quorivio-branded local SVG and existing alpine photograph are bundled as web assets. Structural browser verification is not a pixel-level visual approval.
- Page modifications are queued for **debounced auto-save (850 ms)**. Writes use PostgreSQL design-revision compare-and-swap; only a matching API read-back marks the revision as synchronized. The draft remains local on failed saves or concurrent revision conflicts. Explicit save controls under the canvas have been removed; **Save now** exists only in the canvas context menu.
- Canvas context menu uses native right-click or a hold gesture on touch (580 ms), with no permanent menu trigger. Page-specific thumbnail context menus offer import/export versioned JSON draft and page operations.
- Each of the 17 widget types receives a distinct icon. Tooltip is accessible by focus and touch; duplicative native title was removed from the widget palette.
- Replaced outdated Chromium acceptance cases relying on old explicit save buttons. Mock API and real PostgreSQL/browser fixtures now verify autosave, reload persistence, revision collisions and reconciliation. Existing CSS/locator preflights remain active, with a new autosave/Exit hit-test preflight.

## Local verification

- Node API suite: **447/447 PASS**.
- Python complete suite: **832/832 PASS** before a new success-path regression, then targeted regression pass; rerun full suite before committing.
- React/TSX syntax transpilation: PASS. A full Vite + React build is **not locally verified** because this isolated environment lacks the complete npm dependency cache.
- Isolated real Chromium: CSS context preflight, autosave-only controls preflight, Exit hit test and structural 3-column responsive desktop/mobile preflight: **PASS**.
- **Not yet accepted:** real product screenshot compared against the reference mock, full production React/TypeScript build, browser test against the actual running frontend and PostgreSQL, real hardware rotation/resize/touch and 1:1 final projection. These must be verified through the opt-in GitHub full CI and manual operator acceptance.

## Gate and delivery

A2 and A4 remain **partial**; no RC gate was upgraded on local evidence. Weighted RC readiness score remains **53.0%** and `release_candidate_ready=false`. Recommended next action: commit and run `browser_test=true`, `publish_image=false`, `publish_latest=false`; inspect Chromium and PostgreSQL editor suites. Do not equate local fixture passes with visual signoff or production-ready release.
