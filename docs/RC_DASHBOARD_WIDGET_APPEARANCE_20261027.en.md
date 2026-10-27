# RC — Dashboard consolidation and widget appearance (EN)

Date: 27 October 2026. Cumulative base: `quorivio-0.1.0-dev-rc-autosave-widget-inspector-page-rename-preview-cumulative.zip` (not confirmed committed). Last user-confirmed Git baseline: `67a7be939a5930e2f9a49ce3932a4b7f29a682ac`.

## Changes

- Removed duplicate legacy media/design card from the session dashboard. Widget creation now launches the slide editor. Page administration is collapsed under advanced live projection/maintenance (retaining functions not yet fully replaced). Removed duplicate Interaction tab; renamed Results to **Live monitoring**, kept separate from static Settings because it supports live operations.
- Authenticated presenter profiles now include a server-derived `is_owner` flag; primary owner and collaborators appear with distinct gold and cyan badges in the editor. No public identity endpoint changed.
- Improved unique widget icon palette with colored glass/gradients, preserving accessible names and tooltips.
- Removed permanent per-widget menu trigger: right-click, touch long-press and ContextMenu/Shift+F10 activate contextual actions; one dismissible detailed inspector remains.
- All widget kinds now expose background color/transparency, border on/off, dash style, width 0.25–12pt, border color, rounded corners. Reuses the existing backend-approved style schema and a single appearance rendering helper on the editor canvas, participant rehearsal, projected slide and participant page. Autosave remains as in the cumulative baseline.

## Verification

- Node API 447/447 PASS; Node frontend 15/15 PASS; Python 856/856 PASS on initial full test run. One subsequent full Python run did not complete under local HTTP document converter constraints; five new focused tests passed. Standalone real Chromium right-click menu regression PASS; TSX parsing PASS.
- **Pending:** full Vite build, full Chromium/real PostgreSQL persistence, physical touch, independent usability and accessibility review. RC weighted matrix deliberately remains **53.0%**, `release_candidate_ready=false`; no accepted gate promotion. No commits, pushes, tags or Docker publication performed.
