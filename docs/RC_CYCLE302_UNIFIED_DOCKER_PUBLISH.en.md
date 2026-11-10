# RC302 — One authorization, two verified Docker Hub repositories

An explicitly authorized publication now handles **both** `desalvo/quorivio` and `desalvo/quorivio-converter` in a single workflow. Images use native runners for linux/amd64 and linux/arm64, Docker Hub login via the existing protected `production` environment, and immutable digest staging with SBOM and provenance. The ordinary container build gate scans both images with Trivy before publication.

## Trigger, image labels and staging

- The explicitly authorized `[publish-docker]` commit marker on `main` starts the full expanded RC acceptance suite. Only a green campaign permits two native architecture build matrices and the final paired publisher. On `main`, both repositories receive `sha-<12>` and `latest` labels corresponding to that exact source commit.
- A manual `workflow_dispatch` with `publish_image=true` builds/publishes **both** images using the same quality, image-build and architecture checks. `publish_tag` labels both; `publish_latest=true` is only allowed on `main`.
- A manual run on an approved Git semver tag publishes the **same release version label** to both repositories and does not move `latest`.
- `converter-image.yml` remains as a separate emergency converter-only maintenance tool, but is **not** required for normal paired publication.

## Preflight and security

`tools/publish_both_multiarch_manifest.sh` verifies all four native digests and their OCI architecture before changing any mutable tags. It rejects missing/unapproved image references, wrong platforms, invalid digests, duplicated labels and mismatched tags. The existing per-image publisher then creates and verifies each multiarch manifest. Tests use fake Docker CLI calls and assert that a broken converter digest prevents even the main image's tag from moving.

Docker Hub has no cross-repository atomic transaction: an outage occurring after updating the application but before updating the converter could still temporarily leave tags different. Record immutable digests and reconcile only after a verified rerun; monitor both images.

**Release status:** these CI and publication checks do not replace independent accessibility, physical devices, real-provider or external security/legal sign-offs. Strict RC remains blocked at **85.25%** (43 accepted, 17 partial). No Git release tag is created.

Suggested merge commit: `ci: publish Quorivio and converter together after full CI [publish-docker]`.
