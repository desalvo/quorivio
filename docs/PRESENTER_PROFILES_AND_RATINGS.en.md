# Presenter profiles, collaboration and multiple ratings — Quorivio 0.1.0-dev

## Opening a project
The workspace lists projects **owned/authored** by the presenter and projects they were **invited to collaborate on**, with clear labels. Approved administrators are also eligible presenters, but this does not transfer ownership of others' sessions.

## Presenter profile
Presenters can set a public display name (2–100 characters) and an HTTPS photograph URL. This is currently a remote reference, not a built-in photo upload; assess image rights, privacy and third-party transfer. A neutral label is used if no public name is available, avoiding public email disclosure.

## Profile widget
Choose `+ profile` in the page editor, select a presenter belonging to that session, then save. Multiple profile widgets can be inserted and independently removed. Participant pages show the name and optional photograph. Rendering on every page type and result screen remains unfinished.

## Multiple satisfaction widgets
Add multiple `rating` widgets with distinct IDs and target types question, quiz, session or presenter. Choose the target presenter as needed. Each participant may submit one score per widget on the current activity; presenter statistics are grouped by widget and target. The `quiz` target currently references the activity, rather than a distinct multi-question quiz entity.

## Migration and validation
The migration adds presenter profile fields and changes the rating key from `(activity_id,participant_id)` to `(activity_id,participant_id,widget_id)` while mapping historical records to `legacy-rating`. Back up before applying the migration, and test against a real PostgreSQL instance. Production readiness remains conditional on integration and privacy testing.
