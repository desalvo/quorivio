# Timed quiz and Results control — initial implementation (23 October 2026)

## Included in package
- Distinct `timed_quiz` activity selectable as Timed Quiz, single/multiple correct answers, mandatory 5–600 second duration (UI currently sends 30 seconds).
- Server-authoritative start at `activities.opened_at`, assigned when the presenter opens the page and broadcast over WebSocket. Elapsed time is measured server-side upon answer receipt, never trusted from browser clocks.
- `responses.elapsed_ms`, partial ranking index, presenter-authorized endpoint `GET /api/sessions/:id/activities/:aid/timed-leaderboard`: total and correct counts, top 100 correct respondents ordered by elapsed milliseconds, submission timestamp and UUID.
- Correct single/multiple scoring, incorrect/invalidated answers excluded, correct answer keys hidden from public payloads.
- Separate `timed-quiz` and `results-button` palette widgets with persisted geometry. Presenter view exposes a collapsed-by-default Results control and a leaderboard refreshed every two seconds. Participant view does not render the Results control.
- Shared start countdown shown in participant and presenter screens. Frontend/backend builds pass, 90/90 Node tests pass.

## Not yet implemented / validated
- The `timed-quiz` widget is a visual marker for the activity-wide timed quiz, not an independent question with its own submissions on a slide.
- Results button positioning is only approximate, not absolute geometry faithful to the editor. Topic questions and widget-specific details remain in the separate presenter dashboard, not the Results overlay.
- No per-widget context menu selecting bars/pies/word clouds, additional visualizations or live/final display selection yet.
- Start is based on server publication, not guaranteed simultaneous visual display in every browser. Network latency and distributed fairness need testing; millisecond-level competitive fairness is not claimed.
- PostgreSQL, multiuser/browser tests, retries/concurrency, privacy/security checks, multi-replica deployment, and aligned PDF manuals are still pending.
- RC gate score remains **67%**, pending real acceptance; no commit or release performed.
