#!/usr/bin/env python3
"""Disposable PostgreSQL 18 backup/restore acceptance: no production database writes.

Copies a CI-only database into a separate fresh database and checks row parity,
asset fidelity, backup integrity and refusal to restore into nonempty assets.
"""
import os
import pathlib
import subprocess
import tempfile
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
        make_backup(backup, original_assets, SOURCE)
        manifest = verify(backup)
        assert len(manifest['files']) == 2
        subprocess.run(['createdb', '--maintenance-db', SOURCE, db], check=True, env=env, timeout=30)
        try:
            restored_assets = root / 'restored-assets'
            restore(backup, restored_assets, target, 'RESTORE-QUORIVIO-DATA')
            assert (restored_assets / 'ci-session' / 'asset.bin').read_bytes() == payload
            for table in ('users', 'sessions', 'activities', 'widget_answers'):
                query = f'SELECT count(*) FROM {table}'
                def count(url):
                    result = subprocess.run(['psql', url, '-Atc', query], capture_output=True,
                                            text=True, check=True, env=env, timeout=20)
                    return int(result.stdout.strip())
                assert count(SOURCE) == count(target), f'{table} row count differs after restore'
            try:
                restore(backup, restored_assets, target, 'RESTORE-QUORIVIO-DATA')
            except ValueError:
                pass
            else:
                raise AssertionError('Nonempty asset destination must be refused')
            print('PASS PostgreSQL 18 instance DR: archive integrity, fresh DB restore, row parity, asset fidelity, overwrite rejection')
        finally:
            subprocess.run(['dropdb', '--if-exists', '--maintenance-db', SOURCE, db],
                           check=True, env=env, timeout=30)


if __name__ == '__main__':
    run()
