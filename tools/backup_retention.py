#!/usr/bin/env python3
"""Fail-closed, authenticated retention for encrypted Quorivio archives.

Dry-run is the default. Destructive apply requires an explicit confirmation,
owner-only legal-hold registry, all available private encryption keys, and a
private work directory on encrypted storage. Every snapshot is authenticated
and its inner manifest verified BEFORE deleting even one backup. Different
archives may use different keys after rotation. No keys or user data are logged.

This remains an offline operator tool. A successful check is not proof of
remote/offsite recoverability, legal compliance, or a production DR SLA.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import stat
import time

from backup_envelope import MAGIC, key_bytes
from secure_instance_backup import private_workspace, verify_encrypted

CONFIRM = 'PRUNE-QUORIVIO-ENCRYPTED-BACKUPS'
DAY = 86400


def _private_dir(directory: pathlib.Path) -> None:
    directory = pathlib.Path(directory)
    for ancestor in (directory.absolute(), *directory.absolute().parents):
        if ancestor.is_symlink():
            raise ValueError('Archive directory must not traverse symlinks')
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('Archive directory must be owner-only 0700')


def _sealed_files(directory: pathlib.Path):
    files = []
    for path in directory.iterdir():
        if not path.name.endswith('.qenc'):
            continue
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError('Unsafe encrypted backup file or symbolic link')
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
        try:
            stat_at_open = os.fstat(fd)
            if (stat_at_open.st_dev, stat_at_open.st_ino) != (info.st_dev, info.st_ino):
                raise ValueError('Backup changed during retention scan')
            if os.read(fd, len(MAGIC)) != MAGIC:
                raise ValueError('File has .qenc suffix but is not Quorivio sealed backup')
        finally:
            os.close(fd)
        files.append((path, info))
    return sorted(files, key=lambda entry: (entry[1].st_mtime_ns, entry[0].name), reverse=True)


def _legal_holds(path: pathlib.Path | None) -> set[str]:
    """An explicitly supplied, private registry of names subject to no deletion.

    Missing or malformed requested registries fail closed. When applying,
    caller MUST supply a registry (even an empty one), so omissions are visible.
    """
    if path is None:
        return set()
    path = pathlib.Path(path)
    for ancestor in (path.absolute(), *path.absolute().parents):
        if ancestor.is_symlink():
            raise ValueError('Legal hold registry cannot traverse symlinks')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError('Legal hold registry must be an owner-only regular file')
        if info.st_size > 128 * 1024:
            raise ValueError('Legal hold registry too large')
        with os.fdopen(fd, 'rb') as handle:
            fd = -1
            payload = handle.read(128 * 1024 + 1)
    finally:
        if fd >= 0:
            os.close(fd)
    try:
        doc = json.loads(payload)
    except (ValueError, UnicodeDecodeError) as error:
        raise ValueError('Invalid legal hold registry JSON') from error
    if not isinstance(doc, dict) or set(doc) != {'version', 'hold'} or type(doc['version']) is not int or doc['version'] != 1 or not isinstance(doc['hold'], list):
        raise ValueError('Invalid legal hold registry schema')
    records = doc['hold']
    if (len(records) > 10000 or len(records) != len(set(x for x in records if isinstance(x, str))) or
            any(not isinstance(x, str) or x in ('', '.', '..') or '/' in x or '\\' in x or '\x00' in x or
                not x.endswith('.qenc') for x in records)):
        raise ValueError('Unsafe or duplicate legal hold backup name')
    return set(records)


def retention_plan(directory: pathlib.Path, *, days: int = 30, min_keep: int = 3,
                   now: float | None = None, holds_file: pathlib.Path | None = None) -> dict:
    if not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= 36500:
        raise ValueError('Retention days must be between 1 and 36500')
    if not isinstance(min_keep, int) or isinstance(min_keep, bool) or not 1 <= min_keep <= 10000:
        raise ValueError('Minimum snapshots must be between 1 and 10000')
    directory = pathlib.Path(directory)
    _private_dir(directory)
    records = _sealed_files(directory)
    holds = _legal_holds(holds_file)
    unknown = holds - {p.name for p, _ in records}
    if unknown:
        raise ValueError('Legal hold references an absent encrypted backup')
    at = time.time() if now is None else now
    if not isinstance(at, (int, float)) or not 0 < at < float('inf'):
        raise ValueError('Invalid retention clock')
    candidates = []
    retained = []
    unheld_count = 0
    for path, info in records:
        # Protected holds do not count toward the min_keep normal copies.
        held = path.name in holds
        if not held:
            unheld_count += 1
        if held or unheld_count <= min_keep or info.st_mtime > at - days * DAY:
            retained.append((path, info))
        else:
            candidates.append((path, info))
    return {'directory': directory, 'candidates': candidates, 'retained': retained,
            'records': records, 'holds': holds, 'holds_file': holds_file,
            'days': days, 'min_keep': min_keep}


def _identity(info: os.stat_result):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_mode, info.st_uid)


def prune_encrypted(directory: pathlib.Path, *, days: int = 30, min_keep: int = 3,
                    apply: bool = False, confirmation: str = '',
                    holds_file: pathlib.Path | None = None,
                    key_files: tuple[pathlib.Path, ...] = (),
                    work_dir: pathlib.Path | None = None) -> dict:
    if apply and confirmation != CONFIRM:
        raise ValueError('Explicit retention confirmation required')
    if apply and (holds_file is None or not key_files or work_dir is None):
        raise ValueError('Apply requires legal hold registry, encryption keys and protected work directory')
    plan = retention_plan(directory, days=days, min_keep=min_keep, holds_file=holds_file)
    verified = 0
    if apply:
        # Check keys and workspace before inspecting or touching backup data.
        for key_file in key_files:
            key_bytes(pathlib.Path(key_file))
        with private_workspace(pathlib.Path(work_dir)):
            pass
        # Validate *all* snapshots: malformed newer copies must never justify
        # deletion of the last genuinely recoverable, older copy.
        for backup, _ in plan['records']:
            for key_file in key_files:
                try:
                    verify_encrypted(backup, pathlib.Path(key_file), pathlib.Path(work_dir))
                    verified += 1
                    break
                except ValueError:
                    # Rotated archives may be encrypted with different keys.
                    continue
            else:
                raise ValueError('Retention refused: snapshot authentication or content verification failed')
        # A concurrent replacement or updated legal hold must prevent deletion.
        if _legal_holds(holds_file) != plan['holds']:
            raise ValueError('Legal hold registry changed during retention validation')
        rescanned = _sealed_files(pathlib.Path(directory))
        if {p.name: _identity(i) for p, i in rescanned} != {
                p.name: _identity(i) for p, i in plan['records']}:
            raise ValueError('Backup set changed during retention validation')
        for path, original in plan['candidates']:
            current = path.lstat()
            if not stat.S_ISREG(current.st_mode) or _identity(current) != _identity(original):
                raise ValueError('Backup changed during retention execution')
        for path, _ in plan['candidates']:
            path.unlink()
    return {
        'action': 'pruned' if apply else 'dry_run', 'retention_days': days,
        'minimum_copies': min_keep,
        'kept': [p.name for p, _ in plan['retained']],
        'legal_holds': sorted(plan['holds']),
        'candidates': [p.name for p, _ in plan['candidates']],
        'authenticated_snapshots': verified,
        'removed_count': len(plan['candidates']) if apply else 0,
        'warning': 'Authentication is not a full offsite restore or production RPO/RTO. Confirm independent backups and legal holds.',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=pathlib.Path, required=True)
    parser.add_argument('--days', type=int, default=30)
    parser.add_argument('--min-keep', type=int, default=3)
    parser.add_argument('--holds-file', type=pathlib.Path,
                        help='owner-only JSON {"version":1,"hold":["archive.qenc"]}; mandatory to apply')
    parser.add_argument('--key-file', type=pathlib.Path, action='append', default=[],
                        help='private encryption key; repeat for key-rotation generations')
    parser.add_argument('--work-dir', type=pathlib.Path,
                        help='existing private 0700 work directory on encrypted storage')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--confirm', default='')
    args = parser.parse_args()
    try:
        print(json.dumps(prune_encrypted(args.directory, days=args.days,
            min_keep=args.min_keep, apply=args.apply, confirmation=args.confirm,
            holds_file=args.holds_file, key_files=tuple(args.key_file),
            work_dir=args.work_dir), indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, f'Backup retention refused: {error}\n')


if __name__ == '__main__':
    main()
