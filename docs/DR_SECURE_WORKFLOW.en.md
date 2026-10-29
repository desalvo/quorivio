# Encrypted instance disaster recovery — first-class operator workflow

**Quorivio 0.1.0-dev — local implementation, 29 October 2026.** This is an explicit, offline operator tool. It does **not** schedule backups, encrypt legacy `instance_backup.py backup` by default, configure a secret manager or guarantee production RPO/RTO. Use it only with stopped writers and an independently protected copy of the encryption key.

## Initial backup

Provision a **private 0700 directory on an encrypted filesystem**; raw PostgreSQL dumps and `tar.gz` exist only inside this protected workspace while the command runs. Never use an unencrypted shared `/tmp` mount for the work directory. The generated `.qenc` is the only published backup; temporary plaintext is removed on success **and** failure. This removal cannot guarantee secure deletion from SSDs, snapshots or copy-on-write filesystems.

```sh
umask 077
mkdir -m 700 -p /protected-encrypted-volume/quorivio-work
python3 tools/backup_envelope.py keygen --key-file /keys/quorivio-2026-10.key
export DATABASE_URL='postgres://<account>:<password>@<database-host>:5432/quorivio'
python3 tools/secure_instance_backup.py backup --assets /srv/quorivio/assets --key-file /keys/quorivio-2026-10.key --work-dir /protected-encrypted-volume/quorivio-work --output /private-backups/quorivio-2026-10.qenc
python3 tools/secure_instance_backup.py verify --input /private-backups/quorivio-2026-10.qenc --key-file /keys/quorivio-2026-10.key --work-dir /protected-encrypted-volume/quorivio-work
```

Install `cryptography>=43,<47` and the PostgreSQL 18 client tools in the operator environment. Protect `DATABASE_URL` from shell history/process exposure. The key file must contain exactly 32 random bytes, be owned by the process user, and have mode `0600`; never store it alongside the archive. Every destination is exclusive/no-overwrite.

## Rotate and recover

```sh
python3 tools/backup_envelope.py keygen --key-file /keys/quorivio-2026-11.key
python3 tools/secure_instance_backup.py rotate --input /private-backups/quorivio-2026-10.qenc --output /private-backups/quorivio-2026-11.qenc --old-key-file /keys/quorivio-2026-10.key --new-key-file /keys/quorivio-2026-11.key
# On an isolated recovery host, with application writers stopped and a FRESH empty database:
export DATABASE_URL='postgres://<account>:<password>@<restore-host>:5432/quorivio_new'
python3 tools/secure_instance_backup.py restore --input /private-backups/quorivio-2026-11.qenc --assets /srv/quorivio-restored/assets --key-file /keys/quorivio-2026-11.key --work-dir /protected-encrypted-volume/quorivio-work --confirm RESTORE-QUORIVIO-DATA
```

The rotation streams authenticated decrypted chunks directly into new AES-256-GCM encryption. It **never stages a decrypted archive** on disk. A corrupted old tag, wrong old key, same replacement key or write failure prevents publishing a rotated archive. `restore` rejects wrong confirmation, missing database URL, non-empty asset directory and existing database relations before decrypting. The underlying restore rechecks state before committing. Keep both original and rotated archives/keys until the new archive is independently verified, and explicitly record key custody, retention, backup age, measured recovery time and data loss in a representative drill.

**CI coverage:** disposable PostgreSQL 18 backup/restore, real encrypted operator `backup`/`verify`/`restore` into a second fresh database, schema/row/asset parity, wrong-key refusal, and temporary directory cleanup. This local addition must pass a new full GitHub CI before being considered verified. The D2/D6 production recovery, key governance, SLO/RPO/RTO and independent approval gates remain open.


**Cycle 19:** The protected restore rehearsal and conservative backup-retention workflow are documented in [DR_REHEARSAL_AND_RETENTION.en.md](DR_REHEARSAL_AND_RETENTION.en.md). Technical timing and backup age are not production RTO/RPO evidence.
