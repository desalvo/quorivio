# Quiz and reactions — Quorivio 0.1.0-dev

Quizzes and polls: single choice, multiple choice, free text up to 5000 characters, or file references; a required-answer flag; server-side validation. Reactions: 👍 ❤️ 😂 😮 👏 🎉 🤔 😕, limited to one per participant per activity; per-page, per-participant, and per-session presenter statistics. Database persists structured answers in JSONB and enforces reaction uniqueness.

**Not complete:** anonymous upload through the participant UI, reactions on non-activity pages, multi-question quiz grouping, PostgreSQL/browser end-to-end tests, and production readiness.
