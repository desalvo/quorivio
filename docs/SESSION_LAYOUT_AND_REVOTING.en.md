# Sessions, page layouts and invalidated votes — EN

## Container configuration
Docker/Podman Compose and Kubernetes wizard default to `desalvo/quorivo:latest`. Compose supports the `QUORIVIO_IMAGE` override. Source repository remains `github.com/desalvo/quorivio`, while GitHub Actions publishes `desalvo/quorivo` to Docker Hub. Verify the target repository and scoped token exist.

## Presenter workflow
Create a session with title and reference date. Edit them in **Session metadata** even while active, preserving recorded responses. For each activity use **Page layout** to edit question and results headers and HTTPS background URLs independently; global logos use the session theme. Full media rendering still requires browser validation.

## Invalidation and resubmission
Historical invalidated responses remain available for audit and are excluded from live counts. Once invalidated, the same participant may submit one new active answer to that activity when reopened. The migration replaces the original composite uniqueness constraint with a partial unique index limited to responses where `invalidated_at IS NULL`. Apply database migrations before deploying the updated backend and test against actual PostgreSQL.

## Deployment caveats
Full TypeScript build, real PostgreSQL migration and end-to-end browser behavior have not been validated in this development cycle.
