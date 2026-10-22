# Full Quorivio instance backup and restore (EN)

## Scope and status

This first **offline** operation bundles a PostgreSQL custom-format dump and the private asset directory in a `.tar.gz` archive containing a manifest and per-file SHA-256 hashes. It is not yet exposed from the administrator web UI. It has not been exercised with a real PostgreSQL server, S3 storage or Kubernetes cluster.

## Prerequisites

Stop application writes before backup and restore. Install `pg_dump` and `pg_restore` compatible with the PostgreSQL server in a protected administrative environment. Set `DATABASE_URL` without leaking it to shell history. Run with privileges to read the full asset tree. Database contents and uploaded media may contain personal information: **encrypt stored backups, protect encryption keys, enforce retention and restrict access**.

## Backup

```bash
export DATABASE_URL='postgresql://...'
python3 tools/instance_backup.py backup --assets /app/assets --output /secure/backups/quorivio-YYYYMMDD.tar.gz
python3 tools/instance_backup.py verify --input /secure/backups/quorivio-YYYYMMDD.tar.gz
```

In a Compose deployment, run this from an administrative host/sidecar with read-only access to the assets and database connectivity. The application runtime image is not expected to contain PostgreSQL client utilities.

## Restore

1. Create an **empty** PostgreSQL database and an **empty** asset directory in an isolated environment.
2. Run `verify` against the archive and validate its checksums.
3. Stop any writers to the restore target.
4. Run:

```bash
python3 tools/instance_backup.py restore --input /secure/backups/quorivio-YYYYMMDD.tar.gz --assets /new-assets --confirm RESTORE-QUORIVIO-DATA
```

5. Reconcile migrations, asset references, access controls, service health and application behavior in staging before any production use.

The script deliberately does not use `--clean`: **never restore into a populated database**. PostgreSQL and filesystem writes are **not atomic together**; after a failed restore, recreate empty destinations and repeat rather than reuse partially restored data.

## Kubernetes

The wizard generates `15-assets-pvc.yaml` using `asset_storage_size` (default `10Gi`), `asset_storage_class` and `asset_access_mode`, then mounts it at `/app/assets`. Choose `ReadWriteMany` only if the cluster's StorageClass supports it. Coordinated PostgreSQL/PVC snapshots, restore drills and GDPR validation are still necessary.

## Remaining production gaps

Administrator UI controls, built-in scheduling, automatic archive encryption, coordinated snapshots, S3 and real PostgreSQL integration tests are not yet available. This is an initial administrative maintenance mechanism, not certified disaster recovery.
