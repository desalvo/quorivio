# Antivirus scanning for uploads (0.1.0-dev)

Presenter uploads, participant attachments, and imported presentation sources can be scanned using a private ClamAV/clamd service over its `INSTREAM` protocol. Uploads are transmitted in bounded chunks. Malware detections, protocol errors, timeouts, and dropped connections are not considered clean.

Set `QUORIVIO_AV_REQUIRED=true`, configure `CLAMAV_HOST` (private, not publicly exposed), and optionally set `CLAMAV_PORT` (3310) and `CLAMAV_TIMEOUT_MS` (30000). With scanning required, a missing or unreachable scanner blocks the upload before database insertion. Production now always requires a scanner for uploads, even if `QUORIVIO_AV_REQUIRED` is omitted or set to `false`. The optional `false` setting can disable scanning **only outside production**, for controlled local development and tests. An invalid boolean policy is rejected. Connection loss, a premature clean response, oversized scanner output and expiration of the **overall scan deadline** fail closed.

Local tests exercise clean, infected, and erroneous scanner responses with a mock clamd endpoint. Testing with actual ClamAV signature databases, concurrent large files, rate limiting, and multi-replica shared storage remains open. API errors are currently generic rather than antivirus-specific.

## Kubernetes generator (cycle 32)

`tools/k8s_wizard.py` now defaults to `antivirus_mode=managed` and emits a private ClamAV Deployment, ClusterIP Service and ingress-restricting NetworkPolicy. The application gets `QUORIVIO_AV_REQUIRED=true` and the private scanner DNS name. To use an independently managed clamd service instead, configure `antivirus_mode=external` **and** `antivirus_host=<private DNS name>`; no managed scanner objects are generated. Switching modes removes previously generated managed objects. External service availability and signatures are operator responsibilities; a missing scanner makes uploads fail closed.

The managed image may require up to 4 GiB per scanner replica during database update/reload; use suitable memory capacity and review image privilege requirements. The private NetworkPolicy does not replace namespace-wide egress restrictions or a security audit. `clamd` must be configured with sufficient INSTREAM `StreamMaxLength` for the desired accepted uploads; a smaller limit will reject scans, never permit unscanned content. This cycle's manifest/protocol mock tests do **not** certify startup of the actual ClamAV image, infection-signature detection, Pod Security Admission policy, physical devices or storage failover.

## Optional real ClamAV CI test

GitHub workflow dispatch with `clamav_runtime_test=true` runs an isolated ClamAV container, exposes port 3310 to **loopback only**, scans a clean temporary file and a harmless EICAR test signature, and removes the container and test files. This is a real engine/signature acceptance only after that job succeeds; it is NOT a pentest or full production deployment audit. The test is opt-in because signature database initialization and memory use are substantial.
