# Per-widget presenter results — 2026-10-23

The presenter-only Results panel now includes one live result section for each independent `question` widget. Responses are fetched via the existing authenticated `/api/sessions/:id/widget-answers/detail` endpoint and kept separate by widget ID and revision. The editor offers a persistent result presentation setting (bars, pie or table) on each question widget. Charts show selectable-option totals, and count text/attachment submissions without disclosing individual content. Updates are polled every three seconds and the backend authorization remains unchanged. Existing page-wide aggregate results and timed activity leaderboards remain present.

**Not complete:** `timed-quiz` canvas widgets are still not fully independent timed answer channels; they currently act as layout markers for timed activities. Browser/PostgreSQL E2E, WCAG review, revision-specific historical labels, live multi-client tests and manual PDF updates are pending. No new migrations or auth changes. Gate closure remains 67% pending independent acceptance.

Local checks: backend tsc, frontend tsc and Vite production build PASS; Node regression suite 90/90 PASS. Previous CI was confirmed by the user only up to `presenter-results-canvas`; subsequent cumulative cycles are not yet committed.
