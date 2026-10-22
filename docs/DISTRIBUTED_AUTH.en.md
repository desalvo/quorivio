# Cross-replica authorization state and request throttling

The `auth_flows` table stores the SHA-256 hash of OAuth state, flow kind, provider and temporary callback parameters. The first valid callback consumes state atomically with `DELETE ... RETURNING`, after which it is unavailable to subsequent callbacks. States expire after five minutes. The application additionally checks state cookies and requires explicit identity-to-account linking.

The `api_rate_windows` table stores an IP-address hash and a one-minute bucket. The current global limit is 100 API requests/minute per source IP across all replicas, returning HTTP 429 beyond the limit. Database failures return HTTP 503 (fail closed). Hourly maintenance removes expired flow states and stale rate buckets.

**Limitations:** deploy behind a trusted, correctly configured reverse proxy; test client-IP handling and NAT fairness, concurrent requests and real PostgreSQL migrations. External identity-provider registration and integration tests remain pending. Store OAuth client secrets outside source control.
