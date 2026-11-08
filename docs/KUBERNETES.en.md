# Kubernetes Kustomize wizard

**RC258 — Standalone wizard:** copy only `tools/k8s_wizard.py` to an operator host with Python 3 and `kubectl` (the latter needed for live Kubernetes operations). Kustomize generation, read-only inspection, token provisioning and converter sidecar upgrade no longer need other Quorivio modules. `maxUnavailable: 25%` is resolved against actual replicas using Kubernetes rounding; genuinely disruptive rollouts remain blocked. Procedure: `docs/RC_CYCLE258_STANDALONE_K8S_WIZARD.en.md`.

Run the stdlib-only standalone generator from the root repository:

```bash
python3 tools/k8s_wizard.py --unattended --output ./k8s-generated --set host=quorivio.example.org --set image=desalvo/quorivio:v0.1.0
kubectl kustomize ./k8s-generated
```

Or launch `python3 tools/k8s_wizard.py --output ./k8s-generated` for interactive input. Defaults and previous saved overrides are shown first. Repeat runs with identical values generate **identical manifests**; only non-default values are saved in `quorivio-overrides.json`, never passwords. Use `--values path/to/quorivio-overrides.json` to import overrides. Output files: Namespace, ConfigMap, Deployment, Service, Ingress, Kustomization. No apply is performed.

**Preconditions**: provision PostgreSQL independently, create the Kubernetes Secret named `quorivio-app-secrets` containing `DATABASE_URL` and `AUTH_SECRET` (must match actual application variables), create `quorivio-tls` or configure cert-manager. Review WebSocket ingress, CORS/proxy, DNS and HTTPS. Note: the current backend has in-process WebSocket broadcast, so `replicas=1` remains necessary for correct realtime semantics; the wizard can express >1 but must not be deployed multi-replica until Redis/pubsub is implemented. Kubernetes availability and resource limits remain unvalidated.

## PostgreSQL 18 / ingress extensions (third development cycle)

Wizard defaults to internal PostgreSQL `postgres:18.6-alpine` with a StatefulSet and a 10 GiB PVC mounted at `/var/lib/postgresql` (PostgreSQL 18+ image layout). Existing PG17 volumes **cannot** be upgraded just by switching the image: perform a supported major-version migration with backup/restore or `pg_upgrade`, verified independently.

```sh
python3 tools/k8s_wizard.py --unattended --output ./generated --set ingress_controller=haproxy --set haproxy_variant=community
python3 tools/k8s_wizard.py --unattended --output ./external --set postgres_mode=external --set postgres_host=pg.example.org --set postgres_sslmode=verify-full
```

Use `haproxy_variant=community` for the `kubernetes.io/ingress.class` legacy annotation or `haproxy_variant=haproxytech` for `haproxy.org/ingress.class`. Both set `spec.ingressClassName`. Check the actual controller's documented class configuration. NGINX uses `ingressClassName: nginx` by default.

The wizard **never writes credentials**. Before deployment create a secret with `DATABASE_URL` and `AUTH_SECRET`; internal PostgreSQL additionally requires `POSTGRES_PASSWORD`. PostgreSQL URLs must be URL-encoded and include suitable `sslmode` and trusted certificates for external TLS. `PGSSLMODE` in a ConfigMap is *not* a substitute for correctly configuring TLS in `DATABASE_URL`. The generated `StatefulSet` lacks managed backups and HA: configure and test both before production. The API remains deliberately single-replica until cross-replica event synchronization is implemented.

Use `kubectl kustomize ./generated` and validate against your cluster; neither this generator nor the source's Helm chart has yet been cluster-verified.


## RC246 — Safe in-place converter upgrade

For an existing wizard-generated installation, **do not** re-generate or re-apply the old complete Kustomize base. Run `python3 tools/k8s_wizard.py --ensure-converter-token` and then `--upgrade-converter` to prepare a minimal, non-destructive JSON Patch against the live Deployment; explicitly apply via `--apply-converter` only after review. Publish the separate converter image via `.github/workflows/converter-image.yml` (manual workflow only) or Docker Buildx first. No DB/PVC/Ingress/Service/credential replacement, and stale plans are rejected. Full guide: `docs/RC_CYCLE246_EXISTING_K8S_CONVERTER_UPGRADE.en.md`.

## RC247 — Worker image tags

Run the manual converter publisher on `main` with `confirm_publish=true` for `desalvo/quorivio-converter:latest`; run it on a Git tag ref to publish `desalvo/quorivio-converter:<tag-name>`. The live upgrade wizard accepts `latest`, release tags and digests without regenerating database/PVC/Ingress. Since `latest` is mutable, inspect its digest before rollout. No cluster upgrade is automatic.
