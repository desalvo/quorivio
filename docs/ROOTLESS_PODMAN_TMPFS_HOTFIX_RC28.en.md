# Quorivio 0.1.0-dev — RC cycle 28

## CI results after cycle-27 commit

GitHub Actions [40980312270](https://github.com/desalvo/quorivio/actions/runs/40980312270): **six out of seven jobs succeeded**. Production quality (`123818832091`), image build (`123820527899`), AMD64/ARM64 QEMU OCI runtime (`123820527902`), Kubernetes API schema (`123820527914`), Firefox/WebKit (`123820527976`), and single-node KIND runtime (`123820528118`) all passed; publication was skipped.

The rootless Podman job (`123820527939`) failed with `unknown mount option "uid=1000"` (exit 125). Podman built the image, but the Docker-specific tmpfs options prevented application startup. This does **not** establish any rootless app-level result.

## Fix

Replace Docker-specific `--tmpfs` UID/GID ownership with Podman's documented `--mount type=tmpfs,destination=/app/assets,tmpfs-size=268435456,tmpfs-mode=0700,U=true`. `U=true` assigns ownership from the image's configured non-root user while retaining mode 0700, a 256 MiB bound and no privileges. A disposable container executes the real non-root image and the identical tmpfs mount, writes, reads and removes a private file before the API starts. Any failure stops the job without a false positive. Existing internal network, secrets hygiene and cleanup remain in place.

Source: [official Podman run documentation](https://docs.podman.io/en/latest/markdown/podman-run.1.html), tmpfs `U`/`tmpfs-mode`/`tmpfs-size` options.

## Evidence and next check

**79.0% unchanged** (30 accepted, 17 partial gates). New remote OCI AMD64/ARM64 and single-node KIND proof is bounded to the actual CI environments and does not close parent D3. Rootless Podman still needs a successful fresh GitHub run, and production ingress, multi-node RWX CSI, native ARM64, independent accessibility/GDPR/AGID approval remain outstanding. Local shell/static regression tests are not runtime acceptance.

Commit and manually dispatch the workflow with `rootless_podman_test=true`, `runtime_arch_test=true`, `browser_test=true`, `cross_browser_test=true`, `kubernetes_runtime_test=true`, `publish_image=false`, `publish_latest=false`, `rc_strict=false`. No automatic commit/push/image publication.

**Test locali / local tests:** 1,177 Python (1 skipped), 474 API Node, 65 web Node; local TypeScript build unverified because npm type dependencies are incomplete; committed cycle-27 GitHub build passed.
