# Session navigation and control-room rework — 2026-10-23

## Implemented changes

- Dedicated main-content views for the **New session**, **Open session**, and **Calendar** sidebar entries. Opening a session now replaces the selector with the selected session dashboard rather than stacking both.
- Explicit **Create and edit pages** action points to the Pages and content tab. Activity creation remains inside the page tab, now introduced as **Create interactive page**.
- New-session and session metadata forms no longer expose the optional reference-date picker; legacy API/database field is retained for backwards compatibility.
- Existing structured appointments (date/time/duration/timezone) labeled **Session dates**. Legacy date-only schedule remains temporarily accessible rather than being silently deleted.
- Invitation is visually limited to the Settings tab; statistics buttons use clearer labels and tooltips. Presenter waiting state explains how to activate a page.
- Flexible, responsive dashboard grid and wrapping controls to reduce overflowing frames; Terminate button condition correctly groups active and paused states.

## Validation / remaining work

- Local Python 118/118, Node.js 107/107. No full dependency-backed frontend production build, browser, database, or Kubernetes acceptance was performed.
- **Open**: per-page background asset menu, complete upload/link widget media/document workflows with access control, widget-only interactive activity authoring, structural tab composition, real projector/start/pause E2E tests, legacy schedule migration.
- Keep RC evidence at **37.5%** until real end-to-end gates pass. Version remains `0.1.0-dev`; no repository or Kubernetes changes made.
