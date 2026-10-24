#!/usr/bin/env python3
"""Disposable PostgreSQL 18 backup/restore acceptance: no production database writes.

Copies a CI-only database into a separate fresh database and checks row parity,
asset fidelity, backup integrity and refusal to restore into nonempty assets.
"""
import os
import pathlib
import subprocess
import tempfile
import time
from urllib.parse import urlsplit, urlunsplit

from instance_backup import make_backup, verify, restore

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
        # Production-safety invariant: an existing application database is never a restore target.
        try:
            restore(backup, root / 'refused-assets', SOURCE, 'RESTORE-QUORIVIO-DATA')
        except ValueError as error:
            assert 'fresh database' in str(error), f'unexpected rejection: {error}'
        else:
            raise AssertionError('Restore into populated source database must be refused')
        assert not (root / 'refused-assets').exists()
        subprocess.run(['createdb', '--maintenance-db', SOURCE, db], check=True, env=env, timeout=30)
        try:
            restored_assets = root / 'restored-assets'
            restore_started = time.monotonic()
            restore(backup, restored_assets, target, 'RESTORE-QUORIVIO-DATA')
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
                restore(backup, restored_assets, target, 'RESTORE-QUORIVIO-DATA')
            except ValueError:
                pass
            else:
                raise AssertionError('Nonempty asset destination must be refused')
            print(f'PASS PostgreSQL 18 instance DR: populated-DB refusal, schema and row parity, private assets, integrity, overwrite rejection; backup={backup_seconds:.2f}s restore={restore_seconds:.2f}s (CI-only sample, not RTO/RPO SLA)')
        finally:
            subprocess.run(['dropdb', '--if-exists', '--maintenance-db', SOURCE, db],
                           check=True, env=env, timeout=30)


if __name__ == '__main__':
    run()
