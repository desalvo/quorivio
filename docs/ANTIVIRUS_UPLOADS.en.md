# Antivirus scanning for uploads (0.1.0-dev)

Presenter uploads, participant attachments, and imported presentation sources can be scanned using a private ClamAV/clamd service over its `INSTREAM` protocol. Uploads are transmitted in bounded chunks. Malware detections, protocol errors, timeouts, and dropped connections are not considered clean.

Set `QUORIVIO_AV_REQUIRED=true`, configure `CLAMAV_HOST` (private, not publicly exposed), and optionally set `CLAMAV_PORT` (3310) and `CLAMAV_TIMEOUT_MS` (30000). With scanning required, a missing or unreachable scanner blocks the upload before database insertion. The default `false` is for development compatibility **and is not a safe production configuration**.

Local tests exercise clean, infected, and erroneous scanner responses with a mock clamd endpoint. Testing with actual ClamAV signature databases, concurrent large files, rate limiting, and multi-replica shared storage remains open. API errors are currently generic rather than antivirus-specific.
