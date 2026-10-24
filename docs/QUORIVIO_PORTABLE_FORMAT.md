# Quorivio portable session archive (v1)

The `.quorivio` file is a bounded ZIP archive with `manifest.json` plus `media/<UUID>` members. The manifest carries a v1 `quorivio-session` definition and a media manifest with MIME, byte count and SHA-256 for each embedded file. The exporter includes only session-owned, non-participant assets actually referenced by page or result widgets, backgrounds, or the theme. It does **not** contain participant identities, submissions, responses, access cookies, join codes, passwords or MFA secrets. Import always creates a new draft session with fresh join credentials.

The authenticated API endpoints are `GET /api/sessions/:id/export.quorivio` and `POST /api/sessions/import.quorivio` (Content-Type: `application/vnd.quorivio.session+zip`). The frontend presents these alongside legacy JSON and PPTX workflows. Import can use PNG, JPEG, GIF, WebP, PDF, MP4 and WebM assets, with up to 300 embedded files / 80 MiB uncompressed media / 100 MiB archive. The ZIP parser rejects paths outside the exact manifest/media layout, duplicate members, encryption, unsupported compression, corrupted checksums and excess sizes. The API checks the session's asset ownership and hashes on export, and creates new asset records within an import transaction.

## Compatibility and limitations

The original `export.json` and `POST /api/sessions/import` remain supported as a **definition-only legacy format**. The new v1 bundle deliberately excludes participant data and operational session state. Imported sessions are independent drafts. Only media referenced in supported widget fields and background fields are portable; unreferenced uploads and arbitrary external URLs are not embedded. Linked external URLs may not work offline. This is not intended as a full server or account backup.

## Acceptance checks

1. Create a session with image/logo/video/PDF widgets and page/result backgrounds; export `.quorivio`.
2. Import on a separate Quorivio deployment, verify new credentials and that pages/assets render, and edit/save each page.
3. Confirm no participant data or old QR/join code is present.
4. Tamper with an asset hash, member name, ZIP header and manifest; each must fail without leaving an imported session.
5. Confirm legacy JSON import/export still works.
