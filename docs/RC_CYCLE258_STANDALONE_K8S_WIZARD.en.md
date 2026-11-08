# RC258 — Standalone Kubernetes wizard and safe converter rollout

**Baseline:** cumulative RC257; Arial rendering and legacy CI guards unchanged. The converter upgrade previously rejected Kubernetes default `maxUnavailable: 25%` without resolving the percentage against the number of replicas. Kubernetes rounds percentage unavailability *down* and percentage surge *up*. A Deployment with 1–3 replicas has effective unavailable=0; with 4 or more replicas and default 25%, the upgrade remains blocked. Explicit availability loss, Recreate, invalid configurations and stalled rollouts remain blocked.

## Download only one Python wizard file

Copy only `tools/k8s_wizard.py` to the operator host. It now embeds the complete reviewed `k8s_converter_upgrade` and `k8s_cluster_inspection` implementations, with SHA-256 integrity receipts. No Quorivio repository, third-party Python package or external YAML template is required. Python 3 stdlib suffices; live Kubernetes operations still require installed/configured/authorized `kubectl`. Creating manifests is offline; applying them requires Kubernetes client access.

```bash
python3 ./k8s_wizard.py --help
# Fresh install (generates, never applies):
python3 ./k8s_wizard.py --unattended --set host=quorivio.example.org --output ./k8s-new
# Existing installation (read-only):
python3 ./k8s_wizard.py --inspect-cluster --set namespace=quorivio --set name=quorivio --output ./k8s-inspection
# Explicitly provision existing app Secret token only when missing:
python3 ./k8s_wizard.py --ensure-converter-token --set namespace=quorivio --set name=quorivio
# Plan sidecar only; no database, PVC, ingress, app Secret overwrite or Service changes:
python3 ./k8s_wizard.py --upgrade-converter --set namespace=quorivio --set name=quorivio \
  --converter-image 'desalvo/quorivio-converter@sha256:95223a548ca5e813199216e80ce565c6a203c6b6105c8655e8d62048e94d74f7' \
  --output ./converter-upgrade-rc258
# Review plan and patch; server-side dry-run, then explicit guarded apply:
kubectl -n quorivio patch deployment quorivio --type=json \
  --patch-file=./converter-upgrade-rc258/converter-patch.json --dry-run=server -o name
python3 ./k8s_wizard.py --apply-converter --output ./converter-upgrade-rc258
kubectl -n quorivio rollout status deployment/quorivio
```

`--apply-converter` verifies cluster context, UID, resourceVersion and plan integrity before applying. A `Helm`-managed Deployment is not patched. Token values are not included in plans, command-line arguments or logs. The converter is a localhost-only sidecar on port 8099. This mode does not provide arbitrary upgrades of all existing platform resources; use normal cluster-specific procedures for those. No real Kubernetes cluster was altered during validation. Full CI RC258 remains to be run after commit.
