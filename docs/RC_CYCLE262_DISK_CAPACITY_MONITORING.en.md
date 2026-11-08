# Quorivio 0.1.0-dev RC262 — disk capacity dashboard and admin email alerts

For Kubernetes `emptyDir`, `statfs` shows the **underlying filesystem**, not the kubelet-enforced `emptyDir.sizeLimit` quota; a per-pod scratch quota may be exhausted even if filesystem use is below 90%. Probe kubelet quota metrics separately. Scratch alerts are keyed **per pod** to avoid a healthy replica resetting another replica's warning.

The platform admin **Server configuration → Disk space and alerts** screen shows real filesystem capacity for the application asset PVC and conversion scratch volume via Node `statfs`, and the PostgreSQL data PVC via a separate same-pod read-only probe. `pg_database_size()` is shown for context but is **not** used to calculate filesystem fullness: it omits WAL, unrelated databases and other filesystem data. If a sample is missing or older than 15 minutes, its status is **unavailable**, not 0%.

At **90%** fullness on any of the three volumes, Quorivio notifies all approved `platform_admin` email addresses through the existing configured SMTP/SMTPS transport. The system rearms the alert when the measured percentage returns to **85% or less**. A database row lock deduplicates notifications across replicas; failed SMTP delivery is retried without marking the alert sent. A crash immediately after SMTP delivery and before committing state can cause a repeated message; SMTP cannot guarantee exactly-once delivery. There are no new public endpoints or passwords returned to the browser.

The wizard's managed PostgreSQL StatefulSet includes a `db-disk-probe` sidecar for **new internal PostgreSQL installations**. It mounts `/var/lib/postgresql` read-only, executes `df -Pk`, and writes validated volume capacity into `disk_monitor_samples` through `psql` on localhost every five minutes. It does not expose ports, Kubernetes service account credentials, or a privileged container. External PostgreSQL requires operator-managed filesystem telemetry; its UI shows unavailable until such a probe is present.

For **existing Kubernetes installations**, first deploy the RC262 application image, which creates the telemetry and alert state tables at startup. **Adding the DB probe changes the StatefulSet pod template and restarts PostgreSQL; with a single DB replica this may cause downtime.** Back up the DB and plan a maintenance window. From the directory with `k8s-generated`:

```bash
python3 k8s_wizard.py --version
python3 k8s_wizard.py --plan-disk-monitor \
  --generated-dir ./k8s-generated \
  --set namespace=quorivio --set name=quorivio \
  --output ./disk-monitor-plan-rc262
cat ./disk-monitor-plan-rc262/disk-monitor-plan.json
kubectl -n quorivio patch statefulset quorivio-postgres --type=json \
  --patch-file=./disk-monitor-plan-rc262/disk-monitor-json-patch.json \
  --dry-run=server -o name
# Apply ONLY with verified backups and an approved maintenance window:
python3 k8s_wizard.py --apply-disk-monitor --acknowledge-db-restart \
  --output ./disk-monitor-plan-rc262
kubectl -n quorivio rollout status statefulset/quorivio-postgres
kubectl -n quorivio logs statefulset/quorivio-postgres -c db-disk-probe --since=10m
kubectl kustomize ./k8s-generated >/dev/null
```

The apply operation requires the original StatefulSet UID/resourceVersion and generated manifest digests to match the reviewed plan. After a successful rollout it creates `97-postgres-disk-probe-patch.json`, updates `kustomization.yaml` and keeps private backups. For an already-installed probe, `--sync-disk-monitor --generated-dir ./k8s-generated --set namespace=quorivio --set name=quorivio` only reads Kubernetes and reconciles the local Kustomize overlay.

No extra Quorivio modules are needed by the single-file self-updating wizard. Use `--no-self-update` only for an explicitly offline run. Admin SMTP must be configured for outgoing email. The full GitHub CI is still pending; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
