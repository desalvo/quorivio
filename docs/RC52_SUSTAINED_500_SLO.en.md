# Cycle 52 — global 500-client latency SLO acceptance

## Scope
The default CI never runs sustained load. Opt-in `capacity_slo_test=true` creates a disposable PostgreSQL-backed session with 500 independent cookie jars and one presenter observer, 40-second ramp and 90-second hold.

## Evidence
`tools/load_500.py --latency-samples` records numeric-only `join_latency_samples_ms` and `first_snapshot_samples_ms`, never participant identifiers, answer contents or credentials. `tools/aggregate_load_500.py --strict-slo` computes a real global p95 from all raw samples instead of averaging shard quantiles. It rejects missing, contradictory, negative, nonfinite, short-duration or incomplete evidence.

**Default limits:** join p95 <=5000ms; first snapshot p95 <=8000ms; 500/500 joins and WebSockets, >=95% observer peak, zero errors, >=60s hold (CI runs 90s).

**Usage:** maintainer runs CI workflow dispatch with `capacity_slo_test=true`, `publish_image=false`, `rc_strict=false`, optionally also `kubernetes_tls_test=true`. Never use production endpoints. To combine shards: `python3 tools/aggregate_load_500.py shard*.json --strict-slo`. Exit code 2 means the SLO failed; invalid evidence produces a nonzero validation error.

## Independent residual gates
This is not a CPU/memory, WAN, real-host, physical-device, packet-loss or operational availability audit. B4 remains partial until real GitHub evidence and operator review; previously accepted B4-LOAD is never counted twice.
