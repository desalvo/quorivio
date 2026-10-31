# Quorivio 0.1.0-dev — cycle 57: efficient, authorization-scoped WebSocket fanout

**Maintainer baseline:** commit `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; cycles 49–57 remain cumulative and uncommitted. **Certified RC 81.25%** (53 gates: 36 accepted, 17 partial); no credit for uncommitted local-only changes.

## Defect and remediation

Each live refresh independently JSON-serialized the same presenter or public projection for each WebSocket: 500 participants plus one presenter could require 501 serializations, even though only two authorization views exist. Initial connection delivery also read and sent a database snapshot outside the ordered refresh queue, potentially racing newer snapshots.

The new `apps/api/src/live-broadcast.ts` serializes **one message for each nonempty authorized view, per session and replica**. It reuses the presenter message only for authorized presenters and constructs the public message through `participantSnapshot` for audience sockets. Both messages are prepared before sending; public-projection errors cannot cause partial delivery of owner-only data. Slow consumers are closed individually using the existing 2 MiB backpressure bound; a transport failure cannot stop delivery to other sockets.

Initial delivery now joins `broadcastLocal(sid)`, reusing `createLiveSnapshotQueue` shared with PostgreSQL notifications and quiet-session refreshes. The separate asynchronous `snapshot(sid).then(...send...)` path was removed.

## Validation and outstanding gates

New Node tests exercise 501 clients with **exactly two serializations**, privacy isolation, one-view sessions, slow sockets, individual transport errors, mid-flight closure and fail-closed public projection. Python contracts assert the queue integration and immutable cycle-56 catalog. No new npm dependency or client protocol change.

Still required: GitHub TypeScript/Vite build, live PostgreSQL tests, `live_idle_test`, sustained `capacity_slo_test`, and Kubernetes acceptance. These local checks are not independent evidence of CPU savings or p95 latency in production. **Certified RC remains 81.25%.**

After maintainer commit run standard CI, then extended with `capacity_slo_test=true`, `live_idle_test=true`, `kubernetes_tls_test=true`, `publish_image=false`, `rc_strict=false`. No assistant commit, push, tag or publish.
