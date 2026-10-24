# GitHub Actions integration validation

This package extends the CI `validate` job. After Node tests and API/frontend builds, it starts a temporary PostgreSQL 18 service and boots the compiled application using **test-only** credentials. It checks readiness/liveness HTTP endpoints, serves the frontend homepage, validates the bootstrap administrator and selected critical tables, and rejects anonymous account access.

The `image-build` job also builds the isolated document-converter image. The blocking Trivy scan of the main API image remains; a dedicated converter image vulnerability scan is still required before a production release.

## Repository owner action

1. Commit and push this cumulative package to a branch (do not tag a release). The assistant does not commit/push.
2. Run the Quorivio CI workflow in the repository Actions tab or open a pull request, and review the Production quality and Container build gates.
3. If CI fails, supply the logs for the first failing step with secrets removed.
4. Do not deploy to production before real-provider SSO, SMTPS, antivirus, existing-database migrations, and multi-replica behavior have been checked independently.

**Limit:** this full workflow cannot run locally without Docker and npm dependencies. A green CI is necessary but not sufficient for production acceptance.

## Added CI coverage (2026-10-24)

The job now includes `python3 tools/ci_portable_http.py` after PostgreSQL startup and before API shutdown. It uses disposable credentials and exercises authentication, password change, atomic platform-settings rejection, private profile photo upload/deletion, binary image uploads, repeat `.quorivio` imports, duplicated media and corrupted-archive rejection. This script requires a running PostgreSQL 18 API and **has not yet been executed locally**; the existing green CI confirmation applies to the prior committed baseline only. Unit/build checks of this cycle were performed locally using archived npm dependencies; unlike the full CI, Docker, Trivy, real migrations, and SMTP cannot be validated locally.
