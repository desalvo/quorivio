# Quorivio 0.1.0-dev — Release candidate readiness gate

**Status: RC BLOCKED pending CI and operational acceptance.** This document is a reproducible handoff, not a declaration of production readiness. Do not create a tag or change the application version before these gates succeed.

## Verified offline in the 2026-10-22 cumulative source package
- Node domain/API tests: 82 passing.
- Python suite: 60 passing, including HTTP calls against the private worker, authentication, job locking, boundary validation, and PDF rendering on the packaging host.
- API import now checks the converter manifest format, version, source type and SHA-256, page order, PNG signature, byte length and individual page SHA-256 before commit.
- Private worker health now responds with HTTP 503 when credentials or staging storage are unavailable.
- CI configuration installs Poppler and ReportLab, explicitly asserts ReportLab import to prevent accidental PDF-test skipping, invokes Python and real PDF rendering tests, builds API/web, boots PostgreSQL, builds both images, scans both images with Trivy, and runs Gitleaks.

## External release candidate gates (not verified here)
1. Commit the cumulative source changes to a test branch and obtain fully passing GitHub Actions quality and image-build gates, including the added PDF-rendering gate and the converter image vulnerability scan.
2. Run application and converter images from that exact Git SHA on Docker/Podman Compose; verify browser PDF and PPTX import, antivirus rejection, session navigation and participant answers.
3. Verify collaborative editing, activity updates and participant WebSockets from separate browser sessions; check concurrent questions and revisioned answers.
4. If high availability is in scope, run at least two API pods with shared RWX storage and a PostgreSQL service, validate OAuth callback coordination, rate limiting and WebSocket fan-out; verify conversion worker concurrency and crash recovery.
5. Verify approved external OIDC provider registrations, email delivery, backup/restore, accessibility/security and data retention policies using non-production credentials and real operators.

Do not assume percentage completion implies successful acceptance. Preserve `0.1.0-dev` until release approval, retain all project history in `docs/DEVELOPMENT_STATUS.md`, and do not auto-commit or publish.
