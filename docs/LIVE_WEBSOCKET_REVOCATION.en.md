# Live presenter authorization across replicas

As of the current 0.1.0-dev cumulative development cycle, each API replica checks all established authenticated presenter WebSocket connections against PostgreSQL every 10 seconds. User approval, forced password changes, password-change revocation and administrative MFA reset revocation are enforced for existing connections. A revoked socket is closed with code 4003; a database error closes affected presenter sockets with code 1011 (fail closed). Participant WebSockets remain governed by the pre-existing participant identity lifecycle; this change does not add participant revocation.

The database is shared by all replicas, so the policy needs no process-local cross-node broadcasts. Revocation is **not immediate**: expect up to approximately 10 seconds plus scheduling/query latency, and test actual multi-replica behavior before production. In-flight messages before the next audit can still be delivered. A separate integration test is required to validate PostgreSQL behavior, deployed load balancer routing and reconnect handling.

Verified locally: TypeScript API build, Vite production build, 95 Node tests, 93 Python tests. These are not substitutes for a live multi-replica test. The requested optional email second factor and additional admin/SSO work remain open; do not claim they were implemented by this change.
