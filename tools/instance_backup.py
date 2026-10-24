#!/usr/bin/env python3
"""Offline, integrity-checked Quorivio instance backup and controlled restore.

Stop application writers first. Restore ONLY into a freshly created, empty database.
Backups contain personal data: encrypt and restrict access to the archive.
"""
import argparse
import hashlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone

VERSION = 1
MAX_MANIFEST = 1024 * 1024
MAX_FILES = 10000
MAX_FILE_BYTES = 2 * 1024**3
MAX_TOTAL_BYTES = 10 * 1024**3


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_asset_path(name):
    if not isinstance(name, str) or not name.isascii() or '\\' in name or '\x00' in name:
        raise ValueError('Invalid backup asset path')
    parts = pathlib.PurePosixPath(name).parts
    if len(parts) != 3 or parts[0] != 'assets' or any(part in ('', '.', '..') for part in parts):
        raise ValueError('Invalid backup asset path')
    if name != '/'.join(parts):
        raise ValueError('Invalid backup asset path')
    return pathlib.Path(parts[1], parts[2])


def checked_asset_files(root):
    if not root.is_dir() or root.is_symlink():
        raise ValueError('Asset directory does not exist or is a symlink')
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError(f'Symlink in asset directory: {p}')
        if p.is_file():
            rel = p.relative_to(root)
            name = 'assets/' + rel.as_posix()
            safe_asset_path(name)
            yield p, name
        elif not p.is_dir():
            raise ValueError(f'Non-regular asset: {p}')


def make_backup(destination, assets, database_url):
    if not database_url:
        raise ValueError('DATABASE_URL is required')
    destination, assets = pathlib.Path(destination), pathlib.Path(assets)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Refusing to overwrite an existing backup')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='quorivio-backup-') as tmp:
        dump = pathlib.Path(tmp) / 'database.dump'
        env = os.environ.copy()
        env['PGCONNECT_TIMEOUT'] = '15'
        subprocess.run(['pg_dump', '--format=custom', '--no-owner', '--no-acl', '--file', str(dump), database_url],
                       env=env, check=True, timeout=3600)
        objects = [(dump, 'database.dump'), *checked_asset_files(assets)]
        if len(objects) > MAX_FILES:
            raise ValueError('Too many backup objects')
        records = []
        total = 0
        for src, name in objects:
            size = src.stat().st_size
            total += size
            if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                raise ValueError('Backup exceeds configured size limits')
            h = hashlib.sha256()
            with src.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    h.update(chunk)
            records.append({'path': name, 'sha256': h.hexdigest(), 'bytes': size})
        manifest = {'format': 'quorivio-instance-backup', 'version': VERSION,
                    'created_at': datetime.now(timezone.utc).isoformat(), 'files': records,
                    'privacy': 'contains personal data and uploaded content; encrypt and restrict backup storage'}
        encoded = json.dumps(manifest, sort_keys=True, indent=2).encode('utf-8')
        if len(encoded) > MAX_MANIFEST:
            raise ValueError('Manifest exceeds size limit')
        # Write in the destination filesystem and publish atomically; no partial backup is visible.
        fd, temporary = tempfile.mkstemp(prefix='.quorivio-backup-', suffix='.tmp', dir=destination.parent)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, 'wb') as output:
                with tarfile.open(fileobj=output, mode='w:gz') as archive:
                    info = tarfile.TarInfo('manifest.json')
                    info.size = len(encoded)
                    info.mode = 0o600
                    archive.addfile(info, io.BytesIO(encoded))
                    for (src, name), record in zip(objects, records):
                        if src.stat().st_size != record['bytes']:
                            raise ValueError('Backup input changed during capture')
                        info = archive.gettarinfo(str(src), arcname=name)
                        info.mode = 0o600
                        with src.open('rb') as stream:
                            archive.addfile(info, stream)
                output.flush()
                os.fsync(output.fileno())
            # Detect source mutation during archiving before publishing any snapshot.
            verify(temporary)
            # Exclusive hard-link prevents races with another backup writer.
            os.link(temporary, destination)
        finally:
            pathlib.Path(temporary).unlink(missing_ok=True)
    return manifest


