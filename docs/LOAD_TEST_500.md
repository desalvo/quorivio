# Quorivio 500 participant load test

Target: **one presenter and up to 500 concurrent audience connections**. This is an acceptance target, not a measured throughput claim. Use `tools/load_500.py` against an explicitly authorized staging instance, with its join secret, session ID, and authenticated presenter cookie.

For a single-machine generator, provision file descriptors and separate the generator from the server. On staging only, configure `NODE_ENV=development` and a random `LOAD_TEST_TOKEN` (32+ characters) to allow authenticated load requests to bypass the shared HTTP limiter; production never accepts this bypass.

```bash
python -m pip install aiohttp
python tools/load_500.py --url https://staging.example --session-id UUID --join-code JOIN_SECRET --presenter-cookie 'q_auth=...' --load-token "$LOAD_TEST_TOKEN" --users 500 --ramp-seconds 60 --hold-seconds 120
```

Record join p50/p95/p99 latency, failures, count peak, database and ingress metrics, WebSocket update latency, and application CPU/RAM. These have not been measured in Kubernetes yet. Presence uses the database and counts distinct participants across replicas, with a 50-second stale window after an abrupt network loss.

> **Update:** the former `--url` / `--join-code` CLI has been replaced by anonymous QR flow `--join-url`. See `docs/ARCHITECTURE_500.md` for multi-generator setup, resource estimates and acceptance criteria.
