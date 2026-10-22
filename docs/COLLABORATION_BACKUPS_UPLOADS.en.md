# Collaborative sessions, import/export and uploads — 0.1.0-dev

## Implemented in code (not end-to-end validated)

- Session title and ISO 8601 reference date.
- Owner-managed co-presenters, who must be approved and in the same organization.
- `GET /api/sessions/:id/export.json` exports **definitions only**, with no response or personal data. `POST /api/sessions/import` imports validated definitions; `POST /api/sessions/:id/duplicate` creates a clean draft with new access credentials and no responses.
- Live editing of question title and options preserving historical option IDs. An option with responses cannot be removed. The quiz answer key cannot be changed while valid responses exist; invalidate first.
- `POST /api/sessions/:id/activities/:aid/invalidate` marks responses invalid for audit and excludes them from live results/CSV. A new response after invalidation is not yet supported due to uniqueness constraint.
- Configurable upload ceiling `max_upload_mb` (1–1024, default 100). Kubernetes wizard emits corresponding ingress size. File upload ingestion, malware scanning, storage, quotas and conversion are **not yet implemented**.

## Outstanding for production

- Full admin backup/restore with PostgreSQL-consistent snapshot, S3/media objects, manifest, checksums, encryption, validation, versioned restore and recovery rehearsal. Do not expose unvalidated raw database import endpoints.
- Complete session archives including results and attachments with GDPR safeguards; current JSON export contains **definitions only**.
- Full UI for co-presenters, duplicating/import/export and live edits.
- HAProxy community upload-size configuration must be validated for the exact controller distribution; `haproxy.org/max-body-size` applies to HAProxy Technologies.
- PostgreSQL integration, multi-presenter WebSocket and migration verification.