def verify(archive_path):
    with tarfile.open(archive_path, 'r:gz') as archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        if not names or names[0] != 'manifest.json' or len(names) != len(set(names)):
            raise ValueError('Invalid archive member names')
        if len(members) > MAX_FILES + 1:
            raise ValueError('Too many archive members')
        if any(not m.isfile() or m.issym() or m.islnk() for m in members):
            raise ValueError('Non-regular archive entry')
        if members[0].size > MAX_MANIFEST or members[0].size < 1:
            raise ValueError('Invalid manifest size')
        manifest = json.load(archive.extractfile(members[0]))
        if not isinstance(manifest, dict) or manifest.get('format') != 'quorivio-instance-backup' or manifest.get('version') != VERSION:
            raise ValueError('Unsupported backup format')
        declared = manifest.get('files')
        if not isinstance(declared, list) or len(declared) + 1 != len(members) or not declared:
            raise ValueError('Archive/manifest length mismatch')
        total = 0
        for index, (member, record) in enumerate(zip(members[1:], declared)):
            if not isinstance(record, dict):
                raise ValueError('Invalid backup record')
            name, size, checksum = record.get('path'), record.get('bytes'), record.get('sha256')
            if index == 0:
                if name != 'database.dump':
                    raise ValueError('Missing database dump')
            else:
                safe_asset_path(name)
            if not isinstance(size, int) or isinstance(size, bool) or size < 0 or size > MAX_FILE_BYTES:
                raise ValueError('Invalid backup size')
            if not isinstance(checksum, str) or len(checksum) != 64 or any(c not in '0123456789abcdef' for c in checksum):
                raise ValueError('Invalid backup checksum')
            total += size
            if total > MAX_TOTAL_BYTES:
                raise ValueError('Backup exceeds size limit')
            if member.name != name or member.size != size:
                raise ValueError('Manifest file mismatch')
            h = hashlib.sha256()
            with archive.extractfile(member) as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    h.update(chunk)
            if h.hexdigest() != checksum:
                raise ValueError('Checksum mismatch: ' + name)
        return manifest


def restore(archive_path, assets, database_url, confirmation):
    if confirmation != 'RESTORE-QUORIVIO-DATA':
        raise ValueError('Explicit confirmation is required')
    if not database_url:
        raise ValueError('DATABASE_URL is required')
    manifest = verify(archive_path)
    root = pathlib.Path(assets)
    if root.is_symlink() or (root.exists() and (not root.is_dir() or any(root.iterdir()))):
        raise ValueError('Restore requires an EMPTY non-symlink asset directory')
    root.parent.mkdir(parents=True, exist_ok=True)
    if root.parent.is_symlink():
        raise ValueError('Restore asset parent must not be a symlink')
    # Stage and verify all files before touching the database or destination assets.
    with tempfile.TemporaryDirectory(prefix='quorivio-restore-') as tmp, \
         tempfile.TemporaryDirectory(prefix='.quorivio-assets-', dir=root.parent) as staged, \
         tarfile.open(archive_path, 'r:gz') as archive:
        dump = pathlib.Path(tmp) / 'database.dump'
        with dump.open('wb') as output, archive.extractfile('database.dump') as source:
            shutil.copyfileobj(source, output, 1024 * 1024)
        for record in manifest['files'][1:]:
            relative = safe_asset_path(record['path'])
            dest = pathlib.Path(staged) / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as output, archive.extractfile(record['path']) as source:
                shutil.copyfileobj(source, output, 1024 * 1024)
            os.chmod(dest, 0o600)
        # --clean is forbidden: the operator must supply a fresh empty database.
        subprocess.run(['pg_restore', '--exit-on-error', '--no-owner', '--no-acl',
                        '--dbname', database_url, str(dump)], check=True, timeout=3600)
        if root.exists():
            if root.is_symlink() or any(root.iterdir()):
                raise ValueError('Asset directory changed during restore')
            root.rmdir()
        os.rename(staged, root)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='action', required=True)
    backup = actions.add_parser('backup')
    backup.add_argument('--output', required=True)
    backup.add_argument('--assets', required=True)
    verify_command = actions.add_parser('verify')
    verify_command.add_argument('--input', required=True)
    restore_command = actions.add_parser('restore')
    restore_command.add_argument('--input', required=True)
    restore_command.add_argument('--assets', required=True)
    restore_command.add_argument('--confirm', default='')
    args = parser.parse_args()
    try:
        if args.action == 'backup':
            result = make_backup(args.output, args.assets, os.environ.get('DATABASE_URL'))
        elif args.action == 'verify':
            result = verify(args.input)
        else:
            result = restore(args.input, args.assets, os.environ.get('DATABASE_URL'), args.confirm)
        print(json.dumps({'ok': True, 'files': len(result['files']), 'created_at': result['created_at']}, indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, tarfile.TarError) as error:
        print('Backup operation failed: ' + str(error), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
