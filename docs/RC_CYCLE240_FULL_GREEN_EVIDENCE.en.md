# RC240 — Verified green RC campaign and protected external evidence

## Verified remote baseline

The maintainer committed RC239 at `0594b72806a7b6bf27de07a5fb2856747c8fd68d`. GitHub Actions run [42284582481](https://github.com/desalvo/quorivio/actions/runs/42284582481) completed successfully on 6 November 2026 20:18:06 UTC: production quality, ClamAV, Firefox/WebKit, native amd64/arm64 OCI, NGINX and HAProxy TLS/ingress and failover, KIND, PostgreSQL/Podman, container build. The final campaign summary reported 11 of 11 mandatory jobs passed. Fourteen active jobs succeeded, with three publication jobs intentionally skipped. No image publication is claimed.

The machine-readable receipt is `docs/validation/RC239_FULL_CI_ACCEPTANCE_20261107.json`. The live `last_verified_full_ci` ledger pointer has been updated; the 2026-10-31 snapshot is preserved verbatim as `historical_full_ci_20261031`, with its old historical assertions testing that key rather than freezing the current CI pointer. The old RC239 grouped SHA inventory is immutable.

## RC240 implementation and integrity checks

- Harden `tools/rc_external_evidence.py`: evidence files are opened using a pinned regular-file descriptor (`O_NOFOLLOW`, `O_NONBLOCK`), reject symlink substitution, in-place mutation, changed size/inode/path, and excessive/non-regular content.
- Hash the exact bytes copied into the private attachments folder; check destination integrity before committing the manifest. On failure, delete only new files and own temporary manifest, leaving any pre-existing reviewer work untouched.
- Add negative regression tests that simulate source symlink replacement, non-regular FIFO inputs, corrupted destinations, interrupted JSON writes and pre-existing temporary evidence.
- Keep the existing private operator-review CLI, requirements checklist, and full fail-closed strict RC preflight unchanged. Never copy operator evidence or participant data into the cumulative ZIP.
- Add mandatory pre-npm RC240 regression, current RC240 SHA-256 source/ZIP inventory, and bilingual acceptance handoff.

## Remaining independent acceptance

The weighted audit is **85.25%** (43 accepted gates, 17 partial). Automated CI cannot substitute for physically deployed devices, signed independent accessibility/legal reviews, real OIDC/SMTP provider behavior, actual CSI/RWX multi-host operation, offsite DR RPO/RTO or an Office fidelity corpus. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Formal RC remains **blocked**; do not enable publishing or tag without independent evidence and explicit approval. No Git operations performed by the assistant.
