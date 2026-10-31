# RC cycle 58 — Verified GitHub evidence and bounded WebSocket refresh

**Committed baseline:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`. Standard CI `41152434205` and extended CI `41152939003` succeeded. Extended quality job `124393360139` actually ran both `live_idle_test=true` and `capacity_slo_test=true`.

## Evidence-scoped reconciliation

The **70-second idle session with two API processes and shared PostgreSQL** proves real authoritative snapshots, owner/audience privacy separation and no erroneous disconnection. Accepted subgate `B1-IDLE-TWO-REPLICA` has bounded weight 0.5. The separate **500 independent participants, global p95 latencies, >=60s sustained hold and zero errors** proof accepts `B4-500-GLOBAL-SLO`, weight 0.5. Residual parent gates `B1` and `B4` each decrease by 0.5 weight but remain partial. Total weight remains 100, improving the evidence score from 81.25 to **81.75%** (55 gates: 38 accepted, 17 partial). Prior B4-LOAD and B1-RECONNECT scopes are not credited twice.

**Outstanding:** `kubernetes_tls_test=false` in the verified run; no new real KIND TLS proof. No multi-machine CSI/NFS RWX, geographically distributed long-duration load, or independent security/accessibility/GDPR/AGID sign-offs. Strict RC remains blocked, `rc_strict=false`.

## New local functional hardening (requires another CI run)

`apps/api/src/live-periodic-refresh.ts` now bounds cross-session database snapshot reads to eight concurrent workers instead of an unbounded `Promise.all`. A single session still fan-outs only one shared snapshot. Overlapping intervals do not create a second sweep; queued sessions are revisited by the existing workers, and departed sessions are skipped when no longer connected. Failed DB reads and logging exceptions cannot starve later sessions. Valid concurrency is an integer 1–32.

A deterministic test with 500 distinct active sessions and held DB promises proves at most eight simultaneous reads. This is **not** an actual 500-session production test or a guarantee against staleness during a >65-second DB outage. No additional RC score credit until GitHub. Next run: standard and extended CI with `publish_image=false`, `rc_strict=false`. Explicitly enable `kubernetes_tls_test=true` to test real KIND HTTPS.
