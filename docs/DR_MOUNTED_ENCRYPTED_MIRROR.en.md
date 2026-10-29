# Mounted encrypted backup mirror — Quorivio 0.1.0-dev, RC cycle 21

This is a **technical mirror and recoverability test**, not a completed offsite/disaster-recovery service or a production RPO/RTO guarantee. The operator must provision and periodically verify a physically independent backup location, separate credentials and key custody, monitoring, retention, and a recovery process.

`tools/backup_mirror.py` copies **only the AES-256-GCM encrypted `.qenc` archive** to an existing, owner-only (0700) directory on a pre-mounted backup filesystem. If the mount disappears, it refuses to copy to the underlying local directory. It does not support cloud object stores or mount them automatically. The `--mount-root` must be a genuine, non-root filesystem mount point that contains the target directory; `/` is explicitly forbidden. `--work-dir` must be private (0700) on an operator-protected **encrypted** filesystem: archive authentication decrypts temporarily *there*, not onto the mirror. Secure erasure from SSD/COW filesystem snapshots is not guaranteed. Raw encryption keys are never replicated.

The source `.qenc` and key must be private 0600 regular files, owned by the invoking user. No existing archive or receipt is overwritten. The copy is staged, AES-GCM authenticated, inner backup manifest verified and SHA-256 checked before being atomically published. A sanitized owner-only receipt accompanies the archive. `verify` repeats checksum, GCM and manifest verification; a receipt is technical evidence, not a cryptographic signature of the operator's identity.

```sh
# The backup share has already been mounted by an administrator, e.g. /mnt/backup-remote.
# mkdir -m 700 /mnt/backup-remote/quorivio   # on the mounted volume
python3 tools/backup_mirror.py push \
  --source /private-backups/verified-snapshot.qenc \
  --directory /mnt/backup-remote/quorivio \
  --mount-root /mnt/backup-remote \
  --key-file /private-keys/backup-current.key \
  --work-dir /encrypted-work/quorivio
python3 tools/backup_mirror.py verify \
  --name verified-snapshot.qenc \
  --directory /mnt/backup-remote/quorivio \
  --mount-root /mnt/backup-remote \
  --key-file /private-keys/backup-current.key \
  --work-dir /encrypted-work/quorivio
```

For a **real restore** use `tools/secure_instance_backup.py drill` on the mirrored `.qenc` archive, pointing to an isolated, empty PostgreSQL database and an empty asset directory. Follow `DR_REHEARSAL_AND_RETENTION.en.md` to record measured command time and backup-age proxy. Independently measure **actual source-write loss, infrastructure provisioning, client cutover and application availability**, and review legal holds and storage isolation. No automated scheduling, offsite mount creation, provider credential management or backup deletion is enabled by this tool.

In the GitHub Full CI a separate ephemeral `/dev/shm` tmpfs represents a mounted volume. It proves copy/authentication/restore mechanics against disposable PostgreSQL 18 and checks schema/rows/assets in a fourth fresh database; it does **not** prove offsite storage independence, real cloud/NFS network faults, legal compliance, production RTO/RPO or operational acceptance. Until new CI and independent operator sign-off, RC D2/D6 remain partial.
