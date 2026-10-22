# Independent question widgets — 0.1.0-dev

A page can contain multiple `question` widgets with unique identifiers, titles, modes (`single`, `multiple`, `text`, `file`), `required` flags and independent option sets. Presenters configure the question type, required flag and options in the widget editor, then save the page layout. Participants submit each widget separately from the primary page answer.

Endpoint: `POST /api/join/:code/activities/:aid/widgets/:wid/respond`. Use `{ "option_id": "choice-1" }` for single choice, `{ "option_ids": ["choice-1", "choice-2"] }` for multiple choice, `{ "text": "..." }` for free text or `{ "asset_id": "UUID" }` for attachments. Identity comes from the session participant cookie. The server requires an active session and open activity, validates the persisted widget definition and inserts into `widget_answers` with uniqueness `(activity_id,participant_id,widget_id)`.

Authorized presenters can retrieve aggregate counts from `GET /api/sessions/:id/widget-answers`. Private answer content is never broadcast publicly. Limitations: anonymous participant file uploads, integration tests with PostgreSQL/browser and widget version history remain pending. Removing a widget from the layout does not silently delete historical records; they are deleted when its session is purged.
