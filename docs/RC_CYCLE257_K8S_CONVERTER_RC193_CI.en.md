# RC257 — RC193 CI compatibility and existing Kubernetes converter upgrade

**Baseline:** RC256 commit `9023bff41adf05863b7c2c508f836b012c3e2416`, [full CI 42479602496](https://github.com/desalvo/quorivio/actions/runs/42479602496) failed in the Production quality gate at the RC193 font-controls step. Its legacy assertion expected `style?.fontFamily||'Arial'`, the unsafe raw CSS fallback intentionally replaced by `safeWidgetFontFamily(...)` in RC254. The RC193 contract now checks validated answer and submit faces, keeps focus/selection tests, and runs in a new early RC257 gate with a scan for further obsolete source-literal assertions and RC254 Node runtime tests. **No production code changes.**

## Add a PDF/PPTX converter to an existing Kubernetes deployment

Run at repo root with authenticated `kubectl`. These commands modify only the worker-token Secret and existing Deployment pod template; they neither reinstall Quorivio nor touch PostgreSQL, PVCs, Services, Ingress or TLS. The converter is a *sidecar in the Quorivio pod*, not a public worker Deployment or Service.

```bash
kubectl config current-context
kubectl -n quorivio get deployment quorivio
python3 tools/k8s_wizard.py --ensure-converter-token --set namespace=quorivio --set name=quorivio
python3 tools/k8s_wizard.py --upgrade-converter --set namespace=quorivio --set name=quorivio \
  --converter-image 'desalvo/quorivio-converter@sha256:95223a548ca5e813199216e80ce565c6a203c6b6105c8655e8d62048e94d74f7' \
  --output ./converter-upgrade-rc257
kubectl -n quorivio patch deployment quorivio --type=json \
  --patch-file=./converter-upgrade-rc257/converter-patch.json --dry-run=server -o name
python3 tools/k8s_wizard.py --apply-converter --output ./converter-upgrade-rc257
kubectl -n quorivio rollout status deployment/quorivio
kubectl -n quorivio logs deployment/quorivio -c converter --tail=80
```

Inspect `converter-plan.json` and `converter-patch.json` before applying. The digest was verified in [converter workflow 42417918195](https://github.com/desalvo/quorivio/actions/runs/42417918195). Mutable `:latest` is accepted but an immutable digest is safer because the converter uses `imagePullPolicy: IfNotPresent`. The wizard validates context/UID/resourceVersion and refuses a stale plan, unclear secrets or Helm-managed Deployments. Nondefault deployments can be selected with `--converter-deployment`, and container/Secret with `--app-container` and `--converter-secret` at **plan time**, not during apply. Open **Platform admin → Server configuration → PDF/PowerPoint converter → Check worker → Enable import** and smoke-test PDF/PPTX imports. `127.0.0.1:8099` is pod-internal only. **85.25%** (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`; maintainer full CI pending. No assistant commit/push/tag.
