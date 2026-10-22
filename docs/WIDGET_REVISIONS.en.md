# Independent question-widget revisions — 0.1.0-dev

When an authorized presenter changes a question widget's answer mode, required flag or options, the server creates a numbered revision in `widget_revisions`. Earlier responses remain in `widget_answers`, attributed to their historical revision. Cosmetic label/style changes do not create a new revision.

## Procedure

1. Open the session editor as an authorized presenter.
2. Change the question widget's answer settings and save the page.
3. New submissions bind to the new revision. Old submissions remain available for audit.
4. `GET /api/sessions/{id}/widget-answers` returns response counts per revision.
5. `GET /api/sessions/{id}/widget-answers/detail?activity_id={uuid}&widget_id={id}` returns per-revision option frequencies and counts of text/file answers without exposing individual text.

**Limits:** PostgreSQL integration and concurrency tests remain pending, as do an explicit selective widget-answer invalidation workflow and anonymous participant direct uploads. Review SQL migrations and test backup/restore before deployment.
