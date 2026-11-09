# Quorivio 0.1.0-dev — RC277 | Fully rewritten bilingual manuals

## Scope

All six administrator, presenter and participant PDF manuals have been rewritten in Italian and English from editable Markdown sources in `docs/manuals-src/`. The reproducible publisher `tools/generate_manuals.py` uses Mistune and WeasyPrint. Copies in `docs/manuals/` and `apps/web/public/docs/manuals/` are byte-identical. Cover version/build: `0.1.0-dev / RC277 / 9 November 2026`.

- Participant: QR/link/code, single/multiple/text/file submissions, timed quizzes, 0–9 rating, reactions, moderated audience questions, ✓/✕ feedback only after submission, privacy and troubleshooting.
- Presenter: full event workflow, canvas/master editor, all **21 widget types**, separate formatting, mobile/desktop backgrounds, live/preview behavior, bars/pie/table/cloud results and R toggle, PDF/PPTX conversion, Q&A, media, ownership/collaboration, export and acceptance procedures.
- Administrator: Compose/Helm/standalone Kubernetes wizard, PostgreSQL 18, ingress, PVC/RWX, POSIX/NFS/S3/WebDAV backups, schedules and manual restore, LDAP/LDAPS self-registration/approval, SMTP/OIDC/MFA, audit retention, converter, antivirus, monitoring, security/GDPR and runbooks.
- Illustrations: existing photographic-style project cover, six browser-rendered captures of an **illustrative static UI reconstruction**, two charts with invented demonstration data and two process diagrams. They are all labelled **not live screenshots** and must be replaced with verified captures as part of independent D5 editorial acceptance.

## Validation and remaining work

No RC276 runtime changes, no GDPR/AGID certification. Documentation publication does not prove real device or external LDAP/SMTP/storage behavior. PDFs are checked for page structure, text/keywords and identical web copies; sources and visual assets are retained. Independent end-user editorial review, real live screenshots and full CI remain pending.

Certified project baseline remains **85.25%** (43 accepted/17 partial gates); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag.
