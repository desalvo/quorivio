# Quorivio 0.1.0-dev — RC cycle 35 — 30 October 2026 — 80.75% (+0.50pp)

**Maintainer-committed baseline:** `f5ccf9a7545e7c17b4323d067db66aff5eca9b41` (cycle 33); cycle 34 and 35 remain uncommitted. GitHub Actions `41048187760` quality job `124037870206` passed *actual* PostgreSQL 18 simultaneous bootstrap with a single administrator and two ready API replicas, plus rolling `SIGTERM` readiness `503`, WebSocket `1012` and a healthy surviving replica. These distinct verified checks had not been credited separately. They are not the same as B1-WS/B1-RECONNECT or B4-KIND-INGRESS-RECOVERY.

**Verified RC score:** **80.25 → 80.75%**. Keep the original B1 weight of 2 split into B1 residual 1 (partial), `B1-BOOTSTRAP-PG18` 0.5 (accepted) and `B1-GRACEFUL-DRAIN` 0.5 (accepted). 52 gates total: 35 accepted, 17 partial; all weights total 100. This counts *only* the proven prior commit, not cycle34 or cycle35 code.

**New uncommitted code (not scored):** `withBootstrapLock` permanently removes a connection from the pool if lock acquisition or session setup fails; this avoids recycling an uncertain PostgreSQL session retaining `lock_timeout=120s` or an indeterminate advisory lock state. Additional Node regressions cover acquire timeout, setup failure, post-lock reset failure and false unlock acknowledgements. Tests on actual PostgreSQL 18 must be rerun in CI after user commit. No code or CI change is accepted merely because it was written locally.

**Outstanding:** independent multi-machine CSI/NFS RWX and failover, production TLS and HAProxy, real ARM hardware, sustained SLO with faults, browser/device and screen reader reviews, independent GDPR/AGID and security checks. Strict RC remains blocked; no image publish, push or tag. **CI after commit:** run standard quality (including PostgreSQL two-process bootstrap) and opt-in extended `kubernetes_multinode_test=true`, `clamav_runtime_test=true` with `publish_image=false`, `rc_strict=false`.

