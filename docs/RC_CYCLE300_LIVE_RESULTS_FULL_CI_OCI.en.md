# RC300 — Resilient live-result polling and Docker image artifacts

**Baseline:** RC299 merged at `6f48a9de9f2c`. The release version is still `0.1.0-dev`.

- A single-flight poller prevents overlapping presenter HTTP requests (and older results overwriting newer counts).
- Transient failures show a stale-data warning without discarding previously authenticated results. Successful retry clears it; changing source clears old counts, while unmount suppresses late callbacks.
- Deterministic Node regressions check concurrency, recovery, teardown and React wiring.
- CI builds and Trivy-scans both Docker images. On a main commit explicitly containing `[full-ci]`, the images are also saved into downloadable **linux/amd64** `docker save` gzip archives with SHA-256 manifest and seven-day retention in GitHub Actions. Restore with `sha256sum -c SHA256SUMS` followed by `docker load -i <archive>.tar.gz`. The same marker triggers extended browser, capacity, Kubernetes and native OCI tests.
- **No Docker Hub push**, production release or tag: publishing uses a distinct authorized workflow. The native ARM64 runtime gate does not make the downloadable archives multiarch.

Independent physical A4/B3 accessibility and participant sign-offs are still missing; the certified ledger remains **85.25% (43 accepted / 17 partial)**, with `rc_strict=false`, `publish_image=false` and `publish_latest=false`.

**Suggested merge title:** `fix: stabilize live results and archive Docker images [full-ci]`

## Full-CI hotfix after run 42887563358

The first expanded `[full-ci]` run encountered a legacy invalid Python triple-quoted JavaScript expression in `tools/ci_rc295_results_layout_chromium.py`, even though the standard quality/container tests were green. Removed accidental backslashes before its triple quotes. CI now compiles **all** Chromium opt-in scripts in a cheap, mandatory pre-npm stage and executes the actual RC295 R-layout Chromium smoke after browser bootstrap even for regular PRs. This is a fail-closed safeguard, not a claim that the extended campaign passed. A corrected full CI must run on a new main commit; no Docker images were published.
