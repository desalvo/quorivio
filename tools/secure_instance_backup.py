#!/usr/bin/env python3
"""First-class encrypted Quorivio backup, verification and guarded restore.

The operator MUST provide an existing private work directory on an encrypted
filesystem: database dumps and compressed tar files necessarily exist there
for the duration of the operation. Temporary cleartext is never published as a
backup artifact and is removed when the operation finishes. This does not
promise secure erasure from copy-on-write filesystems or physical SSDs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from contextlib import contextmanager

from backup_envelope import decrypt, encrypt, exclusive_output, key_bytes, rotate
from instance_backup import assert_empty_database, make_backup, restore, verify

CONFIRM = 'RESTORE-QUORIVIO-DATA'


def _reject_symlink_ancestors(path: pathlib.Path) -> None:
    """Reject symlink traversal, including ancestors of a workspace/restore root."""
    for component in (path.absolute(), *path.absolute().parents):
        if component.is_symlink():
            raise ValueError('Protected path cannot traverse a symlink')



@contextmanager
def private_workspace(work_dir: pathlib.Path):
    """Reject public, symlinked, unowned or non-regular temporary roots."""
    parent = pathlib.Path(work_dir)
    _reject_symlink_ancestors(parent)
    st = parent.lstat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise ValueError('Work directory must be an existing private owner-only directory')
    with tempfile.TemporaryDirectory(prefix='quorivio-sealed-', dir=parent) as name:
        staging = pathlib.Path(name)
        os.chmod(staging, 0o700)
        yield staging


def _restore_assets_preflight(assets: pathlib.Path):
    if assets.is_symlink() or (assets.exists() and
        (not assets.is_dir() or any(assets.iterdir()))):
        raise ValueError('Restore requires an EMPTY non-symlink asset directory')
    # A symlinked parent could redirect the restored assets outside its scope.
    _reject_symlink_ancestors(assets)


def backup_encrypted(destination: pathlib.Path, assets: pathlib.Path, database_url: str,
                     key_file: pathlib.Path, work_dir: pathlib.Path) -> dict:
    """Capture, verify and publish an authenticated envelope with no raw output."""
    key_bytes(key_file)  # fail before expensive or sensitive database access
    destination = pathlib.Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Refusing to overwrite encrypted backup')
    with private_workspace(work_dir) as staging:
        clear = staging / 'snapshot.tar.gz'
        result = make_backup(clear, assets, database_url)
        if verify(clear) != result:
            raise ValueError('New backup failed verification')
        encrypt(clear, destination, key_file)
        return result


def verify_encrypted(source: pathlib.Path, key_file: pathlib.Path,
                     work_dir: pathlib.Path) -> dict:
    """Authenticate and inspect the plaintext backup; publish no clear archive."""
    with private_workspace(work_dir) as staging:
        clear = staging / 'verify.tar.gz'
        decrypt(source, clear, key_file)
        return verify(clear)


def restore_encrypted(source: pathlib.Path, assets: pathlib.Path, database_url: str,
                      key_file: pathlib.Path, work_dir: pathlib.Path, confirmation: str) -> dict:
    """Refuse unsafe restore targets before decrypting the archive."""
    if confirmation != CONFIRM:
        raise ValueError('Explicit restore confirmation is required')
    if not database_url:
        raise ValueError('DATABASE_URL is required')
    _restore_assets_preflight(pathlib.Path(assets))
    assert_empty_database(database_url)
    with private_workspace(work_dir) as staging:
        clear = staging / 'restore.tar.gz'
        decrypt(source, clear, key_file)
        verify(clear)
        return restore(clear, assets, database_url, confirmation)


def _backup_age_seconds(created_at: str, now: datetime) -> float:
    """Authenticated manifest timestamp is a backup-age *proxy*, never real RPO."""
    try:
        timestamp = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    except (ValueError, AttributeError) as error:
        raise ValueError('Invalid backup creation timestamp') from error
    if timestamp.tzinfo is None:
        raise ValueError('Backup creation timestamp must include a timezone')
    age = (now - timestamp).total_seconds()
    if age < -300:
        raise ValueError('Backup timestamp is in the future')
    return max(0.0, age)


def restore_drill(source: pathlib.Path, assets: pathlib.Path, database_url: str,
                  key_file: pathlib.Path, work_dir: pathlib.Path, confirmation: str,
                  receipt: pathlib.Path, max_age_seconds: float | None = None,
                  max_restore_seconds: float | None = None) -> dict:
    """Practice a guarded real restore and publish a private evidence receipt.

    Does NOT claim RPO/RTO compliance: the duration only measures this command;
    backup age is a proxy for currency, not the point of last committed write.
    Use disposable/stopped-writer destinations, not a live service.
    """
    receipt = pathlib.Path(receipt)
    _reject_symlink_ancestors(receipt.parent)
    if receipt.exists() or receipt.is_symlink():
        raise FileExistsError('Refusing to overwrite DR evidence receipt')
    for name, limit in (('max_age_seconds', max_age_seconds),
                        ('max_restore_seconds', max_restore_seconds)):
        if limit is not None and (not isinstance(limit, (int, float)) or
            not 0 < limit < 365 * 86400):
            raise ValueError(f'Invalid {name}')
    if confirmation != CONFIRM:
        raise ValueError('Explicit restore confirmation is required')
    if not database_url:
        raise ValueError('DATABASE_URL is required')
    _restore_assets_preflight(pathlib.Path(assets))
    # Verify the sealed manifest *before* any database or asset mutation.
    observed = datetime.now(timezone.utc)
    metadata = verify_encrypted(source, key_file, work_dir)
    age = _backup_age_seconds(metadata.get('created_at'), observed)
    if max_age_seconds is not None and age > max_age_seconds:
        raise ValueError('Backup age exceeds the requested pre-restore threshold')
    started = time.monotonic()
    restored = restore_encrypted(source, assets, database_url, key_file,
                                 work_dir, confirmation)
    duration = time.monotonic() - started
    if metadata != restored:
        raise ValueError('Backup manifest changed between preflight and restore')
    receipt_record = {
        'format': 'quorivio-dr-rehearsal', 'version': 1,
        'status': 'restore_completed',
        'observed_at': observed.isoformat(),
        'backup_created_at': metadata['created_at'],
        'backup_age_seconds_at_start': round(age, 3),
        'restore_command_seconds': round(duration, 3),
        'objects_verified': len(metadata['files']),
        'age_threshold_seconds': max_age_seconds,
        'restore_duration_threshold_seconds': max_restore_seconds,
        'age_threshold_met': max_age_seconds is None or age <= max_age_seconds,
        'restore_duration_threshold_met': max_restore_seconds is None or duration <= max_restore_seconds,
        'limitations': 'Not production RPO/RTO: does not measure application cutover, data loss, external infrastructure or recovery SLA.',
    }
    # Output contains no database URL, key, user content, asset paths or token.
    with exclusive_output(receipt) as output:
        output.write((json.dumps(receipt_record, sort_keys=True, indent=2) + '\n').encode('utf-8'))
    # The restore already happened; never imply that a late threshold failure
    # rolls back committed data. Preserve receipt as evidence of failure.
    if not receipt_record['restore_duration_threshold_met']:
        raise ValueError('Restore completed but exceeded the duration threshold; consult DR receipt')
    return receipt_record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    for action in ('backup', 'verify', 'restore', 'rotate', 'drill'):
        command = commands.add_parser(action)
        command.add_argument('--input', required=action in ('verify', 'restore', 'rotate', 'drill'))
        command.add_argument('--output', required=action in ('backup', 'rotate'))
        command.add_argument('--key-file', required=action != 'rotate')
        if action != 'rotate':
            command.add_argument('--work-dir', required=True,
                                 help='private 0700 directory on operator-protected encrypted storage')
        if action in ('backup', 'restore', 'drill'):
            command.add_argument('--assets', required=True)
        if action in ('restore', 'drill'):
            command.add_argument('--confirm', default='')
        if action == 'drill':
            command.add_argument('--receipt', required=True)
            command.add_argument('--max-backup-age-seconds', type=float)
            command.add_argument('--max-restore-seconds', type=float)
        if action == 'rotate':
            command.add_argument('--old-key-file', required=True)
            command.add_argument('--new-key-file', required=True)
    args = parser.parse_args()
    try:
        if args.action == 'backup':
            manifest = backup_encrypted(pathlib.Path(args.output), pathlib.Path(args.assets),
                        os.environ.get('DATABASE_URL', ''), pathlib.Path(args.key_file), pathlib.Path(args.work_dir))
        elif args.action == 'verify':
            manifest = verify_encrypted(pathlib.Path(args.input), pathlib.Path(args.key_file),
                                        pathlib.Path(args.work_dir))
        elif args.action == 'restore':
            manifest = restore_encrypted(pathlib.Path(args.input), pathlib.Path(args.assets),
                        os.environ.get('DATABASE_URL', ''), pathlib.Path(args.key_file),
                        pathlib.Path(args.work_dir), args.confirm)
        elif args.action == 'drill':
            manifest = restore_drill(pathlib.Path(args.input), pathlib.Path(args.assets),
                os.environ.get('DATABASE_URL', ''), pathlib.Path(args.key_file),
                pathlib.Path(args.work_dir), args.confirm, pathlib.Path(args.receipt),
                args.max_backup_age_seconds, args.max_restore_seconds)
            print(json.dumps(manifest))
            return
        else:
            rotate(pathlib.Path(args.input), pathlib.Path(args.output),
                   pathlib.Path(args.old_key_file), pathlib.Path(args.new_key_file))
            manifest = None
        print(json.dumps({'ok': True, 'action': args.action,
            **({'files': len(manifest['files']), 'created_at': manifest['created_at']}
               if manifest is not None else {})}))
    except (OSError, ValueError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired, tarfile.TarError) as exc:
        print(f'Encrypted backup operation failed: {exc}', file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
