# Live snapshot queue: failure recovery and acceptance boundary

The local per-session queue coalesces overlapping notifications into a final DB read. Calls joining an in-progress read now await its final completion instead of immediately resolving. Read errors are logged and surfaced to the caller even if later coalesced reads succeed; this causes PostgreSQL LISTEN recovery to reconnect and resnapshot. A failed queue can be reused after cleanup.

## Evidence
- `npm run build`: backend TypeScript and frontend TypeScript/Vite PASS.
- `npm run test -w @quorivio/api`: 152/152 PASS.
- `python -m pytest -q tools/tests`: 252 PASS, 10 subtests PASS.
- New tests cover concurrent completion and failure/reuse.

## Not accepted yet
- PostgreSQL 18 multi-replica delivery and restart, two-browser lifecycle, 500 participants and latency under load have not been executed in this cycle.
- RC B1 remains partial. No real server, GitHub, tag or deployment changes.
