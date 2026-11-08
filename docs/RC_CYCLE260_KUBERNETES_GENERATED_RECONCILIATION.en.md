# RC260 — Reconcile Kubernetes `generated` manifests

The **standalone** Kubernetes wizard (version `0.1.0-dev-rc260`) now prevents the original Kustomize directory from silently losing the PDF/PPTX converter after an update of a live cluster. ChatGPT has not modified the live cluster.

## Already installed converter

```bash
python3 k8s_wizard.py --sync-generated --generated-dir ./generated \
  --set namespace=quorivio --set name=quorivio
kubectl kustomize ./generated > /dev/null
```

This command reads the live Deployment/Secret and **changes only local files**, not Kubernetes. Use `./k8s-generated` if that was the original wizard output. The wizard discovers a single `generated` or `k8s-generated` directory automatically; specify `--generated-dir` if ambiguous.

## New converter upgrade

```bash
python3 k8s_wizard.py --ensure-converter-token --generated-dir ./generated \
  --set namespace=quorivio --set name=quorivio
python3 k8s_wizard.py --upgrade-converter --generated-dir ./generated \
  --set namespace=quorivio --set name=quorivio \
  --converter-image desalvo/quorivio-converter:latest \
  --output ./converter-upgrade-rc260
# Review plan and server dry-run first.
python3 k8s_wizard.py --apply-converter --output ./converter-upgrade-rc260
kubectl kustomize ./generated > /dev/null
```

The reconciled Kustomize output includes `95-converter-sidecar-patch.json` as a strategic merge overlay, a `patches:` reference in `kustomization.yaml`, and the live `QUORIVIO_WORKER_TOKEN` in the existing `05-app-secret.yaml`. The secret file and previous-manifest backups under `.quorivio-manifest-backups/` are private; keep them out of source control. Secret data is never printed. Changes to live Kubernetes remain an explicit separate action.

Safety: verify live resource identity, fail on local Secret drift, protect against symlinks and edited manifest fingerprints, do not touch PostgreSQL/PVC/Ingress/Service, reconcile local files only after a successful rollout. If the update was already applied by an older wizard, use `--sync-generated`; the wizard does not re-patch Kubernetes. Subsequent regeneration in the original directory preserves the converter overlay and token. This is **not** a general-purpose three-way synchronization of every Kubernetes field: review unrelated manual drift before any future `kubectl apply -k`. The new tests use a fake cluster; full GitHub CI is still required. Completion 85.25% unchanged.
