# Scheduling, pagination and session lifecycle

`GET /api/sessions?page=1&page_size=10&search=...&role=all|owner|collaborator` and `GET /api/admin/users?page=1&page_size=10&search=...&approval=all|approved|pending` return `{items,total,page,page_size}`. Older requests without `page` retain their legacy array response.

`GET /api/calendar?from=YYYY-MM-DD&to=YYYY-MM-DD` lists the current user's owner/collaborator appointments. `GET /api/sessions/:id/appointments` and `PUT /api/sessions/:id/appointments` read and replace scheduled dates, HH:MM local start times, durations (5–1440 minutes), and IANA timezones. Updating requires session ownership.

Use `POST /api/sessions/:id/status` with `paused`, then `active` to resume. Validate PostgreSQL migrations on a backup and test DST boundaries, browser rendering, and multi-replica behavior before production. The new monthly calendar is an initial implementation, not feature parity with Google Calendar.
