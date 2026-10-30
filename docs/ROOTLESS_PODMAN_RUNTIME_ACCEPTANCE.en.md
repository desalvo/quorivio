# RC cycle 27: real rootless Podman acceptance (opt-in, not yet remotely validated)

Quorivio keeps `0.1.0-dev` and its EUPL-1.2 license. The new **manual-only** GitHub Actions input `rootless_podman_test=true` builds the actual production `Dockerfile` **as the unprivileged runner account**, then uses Podman rootlessly to launch two disposable containers with an internal network: PostgreSQL 18 Alpine and the Quorivio API/web image. It does not push to a registry, enable privileged mode, publish a port, or access production data. The script rejects root execution, rootful Podman and configured remote engines.

Runtime checks require actual Node execution as a non-root UID, the compiled API and web assets, no npm CLI in the production image, PostgreSQL availability, a live process, HTTP `/api/health/ready` and `/api/health/live` 2xx, and an HTML root page. Ephemeral secrets never enter logs/artifacts and cleanup executes on exit. A failed process, timeout or inaccessible resource fails the job. The workflow uses an isolated single host; it **does not** establish multi-node high availability, CSI RWX, production ingress, a native ARM64 test, rootless Podman under arbitrary SELinux hosts, operator sign-off or GDPR/AGID certification.

## Running the next acceptance

After manually committing the cycle-27 cumulative package, trigger **Quorivio CI and Docker Hub** → `workflow_dispatch`, setting `rootless_podman_test=true` and `runtime_arch_test=true` along with existing desired browser/Kubernetes checks; **keep `publish_image=false`, `publish_latest=false` and `rc_strict=false`**. The existing OCI AMD64/ARM64 smoke is separate; the cycle-26 x64 architecture fix is still pending that rerun. Rootless Podman boot cannot be claimed as passed until the job is green. CI normally installs Podman and user-namespace utilities on the Ubuntu 24.04 runner; an unavailable rootless runtime should fail clearly rather than silently fall back to Docker/root.

## Local evidence and limitations

Local Python 1,172/1,172 passed (one skipped), backend Node 474/474 passed, frontend Node 65/65 passed, with source/syntax and negative Podman error-path checks. New TypeScript/Vite build was NOT verified because npm dependencies were incomplete; the execution environment has no Podman, Docker, QEMU or PostgreSQL services. The conservative weighted score stays **79.0%**, with **30 accepted / 17 partial** gates. No accepted gate is promoted from code-only evidence. Production publication remains strictly opt-in and separate from these tests.
