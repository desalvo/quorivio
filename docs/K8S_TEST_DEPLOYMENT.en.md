# Kubernetes test deployment — Quorivio 0.1.0-dev

## Image name and CI
The default application image is now **`desalvo/quorivio:latest`** in Compose, Kubernetes wizard, Helm and GitHub Actions publishing. Source remains `desalvo/quorivio`. The maintainer must commit and push this change, confirm green CI and verify that the new image exists on Docker Hub **before** deployment. The separate converter image, where used, defaults to `desalvo/quorivio-converter:0.1.0-dev`; changing its reference does **not** publish it. Check registry availability before deploying the Helm chart.

## Kustomize wizard
For termination using the ingress controller's configured default certificate:

```sh
python3 tools/k8s_wizard.py --unattended --output ./k8s-generated \
  --set host=quorivio.example.org --set ingress_controller=nginx \
  --set tls_termination=true --set tls_secret= \
  --set app_node_selector=kubernetes.io/arch=amd64,disktype=ssd \
  --set postgres_node_selector=disktype=hdd
kubectl kustomize ./k8s-generated
```

With `tls_termination=true`, the Ingress contains `spec.tls` with hosts; an empty `tls_secret` omits `secretName`. This requires a preconfigured **default TLS certificate on the ingress controller**. For a dedicated certificate use `--set tls_secret=my-cert`. Setting `tls_termination=false` omits `spec.tls` entirely. Existing `quorivio-overrides.json` overrides are reused; use `--set tls_secret=` to clear an earlier value. Node selectors are comma-separated `key=value` pairs scoped independently to the application Deployment and the internal PostgreSQL StatefulSet; external database mode creates no PostgreSQL pod.

Create the required Kubernetes Secrets and prepare appropriate test-only credentials before applying any manifests. Inspect IngressClass, PVC/StorageClass, image architecture and registry availability. Run `kubectl apply -k ./k8s-generated` only against the test namespace and an isolated database. Actual Kubernetes/Ingress TLS/PostgreSQL runtime behavior is not yet validated.

## Helm
The chart defaults to `desalvo/quorivio:latest`, `ingress.tlsTermination=true`, and empty `ingress.tlsSecret`. Set `nodeSelector` for the chart's app/converter/ClamAV pod. Those three containers share **one pod** and thus one pod-level node selector. Check converter image registry availability first.
