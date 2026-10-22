# CI security gate follow-up — 2026-10-22

The GitHub Actions run `107927415489` passed dependency installation, 82 Node unit tests, TypeScript frontend/backend compilation, PostgreSQL 18 API startup, readiness/liveness and database bootstrapping tests. Its `Production quality gate` failed solely at `npm audit --omit=dev --audit-level=high` because Nodemailer 6 was flagged as high risk.

Remediation: require Nodemailer `^10.2.1` and remove `@types/nodemailer` (Nodemailer 10 bundles its own typings). Maintain the existing SMTPS-only transport and Node.js 22 requirement. The build and audit must be re-run in GitHub Actions to confirm the patched dependency graph. Do not disable the vulnerability gate.

When requesting a new CI run: apply this package, commit and push on a test branch, inspect the production quality and container build gates, and supply the first failing step logs if any. No Git operation is performed by the assistant.
