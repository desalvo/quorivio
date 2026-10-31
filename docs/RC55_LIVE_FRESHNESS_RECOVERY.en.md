# Quorivio 0.1.0-dev — RC cycle 55: WebSocket snapshot freshness and stale data visibility (30 October 2026)

**Last confirmed commit:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; **cycles 49–55 remain uncommitted and cumulative**. **Certified RC unchanged at 81.25% (53 gates, 36 accepted / 17 partial)**; no score promotion from local changes.

**Functional change:** a 65-second snapshot-freshness watchdog for browser live WebSockets, vs server snapshots approximately every 20 seconds. Only valid matching-session snapshots renew freshness. A stale or errored socket is retired/fenced, stale events cannot replace fresh session state, reconnect uses existing bounded jittered backoff, and timers are cleaned on offline/dispose/terminal close.

**UI:** accessible connection-loss/access-revocation warnings on presenter statistics and the projection screen to mark retained data as potentially stale, without hiding it. No database protocol or stored response change.

**Evidence/limits:** 505 backend / 99 frontend Node tests PASS; 1,347 Python tests PASS in eight groups (one skipped); focused TypeScript compile PASS; deterministic new frontend Node tests, Python integration contracts, manifests. Full CI, actual multi-replica impairment, realistic 500-client latency/recovery and independent hardware/device acceptance remain required. HTTPS and SLO opt-in acceptance from earlier cycles still requires GitHub on the uncommitted cumulative.

---

