# GitHub Actions 40379416187 — timed leaderboard BIGINT regression (2026-10-26)

**Committed SHA:** `5369f4384358face1822d4ada8a2df20425e32c2` (timed widgets + contextual editor).
**Failure:** required PostgreSQL E2E `tools/ci_timed_widgets_postgres.py:79`: `TypeError` comparing string `duration_ms` with integer. The failure followed 447 successful Node tests, successful TypeScript frontend/backend compilation, SMTP MFA E2E and real PostgreSQL audience moderation. Container skipped; Docker publication skipped by opt-in policy.

## Root cause / scope

The two timed ranking SQL queries project PostgreSQL `BIGINT` (int8) `elapsed_ms` as `duration_ms`. The Node PostgreSQL driver returns an int8 as **string** to avoid numeric precision loss. The frontend already formats it explicitly using `Number(duration_ms)` in its UI. The new Python CI test assumed an integer at its first ranking assertion. This is a test-contract bug, not a missing timer or UI bug.

## Changes

- `tools/ci_timed_widgets_postgres.py`: lossless parser validates nonnegative decimal-string int8, compares values as Python integers; applies checks to both widget and legacy rank endpoints as well as the deterministic tied-rank fixture. Never changes SQL types, ranking behavior, storage or auth.
- `tools/tests/test_ci_timed_leaderboard_duration.py`: four focused test methods cover correct full int8 precision, non-string/lossy encodings, SQL projections and verification that actual HTTP acceptance uses the parser.
- IT/EN status and RC ledger document the real failed run, unchanged 48.0% readiness and next verification requirements.

## Acceptance required

On next commit run the standard GitHub Actions pipeline and verify **PostgreSQL timed-widget fairness, retry and topic concurrency acceptance: SUCCESS**, quality/container gates: SUCCESS, production publication: SKIPPED. Then run manual Chromium/browser test with publishing disabled to certify the contextual editor. No assistant commit or push was made.
