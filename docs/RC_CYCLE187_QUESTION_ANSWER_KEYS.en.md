# Quorivio 0.1.0-dev — RC187 — Optional true/false answer keys

## Feature

**Question** widgets in **single-choice** or **multiple-choice** mode support optional answer-key grading. The editor exposes a True/False selector for every choice in the widget properties and its canvas context menu (right click / long-press the question text), including independent subquestions. Enabling the feature sets every choice to **False** by default. Single-choice questions permit at most one True choice; multiple-choice grading compares the exact set of selected choices to the True choices. **Reset true/false states** disables ordinary question grading and restores the original behavior. Open text and attachment questions remain ungraded.

Timed quizzes keep their existing mandatory answer key; the editor must not remove the final correct choice. Previously authored questions stay unchanged unless explicitly configured.

## Participant feedback and privacy

The server validates and persists an answer before returning **private, response-scoped feedback** to that participant: *Correct answer* or *Incorrect answer*, followed by the correct/incorrect status of each choice. The browser displays this result only following a successful submission. Answer keys are stripped from public activity projections, public result designs, session master layouts and WebSocket snapshots. Retries refer to the **previously stored answer**, never to the new guess in an idempotent duplicate request. Ungraded questions reveal no answer key or assessment.

Changing a key creates a new answer-definition revision; historical responses cannot be reinterpreted. Independent questions retain independent revisions and keys. With an explicitly enabled all-False key, any non-empty response is incorrect.

## Verification and limits

- Node API test coverage: opt-in, single/multiple truth, exact matches, reset, validation, public redaction, revisions, and persisted-response behavior.
- Node frontend coverage: property editor, context menu, independent question controls and post-submit feedback.
- Early Python CI preflight for privacy and mandatory guards.
- Full TypeScript/Vite build and authenticated React/PostgreSQL E2E remain **pending next GitHub CI** and are not claimed to have run locally.

Previous cumulative baseline RC186; last verified all-green campaign RC184 (`41993094578`). Certified completion **85.25%** (43 accepted and 17 partial gates). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. The assistant did not commit, push, tag or publish.
