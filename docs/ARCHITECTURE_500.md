# Quorivio — reference deployment for 1 presenter and 500 anonymous participants

**Planning estimate, not certified capacity.** The test mirrors the invitation QR URL: fetch `/join/<token>`, read public session details, anonymously join with a unique cookie, and connect to `/live?session=<uuid>`. No participant accounts are created.

## Topology and initial sizing

Internet/mobile clients → TLS load balancer → 2 Ingress NGINX or HAProxy replicas → Kubernetes Service → 3 Quorivio pods → PostgreSQL 18 and shared RWX media storage. The Quorivio Helm deployment currently includes a converter and ClamAV sidecar in each pod; factor both into memory planning. `helm/quorivio/values-500-staging.yaml` provides an **optional staging sizing profile**, not validated production settings.

| Component | Count | CPU requested / maximum | Memory requested / maximum |
|---|---:|---|---|
| API | 3 | 0.5 / 2 CPU each | 512 MiB / 1 GiB each |
| Converter sidecar | 3 | 0.25 / 2 CPU each | 512 MiB / 2 GiB each |
| ClamAV sidecar | 3 | 0.2 / 2 CPU each | 768 MiB / 2 GiB each |
| PostgreSQL 18 | 1 primary | reserve 2–4 CPU | reserve 4–8 GiB |
| Ingress | 2 | 0.5–1 CPU each | 256–512 MiB each |

Plan three worker nodes with ~4 CPUs and 8–16 GiB available each plus headroom (at least 30%), appropriate spread/anti-affinity, a PDB and graceful WebSocket draining. Use RWX for shared assets, SSD-backed PostgreSQL with bounded connection pools, and pre-scale before an event. An HPA minimum 3 / maximum 6 at 60–70% CPU is a candidate **only after cross-pod broadcast is validated**.

**Important:** PostgreSQL LISTEN/NOTIFY provides cross-pod fan-out, including resynchronization after reconnect. Its actual latency and recovery under load remain to be validated with multiple Kubernetes replicas.

At 500 receivers, 10 KiB snapshots at 1 Hz cost ~41 Mbit/s payload; 100 KiB cost ~410 Mbit/s before TLS/network overhead. Plan at least 1 Gbit/s internal networking and measure real internet egress; prefer delta events and cacheable authorized media. Ingress needs WebSocket upgrade, TLS/origin forwarding, idle read/send timeout ≥3600 seconds. NGINX sample annotations are in the staging values profile; configure equivalent tunnel timeouts on HAProxy using its own controller syntax.

## Load simulation and distributed IP sources

```bash
python -m pip install aiohttp
python tools/load_500.py --join-url 'https://staging.example/join/QR_TOKEN' --session-id UUID --users 500 --ramp-seconds 120 --hold-seconds 300 --presenter-cookie 'q_auth=...' --load-token "$LOAD_TEST_TOKEN" --json-out metrics.json
```

For five real load-generator hosts, run the same command with `--shards 5` on all machines and distinct `--shard-index 0` to `4`; only the observer shard needs the presenter cookie. Each host then simulates 100 participants, yielding 500 overall. `--source-ips` can bind to locally assigned addresses, but cannot invent public egress IP addresses. Use authorized hosts/networks only. The staging-only rate-limit test token must not be enabled in production.

## Proposed acceptance gates

* 500 distinct anonymous participants concurrently connected for five minutes, plus one presenter, with no OOM or crashes.
* ≥99% join success; 5xx below 0.5%; join latency p95 <3 seconds on controlled test networking.
* ≥99% page switches and quiz publication received within 2 seconds (p95) on **different pods**.
* Presence converges within 5 seconds after all join; stale disconnected clients disappear within 60 seconds.
* Reconnect, pod loss, parallel answer submissions, ingress failover, database locks/pool, CPU, RAM and egress measured.

The provided script measures join time, first snapshot and presenter-observed peak (when credentials are provided); it does **not yet automatically verify cross-pod event-latency gates**. Obtain those metrics using dedicated event probes and cluster monitoring. The requirement is not yet certified.


## Event bus recovery / Ripristino del bus

The API already uses PostgreSQL LISTEN/NOTIFY for cross-pod event fan-out. Each instance subscribes on a dedicated connection and reloads snapshots from PostgreSQL when notified. The listener automatically reconnects after failures; after each successful LISTEN it re-snapshots all sessions having local WebSocket clients to recover missed events. This mechanism requires a connectivity and failover test with multiple replicas; it does not constitute a certified 500-user result.
