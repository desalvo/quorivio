# 500-participant staging load — shard reconciliation (2026-10-24)

**Not an executed load-test report.** Run only against an authorized staging endpoint. Do not run against production without a controlled test window. The existing `tools/load_500.py` creates independent anonymous participants in each shard and saves a JSON report per shard; shards must target the *same* session. To reconcile five hosts/processes, give every generator `--users 500 --shards 5 --shard-index N --json-out shard-N.json`. Exactly one shard may use the presenter observer cookie. The simulated participants are apportioned by their global index rather than duplicated between shards.

Once all five processes have finished, copy their JSON reports to the review machine and run:

```bash
python tools/aggregate_load_500.py shard-0.json shard-1.json shard-2.json shard-3.json shard-4.json --expected 500 --json-out 500-review.json
```

The tool fails closed (exit code 2) on incomplete joins, WebSocket failures, reported errors, missing presenter observer or an observed peak below 95% (475) of the target. Malformed, duplicated, missing or inconsistent shard topology is rejected with a command-line error. It does not add peak measurements across independent observers, since that would exaggerate concurrency. An aggregate PASS only means the reported QR join/WebSocket checks passed; it **does not** establish actual simultaneous distinct connections, response/quiz fairness, PostgreSQL consistency, multi-replica behavior, latency SLO compliance or RC acceptance. Review timestamps, server-side metrics, traffic profiles, memory/CPU, PostgreSQL pool activity, and privacy protections. Keep D4 open until those independent criteria pass.
