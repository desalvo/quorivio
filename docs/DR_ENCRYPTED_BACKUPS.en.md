# Quorivio disaster recovery — encrypted backups (operator procedure)

**Version 0.1.0-dev; RC cycle 17.** The existing `tools/instance_backup.py` continues to emit/restore checked `tar.gz` backups. It does **not** encrypt by itself. Protect every archive before transferring it off the backup host. These commands operate on local files and never contact a key service.

Install the runtime dependency in a trusted environment: `python3 -m pip install 'cryptography>=43,<47'`. Stop all database and asset writers, take a consistent local backup, and create a **random private 32-byte key**:

```bash
umask 077
python3 tools/backup_envelope.py keygen --key-file /secure/keys/quorivio-2026-10.key
python3 tools/instance_backup.py backup --assets /srv/quorivio/assets --output /private/quorivio-raw.tar.gz
python3 tools/backup_envelope.py encrypt --key-file /secure/keys/quorivio-2026-10.key --input /private/quorivio-raw.tar.gz --output /safe-offsite/quorivio.qenc
python3 tools/backup_envelope.py decrypt --key-file /secure/keys/quorivio-2026-10.key --input /safe-offsite/quorivio.qenc --output /private/verified-restore.tar.gz
python3 tools/instance_backup.py verify --input /private/verified-restore.tar.gz
```

Restore only after the normal **empty database**, **empty asset directory**, **stopped writers** and operator confirmation preflights. Never put the raw key in a shell argument, CI log, application config, or backup archive. Encrypt the database dump immediately, restrict and remove the raw `tar.gz` and temporary decrypted files (secure deletion is not guaranteed on SSD/copy-on-write filesystems). Place temporary plaintext on a protected encrypted filesystem if possible. Protect the key with an independent secret manager and keep an offline recovery copy. Loss of the key makes backups irrecoverable.

To **rotate** a key without losing the old archive, generate a new key and re-encrypt into a *different* destination; rotation authenticates the old envelope before publishing a replacement:

```bash
python3 tools/backup_envelope.py keygen --key-file /secure/keys/quorivio-2026-11.key
python3 tools/backup_envelope.py rotate --old-key-file /secure/keys/quorivio-2026-10.key --new-key-file /secure/keys/quorivio-2026-11.key --input /safe-offsite/quorivio.qenc --output /safe-offsite/quorivio-rotated.qenc
```

Envelope v1: `QVBKENC1` magic, 96-bit random nonce, AES-256-GCM ciphertext and 128-bit authentication tag. Header is authenticated as additional data; a failed authentication never publishes plaintext. Files/keys require owner-only permissions, and outputs are created atomically without overwriting. The system does not derive keys from human passwords. Rotating an already published encrypted archive does not automatically revoke all old copies. Make retention, key custody, backup consistency, RPO/RTO and restore drills part of operational approval.

**CI scope:** disposable PostgreSQL 18 backup → encryption → wrong-key rejection → key rotation → authenticated decryption → restore into fresh database → schema, rows, assets and privacy checks. A successful CI is **not** a production-like disaster recovery exercise or a formal RPO/RTO guarantee. Production operational acceptance and recovery key custody remain open in D2/D6.

## Integrated operator workflow (cycle 18)

The new [`secure_instance_backup.py`](../tools/secure_instance_backup.py) adds explicit `backup`, `verify`, `rotate` and `restore` commands; see [operator workflow](DR_SECURE_WORKFLOW.en.md). Streaming key rotation no longer creates temporary plaintext files. The older two-step backup/encrypt workflow above remains valid and deliberately unencrypted until manually sealed. No production DR sign-off is claimed.
