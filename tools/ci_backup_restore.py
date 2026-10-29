#!/usr/bin/env python3
"""Disposable PostgreSQL 18 backup/restore acceptance: no production database writes.

Copies a CI-only database into a separate fresh database and checks row parity,
asset fidelity, backup integrity and refusal to restore into nonempty assets.
"""
import os
import json
import shutil
import pathlib
import subprocess
import tempfile
import time
from urllib.parse import urlsplit, urlunsplit

from instance_backup import make_backup, verify, restore
from backup_envelope import private_keygen, encrypt, decrypt, rotate
from secure_instance_backup import backup_encrypted, verify_encrypted, restore_encrypted, restore_drill, CONFIRM
from backup_retention import prune_encrypted, CONFIRM as PRUNE_CONFIRM
from backup_mirror import mirror_backup, verify_mirror

SOURCE = os.environ.get('DATABASE_URL', '')
ASSETS = pathlib.Path(os.environ.get('QUORIVIO_ASSET_DIR', '/tmp/quorivio-ci-assets'))


def run():
    parts = urlsplit(SOURCE)
    if parts.hostname not in ('127.0.0.1', 'localhost') or parts.path != '/quorivio':
        raise RuntimeError('Backup acceptance is restricted to disposable local CI database')
    target = urlunsplit((parts.scheme, parts.netloc, '/quorivio_restore_acceptance', '', ''))
    db = 'quorivio_restore_acceptance'
    env = dict(os.environ)
    env['PGCONNECT_TIMEOUT'] = '15'
    with tempfile.TemporaryDirectory(prefix='quorivio-dr-acceptance-') as temp:
        root = pathlib.Path(temp)
        original_assets = root / 'source-assets'
        (original_assets / 'ci-session').mkdir(parents=True)
        payload = b'Quorivio CI disaster recovery asset verification\x00\xff'
        (original_assets / 'ci-session' / 'asset.bin').write_bytes(payload)
        backup = root / 'snapshot.tar.gz'
        backup_started = time.monotonic()
        make_backup(backup, original_assets, SOURCE)
        backup_seconds = time.monotonic() - backup_started
        manifest = verify(backup)
        assert len(manifest['files']) == 2
        # Real PostgreSQL backup contents are protected with authenticated
        # AES-256-GCM encryption before being restored. Exercise key rotation
        # and ensure a wrong key cannot publish even a partial plaintext file.
        old_key, new_key = root / 'old.key', root / 'new.key'
        private_keygen(old_key)
        private_keygen(new_key)
        encrypted = root / 'snapshot.qenc'
        rotated = root / 'rotated.qenc'
        decrypted = root / 'restorable.tgz'
        encrypt(backup, encrypted, old_key)
        try:
            decrypt(encrypted, root / 'wrong-key.tgz', new_key)
        except ValueError as error:
            assert 'authentication failed' in str(error)
        else:
            raise AssertionError('Wrong backup key must fail authentication')
        assert not (root / 'wrong-key.tgz').exists(), 'Authentication error published plaintext'
        rotate(encrypted, rotated, old_key, new_key)
        try:
            decrypt(rotated, root / 'old-key.tgz', old_key)
        except ValueError:
            pass
        else:
            raise AssertionError('Rotated archive must reject old key')
        assert not (root / 'old-key.tgz').exists()
        decrypt(rotated, decrypted, new_key)
        assert decrypted.read_bytes() == backup.read_bytes(), 'Rotated encrypted backup data mismatch'
        assert verify(decrypted) == manifest, 'Rotated decrypted backup failed integrity check'
        # Production-safety invariant: an existing application database is never a restore target.
        try:
            restore(decrypted, root / 'refused-assets', SOURCE, 'RESTORE-QUORIVIO-DATA')
        except ValueError as error:
            assert 'fresh database' in str(error), f'unexpected rejection: {error}'
        else:
            raise AssertionError('Restore into populated source database must be refused')
        assert not (root / 'refused-assets').exists()
        subprocess.run(['createdb', '--maintenance-db', SOURCE, db], check=True, env=env, timeout=30)
        try:
            restored_assets = root / 'restored-assets'
            restore_started = time.monotonic()
            restore(decrypted, restored_assets, target, 'RESTORE-QUORIVIO-DATA')
            restore_seconds = time.monotonic() - restore_started
            assert (restored_assets / 'ci-session' / 'asset.bin').read_bytes() == payload
            for table in ('users', 'sessions', 'activities', 'widget_answers'):
                query = f'SELECT count(*) FROM {table}'
                def count(url):
                    result = subprocess.run(['psql', url, '-Atc', query], capture_output=True,
                                            text=True, check=True, env=env, timeout=20)
                    return int(result.stdout.strip())
                assert count(SOURCE) == count(target), f'{table} row count differs after restore'
            # Schema parity checks detect silent omissions beyond row-count parity.
            def tables(url):
                result = subprocess.run(['psql', url, '-Atc',
                    "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public' ORDER BY tablename"],
                    capture_output=True, text=True, check=True, env=env, timeout=20)
                return result.stdout.splitlines()
            assert tables(SOURCE) == tables(target), 'Schema table list differs after restore'
            assert restored_assets.stat().st_mode & 0o077 == 0, 'Restored assets directory is not private'
            try:
                restore(decrypted, restored_assets, target, 'RESTORE-QUORIVIO-DATA')
            except ValueError:
                pass
            else:
                raise AssertionError('Nonempty asset destination must be refused')
            # Independent full operator workflow: direct encrypted backup and
            # guarded restore into ANOTHER fresh PostgreSQL 18 database. It
            # must leave no cleartext tarball or dump in the work directory.
            protected_spool = root / 'private-encrypted-workspace'
            protected_spool.mkdir(mode=0o700)
            managed_archive = root / 'managed-backup.qenc'
            managed_manifest = backup_encrypted(managed_archive, original_assets, SOURCE,
                                                old_key, protected_spool)
            # Custom-format pg_dump contains a creation timestamp and may have different
            # bytes across consecutive consistent snapshots. Compare logical
            # asset records here; database schema and rows are checked below.
            assert managed_manifest['files'][1:] == manifest['files'][1:]
            assert len(managed_manifest['files']) == len(manifest['files'])
            assert verify_encrypted(managed_archive, old_key, protected_spool) == managed_manifest
            assert not list(protected_spool.iterdir()), 'Managed backup left a plaintext intermediate'
            alternate_db = 'quorivio_restore_sealed_acceptance'
            alternate_url = urlunsplit((parts.scheme, parts.netloc, '/' + alternate_db, '', ''))
            subprocess.run(['createdb', '--maintenance-db', SOURCE, alternate_db],
                           check=True, env=env, timeout=30)
            try:
                alternate_assets = root / 'managed-restored-assets'
                try:
                    restore_encrypted(managed_archive, alternate_assets, alternate_url,
                                      new_key, protected_spool, CONFIRM)
                except ValueError as error:
                    assert 'authentication failed' in str(error)
                else:
                    raise AssertionError('Managed restore accepted a wrong key')
                assert not alternate_assets.exists(), 'Wrong key published asset bytes'
                restore_encrypted(managed_archive, alternate_assets, alternate_url,
                                  old_key, protected_spool, CONFIRM)
                assert (alternate_assets / 'ci-session' / 'asset.bin').read_bytes() == payload
                assert tables(SOURCE) == tables(alternate_url), 'Managed encrypted schema mismatch'
                for table in ('users', 'sessions', 'activities', 'widget_answers'):
                    query = f'SELECT count(*) FROM {table}'
                    counts = []
                    for url in (SOURCE, alternate_url):
                        result = subprocess.run(['psql', url, '-Atc', query],
                                capture_output=True, text=True, check=True, env=env, timeout=20)
                        counts.append(int(result.stdout.strip()))
                    assert counts[0] == counts[1], f'Managed encrypted {table} row count differs'
                assert not list(protected_spool.iterdir()), 'Managed restore left a plaintext intermediate'
                # Operational DR rehearsal: a DIFFERENT disposable empty database
                # with rotated key, explicit age/restore-time targets and private
                # credential-free evidence. These sample timings are not SLO/RPO/RTO.
                drill_db = 'quorivio_restore_drill_acceptance'
                drill_url = urlunsplit((parts.scheme, parts.netloc, '/' + drill_db, '', ''))
                rotated_managed = root / 'managed-rotated.qenc'
                rotate(managed_archive, rotated_managed, old_key, new_key)
                subprocess.run(['createdb', '--maintenance-db', SOURCE, drill_db],
                               check=True, env=env, timeout=30)
                try:
                    drill_assets = root / 'drill-assets'
                    evidence_path = pathlib.Path(os.environ.get('QUORIVIO_CI_DR_RECEIPT',
                                                                '/tmp/quorivio-dr-rehearsal.json'))
                    receipt = restore_drill(rotated_managed, drill_assets, drill_url,
                            new_key, protected_spool, CONFIRM, evidence_path,
                            max_age_seconds=3600, max_restore_seconds=120)
                    assert receipt['status'] == 'restore_completed'
                    assert receipt['age_threshold_met'] and receipt['restore_duration_threshold_met']
                    assert not list(protected_spool.iterdir()), 'DR rehearsal left plaintext files'
                    assert (drill_assets / 'ci-session' / 'asset.bin').read_bytes() == payload
                    assert tables(SOURCE) == tables(drill_url), 'DR rehearsal schema mismatch'
                    for table in ('users', 'sessions', 'activities', 'widget_answers'):
                        query = f'SELECT count(*) FROM {table}'
                        def count_rows(url):
                            response = subprocess.run(['psql', url, '-Atc', query],
                                capture_output=True, text=True, check=True, env=env, timeout=20)
                            return int(response.stdout.strip())
                        assert count_rows(SOURCE) == count_rows(drill_url), f'DR rehearsal {table} parity failed'
                    assert evidence_path.stat().st_mode & 0o077 == 0
                    print('PASS PostgreSQL 18 DR rehearsal: rotated authenticated backup, distinct empty database, private assets and metadata-only receipt; NOT production RPO/RTO')
                finally:
                    subprocess.run(['dropdb', '--if-exists', '--maintenance-db', SOURCE, drill_db],
                                   check=True, env=env, timeout=30)
                # Real PostgreSQL 18 remote-volume recovery rehearsal: copy only
                # authenticated ciphertext onto an independent ephemeral tmpfs.
                # /dev/shm is a separate mounted filesystem in CI, NOT offsite
                # production storage; no key or plaintext is written to it.
                if not os.path.ismount('/dev/shm'):
                    raise RuntimeError('CI mirror acceptance needs the mounted tmpfs /dev/shm')
                with tempfile.TemporaryDirectory(prefix='quorivio-ci-mirror-', dir='/dev/shm') as temp_mirror:
                    mirror_dir = pathlib.Path(temp_mirror)
                    mirror_dir.chmod(0o700)
                    transfer = mirror_backup(rotated_managed, mirror_dir,
                                    pathlib.Path('/dev/shm'), new_key, protected_spool)
                    checked = verify_mirror(mirror_dir, pathlib.Path('/dev/shm'),
                                    rotated_managed.name, new_key, protected_spool)
                    assert checked['status'] == 'verified'
                    assert checked['files'] == len(managed_manifest['files'])
                    assert transfer['verified_files'] == checked['files']
                    mirror_db = 'quorivio_remote_mirror_restore_ci'
                    mirror_url = urlunsplit((parts.scheme, parts.netloc, '/' + mirror_db, '', ''))
                    subprocess.run(['createdb', '--maintenance-db', SOURCE, mirror_db],
                                   check=True, env=env, timeout=30)
                    try:
                        mirror_assets = root / 'mirror-restored-assets'
                        restore_encrypted(mirror_dir / rotated_managed.name, mirror_assets,
                                          mirror_url, new_key, protected_spool, CONFIRM)
                        assert (mirror_assets / 'ci-session' / 'asset.bin').read_bytes() == payload
                        assert tables(SOURCE) == tables(mirror_url), 'Mirror restored schema differs'
                        for table in ('users', 'sessions', 'activities', 'widget_answers'):
                            query = f'SELECT count(*) FROM {table}'
                            expected = subprocess.run(['psql', SOURCE, '-Atc', query],
                                capture_output=True, text=True, check=True, env=env, timeout=20)
                            actual = subprocess.run(['psql', mirror_url, '-Atc', query],
                                capture_output=True, text=True, check=True, env=env, timeout=20)
                            assert expected.stdout == actual.stdout, f'Mirrored {table} data differs'
                        assert not list(protected_spool.iterdir())
                        assert sorted(p.name for p in mirror_dir.iterdir()) == [
                            'managed-rotated.qenc', 'managed-rotated.qenc.receipt.json']
                        print('PASS PostgreSQL 18 mounted-volume encrypted mirror: authentic copy, private receipt, independent empty database restore, schema/data/assets parity; CI-only, NOT offsite or RTO/RPO')
                    finally:
                        subprocess.run(['dropdb', '--if-exists', '--maintenance-db', SOURCE, mirror_db],
                                       check=True, env=env, timeout=30)
                # Authenticated retention is exercised on REAL PostgreSQL 18
                # snapshots, including both generations of encryption keys.
                retention_dir = root / 'retention-exercise'
                retention_dir.mkdir(mode=0o700)
                current = retention_dir / 'current.qenc'
                stale = retention_dir / 'stale.qenc'
                shutil.copyfile(rotated_managed, current)
                shutil.copyfile(managed_archive, stale)
                for item in (current, stale):
                    os.chmod(item, 0o600)
                old_time = time.time() - 90 * 86400
                os.utime(stale, (old_time, old_time))
                holds = root / 'legal-holds.json'
                holds.write_text(json.dumps({'version': 1, 'hold': ['stale.qenc']}))
                holds.chmod(0o600)
                dry = prune_encrypted(retention_dir, days=30, min_keep=1,
                                      holds_file=holds)
                assert dry['removed_count'] == 0 and not dry['candidates']
                held = prune_encrypted(retention_dir, days=30, min_keep=1, apply=True,
                                      confirmation=PRUNE_CONFIRM, holds_file=holds,
                                      key_files=(old_key, new_key), work_dir=protected_spool)
                assert held['removed_count'] == 0 and held['authenticated_snapshots'] == 2
                holds.write_text(json.dumps({'version': 1, 'hold': []}))
                os.chmod(holds, 0o600)
                pruned = prune_encrypted(retention_dir, days=30, min_keep=1, apply=True,
                                        confirmation=PRUNE_CONFIRM, holds_file=holds,
                                        key_files=(old_key, new_key), work_dir=protected_spool)
                assert pruned['removed_count'] == 1 and pruned['authenticated_snapshots'] == 2
                assert current.exists() and not stale.exists()
                assert not list(protected_spool.iterdir()), 'Retention left plaintext intermediates'
                print('PASS PostgreSQL 18 authenticated DR retention: key generations, legal hold, checksum and age policy, no plaintext residue')
                print('PASS PostgreSQL 18 first-class encrypted DR: sealed backup, verify, wrong-key failure, guarded empty-db restore, schema, rows and private assets; private workspace cleared')
            finally:
                subprocess.run(['dropdb', '--if-exists', '--maintenance-db', SOURCE, alternate_db],
                               check=True, env=env, timeout=30)
            print(f'PASS PostgreSQL 18 encrypted instance DR: AES-256-GCM, key rotation, wrong-key refusal, populated-DB refusal, schema and row parity, private assets, integrity, overwrite rejection; backup={backup_seconds:.2f}s restore={restore_seconds:.2f}s (CI-only sample, not RTO/RPO SLA)')
        finally:
            subprocess.run(['dropdb', '--if-exists', '--maintenance-db', SOURCE, db],
                           check=True, env=env, timeout=30)


if __name__ == '__main__':
    run()
