# RC246 — Add isolated PDF/PPTX converter to an EXISTING wizard-managed Kubernetes deployment

**Verified baseline:** RC245 commit `c108694705d2bd0d8d8444f7840a944b5913e25d`; full GitHub acceptance [42382296263](https://github.com/desalvo/quorivio/actions/runs/42382296263) passed all 11 required gates (14 jobs successful); existing main-app image published under `desalvo/quorivio:sha-c108694705d2` and `:latest` in [42385404670](https://github.com/desalvo/quorivio/actions/runs/42385404670). **The converter image is separate** and was not implicitly published. RC246 itself still requires CI.

The original Kubernetes/Kustomize wizard remains unchanged for new installations. The new modes of `tools/k8s_wizard.py` inspect the **live existing Deployment** using the operator's `kubectl` context. They never regenerate PostgreSQL, Secrets, PVCs, Ingress, Service, ConfigMaps, TLS resources or the old wizard-generated source manifests.

## 0. Build/publish the converter image separately

Run the new explicit-authorization-only GitHub Actions workflow `Publish Quorivio PDF/PPTX converter (manual only)`, using `confirm_publish=true` (optionally `publish_tag=0.1.0-dev`) after a green CI. It uses the existing Docker Hub credentials to build `Dockerfile.converter` for linux/amd64 and linux/arm64, publish `desalvo/quorivio-converter:sha-<12-digit-commit>` plus the optional tag, and inspect the manifest. It never runs on push or pull request. Alternatively:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -f Dockerfile.converter \
  -t YOUR_REGISTRY/quorivio-converter:rc246 --push .
docker buildx imagetools inspect YOUR_REGISTRY/quorivio-converter:rc246
```

An existing `desalvo/quorivio` app image is NOT a converter worker. Verify image pull access for every cluster architecture.

## 1. Provision the isolated token, exactly once (explicit Secret modification)

```bash
kubectl config current-context
kubectl -n quorivio get deployment quorivio
python3 tools/k8s_wizard.py --ensure-converter-token \
  --set namespace=quorivio --set name=quorivio
```

The wizard discovers the app's existing Kubernetes Secret (or accepts `--converter-secret NAME`); only when `QUORIVIO_WORKER_TOKEN` is absent, it generates a random 32-byte internal token, sent directly through stdin to an atomic Kubernetes Secret JSON Patch with `resourceVersion` preconditions. No Secret content is printed or stored in the source tree, command line or generated plan. Invalid tokens, ambiguous/missing or immutable Secrets cause failure without replacing credentials.

## 2. Produce a non-destructive, read-only upgrade plan

```bash
python3 tools/k8s_wizard.py --upgrade-converter \
  --set namespace=quorivio --set name=quorivio \
  --converter-image desalvo/quorivio-converter:sha-YOUR_SHA \
  --output ./converter-upgrade-rc246
```

Use a **new, empty output directory**; NEVER use the existing generated Kustomize base. Options: `--converter-deployment` for a nonstandard Deployment, `--app-container` for a nonstandard API container, `--converter-secret` for the existing Secret. The wizard writes `converter-patch.json`, `converter-plan.json`, and `LEGGIMI.txt` with restrictive permissions. No Kubernetes writes occur. The JSON Patch contains only pod-template changes (API env/mount and converter sidecar plus two private temporary `emptyDir` volumes). It tests the original Deployment UID, resourceVersion and API container name. The plan stores context, namespace, Deployment and a SHA-256 receipt; never credentials.

The wizard rejects pre-existing or conflicting converter env/mounts/volumes, missing `fsGroup`, untagged/unsafe converter image refs and Helm-managed Deployments rather than changing storage ownership or unrelated resources.

## 3. Review, server-side dry-run, and explicitly apply

```bash
kubectl -n quorivio patch deployment quorivio \
  --type=json --patch-file=./converter-upgrade-rc246/converter-patch.json \
  --dry-run=server -o name
python3 tools/k8s_wizard.py --apply-converter --output ./converter-upgrade-rc246
```

`--apply-converter` checks the current Kubernetes context, Deployment UID and resourceVersion, the existing Secret/token, patch SHA-256 and a freshly rebuilt allowlisted JSON Patch before server-side dry-run, **one atomic Deployment patch**, and rollout status. If the live Deployment changed, replan into a fresh directory. No original manifests or PostgreSQL/Secret/PVC/Ingress/Service are recreated. A failed rollout should be inspected, and an authorized operator may use `kubectl -n quorivio rollout undo deployment/quorivio` as appropriate.

## 4. Verify health and activate the admin toggle

```bash
kubectl -n quorivio rollout status deployment/quorivio
kubectl -n quorivio get pods
kubectl -n quorivio logs deployment/quorivio -c converter --tail=80
```

In Quorivio: **Platform admin → Server configuration → Isolated PDF/PowerPoint converter → Check worker → Enable PDF/PPTX import**. Test actual PDF and PPTX files, preserving prior session and database state. The private worker uses `127.0.0.1:8099` within the same pod and shares `/conversions` with that pod's API only; it requires no external Service or Ingress. `/conversions` and `/tmp` are bounded, pod-local `emptyDir` volumes, NOT RWX/CSI cluster storage. Worker is UID 1000, root filesystem read-only, with CPU/memory limits.

**Release safety:** This is implementation and local test evidence, not proof of physical cluster readiness. Retain `0.1.0-dev`, `rc_strict=false` and **85.25% certified (43 accepted/17 partial)** until independent production/storage/operator acceptance. No assistant commits/pushes/tags/releases.
