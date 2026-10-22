# Cross-replica session synchronization (experimental)

## Implemented

- The API publishes PostgreSQL `pg_notify('quorivio_session_update', sessionId)` after existing broadcast-worthy session mutations.
- Each instance has a dedicated `LISTEN` connection with reconnection. Only UUID payloads are accepted; no personal data travels in notifications and the receiving instance reloads an authorized snapshot from PostgreSQL.
- The Kubernetes generator permits 2–20 replicas only when assets use a `ReadWriteMany` PVC. Helm can mount a managed assets claim or a pre-existing one.
- Existing local WebSocket delivery remains available.

## Outstanding constraints

- PostgreSQL notifications are *best effort*, not a durable event stream. Reconnecting clients must obtain a fresh snapshot.
- OAuth/OIDC pending states and per-IP throttling remain process-local: **full multi-replica authentication is not yet supported**. Session affinity is useful for testing but does not replace shared state.
- The storage provider must really support RWX access; requesting `ReadWriteMany` does not implement it. Cross-pod file access and concurrency tests remain pending.
- Helm and Kubernetes have not been exercised on a real cluster.

## Acceptance tests

Deploy PostgreSQL, two API pods and a real RWX volume; connect browsers to different replicas, submit votes and confirm remote WebSocket snapshots; interrupt/reconnect a listener; verify cross-pod asset retrieval. Distributed OAuth state and throttling remain required before production multi-replica activation.
