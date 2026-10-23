# Presenter-controlled audience page synchronization

The participant live WebSocket snapshot now selects the activity by `session.current_activity_id` and only when its status is `open`. Previously the client picked the first activity in the list, causing the audience to stay on page one as the presenter advanced. When no page is open, the participant screen returns to the waiting state instead of exposing a stale question. The change does not use client wall-clock timestamps and preserves the server-derived opening time used by timed quizzes.

## Evidence and limits

Backend and Vite production builds PASS; 107 Node API tests and 96 Python unittest tests PASS (including new static synchronization contract). Live two-browser and PostgreSQL checks have not been performed. The new test is source-level, not end-to-end acceptance.
