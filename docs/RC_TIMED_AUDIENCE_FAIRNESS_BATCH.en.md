# RC batch — timed quizzes, topic questions, tied leaderboards (2026-10-26)

**Baseline (already committed):** `d4ccead518f00ce00f6cd58cb0ff93fc81a26f91`. Standard CI `40368807527` and full Chromium/PostgreSQL CI `40369919680` **PASS**. The last publication stage is **SKIPPED**, by design. All changes described below are **post-baseline and uncommitted**.

## Functional delivery

1. **B2: widget quiz pool safety** — resolve participant identity before taking a PostgreSQL connection; preserve session/activity shared transaction locks, stable revision attribution, validation and duration checks. Release the connection after COMMIT and before WebSocket/PostgreSQL broadcast.
2. **B2: safe retries under the timer** — a committed widget answer receives `already_submitted:true` on retry even after the deadline. No double scoring or overwrite. New answers after expiry remain forbidden and time is measured from `clock_timestamp()` in PostgreSQL. The legacy timed-quiz endpoint now has matching retry semantics, a correct timed-only deadline condition and releases connections before notifications.
3. **B2/A3: fair tied scores** — both legacy and widget presenter-only rankings use `rank() over (order by elapsed_ms)`, computed before pagination. Equal millisecond scores share a rank; following ranks skip appropriately (e.g. 1,1,3). Timestamp/ID still provide deterministic secondary ordering. Revision scoping, invalidation filtering, authenticated presenter access and opaque participation are unchanged.
4. **B3: atomic topic question cap** — replace count-then-insert with `FOR UPDATE` on the same participant after locking the active session/page. Twelve simultaneous requests cannot create more than ten questions per participant/widget. The topic is validated against the current page while locked; inactive/closed pages reject writes. Notification occurs after commit and release.
5. **A3: participant/presenter usability** — tied ranks are visible to screen-reader and visual users with distinct React keys; timed-widget submission prevents rapid duplicate clicks, disables invalid empty answers, displays busy state and announces success/expiry via a live status region.

## Evidence and acceptance limits

- `npm test`: **447/447 Node PASS**, including five new server regression contracts.
- Focused Python suites: **21 widget + 18 moderation + 15 browser + 6 new delivery = 60/60 PASS**.
- TypeScript server parsing, Python compile, workflow YAML parse: **PASS**.
- The complete Python suite was attempted but exceeded the local runtime limit in document converter HTTP tests. No overall pass is claimed.
- Full TypeScript/Vite production build, actual PostgreSQL 18 acceptance and Chromium on the **new** batch were not available locally: **PENDING GitHub CI**.
- New mandatory CI test `tools/ci_timed_widgets_postgres.py`: 12 separate clients sharing one participant cookie, 12 topic submissions/10-limit, deterministic equal-time ranking fixture, expiration and retry of widget and legacy timed quizzes, session isolation and private leaderboard. The test requires a disposable loopback HTTP service, a separate opt-in flag and a 32+ character ephemeral token; SQL fixture also checks the exact disposable database URL. The test itself has **not** yet run against PostgreSQL.

## Release gate ledger

- B3 now has confirmed PostgreSQL and Chromium evidence from `40368807527`/`40369919680` but remains **partial** until independent accessibility/cross-browser/device review and new topic-quota replay. Do not mark accepted on Chromium alone.
- B2 and A3 remain **partial** until new PostgreSQL test, fresh Chromium/build and further fairness/device/visual evidence.
- D1 was **accepted for the green committed baseline**; future new code still requires a green CI.
- Strict weighted RC score: **48.0% (1 accepted / 15 partial / 2 open)**. This is not source code coverage and not a release-ready claim.
- Docker publishing remains **manual opt-in only**, including a separate consent for `latest`. No commit/push/tag/release was performed by the assistant.

**Recommended CI:** ordinary push quality+container (publication MUST be SKIPPED), followed by manual `workflow_dispatch` with `browser_test=true`, `publish_image=false` for browser acceptance. Do not run the optional 500-user load unless needed to evaluate B4.
