# Word cloud and moderated Q&A — Quorivio 0.1.0-dev

Audience members with a valid technical participation cookie can contribute one word (up to 48 characters) and up to three questions (5–500 characters) for each open activity. Questions are pending by default and are not shown publicly before approval.

Authorized presenters can retrieve word frequency counts, inspect pending questions, and approve or reject each question. The participant page lists approved questions only; each participant can upvote each approved question once.

Endpoints: `POST /api/join/:code/activities/:aid/words`, `POST /api/join/:code/activities/:aid/questions`, `GET /api/join/:code/activities/:aid/questions`, `POST /api/join/:code/activities/:aid/questions/:qid/upvote`, `GET /api/sessions/:id/activities/:aid/words`, `GET /api/sessions/:id/activities/:aid/questions`, `PATCH /api/sessions/:id/activities/:aid/questions/:qid`.

PostgreSQL tables: `audience_words`, `audience_questions` and `audience_question_votes`. Audience submissions may be personal data and require appropriate moderation, privacy notices and retention. Real PostgreSQL/browser/concurrency verification is pending.
