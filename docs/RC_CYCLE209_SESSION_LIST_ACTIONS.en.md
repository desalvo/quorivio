# RC209 — Owner session management from the Open Session list

Product version unchanged: `0.1.0-dev`.

## Changes

The authenticated **Open Session** list now allows the primary owner to:

- reset an **active, paused or closed** session to **ready** without opening it;
- permanently delete a session regardless of state.

Reset irreversibly removes audience identities, answers, ratings, results, and private participant files while retaining slide pages, widgets, authored media, and settings. Join code and URL rotate; the expiry is extended to at least 24 hours, including for closed sessions. Deletion uses the existing complete session erasure and cleanup path.

Only primary owners see these controls, and the backend independently checks authorization. Both actions require a session-named destructive confirmation; the listing disables concurrent actions, refreshes after success, and backs up a pagination page if the last item was deleted. Removing a stale selected-session reference clears only browser workspace navigation, **not authentication cookies**. Recoverable errors keep the listing available.

## Validation

- Node API suite: **616/616**; frontend suite: **368/368**.
- New RC209 Node tests: **4/4**, RC209 dependency-free Python tests: **4/4**. Focused RC71/RC208/RC209 Python regressions: **18/18**.
- The disposable PostgreSQL `ci_rc71_lifecycle_postgres.py` exercise now covers closed-to-ready reset, preserved design, rotated join code, and rejection of repeat reset on ready. GitHub CI execution is still pending.
- Full integrated React/TypeScript build and RC209 full CI still need verification; last independently verified full-green baseline: RC203, run `42110429701`.
- Certified product completion remains **85.25%** (43 accepted, 17 partial gates).

`rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, or tag.
