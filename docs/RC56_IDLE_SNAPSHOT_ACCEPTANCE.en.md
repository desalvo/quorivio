# Quorivio RC56 — Quiet live-session acceptance

## Defect and correction

WebSocket presence heartbeats updated PostgreSQL every 20 seconds, but idle browser sockets received no authoritative snapshots after opening. The cycle-55 65-second freshness watchdog could therefore close **healthy sockets**, creating unnecessary reconnect waves for large audiences.

`apps/api/src/live-periodic-refresh.ts` schedules one coalesced authoritative snapshot read/fanout **per active session** every 20 seconds. It reuses the existing session snapshot queue without additional PostgreSQL NOTIFY or per-participant reads; it sends the same role-filtered snapshot format as other live updates. Database failures cannot forge a heartbeat and leave client recovery enabled.

## Local tests and acceptance

- `node --experimental-strip-types --test apps/api/test/live-periodic-*-cycle56.test.ts` validates 500 subscribers to one session, overlap, failures, and a 10-minute synthetic idle session.
- `python3 -m unittest tools.tests.test_idle_live_postgres_cycle56 tools.tests.test_live_heartbeat_cycle56` validates the operator test and integration contracts.
- **After maintainer commit**, run `workflow_dispatch` with `live_idle_test=true`, `publish_image=false`, `rc_strict=false`. The opt-in acceptance only permits disposable `localhost:8080/8081` endpoints with PostgreSQL, creates a temporary session, watches presenter and participant sockets on opposite replicas for 70 seconds without any user mutations, requires snapshots at 35s/55s, checks privacy and deletes the session.

Do not target production: the test rejects non-loopback origins. A passing GitHub job may establish narrowly scoped real idle snapshot freshness, not a 500-client sustained SLO, real network failure recovery, public TLS, CSI RWX storage or external compliance acceptance. **Certified RC remains 81.25% until verified independently.**
