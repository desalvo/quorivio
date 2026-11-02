# RC127 — Native dual-architecture runtime and external RC acceptance (2 November 2026)

## Verified GitHub baseline

GitHub Actions **41377221623** (commit `d5cff85367a8e906d6e0d59a41ecf82477245b99`, explicit `[publish-docker]`) passed the complete RC126 CI campaign, including PostgreSQL/Chromium, Kubernetes/NGINX/HAProxy, ClamAV, Podman, independent native AMD64/ARM64 image builds and Docker Hub publication. Both `desalvo/quorivio:sha-d5cff85367a8` and `:latest` were verified against manifest `sha256:752b3108dd3a7a8a351fbfe93870bbc8455bacd8e5349746dcaca5882066ec5d`. This is **not** evidence of native ARM application execution against PostgreSQL.

## RC127 changes

- The non-publishing runtime acceptance no longer compiles ARM64 under QEMU. A **native** AMD64 runner and separate **native** ARM64 runner each build their own image, enforce CPU identity, start disposable PostgreSQL 18, and exercise the real non-root application, HTTP live/ready/root endpoints, compiled artifacts and CSP/Permissions-Policy.
- Both architecture jobs are required by the RC campaign. Failure of one does not cancel evidence collection for the other. Build outputs are local only: no Docker Hub credentials, push or release tags.
- Reconciled historical tests that incorrectly required an emulated ARM64 runtime, and added early fail-closed matrix checks.
- Added `docs/validation/RC127_OPERATOR_ACCEPTANCE_PLAN_20261102.json`, a deterministic external-acceptance plan enumerating all **17 partially accepted gates**, evidence needed and **unsubmitted** operator approvals. The CI checks that this plan is current; it never creates an approval or credits external sign-off.

## RC decision

Certified completion remains **85.25%** (43 accepted and 17 partial gates out of 60); provisional local engineering estimate **85.75%**. GitHub Actions must validate the new native runtime workflow after the next commit. A release candidate is **NOT APPROVED** until independent device/accessibility, actual OIDC/SMTP, physically separate RWX/CSI, capacity, restore/offsite, security/GDPR and manuals review evidence has been accepted. Do not bypass `rc_strict`; do not use `[publish-docker]` merely to test this cycle.

## Verifiche locali / Local verification

Complete Python suite: **1,661 tests run, OK (1 skipped)**. The strict RC preflight intentionally exits 2 because 17 gates are not accepted. Source ZIP/SHA-256 inventory is verified. Actual native ARM64 runner execution and Node/TypeScript build must be confirmed by the next GitHub CI.
