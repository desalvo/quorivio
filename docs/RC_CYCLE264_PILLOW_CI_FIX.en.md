# Quorivio RC264 — Dependency-free synthetic PDF preflight

The RC263 full GitHub Actions run [42496843522](https://github.com/desalvo/quorivio/actions/runs/42496843522) failed at a pre-npm test: simulated Poppler was in place, but synthetic PDF mount regressions still invoked `_verify_png` requiring Pillow, which the runner had not installed. Its exception handler then raised an unintended `UnboundLocalError`.

The two **filesystem staging** regressions now validate exact deterministic synthetic PNG bytes rather than calling the Pillow decoder. The real converter keeps full `Image.verify()` and `Image.load()` decoding plus strict PNG header, CRC, chunk, dimension and terminator checks. A separate negative regression checks missing Pillow fails closed with a meaningful error. No production security check is skipped. Post-install tests still exercise actual PDF/PPTX conversion.

Reproduce the dependency-free runner with:

```bash
python3 -S -m unittest -q tools.tests.test_rc264_pillow_independent_ci tools.tests.test_rc261_conversion_mount_and_zlib tools.tests.test_rc263_kube_defaults_and_ci tools.tests.test_rc262_disk_monitor_wizard
```

Trivy HIGH/CRITICAL remains blocking. Do not re-apply the PostgreSQL probe: its live rollout and generated manifests are already synchronized. Wait for a successful new full CI and published application images before upgrading Kubernetes.
