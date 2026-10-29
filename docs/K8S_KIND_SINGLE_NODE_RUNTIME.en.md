# Single-node disposable KIND deployment smoke — RC cycle 24

**Scope:** opt-in GitHub Actions input `kubernetes_runtime_test=true`. A brand-new
single-node KIND cluster is created in the CI job, an application image is
built locally and loaded into KIND **without publication**, and the original
`tools/k8s_wizard.py` renders a real application deployment with PostgreSQL 18,
2 API replicas, a PVC, a PodDisruptionBudget, and an unserved Ingress.

The test uses a disposable hostPath-backed `ReadWriteMany` PersistentVolume
**inside the same KIND node only** with a disposable static, non-provisioning StorageClass, purely to prove that both application pods
can read and write the same `/app/assets` filesystem. It is **not** a suitable
production StorageClass, nor evidence of multi-node RWX or storage failover.
Do **not** copy this hostPath/PV configuration into production.

The automated steps wait for PostgreSQL StatefulSet and both application pods
to roll out, query actual service readiness and liveness through ClusterIP,
check the application landing page, write an asset in one pod and read it from
the other, delete one pod while probing through the surviving pod, and ensure
the deployment returns to two ready pods. It refuses to run unless Kubernetes
context is exactly `kind-quorivio-runtime`, avoids printing generated
credentials, and never publishes container images. A timeout or failing probe
is a failed CI gate (no silent skip). Build/runner availability still need a
first successful GitHub workflow run for acceptance.

## Boundaries still open for RC

This **does not** exercise real NGINX/HAProxy ingress routing, TLS, ClamAV,
Podman rootless, dedicated ARM64 hardware, independent Kubernetes worker
nodes, CSI-backed RWX, network partition or a production HA/RPO/RTO service
objective. `kubernetes_manifest_test=true` independently validates schema on
a disposable API server; `runtime_arch_test=true` uses Docker/QEMU. These three
inputs test different scopes and must not be counted as the same acceptance.

Recommended nonpublishing manual workflow inputs:

```yaml
browser_test: true
cross_browser_test: true
capacity_test: true
kubernetes_manifest_test: true
kubernetes_runtime_test: true
runtime_arch_test: true
publish_image: false
publish_latest: false
rc_strict: false
```

For a production-like acceptance stage, use at least two workers, actual
shared RWX storage, correctly installed ingress controllers, dedicated TLS,
ClamAV and a real disruption/recovery exercise with independent evidence.
