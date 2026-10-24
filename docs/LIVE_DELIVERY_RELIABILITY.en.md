# Live delivery reliability — 2026-10-24

## Changes

- Live snapshots on each replica now use a per-session coalescing dispatcher. Multiple PostgreSQL notifications during a running snapshot trigger one additional fresh read, rather than concurrent reads that could deliver stale snapshots after newer snapshots.
- Each WebSocket consumer has a 2 MiB queued-byte limit. Slow consumers are closed with WebSocket status 1013 (`slow_consumer`), avoiding unbounded memory retention on a presenter replica. The client must reconnect to receive a fresh snapshot.
- Failures in a snapshot read are logged; a newer notification queued during that read is still processed.

## Verification

Backend TypeScript PASS, frontend TypeScript/Vite production build PASS, Node tests 143/143 PASS, Python tests 235/235 PASS (local environment). Five new Node tests cover notification coalescing, independent sessions, transient failures and bounded socket buffering. No real PostgreSQL, browser, multi-replica or 500-participant test was performed in this cycle.

## RC acceptance still required

Two-browser session lifecycle, PostgreSQL LISTEN/NOTIFY across at least two API replicas, network interruption/reconnect, timed quiz and results consistency, 500 concurrent participants, WebSocket memory and reconnect telemetry. These are external runtime gates and remain open/partial.
