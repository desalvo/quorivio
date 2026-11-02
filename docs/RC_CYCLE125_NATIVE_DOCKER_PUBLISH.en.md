# RC125 — Native AMD64/ARM64 Docker Hub publication without QEMU (2 November 2026)

## Evidence and cause

The supplied GitHub Actions log for run `41361426087`, attempt 2, commit `a97b80b8d09ebd1a6054111bf88326581e2cc80f`, ends while building `linux/arm64` on an AMD64 host: `RUN npm install --no-audit --no-fund` prints `qemu: uncaught target signal 4 (Illegal instruction) - core dumped` and the BuildKit line remains pending. The simultaneous AMD64 branch completes the API/web build and SBOM. The fault occurs **before** manifest creation and Docker Hub tag publication; it is neither an authentication error nor the Node punycode deprecation warning. This log alone does not prove that every subsequent occurrence shares the same root cause.

## Implementation

The old QEMU-based single-job multiarch **publishing** build is replaced by a two-platform matrix: GitHub `ubuntu-24.04` for native `linux/amd64` and `ubuntu-24.04-arm` for native `linux/arm64` (supported in this public GitHub repository). Both platform jobs push only immutable, untagged OCI digests with SBOM and maximum provenance, then upload narrowly scoped per-run digest artifacts. The final manual `publish` or explicitly authorized commit `publish-on-commit` job downloads **both** digests, validates their syntax, independently inspects each digest's OS/CPU architecture and then uses `docker buildx imagetools create` to assign the requested version/SHA and optional `latest` tags. It also verifies the resulting multiarch index contains both `linux/amd64` and `linux/arm64`.

An incorrect/missing platform, invalid digest/tag, broken login, failed platform build, timed-out job, missing artifact or failed quality/campaign requirement prevents all final mutable tags. Native platform jobs timeout at 35 minutes; manifest stages at 10. No application image is silently downgraded to AMD64-only, and the non-publishing acceptance campaign is unchanged. A manual `workflow_dispatch` must still have `publish_image=true`, `rc_acceptance_suite=false` and be on `main` or an eligible semver release tag. Commit publication still requires the literal `[publish-docker]` marker **and** complete RC campaign success; `[full-ci]` alone never publishes. Publication remains protected by the GitHub `production` environment and existing Docker Hub token; no additional credential is introduced.

## Validation and limits

Local Python source/contract tests and fake-Docker failure-injection tests confirm both independent digests, architecture checking before tags, and no QEMU in the publication build. The exact real workflow including native hosted ARM64 Docker build, registry push, attestations and manifest inspection **must still be executed on GitHub**. No commit, Docker push, tag or release has been run by the assistant.

Recommended order: commit this complete cumulative package with `[full-ci]` (non-publishing); confirm standard and extended automated CI; then manually dispatch `publish_image=true`, `publish_latest=true` only when ready to replace `latest`, leaving `rc_acceptance_suite=false` and `rc_strict=false`. For an explicitly approved commit-driven publication use `[publish-docker]` instead, which runs the campaign first. Do not retry the hung QEMU builder on the earlier commit.

**RC certification unchanged: 85.25%** (43 accepted / 17 partial of 60). The provisional **85.75%** local engineering estimate from RC124 guide/grid functionality is not yet independently verified or promoted. `rc_strict=false`, `publish_image=false`, `publish_latest=false` are the recommended defaults.
