# Isolated PDF/PPTX conversion worker

Quorivio runs PDF/PPTX conversion **only in the dedicated converter container** (`Dockerfile.converter`), never in the API process. Containers share a private temporary volume and authenticate requests with a `QUORIVIO_WORKER_TOKEN` of at least 32 characters. Port 8099 is private to Compose, and Kubernetes pods use loopback. The worker runs as a non-root user with a read-only root filesystem and deployment resource limits.

## Compose
Generate a strong random `QUORIVIO_WORKER_TOKEN` (e.g. `openssl rand -hex 32`) and configure it in the deployment environment. Compose provisions the conversion worker and scratch volume. Never expose port 8099.

## Helm
Store `QUORIVIO_WORKER_TOKEN` in `existingSecret`. The API and worker share a pod-local `emptyDir`, with an additional `/tmp` mount for conversion utilities. Allocate realistic memory and CPU quotas.

## Status and limitations
Python worker path and protocol tests pass, but a real Compose/Helm worker runtime is untested. Conversion binaries need to be tested in the container with representative documents. Animations are not preserved. Monitor and protect the scratch volume. Do not treat this as production validated before browser/PostgreSQL integration, cluster tests and container isolation checks.
