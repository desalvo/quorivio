# GitHub Actions integration validation

This package extends the CI `validate` job. After Node tests and API/frontend builds, it starts a temporary PostgreSQL 18 service and boots the compiled application using **test-only** credentials. It checks readiness/liveness HTTP endpoints, serves the frontend homepage, validates the bootstrap administrator and selected critical tables, and rejects anonymous account access.

The `image-build` job also builds the isolated document-converter image. The blocking Trivy scan of the main API image remains; a dedicated converter image vulnerability scan is still required before a production release.

## Repository owner action

1. Commit and push this cumulative package to a branch (do not tag a release). The assistant does not commit/push.
2. Run the Quorivio CI workflow in the repository Actions tab or open a pull request, and review the Production quality and Container build gates.
3. If CI fails, supply the logs for the first failing step with secrets removed.
4. Do not deploy to production before real-provider SSO, SMTPS, antivirus, existing-database migrations, and multi-replica behavior have been checked independently.

**Limit:** this full workflow cannot run locally without Docker and npm dependencies. A green CI is necessary but not sufficient for production acceptance.
