# Disaster recovery rehearsal and encrypted-backup retention

**Quorivio 0.1.0-dev — cycle 19, 29 October 2026.** This is a technical procedure; it does not constitute a production recovery SLA, GDPR sign-off, or independent disaster-recovery approval.

## Prerequisites and safety boundary

Install Python cryptography and PostgreSQL 18 clients. Stop writers on the source instance before obtaining a snapshot, and **never restore into a populated database**. Supply a newly-created empty database and an empty, non-symlinked asset directory. The `--work-dir` must be a private **0700 directory on an encrypted filesystem**; the command stages authenticated plaintext in that protected directory while verifying and restoring and deletes it on exit. This is *not* secure erasure from SSDs, copy-on-write snapshots, or backups. Keep key files private (0600), under independent custody, and never commit them.

## Record a real restore rehearsal

After generating a sealed backup and optionally rotating its key using `tools/secure_instance_backup.py`, set `DATABASE_URL` to a **fresh, empty test database** and run:

```sh
export DATABASE_URL='postgres://<operator>:<password>@<isolated-recovery-host>:5432/quorivio_dr_drill'
python3 tools/secure_instance_backup.py drill \
  --input /private-backups/quorivio-2026-10.qenc \
  --assets /private-recovery/empty-assets \
  --key-file /private-keys/quorivio-2026-10.key \
  --work-dir /encrypted-work/quorivio \
  --receipt /private-reports/quorivio-dr-receipt.json \
  --max-backup-age-seconds 86400 \
  --max-restore-seconds 3600 \
  --confirm RESTORE-QUORIVIO-DATA
```

The command authenticates and verifies the encrypted archive *before* restoring, refuses stale archives if a max-age limit is supplied, and checks for empty restore targets. An existing receipt is never overwritten. On successful restore, the private (0600) JSON receipt contains the age of the backup and duration of **this restore command only**, along with the number of verified objects and pass/fail thresholds. No DB URL, keys, asset paths, uploaded contents, or tokens are recorded. A restore that exceeds its duration threshold has **already completed**; the command exits with an error while preserving the receipt indicating the missed threshold. It **does not roll back** the restored database or assets.

**Important:** A backup's age is a *freshness proxy*, not actual recovery point objective (RPO). The measured command duration is not full recovery time objective (RTO): it excludes site failover, infrastructure provisioning, traffic cutover, DNS, user acceptance and source-write loss. An operator must document those separately on a representative dataset and obtain independent sign-off before D2 can be accepted.

## Authenticated retention and legal holds (cycle 20)

**Important behavior change:** even when the operator has explicitly confirmed deletion, `--apply` now **requires** a private legal-hold registry, all relevant encryption key generations, and an existing protected work directory. The previous `--apply --confirm ...` command without these arguments intentionally refuses deletion. The register is a 0600 JSON file created and maintained by the operator, for example:

```json
{"version":1,"hold":["quorivio-regulatory-hold-2026.qenc"]}
```

Names must refer to real `.qenc` archives in the target owner-only 0700 directory. Invalid/missing records and symlinks fail closed. **An empty hold array is an explicit declaration, not proof of legal approval.** The operator must still check organizational hold registers and independent/offsite copies. Held archives never count toward the `--min-keep` floor for other recoverable copies.

```sh
# Safe read-only planning, no keys needed:
python3 tools/backup_retention.py --directory /private-backups --days 30 --min-keep 3 \
  --holds-file /private-keys/quorivio-legal-holds.json
# Destructive application: authenticate every sealed archive and its inner
# backup manifest BEFORE the first unlink; specify keys from all generations.
python3 tools/backup_retention.py --directory /private-backups --days 30 --min-keep 3 \
  --holds-file /private-keys/quorivio-legal-holds.json \
  --key-file /private-keys/quorivio-2026.key \
  --key-file /private-keys/quorivio-rotated.key \
  --work-dir /encrypted-work/quorivio \
  --apply --confirm PRUNE-QUORIVIO-ENCRYPTED-BACKUPS
```

The authenticating preflight tests **all** archives, including those about to be deleted: if a recent retained archive is corrupted, no older candidate is deleted. The tool rechecks the file identities and hold registry after validation, and refuses concurrent changes. The `--work-dir` must be private 0700 on an encrypted filesystem; verification can stage decrypted files there temporarily and cleans them afterward, but SSD secure erasure is not guaranteed. No automatic schedule or Kubernetes default pruning is enabled. Storage mtime is only a planning input, not proof of RPO, restore success or offsite availability. Operator acceptance and independent legal review remain required for D2/D6.

## GitHub CI evidence

The disposable PostgreSQL 18 test now restores another **independent** fresh database from a rotated encrypted archive, checks schema, row and asset parity, and publishes a sanitized, private technical receipt as the `dr-rehearsal-ci-only` artifact. The artifact has no credentials and is explicitly labeled a CI sample, not an RPO/RTO claim. This test and the new CLI must pass on the next GitHub Full CI before this functionality is counted as externally verified. D2/D6 remain partially open pending independent operational exercises and review.
