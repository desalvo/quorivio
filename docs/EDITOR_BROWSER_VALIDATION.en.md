
## 2026-10-23 — Chromium editor validation: local-server access blocked
- Chromium 144 and Python Playwright are installed and launch successfully, but the managed browser blocks navigation to the local Vite server at 127.0.0.1 (`ERR_BLOCKED_BY_ADMINISTRATOR`). No browser E2E or PostgreSQL acceptance was performed (PostgreSQL server unavailable).
- Fixed accidental drag gestures when interacting with widget input fields; lost pointer capture now cancels the active gesture and restores the previous geometry. Regression tests were updated.
- Backend/frontend builds passed; Node 107/107 and Python 104/104. RC gate score remains 37.5% under the existing matrix; source tests are not counted as real browser acceptance.

### Pending acceptance
- Mouse and touch drag/resize/rotation in browsers.
- Save and reload with PostgreSQL 18.
- Keyboard and screen-reader review; mobile and tablet viewport inspection.
