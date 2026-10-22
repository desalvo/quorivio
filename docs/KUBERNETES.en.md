# Kubernetes Kustomize wizard

Run the stdlib-only standalone generator from the root repository:

```bash
python3 tools/k8s_wizard.py --unattended --output ./k8s-generated --set host=quorivio.example.org --set image=desalvo/quorivo:v0.1.0
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
