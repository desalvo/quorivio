# Participant uploads — Quorivio 0.1.0-dev

A joined anonymous participant can upload a file directly from an open `file` question widget. Allowed types: PNG, JPEG, GIF, WebP, PDF, MP4 and WebM; size is governed by the administrative setting (default 100 MB) and ingress limits. The API validates the session, active page, participant cookie, file widget, MIME type and binary signature. Upload returns an asset ID, which the UI passes automatically when the participant submits their answer. Uploaded files are private and bound to the participant identity; other participants cannot reference them in answers.

## Outstanding production safeguards

The API currently buffers files in memory. Antivirus scanning, streaming to shared storage, durable cleanup of abandoned uploads, and concurrency-safe quotas are not implemented. A provisional limit of ten uploads per participant/session is enforced but is not transactional. PostgreSQL migration and real-browser/identity integration tests are still required.
